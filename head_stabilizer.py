import cv2
import numpy as np
import mediapipe as mp
import os
import glob

def euclidean_distance(p1, p2):
    """计算两点间的欧几里得距离"""
    return np.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)

class HeadStabilizer:
    def __init__(self, output_size=(512, 512), face_scale=1.5, preserve_background=True, force_reference_size=True, tilt_threshold=5.0):
        # 初始化面部检测模型
        self.mp_face = mp.solutions.face_mesh
        self.face = self.mp_face.FaceMesh(static_image_mode=True, max_num_faces=1, min_detection_confidence=0.5)
        self.mp_face_detection = mp.solutions.face_detection
        self.face_detection = self.mp_face_detection.FaceDetection(min_detection_confidence=0.7)
        
        # 设置输出尺寸和人脸缩放比例
        self.output_size = output_size
        self.face_scale = face_scale
        self.preserve_background = preserve_background
        self.force_reference_size = force_reference_size  # 强制使用参考图片尺寸
        self.tilt_threshold = tilt_threshold  # 头部倾斜角度阈值(度)
        
        # 参考模板数据
        self.ref_eyes = None
        self.ref_center = (output_size[0]//2, output_size[1]//2)  # 输出图像中心
        
        # 调试模式
        self.debug = False
        self.ref_image = None
        self.ref_image_size = None
        
        # 新增：精度控制参数
        self.alignment_tolerance = 2.0  # 对齐容差（像素）
        self.max_iterations = 3  # 最大优化迭代次数
        self.quality_threshold = 0.95  # 对齐质量阈值

    def _get_stable_landmarks(self, image):
        """获取最稳定的关键点组合，专注于眼睛和鼻子的精确定位"""
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # 使用更高精度的检测
        face_mesh = self.mp_face.FaceMesh(
            static_image_mode=True, 
            max_num_faces=1, 
            refine_landmarks=True,  # 启用精细化标记点
            min_detection_confidence=0.7,
            min_tracking_confidence=0.5
        )
        
        results = face_mesh.process(rgb_image)
        if not results.multi_face_landmarks:
            # 降低阈值重试
            face_mesh = self.mp_face.FaceMesh(
                static_image_mode=True, 
                max_num_faces=1, 
                refine_landmarks=True,
                min_detection_confidence=0.3
            )
            results = face_mesh.process(rgb_image)
            if not results.multi_face_landmarks:
                return None

        landmarks = results.multi_face_landmarks[0].landmark
        h, w = image.shape[:2]
        
        # 选择最稳定的关键点 - 只使用眼角和鼻尖
        # 这些点在不同表情下最稳定
        stable_points = {
            # 眼角（最稳定的点）
            'left_eye_outer': (int(landmarks[33].x*w), int(landmarks[33].y*h)),    # 左眼外角
            'left_eye_inner': (int(landmarks[133].x*w), int(landmarks[133].y*h)),  # 左眼内角
            'right_eye_inner': (int(landmarks[362].x*w), int(landmarks[362].y*h)), # 右眼内角  
            'right_eye_outer': (int(landmarks[263].x*w), int(landmarks[263].y*h)), # 右眼外角
            
            # 鼻尖（第二稳定）
            'nose_tip': (int(landmarks[4].x*w), int(landmarks[4].y*h)),            # 鼻尖
        }
        
        # 计算眼睛中心（通过内外角计算，更精确）
        left_eye_center = (
            (stable_points['left_eye_outer'][0] + stable_points['left_eye_inner'][0]) // 2,
            (stable_points['left_eye_outer'][1] + stable_points['left_eye_inner'][1]) // 2
        )
        right_eye_center = (
            (stable_points['right_eye_inner'][0] + stable_points['right_eye_outer'][0]) // 2,
            (stable_points['right_eye_inner'][1] + stable_points['right_eye_outer'][1]) // 2
        )
        
        stable_points['left_eye'] = left_eye_center
        stable_points['right_eye'] = right_eye_center
        
        # 计算眼睛中点（面部中心）
        eye_center = (
            (left_eye_center[0] + right_eye_center[0]) // 2,
            (left_eye_center[1] + right_eye_center[1]) // 2
        )
        stable_points['eye_center'] = eye_center
        
        return stable_points

    def _calculate_similarity_transform(self, src_points, dst_points):
        """计算相似变换矩阵（只包含旋转、缩放、平移，无拉伸）"""
        assert len(src_points) >= 2, "至少需要2个点来计算相似变换"
        
        # 使用最稳定的点对：两个眼睛中心
        src_eye1, src_eye2 = src_points[0], src_points[1]
        dst_eye1, dst_eye2 = dst_points[0], dst_points[1]
        
        # 计算源图像和目标图像的眼睛间距
        src_eye_dist = euclidean_distance(src_eye1, src_eye2)
        dst_eye_dist = euclidean_distance(dst_eye1, dst_eye2)
        
        if src_eye_dist == 0:
            return None
            
        # 计算缩放比例
        scale = dst_eye_dist / src_eye_dist
        
        # 计算旋转角度
        src_angle = np.arctan2(src_eye2[1] - src_eye1[1], src_eye2[0] - src_eye1[0])
        dst_angle = np.arctan2(dst_eye2[1] - dst_eye1[1], dst_eye2[0] - dst_eye1[0])
        rotation_angle = dst_angle - src_angle
        
        # 计算源眼睛中心
        src_center = ((src_eye1[0] + src_eye2[0]) / 2, (src_eye1[1] + src_eye2[1]) / 2)
        dst_center = ((dst_eye1[0] + dst_eye2[0]) / 2, (dst_eye1[1] + dst_eye2[1]) / 2)
        
        # 构建相似变换矩阵
        cos_angle = np.cos(rotation_angle) * scale
        sin_angle = np.sin(rotation_angle) * scale
        
        # 计算平移量
        tx = dst_center[0] - (cos_angle * src_center[0] - sin_angle * src_center[1])
        ty = dst_center[1] - (sin_angle * src_center[0] + cos_angle * src_center[1])
        
        # 构建2x3变换矩阵
        M = np.array([
            [cos_angle, -sin_angle, tx],
            [sin_angle, cos_angle, ty]
        ], dtype=np.float32)
        
        return M

    def _refine_transform_with_additional_points(self, M, src_landmarks, dst_landmarks):
        """使用额外的点来优化变换矩阵"""
        if M is None or 'nose_tip' not in src_landmarks or 'nose_tip' not in dst_landmarks:
            return M
            
        # 使用鼻尖进行验证和微调
        src_nose = np.array([src_landmarks['nose_tip'][0], src_landmarks['nose_tip'][1], 1])
        transformed_nose = M @ src_nose
        dst_nose = np.array(dst_landmarks['nose_tip'])
        
        # 计算鼻尖的对齐误差
        nose_error = euclidean_distance(transformed_nose[:2], dst_nose)
        
        # 如果误差较大，进行微调
        if nose_error > self.alignment_tolerance:
            # 计算鼻尖的偏移量
            offset_x = dst_nose[0] - transformed_nose[0]
            offset_y = dst_nose[1] - transformed_nose[1]
            
            # 对变换矩阵进行微调（只调整平移量）
            M_refined = M.copy()
            M_refined[0, 2] += offset_x * 0.3  # 30%的修正力度
            M_refined[1, 2] += offset_y * 0.3
            
            return M_refined
        
        return M

    def _validate_alignment_quality(self, M, src_landmarks, dst_landmarks):
        """验证对齐质量"""
        if M is None:
            return 0.0
            
        # 计算关键点的对齐误差
        errors = []
        key_points = ['left_eye', 'right_eye', 'nose_tip']
        
        for point_name in key_points:
            if point_name in src_landmarks and point_name in dst_landmarks:
                src_point = np.array([src_landmarks[point_name][0], src_landmarks[point_name][1], 1])
                transformed_point = M @ src_point
                dst_point = np.array(dst_landmarks[point_name])
                error = euclidean_distance(transformed_point[:2], dst_point)
                errors.append(error)
        
        if not errors:
            return 0.0
            
        # 根据输出尺寸动态调整误差阈值
        # 高分辨率图片允许更大的像素误差
        output_diagonal = np.sqrt(self.output_size[0]**2 + self.output_size[1]**2)
        # 基于图片对角线长度的1%作为基准误差
        base_error = output_diagonal * 0.01
        max_acceptable_error = max(15.0, base_error)  # 至少15像素，适应高分辨率
        
        # 计算质量分数（基于平均误差）
        avg_error = np.mean(errors)
        quality_score = max(0, (max_acceptable_error - avg_error) / max_acceptable_error)
        
        # 添加详细的调试信息（仅在调试模式下）
        if self.debug:
            print(f"  质量评估详情:")
            print(f"    平均误差: {avg_error:.2f} 像素")
            print(f"    最大可接受误差: {max_acceptable_error:.2f} 像素")
            print(f"    质量分数: {quality_score:.3f}")
            for i, (point_name, error) in enumerate(zip(key_points, errors)):
                if i < len(errors):
                    print(f"    {point_name}: {error:.2f} 像素")
        
        return quality_score

    def set_reference_eyes_position(self, eye_distance_percent=30):
        """设置参考人脸关键点位置（改进精度）"""
        # 根据输出尺寸和眼睛间距百分比计算参考眼睛位置
        output_w, output_h = self.output_size
        eye_distance = int(output_w * eye_distance_percent / 100)
        
        # 将Y位置向上移动，确保更居中的脸部位置
        eye_y = int(output_h * 0.38)  # 稍微提高位置
        
        # 计算双眼的X位置（在图像宽度居中）
        center_x = output_w // 2
        left_eye_x = center_x - eye_distance // 2
        right_eye_x = center_x + eye_distance // 2
        
        # 计算鼻尖位置（在眼睛下方）
        nose_tip_x = center_x
        nose_tip_y = int(eye_y + 0.08 * output_h)
        
        # 计算眼睛中心
        eye_center_x = center_x
        eye_center_y = eye_y
        
        # 计算眼角位置
        left_eye_outer_x = left_eye_x - int(0.05 * output_w)
        left_eye_inner_x = left_eye_x + int(0.03 * output_w)
        right_eye_inner_x = right_eye_x - int(0.03 * output_w)
        right_eye_outer_x = right_eye_x + int(0.05 * output_w)
        
        self.ref_eyes = {
            'left_eye': (left_eye_x, eye_y),
            'right_eye': (right_eye_x, eye_y),
            'nose_tip': (nose_tip_x, nose_tip_y),
            'eye_center': (eye_center_x, eye_center_y),
            'left_eye_outer': (left_eye_outer_x, eye_y),
            'left_eye_inner': (left_eye_inner_x, eye_y),
            'right_eye_inner': (right_eye_inner_x, eye_y),
            'right_eye_outer': (right_eye_outer_x, eye_y)
        }
        print(f"参考人脸关键点已设置")

    def set_reference_from_image(self, ref_image):
        """从参考图片中提取人脸特征作为对齐基准（改进版）"""
        # 保存参考图像用于显示
        self.ref_image = ref_image.copy()
        self.ref_image_size = ref_image.shape[:2]
        
        # 如果强制使用参考图片尺寸，更新输出尺寸
        if self.force_reference_size:
            self.output_size = (ref_image.shape[1], ref_image.shape[0])
            print(f"已更新输出尺寸为参考图片尺寸: {self.output_size}")
        
        # 获取参考图片中的稳定关键点
        ref_landmarks = self._get_stable_landmarks(ref_image)
        if ref_landmarks is None:
            raise ValueError("参考图片中未检测到面部关键点，请选择清晰的正面人像照片")
        
        # 保存参考图片中的面部关键点
        self.ref_eyes = ref_landmarks
        print(f"从参考图片中提取的稳定面部特征已设置为对齐基准")
        
        return ref_landmarks

    def align_and_crop_face(self, image, crop_size=None, show_landmarks=False):
        """改进的对齐算法 - 使用相似变换确保无拉伸变形"""
        # 确定输出尺寸
        if crop_size is None:
            if self.force_reference_size and self.ref_image_size is not None:
                crop_size = (self.ref_image.shape[1], self.ref_image.shape[0])
            else:
                crop_size = self.output_size
        
        # 获取稳定的人脸关键点
        face_landmarks = self._get_stable_landmarks(image)
        if face_landmarks is None:
            raise ValueError("未检测到面部关键点，请确保图片中有清晰的人脸")
        
        # 如果还没有参考关键点，设置默认的
        if self.ref_eyes is None:
            self.set_reference_eyes_position()
        
        # 准备用于相似变换的关键点对
        # 使用最稳定的眼睛中心点对
        src_points = [
            face_landmarks['left_eye'],
            face_landmarks['right_eye']
        ]
        dst_points = [
            self.ref_eyes['left_eye'],
            self.ref_eyes['right_eye']
        ]
        
        # 计算初始相似变换矩阵
        M = self._calculate_similarity_transform(src_points, dst_points)
        
        if M is None:
            raise ValueError("无法计算变换矩阵")
        
        # 使用额外点进行优化
        M = self._refine_transform_with_additional_points(M, face_landmarks, self.ref_eyes)
        
        # 验证对齐质量
        quality_score = self._validate_alignment_quality(M, face_landmarks, self.ref_eyes)
        
        if quality_score < self.quality_threshold:
            if self.debug:
                print(f"提示：对齐质量为 {quality_score:.2f}，建议检查图片质量和光照条件")
            # 非调试模式下不显示警告，避免干扰用户
        
        # 应用变换 - 使用高质量插值
        if self.preserve_background and not self.force_reference_size:
            h, w = image.shape[:2]
            aligned = cv2.warpAffine(
                image, M, (w, h), 
                flags=cv2.INTER_CUBIC,  # 使用立方插值获得更好质量
                borderMode=cv2.BORDER_REFLECT_101  # 使用镜像边界减少伪影
            )
        else:
            aligned = cv2.warpAffine(
                image, M, (crop_size[0], crop_size[1]), 
                flags=cv2.INTER_CUBIC,
                borderMode=cv2.BORDER_REFLECT_101
            )
        
        # 调试模式
        if show_landmarks or self.debug:
            debug_image = self.draw_landmarks(image, face_landmarks)
            return aligned, debug_image
        
        return aligned

    def _get_face_bbox(self, image):
        """获取人脸边界框"""
        results = self.face_detection.process(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
        if not results.detections:
            return None
        
        detection = results.detections[0]
        bbox = detection.location_data.relative_bounding_box
        
        # 转换为像素坐标
        h, w = image.shape[:2]
        xmin = int(bbox.xmin * w)
        ymin = int(bbox.ymin * h)
        width = int(bbox.width * w)
        height = int(bbox.height * h)
        
        return (xmin, ymin, width, height)

    def _get_eye_points(self, image):
        """保持向后兼容性的方法"""
        return self._get_stable_landmarks(image)

    def draw_landmarks(self, image, landmarks):
        """在图像上绘制面部关键点（用于调试）"""
        debug_img = image.copy()
        
        # 绘制主要关键点
        colors = {
            'left_eye': (0, 255, 0),
            'right_eye': (0, 255, 0), 
            'nose_tip': (255, 0, 0),
            'eye_center': (0, 0, 255),
            'left_eye_outer': (255, 255, 0),
            'left_eye_inner': (255, 255, 0),
            'right_eye_inner': (255, 255, 0),
            'right_eye_outer': (255, 255, 0)
        }
        
        for key, point in landmarks.items():
            color = colors.get(key, (128, 128, 128))
            cv2.circle(debug_img, point, 3, color, -1)
            cv2.putText(debug_img, key, (point[0]+5, point[1]-5), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.3, color, 1)
        
        return debug_img

    def check_head_tilt(self, image):
        """检查头部倾斜度，返回是否端正和倾斜角度"""
        # 获取稳定的面部关键点
        face_landmarks = self._get_stable_landmarks(image)
        if face_landmarks is None:
            return False, None, "未检测到面部关键点"
        
        # 计算眼睛连线与水平线的夹角
        left_eye = face_landmarks['left_eye']
        right_eye = face_landmarks['right_eye']
        
        # 计算双眼连线角度
        dx = right_eye[0] - left_eye[0]
        dy = right_eye[1] - left_eye[1]
        horizontal_angle = np.degrees(np.arctan2(dy, dx))
        
        # 判断是否倾斜
        is_tilted = abs(horizontal_angle) > self.tilt_threshold
        
        tilt_info = {
            'horizontal_angle': horizontal_angle,
            'threshold': self.tilt_threshold
        }
        
        reason = ""
        if is_tilted:
            reason = f"水平倾斜角度{horizontal_angle:.1f}°超过阈值{self.tilt_threshold}°"
        
        return not is_tilted, tilt_info, reason

    def process_batch(self, image_paths, reference_image_path=None, eye_distance_percent=30, filter_tilted=True):
        """批量处理多张图片，可以指定参考图片路径"""
        # 如果提供了参考图片路径，则从参考图片中设置基准
        if reference_image_path and os.path.exists(reference_image_path):
            try:
                ref_img = cv2.imread(reference_image_path)
                if ref_img is not None:
                    self.set_reference_from_image(ref_img)
                    print(f"已使用参考图片: {reference_image_path}")
                else:
                    print(f"无法读取参考图片: {reference_image_path}")
                    self.set_reference_eyes_position(eye_distance_percent)
            except Exception as e:
                print(f"使用参考图片失败: {e}")
                self.set_reference_eyes_position(eye_distance_percent)
        else:
            print(f"警告：未提供参考图片，使用眼睛间距百分比: {eye_distance_percent}%")
            self.set_reference_eyes_position(eye_distance_percent)
        
        aligned_images = []
        successful_images = []
        debug_images = []
        skipped_images = []  # 记录被跳过的图片及原因
        
        # 遍历处理所有图片
        for img_path in image_paths:
            try:
                img = cv2.imread(img_path)
                if img is None:
                    print(f"无法读取图片: {img_path}")
                    skipped_images.append((img_path, "无法读取图片"))
                    continue
                
                # 如果启用了过滤倾斜头部，检查头部是否端正
                if filter_tilted:
                    is_straight, tilt_info, reason = self.check_head_tilt(img)
                    if not is_straight:
                        print(f"跳过倾斜头部的图片: {img_path}, 原因: {reason}")
                        skipped_images.append((img_path, f"头部倾斜: {reason}"))
                        continue
                
                # 处理图片，可选是否返回调试信息
                if self.debug:
                    aligned, debug_img = self.align_and_crop_face(img, show_landmarks=True)
                    debug_images.append(debug_img)
                else:
                    aligned = self.align_and_crop_face(img)
                
                aligned_images.append(aligned)
                successful_images.append(img_path)
                print(f"成功处理: {img_path}")
            except Exception as e:
                print(f"处理图片失败 {img_path}: {e}")
                skipped_images.append((img_path, f"处理失败: {e}"))
                
        if self.debug:
            return aligned_images, successful_images, debug_images, skipped_images
        return aligned_images, successful_images, skipped_images 
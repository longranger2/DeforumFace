import cv2
import numpy as np
import mediapipe as mp
import os
import glob

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
        """获取人脸关键点（改进版：增加可靠性和精度）"""
        # 转换图像颜色
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # 使用FaceMesh进行细粒度特征检测
        results = self.face.process(rgb_image)
        if not results.multi_face_landmarks:
            # 尝试降低阈值再次检测
            self.face = self.mp_face.FaceMesh(static_image_mode=True, max_num_faces=1, min_detection_confidence=0.2)
            results = self.face.process(rgb_image)
            if not results.multi_face_landmarks:
                print(f"无法检测到面部关键点，请确保图片中有清晰的人脸")
                return None
            # 恢复阈值
            self.face = self.mp_face.FaceMesh(static_image_mode=True, max_num_faces=1, min_detection_confidence=0.5)

        # 获取面部关键点坐标
        landmarks = results.multi_face_landmarks[0].landmark
        
        # 左眼关键点（选取更稳定的点：眼角和眼睑中点）
        left_eye_points = [33, 133, 157, 158, 159, 160, 161, 246]
        left_eye_x = sum(landmarks[idx].x for idx in left_eye_points) / len(left_eye_points)
        left_eye_y = sum(landmarks[idx].y for idx in left_eye_points) / len(left_eye_points)
        
        # 右眼关键点
        right_eye_points = [263, 362, 385, 386, 387, 388, 390, 466]
        right_eye_x = sum(landmarks[idx].x for idx in right_eye_points) / len(right_eye_points)
        right_eye_y = sum(landmarks[idx].y for idx in right_eye_points) / len(right_eye_points)
        
        # 鼻尖 (使用多个点的平均以增加稳定性)
        nose_points = [1, 4, 5, 6, 19, 94, 197]
        nose_x = sum(landmarks[idx].x for idx in nose_points) / len(nose_points)
        nose_y = sum(landmarks[idx].y for idx in nose_points) / len(nose_points)
        
        # 嘴巴中心 (使用上下唇中点)
        mouth_points = [0, 13, 14, 17, 37, 87, 178, 317]
        mouth_x = sum(landmarks[idx].x for idx in mouth_points) / len(mouth_points)
        mouth_y = sum(landmarks[idx].y for idx in mouth_points) / len(mouth_points)
        
        # 下巴
        chin_points = [152, 199, 200, 175, 201]
        chin_x = sum(landmarks[idx].x for idx in chin_points) / len(chin_points)
        chin_y = sum(landmarks[idx].y for idx in chin_points) / len(chin_points)
        
        # 额头中心 (使用发际线点)
        forehead_points = [10, 108, 151, 337, 338, 297]
        forehead_x = sum(landmarks[idx].x for idx in forehead_points) / len(forehead_points)
        forehead_y = sum(landmarks[idx].y for idx in forehead_points) / len(forehead_points)
        
        # 转换为像素坐标
        h, w = image.shape[:2]
        
        # 构建返回结果
        face_landmarks = {
            'left_eye': (int(left_eye_x*w), int(left_eye_y*h)),
            'right_eye': (int(right_eye_x*w), int(right_eye_y*h)),
            'nose': (int(nose_x*w), int(nose_y*h)),
            'mouth': (int(mouth_x*w), int(mouth_y*h)),
            'chin': (int(chin_x*w), int(chin_y*h)),
            'forehead': (int(forehead_x*w), int(forehead_y*h))
        }
        
        # 添加更多用于精确对齐的点
        face_landmarks['left_eye_corner'] = (int(landmarks[33].x*w), int(landmarks[33].y*h))
        face_landmarks['right_eye_corner'] = (int(landmarks[263].x*w), int(landmarks[263].y*h))
        face_landmarks['left_eye_inner'] = (int(landmarks[133].x*w), int(landmarks[133].y*h))
        face_landmarks['right_eye_inner'] = (int(landmarks[362].x*w), int(landmarks[362].y*h))
        
        # 添加更多面部特征点以提高对齐精度
        face_landmarks['nose_tip'] = (int(landmarks[4].x*w), int(landmarks[4].y*h))
        face_landmarks['top_nose'] = (int(landmarks[168].x*w), int(landmarks[168].y*h))
        face_landmarks['bottom_nose'] = (int(landmarks[2].x*w), int(landmarks[2].y*h))
        face_landmarks['left_mouth'] = (int(landmarks[61].x*w), int(landmarks[61].y*h))
        face_landmarks['right_mouth'] = (int(landmarks[291].x*w), int(landmarks[291].y*h))
        face_landmarks['upper_lip'] = (int(landmarks[13].x*w), int(landmarks[13].y*h))
        face_landmarks['lower_lip'] = (int(landmarks[14].x*w), int(landmarks[14].y*h))
        
        # 调试用：保存所有关键点
        if self.debug:
            face_landmarks['all_points'] = [(int(landmarks[i].x*w), int(landmarks[i].y*h)) for i in range(len(landmarks))]
        
        return face_landmarks

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
        
        # 计算鼻子位置（在眼睛下方）- 精确定位
        nose_y = int(eye_y + 0.12 * output_h)
        nose_x = center_x
        
        # 计算嘴巴位置（在鼻子下方）
        mouth_y = int(eye_y + 0.22 * output_h)
        mouth_x = center_x
        
        # 计算下巴位置（在嘴巴下方）
        chin_y = int(eye_y + 0.35 * output_h)
        chin_x = center_x
        
        # 计算额头位置（在眼睛上方）
        forehead_y = int(eye_y - 0.15 * output_h)
        forehead_x = center_x
        
        # 增加更多精确参考点
        left_eye_corner_x = left_eye_x - int(0.05 * output_w)
        left_eye_corner_y = eye_y
        right_eye_corner_x = right_eye_x + int(0.05 * output_w)
        right_eye_corner_y = eye_y
        
        left_eye_inner_x = left_eye_x + int(0.03 * output_w)
        left_eye_inner_y = eye_y
        right_eye_inner_x = right_eye_x - int(0.03 * output_w)
        right_eye_inner_y = eye_y
        
        # 添加更多面部特征点的参考位置
        nose_tip_x = center_x
        nose_tip_y = int(eye_y + 0.08 * output_h)
        
        top_nose_x = center_x
        top_nose_y = int(eye_y + 0.04 * output_h)
        
        bottom_nose_x = center_x
        bottom_nose_y = int(eye_y + 0.16 * output_h)
        
        left_mouth_x = center_x - int(0.08 * output_w)
        left_mouth_y = mouth_y
        
        right_mouth_x = center_x + int(0.08 * output_w)
        right_mouth_y = mouth_y
        
        upper_lip_x = center_x
        upper_lip_y = int(eye_y + 0.19 * output_h)
        
        lower_lip_x = center_x
        lower_lip_y = int(eye_y + 0.24 * output_h)
        
        self.ref_eyes = {
            'left_eye': (left_eye_x, eye_y),
            'right_eye': (right_eye_x, eye_y),
            'nose': (nose_x, nose_y),
            'mouth': (mouth_x, mouth_y),
            'chin': (chin_x, chin_y),
            'forehead': (forehead_x, forehead_y),
            'left_eye_corner': (left_eye_corner_x, left_eye_corner_y),
            'right_eye_corner': (right_eye_corner_x, right_eye_corner_y),
            'left_eye_inner': (left_eye_inner_x, left_eye_inner_y),
            'right_eye_inner': (right_eye_inner_x, right_eye_inner_y),
            'nose_tip': (nose_tip_x, nose_tip_y),
            'top_nose': (top_nose_x, top_nose_y),
            'bottom_nose': (bottom_nose_x, bottom_nose_y),
            'left_mouth': (left_mouth_x, left_mouth_y),
            'right_mouth': (right_mouth_x, right_mouth_y),
            'upper_lip': (upper_lip_x, upper_lip_y),
            'lower_lip': (lower_lip_x, lower_lip_y)
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
        
        # 获取参考图片中的人脸关键点
        ref_landmarks = self._get_eye_points(ref_image)
        if ref_landmarks is None:
            raise ValueError("参考图片中未检测到面部关键点，请选择清晰的正面人像照片")
        
        # 保存参考图片中的面部关键点
        self.ref_eyes = ref_landmarks
        print(f"从参考图片中提取的面部特征已设置为对齐基准")
        
        # 返回关键点以便调试
        return ref_landmarks

    def draw_landmarks(self, image, landmarks):
        """在图像上绘制面部关键点（用于调试）"""
        debug_img = image.copy()
        
        # 绘制主要关键点
        for key, point in landmarks.items():
            if key != 'all_points':
                cv2.circle(debug_img, point, 3, (0, 255, 0), -1)
                cv2.putText(debug_img, key, (point[0]+5, point[1]-5), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 0), 1)
        
        # 绘制所有点（如果有）
        if 'all_points' in landmarks and self.debug:
            for i, point in enumerate(landmarks['all_points']):
                if i % 10 == 0:  # 只绘制部分点以避免过于混乱
                    cv2.circle(debug_img, point, 1, (255, 0, 0), -1)
        
        return debug_img

    def align_and_crop_face(self, image, crop_size=None, show_landmarks=False):
        """改进的对齐算法 - 使用多点精确对齐并裁剪照片"""
        # 确定输出尺寸
        if crop_size is None:
            if self.force_reference_size and self.ref_image_size is not None:
                # 如果强制使用参考图片尺寸，使用参考图片的尺寸
                crop_size = (self.ref_image.shape[1], self.ref_image.shape[0])
            else:
                crop_size = self.output_size
            
        # 获取人脸关键点
        face_landmarks = self._get_eye_points(image)
        if face_landmarks is None:
            raise ValueError("未检测到面部关键点，请确保图片中有清晰的人脸")
        
        # 调试模式：显示关键点
        debug_image = None
        if show_landmarks or self.debug:
            debug_image = self.draw_landmarks(image, face_landmarks)
        
        # 如果还没有参考眼睛位置，设置一个
        if self.ref_eyes is None:
            self.set_reference_eyes_position()
            
        # 收集要用于对齐的关键点
        # 确保源图像和目标图像具有相同的关键点集合
        common_landmarks = set(face_landmarks.keys()).intersection(set(self.ref_eyes.keys()))
        common_landmarks = [key for key in common_landmarks if key != 'all_points']  # 排除调试用的点集
        
        # 如果没有足够的共同关键点，使用基本的眼睛和鼻子
        if len(common_landmarks) < 3:
            common_landmarks = ['left_eye', 'right_eye', 'nose']
            
        # 构建源点和目标点数组
        src_points = []
        dst_points = []
        
        # 为不同的点指定不同的权重（通过重复添加重要的点）
        key_points = ['left_eye', 'right_eye', 'nose', 'left_eye_inner', 'right_eye_inner']
        for landmark in common_landmarks:
            src_points.append(face_landmarks[landmark])
            dst_points.append(self.ref_eyes[landmark])
            
            # 对重要点增加权重（通过重复添加）
            if landmark in key_points:
                # 重要点添加3次以增加其权重
                for _ in range(3):
                    src_points.append(face_landmarks[landmark])
                    dst_points.append(self.ref_eyes[landmark])
        
        # 转换为NumPy数组
        src_points = np.float32(src_points)
        dst_points = np.float32(dst_points)
        
        # 使用estimateAffinePartial2D计算变换矩阵
        # 这比手动计算更精确，并使用RANSAC算法排除异常值
        M, inliers = cv2.estimateAffinePartial2D(
            src_points, dst_points, 
            method=cv2.RANSAC, 
            ransacReprojThreshold=3.0,  # 3像素的重投影误差阈值
            maxIters=2000,              # 增加迭代次数以获得更好的结果
            confidence=0.99             # 高置信度
        )
        
        if M is None:
            print("无法计算变换矩阵，使用简单平移")
            # 使用简单的平移作为后备方案
            M = np.array([
                [1, 0, 0],
                [0, 1, 0]
            ], dtype=np.float32)
        
        # 执行仿射变换
        if self.preserve_background and not self.force_reference_size:
            # 如果保留背景且不强制使用参考图片尺寸，使用原图大小
            h, w = image.shape[:2]
            aligned = cv2.warpAffine(image, M, (w, h), flags=cv2.INTER_LANCZOS4, borderMode=cv2.BORDER_REPLICATE)
        else:
            # 否则裁剪为指定大小或参考图片大小
            aligned = cv2.warpAffine(image, M, (crop_size[0], crop_size[1]), flags=cv2.INTER_LANCZOS4, borderMode=cv2.BORDER_REPLICATE)
        
        # 如果是调试模式且有调试图像，返回带关键点的图像
        if show_landmarks or self.debug:
            if debug_image is not None:
                return aligned, debug_image
        
        return aligned
        
    def check_head_tilt(self, image):
        """检查头部倾斜度，返回是否端正和倾斜角度"""
        # 获取面部关键点
        face_landmarks = self._get_eye_points(image)
        if face_landmarks is None:
            return False, None, "未检测到面部关键点"
        
        # 计算眼睛连线与水平线的夹角
        left_eye = face_landmarks['left_eye']
        right_eye = face_landmarks['right_eye']
        
        # 计算双眼连线角度 - 只关注水平倾斜
        dx = right_eye[0] - left_eye[0]
        dy = right_eye[1] - left_eye[1]
        
        # 计算眼睛的水平倾斜角度
        horizontal_angle = np.degrees(np.arctan2(dy, dx))
        
        # 简化判断: 只检查眼睛连线的水平倾斜度
        is_tilted = abs(horizontal_angle) > self.tilt_threshold
        
        # 返回结果和倾斜详情
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
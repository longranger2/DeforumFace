import cv2
import numpy as np
import mediapipe as mp
import os
import glob
from tkinter import Tk, Button, Label, Frame
from PIL import Image, ImageTk

class HeadStabilizer:
    def __init__(self, ref_image_path=None, target_size=(640, 800), face_scale=1.5):
        # 初始化面部检测模型
        self.mp_face = mp.solutions.face_mesh
        self.face = self.mp_face.FaceMesh(static_image_mode=True, max_num_faces=1)
        self.mp_face_detection = mp.solutions.face_detection
        self.face_detection = self.mp_face_detection.FaceDetection(min_detection_confidence=0.5)
        
        # 设置目标尺寸和人脸缩放比例
        self.target_size = target_size
        self.face_scale = face_scale
        
        # 参考模板图像
        if ref_image_path:
            self.set_reference(ref_image_path)
        else:
            self.ref_image = None
            self.ref_face_bbox = None
            self.ref_eyes = None
            self.ref_height = self.target_size[1]
            self.ref_width = self.target_size[0]

    def set_reference(self, image_path):
        """设置参考图像"""
        self.ref_image = cv2.imread(image_path)
        
        # 确保参考图像尺寸正确
        self.ref_image = self._resize_with_aspect_ratio(self.ref_image, self.target_size)
        self.ref_height, self.ref_width = self.ref_image.shape[:2]
        
        # 获取人脸关键点
        self.ref_face_bbox = self._get_face_bbox(self.ref_image)
        self.ref_eyes = self._get_eye_points(self.ref_image)
        
        if self.ref_eyes is None or self.ref_face_bbox is None:
            raise ValueError(f"未能在参考图像中检测到面部: {image_path}")
            
        return self.ref_image
    
    def _resize_with_aspect_ratio(self, image, target_size):
        """保持宽高比的调整图像尺寸"""
        height, width = image.shape[:2]
        target_width, target_height = target_size
        
        # 计算缩放比例
        scale = min(target_width / width, target_height / height)
        new_width = int(width * scale)
        new_height = int(height * scale)
        
        # 调整图像大小
        resized = cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_AREA)
        
        # 创建目标尺寸的画布
        result = np.zeros((target_height, target_width, 3), dtype=np.uint8)
        
        # 计算偏移量使图像居中
        offset_x = (target_width - new_width) // 2
        offset_y = (target_height - new_height) // 2
        
        # 将调整大小的图像放在画布中心
        result[offset_y:offset_y+new_height, offset_x:offset_x+new_width] = resized
        
        return result
    
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
        """获取双眼中心坐标"""
        results = self.face.process(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
        if not results.multi_face_landmarks:
            return None

        # 左眼（landmark索引：159）
        # 右眼（landmark索引：386）
        landmarks = results.multi_face_landmarks[0].landmark
        left_eye = (landmarks[159].x, landmarks[159].y)
        right_eye = (landmarks[386].x, landmarks[386].y)
        
        # 鼻尖（landmark索引：1）
        nose = (landmarks[1].x, landmarks[1].y)
        
        # 转换为像素坐标
        h, w = image.shape[:2]
        return np.array([
            (left_eye[0]*w, left_eye[1]*h),
            (right_eye[0]*w, right_eye[1]*h),
            (nose[0]*w, nose[1]*h)
        ])

    def _calculate_transform(self, src_eyes):
        """计算仿射变换矩阵"""
        # 使用眼睛和鼻尖三点进行仿射变换
        src_points = src_eyes
        dst_points = self.ref_eyes
        
        # 计算仿射变换矩阵
        M = cv2.getAffineTransform(
            src_points.astype(np.float32)[:3],
            dst_points.astype(np.float32)[:3]
        )
        
        return M

    def align_image(self, src_image):
        """执行对齐操作"""
        # 先调整输入图像大小
        src_image = self._resize_with_aspect_ratio(src_image, self.target_size)
        
        # 获取人脸关键点
        src_eyes = self._get_eye_points(src_image)
        src_face_bbox = self._get_face_bbox(src_image)
        
        if src_eyes is None or src_face_bbox is None:
            raise ValueError("未检测到面部关键点")
        
        # 计算变换矩阵
        M = self._calculate_transform(src_eyes)
        
        # 执行仿射变换
        aligned = cv2.warpAffine(
            src_image, M, (self.ref_width, self.ref_height),
            flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT,
            borderValue=(255, 255, 255)  # 使用白色填充边缘
        )
        
        return aligned
    
    def process_batch(self, image_paths):
        """批量处理多张图片"""
        aligned_images = []
        
        # 如果没有设置参考图像，使用第一张作为参考
        if self.ref_image is None and image_paths:
            print(f"使用第一张图片作为参考模板: {image_paths[0]}")
            self.set_reference(image_paths[0])
            aligned_images.append(self.ref_image)  # 第一张无需对齐
            image_paths = image_paths[1:]  # 跳过第一张
            
        for img_path in image_paths:
            try:
                img = cv2.imread(img_path)
                if img is None:
                    print(f"无法读取图片: {img_path}")
                    continue
                    
                aligned = self.align_image(img)
                aligned_images.append(aligned)
                print(f"成功处理: {img_path}")
            except Exception as e:
                print(f"处理图片失败 {img_path}: {e}")
                
        return aligned_images


class HeadAlignmentViewer:
    def __init__(self, folder_path, target_size=(640, 800)):
        # 初始化窗口
        self.root = Tk()
        self.root.title("头部对齐查看器")
        
        # 设置窗口大小
        self.target_size = target_size
        
        # 查找所有图片
        self.image_paths = glob.glob(os.path.join(folder_path, "*.jpg")) + \
                          glob.glob(os.path.join(folder_path, "*.jpeg")) + \
                          glob.glob(os.path.join(folder_path, "*.png"))
        
        if not self.image_paths:
            raise ValueError(f"在 {folder_path} 中未找到图片")
            
        # 初始化稳定器
        self.stabilizer = HeadStabilizer(target_size=self.target_size)
        
        # 处理所有图片
        print(f"开始处理共 {len(self.image_paths)} 张图片...")
        self.processed_images = self.stabilizer.process_batch(self.image_paths)
        print(f"处理完成，成功处理 {len(self.processed_images)} 张图片")
        
        # 当前显示的图片索引
        self.current_index = 0
        
        # 创建UI元素
        self.img_label = Label(self.root)
        self.img_label.pack(pady=10)
        
        button_frame = Frame(self.root)
        button_frame.pack(pady=5)
        
        prev_button = Button(button_frame, text="上一张", command=self.prev_image, width=10, height=2)
        prev_button.pack(side="left", padx=10)
        
        next_button = Button(button_frame, text="下一张", command=self.next_image, width=10, height=2)
        next_button.pack(side="left", padx=10)
        
        # 添加帮助信息
        help_text = "使用按钮或键盘方向键和空格键切换图片"
        help_label = Label(self.root, text=help_text, font=("Arial", 10))
        help_label.pack(pady=5)
        
        # 显示图片计数
        self.counter_label = Label(self.root, text=f"1/{len(self.processed_images)}", font=("Arial", 10))
        self.counter_label.pack(pady=5)
        
        # 添加键盘快捷键
        self.root.bind('<Left>', lambda event: self.prev_image())
        self.root.bind('<Right>', lambda event: self.next_image())
        self.root.bind('<space>', lambda event: self.next_image())
        
        # 显示第一张图片
        self.update_display()
        
    def update_display(self):
        """更新显示的图片"""
        img = self.processed_images[self.current_index]
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        pil_img = Image.fromarray(img_rgb)
        tk_img = ImageTk.PhotoImage(image=pil_img)
        
        self.img_label.configure(image=tk_img)
        self.img_label.image = tk_img  # 防止垃圾回收
        self.counter_label.configure(text=f"{self.current_index+1}/{len(self.processed_images)}")
        self.root.title(f"头部对齐查看器 - {self.current_index+1}/{len(self.processed_images)}")
        
    def next_image(self):
        """显示下一张图片"""
        self.current_index = (self.current_index + 1) % len(self.processed_images)
        self.update_display()
        
    def prev_image(self):
        """显示上一张图片"""
        self.current_index = (self.current_index - 1) % len(self.processed_images)
        self.update_display()
        
    def run(self):
        """启动查看器"""
        self.root.mainloop()


# 使用示例
if __name__ == "__main__":
    # 方法1: 单独处理两张图片
    # stabilizer = HeadStabilizer("1.jpg")  # 模板图片
    # input_img = cv2.imread("2.jpg")
    # aligned_img = stabilizer.align_image(input_img)
    # cv2.imshow("Original", input_img)
    # cv2.imshow("Aligned", aligned_img)
    # cv2.waitKey(0)
    
    # 方法2: 查看器模式处理文件夹中的所有照片
    viewer = HeadAlignmentViewer("/Users/loneranger/Project/DeforumAI/photos")
    viewer.run()
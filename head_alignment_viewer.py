import cv2
import numpy as np
import os
import glob
import threading
import queue
import time
from tkinter import Tk, Button, Label, Frame, Scale, HORIZONTAL, IntVar, StringVar, ttk, Checkbutton, messagebox, Scrollbar, Canvas, filedialog
from PIL import Image, ImageTk

from head_stabilizer import HeadStabilizer

class HeadAlignmentViewer:
    def __init__(self, folder_path, output_size=(512, 512)):
        # 初始化窗口
        self.root = Tk()
        self.root.title("头部对齐查看器")
        self.root.geometry("900x700")  # 设置更大的窗口尺寸
        
        # 保存文件夹路径和尺寸设置
        self.folder_path = folder_path
        self.output_size = output_size
        
        # 创建多线程任务队列
        self.task_queue = queue.Queue()
        self.is_processing = False
        
        # 查找所有图片
        self.image_paths = glob.glob(os.path.join(folder_path, "*.jpg")) + \
                          glob.glob(os.path.join(folder_path, "*.jpeg")) + \
                          glob.glob(os.path.join(folder_path, "*.png"))
        
        if not self.image_paths:
            raise ValueError(f"在 {folder_path} 中未找到图片")
        
        # 创建主框架
        main_frame = Frame(self.root, bg="#333333")
        main_frame.pack(fill="both", expand=True)
        
        # 左侧控制面板
        control_frame = Frame(main_frame, width=270, borderwidth=2, relief="groove", bg="#333333")
        control_frame.pack(side="left", fill="y", padx=10, pady=10)
        control_frame.pack_propagate(False)  # 固定宽度
        
        # 右侧显示区域
        display_frame = Frame(main_frame, bg="#222222")
        display_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)
            
        # 添加标题
        Label(control_frame, text="头部对齐查看器", font=("Arial", 16, "bold"), 
              bg="#333333", fg="white").pack(pady=10)
        
        # 创建设置面板
        settings_frame = Frame(control_frame, bg="#333333")
        settings_frame.pack(fill="x", pady=5)
        
        # 眼睛间距调整滑块
        self.eye_distance = IntVar(value=30)  # 默认为照片宽度的30%
        
        eye_frame = Frame(settings_frame, bg="#333333")
        eye_frame.pack(fill="x", pady=5)
        
        Label(eye_frame, text="眼睛间距:", font=("Arial", 10), 
              bg="#333333", fg="white").pack(anchor="w")
        Label(eye_frame, text="决定人脸在画面中的大小比例", font=("Arial", 8), 
              bg="#333333", fg="#AAAAAA").pack(anchor="w")
        
        # 添加当前值显示
        self.eye_distance_display = StringVar(value="30%")
        Label(eye_frame, textvariable=self.eye_distance_display, 
              font=("Arial", 10, "bold"), bg="#333333", fg="#00FF00").pack(anchor="e")
        
        self.eye_slider = Scale(eye_frame, from_=15, to=45, orient=HORIZONTAL, 
                              variable=self.eye_distance, length=240,
                              command=self.update_eye_distance_display,
                              bg="#444444", fg="white", highlightthickness=0)
        self.eye_slider.pack(fill="x", padx=5)
        
        # 添加头部倾斜度检测设置
        tilt_frame = Frame(settings_frame, bg="#333333")
        tilt_frame.pack(fill="x", pady=5)
        
        Label(tilt_frame, text="头部倾斜检测:", font=("Arial", 10), 
              bg="#333333", fg="white").pack(anchor="w")
        Label(tilt_frame, text="过滤掉头部不端正的照片", font=("Arial", 8), 
              bg="#333333", fg="#AAAAAA").pack(anchor="w")
        
        # 启用头部倾斜筛选
        self.filter_tilted = IntVar(value=1)  # 默认开启
        Checkbutton(tilt_frame, text="启用头部倾斜筛选", variable=self.filter_tilted,
                   bg="#333333", fg="white", selectcolor="#555555",
                   activebackground="#333333", activeforeground="white").pack(anchor="w", pady=2)
        
        # 头部倾斜角度阈值
        tilt_slider_frame = Frame(tilt_frame, bg="#333333")
        tilt_slider_frame.pack(fill="x", pady=2)
        
        Label(tilt_slider_frame, text="倾斜阈值:", bg="#333333", fg="white").pack(side="left")
        
        self.tilt_threshold = IntVar(value=5)  # 默认5度
        self.tilt_threshold_display = StringVar(value="5°")
        Label(tilt_slider_frame, textvariable=self.tilt_threshold_display, 
              bg="#333333", fg="#00FF00", width=4).pack(side="right")
        
        self.tilt_slider = Scale(tilt_frame, from_=1, to=30, orient=HORIZONTAL, 
                               variable=self.tilt_threshold, length=240,
                               command=self.update_tilt_threshold_display,
                               bg="#444444", fg="white", highlightthickness=0)
        self.tilt_slider.pack(fill="x", padx=5)
        
        # 创建参数调整区域
        params_frame = Frame(control_frame, bg="#333333")
        params_frame.pack(fill="x", pady=5)
        
        # 参考图片选择按钮
        reference_frame = Frame(params_frame, bg="#333333")
        reference_frame.pack(fill="x", pady=5)
        
        Label(reference_frame, text="参考图片设置:", font=("Arial", 10, "bold"), 
              bg="#333333", fg="white").pack(anchor="w")
        
        self.ref_button = Button(reference_frame, text="选择参考图片", 
               command=self.select_reference_image, width=20, height=1,
               bg="#555555", fg="white", activebackground="#777777")
        self.ref_button.pack(pady=5)
        
        # 标签显示当前参考图片
        self.ref_image_label = Label(reference_frame, text="未选择参考图片", 
                                   wraplength=230, fg="red", bg="#333333")
        self.ref_image_label.pack(pady=2)
        
        # 强制使用参考图片选项
        self.force_reference_size = IntVar(value=1)  # 默认选中
        Checkbutton(reference_frame, text="强制使用参考图片尺寸（推荐）", 
                   variable=self.force_reference_size, 
                   bg="#333333", fg="white", selectcolor="#555555",
                   activebackground="#333333", activeforeground="white").pack(anchor="w", pady=2)
        
        # 保留背景选项
        self.preserve_bg = IntVar(value=0)  # 默认不选中
        Checkbutton(params_frame, text="保留背景（不推荐）", variable=self.preserve_bg,
                   command=self.toggle_preserve_bg,
                   bg="#333333", fg="white", selectcolor="#555555",
                   activebackground="#333333", activeforeground="white").pack(anchor="w", pady=5)
        
        # 添加调试模式选项
        self.debug_mode = IntVar(value=0)
        Checkbutton(params_frame, text="调试模式（显示关键点）", variable=self.debug_mode,
                   command=self.toggle_debug_mode,
                   bg="#333333", fg="white", selectcolor="#555555",
                   activebackground="#333333", activeforeground="white").pack(anchor="w", pady=5)
        
        # 操作按钮区
        buttons_frame = Frame(control_frame, bg="#333333")
        buttons_frame.pack(fill="x", pady=10)
        
        # 重新处理按钮
        self.process_all_button = Button(buttons_frame, text="重新处理所有图片", 
               command=self.reprocess_images, width=20, height=1,
               bg="#4CAF50", fg="white", activebackground="#45a049")
        self.process_all_button.pack(pady=5)
        
        # 处理当前图片按钮
        self.process_current_button = Button(buttons_frame, text="仅处理当前图片", 
               command=self.process_current_image, width=20, height=1,
               bg="#2196F3", fg="white", activebackground="#0b7dda")
        self.process_current_button.pack(pady=5)
               
        # 保存按钮
        self.save_current_button = Button(buttons_frame, text="保存当前图片", 
               command=self.save_current_image, width=20, height=1,
               bg="#FF9800", fg="white", activebackground="#e68a00")
        self.save_current_button.pack(pady=5)
               
        self.save_all_button = Button(buttons_frame, text="保存所有图片", 
               command=self.save_all_images, width=20, height=1,
               bg="#FF5722", fg="white", activebackground="#e64a19")
        self.save_all_button.pack(pady=5)
        
        # 添加查看被跳过的图片按钮
        self.show_skipped_button = Button(buttons_frame, text="查看被跳过的图片", 
                                       command=self.show_skipped_images, width=20, height=1,
                                       bg="#9C27B0", fg="white", activebackground="#7B1FA2")
        self.show_skipped_button.pack(pady=5)
        
        # 添加进度条
        progress_frame = Frame(control_frame, bg="#333333")
        progress_frame.pack(fill="x", pady=10)
        
        Label(progress_frame, text="处理进度:", bg="#333333", fg="white").pack(anchor="w")
        self.progress_var = IntVar()
        self.progress_bar = ttk.Progressbar(progress_frame, orient="horizontal", 
                                          length=240, mode="determinate", 
                                          variable=self.progress_var)
        self.progress_bar.pack(fill="x", padx=5, pady=2)
        
        # 添加状态显示区域
        status_frame = Frame(control_frame, bg="#333333")
        status_frame.pack(fill="x", side="bottom", pady=5)
        
        self.status_label = Label(status_frame, text="准备就绪", font=("Arial", 10), 
                                wraplength=230, bg="#333333", fg="#AAAAAA")
        self.status_label.pack(pady=5)
        
        # 图片计数显示
        self.counter_label = Label(status_frame, text="0/0", font=("Arial", 10, "bold"),
                                 bg="#333333", fg="white")
        self.counter_label.pack(pady=5)
        
        # 在显示区域创建导航区域
        nav_frame = Frame(display_frame, bg="#222222")
        nav_frame.pack(side="bottom", fill="x", pady=5)
        
        self.prev_button = Button(nav_frame, text="上一张", command=self.prev_image, 
                                width=10, height=1, bg="#555555", fg="white")
        self.prev_button.pack(side="left", padx=20)
        
        self.next_button = Button(nav_frame, text="下一张", command=self.next_image, 
                                width=10, height=1, bg="#555555", fg="white")
        self.next_button.pack(side="right", padx=20)
        
        # 创建图像显示区域
        self.img_frame = Frame(display_frame, bg="#222222")
        self.img_frame.pack(fill="both", expand=True)
        
        self.img_label = Label(self.img_frame, bg="#222222")
        self.img_label.pack(expand=True)
        
        # 初始化稳定器
        self.stabilizer = HeadStabilizer(output_size=self.output_size, 
                                        preserve_background=bool(self.preserve_bg.get()),
                                        force_reference_size=bool(self.force_reference_size.get()),
                                        tilt_threshold=float(self.tilt_threshold.get()))
        
        # 参考图片路径
        self.reference_image_path = None
        
        # 当前显示的图片索引
        self.current_index = 0
        
        # 处理结果
        self.processed_images = []
        self.successful_paths = []
        self.debug_images = []
        self.skipped_images = []  # 存储被跳过的图片及原因
        
        # 添加键盘快捷键
        self.root.bind('<Left>', lambda event: self.prev_image())
        self.root.bind('<Right>', lambda event: self.next_image())
        self.root.bind('<space>', lambda event: self.next_image())
        
        # 首先要求选择参考图片
        self.update_status("请先选择一张参考图片")
        self.root.after(500, self.prompt_for_reference_image)
        
        # 启动工作线程
        self.start_worker_thread()
        
    def update_eye_distance_display(self, value):
        """更新眼睛间距显示值"""
        self.eye_distance_display.set(f"{int(value)}%")
    
    def update_tilt_threshold_display(self, value):
        """更新倾斜阈值显示值"""
        self.tilt_threshold_display.set(f"{int(value)}°")
        # 同时更新稳定器的阈值
        self.stabilizer.tilt_threshold = float(value)
    
    def start_worker_thread(self):
        """启动工作线程处理队列中的任务"""
        threading.Thread(target=self.worker_thread, daemon=True).start()
        
    def worker_thread(self):
        """工作线程函数，处理队列中的任务"""
        while True:
            try:
                # 获取任务
                task, args, kwargs = self.task_queue.get(block=True)
                
                # 设置处理中标志
                self.is_processing = True
                
                # 禁用按钮
                self.root.after(0, self.disable_buttons)
                
                # 执行任务
                result = task(*args, **kwargs)
                
                # 处理完成
                self.is_processing = False
                
                # 启用按钮
                self.root.after(0, self.enable_buttons)
                
                # 标记任务完成
                self.task_queue.task_done()
                
                # 设置进度条为100%
                self.root.after(0, lambda: self.progress_var.set(100))
                
                # 更新UI (如果需要)
                if result:
                    callback, callback_args = result
                    self.root.after(0, lambda: callback(*callback_args))
                    
            except Exception as e:
                # 处理错误
                self.is_processing = False
                self.root.after(0, lambda: self.update_status(f"处理出错: {e}"))
                self.root.after(0, self.enable_buttons)
                self.task_queue.task_done()
                
                # 重置进度条
                self.root.after(0, lambda: self.progress_var.set(0))
    
    def disable_buttons(self):
        """禁用所有按钮"""
        for button in [self.process_all_button, self.process_current_button, 
                      self.save_current_button, self.save_all_button,
                      self.prev_button, self.next_button, self.ref_button, self.show_skipped_button]:
            button.config(state="disabled")
    
    def enable_buttons(self):
        """启用所有按钮"""
        for button in [self.process_all_button, self.process_current_button, 
                      self.save_current_button, self.save_all_button,
                      self.prev_button, self.next_button, self.ref_button, self.show_skipped_button]:
            button.config(state="normal")
        
    def prompt_for_reference_image(self):
        """提示用户选择参考图片"""
        response = messagebox.askyesno("选择参考图片", 
                                     "要获得最佳对齐效果，建议先选择一张参考图片。\n是否现在选择？")
        if response:
            self.select_reference_image()
        else:
            self.update_status("警告：未选择参考图片，将使用默认参数")
            self.add_task(self.process_images_task, callback=self.update_after_processing)

    def toggle_preserve_bg(self):
        """切换保留背景选项并给出警告"""
        if self.preserve_bg.get() == 1:
            messagebox.showwarning("注意", "保留背景可能导致照片尺寸不一致，不推荐选择此选项")
        
        # 更新稳定器设置
        self.stabilizer.preserve_background = bool(self.preserve_bg.get())
    
    def toggle_debug_mode(self):
        """切换调试模式"""
        self.stabilizer.debug = bool(self.debug_mode.get())
        self.update_status(f"调试模式: {'开启' if self.stabilizer.debug else '关闭'}")
        
        # 如果启用调试模式，重新处理当前图片
        if self.stabilizer.debug and self.processed_images:
            self.process_current_image()
    
    def update_status(self, message):
        """更新状态信息"""
        self.status_label.config(text=message)
        self.root.update_idletasks()  # 强制更新界面
        
    def add_task(self, task, *args, callback=None, **kwargs):
        """添加任务到队列"""
        if self.is_processing:
            messagebox.showinfo("提示", "当前有任务正在处理中，请稍候...")
            return
            
        # 重置进度条
        self.progress_var.set(0)
        
        # 添加任务到队列
        self.task_queue.put((task, args, kwargs))
    
    def update_progress(self, value):
        """更新进度条"""
        self.progress_var.set(value)
        self.root.update_idletasks()
    
    def process_images_task(self):
        """处理所有图片的任务函数"""
        try:
            # 检查是否已选择参考图片
            if not self.reference_image_path:
                self.update_status("警告：未选择参考图片，对齐效果可能不理想")
            
            self.update_status(f"开始处理共 {len(self.image_paths)} 张图片...")
            
            # 获取当前设置
            filter_tilted = bool(self.filter_tilted.get())
            
            # 根据是否启用调试模式选择不同的处理方法
            total = len(self.image_paths)
            
            if self.stabilizer.debug:
                processed_images = []
                successful_paths = []
                debug_images = []
                skipped_images = []
                
                for i, img_path in enumerate(self.image_paths):
                    try:
                        img = cv2.imread(img_path)
                        if img is None:
                            skipped_images.append((img_path, "无法读取图片"))
                            continue
                        
                        # 如果启用了头部倾斜筛选
                        if filter_tilted:
                            is_straight, tilt_info, reason = self.stabilizer.check_head_tilt(img)
                            if not is_straight:
                                skipped_images.append((img_path, f"头部倾斜: {reason}"))
                                self.update_status(f"跳过倾斜头部: {os.path.basename(img_path)}")
                                continue
                            
                        aligned, debug_img = self.stabilizer.align_and_crop_face(img, show_landmarks=True)
                        processed_images.append(aligned)
                        successful_paths.append(img_path)
                        debug_images.append(debug_img)
                        
                        # 更新进度
                        progress = int((i + 1) / total * 100)
                        self.root.after(0, lambda p=progress: self.update_progress(p))
                        self.root.after(0, lambda p=i+1, t=total: 
                                       self.update_status(f"处理进度: {p}/{t}"))
                        
                    except Exception as e:
                        print(f"处理图片失败 {img_path}: {e}")
                        skipped_images.append((img_path, f"处理失败: {e}"))
                
                self.processed_images = processed_images
                self.successful_paths = successful_paths
                self.debug_images = debug_images
                self.skipped_images = skipped_images
            else:
                processed_images = []
                successful_paths = []
                skipped_images = []
                
                for i, img_path in enumerate(self.image_paths):
                    try:
                        img = cv2.imread(img_path)
                        if img is None:
                            skipped_images.append((img_path, "无法读取图片"))
                            continue
                        
                        # 如果启用了头部倾斜筛选
                        if filter_tilted:
                            is_straight, tilt_info, reason = self.stabilizer.check_head_tilt(img)
                            if not is_straight:
                                skipped_images.append((img_path, f"头部倾斜: {reason}"))
                                self.update_status(f"跳过倾斜头部: {os.path.basename(img_path)}")
                                continue
                            
                        aligned = self.stabilizer.align_and_crop_face(img)
                        processed_images.append(aligned)
                        successful_paths.append(img_path)
                        
                        # 更新进度
                        progress = int((i + 1) / total * 100)
                        self.root.after(0, lambda p=progress: self.update_progress(p))
                        self.root.after(0, lambda p=i+1, t=total: 
                                       self.update_status(f"处理进度: {p}/{t}"))
                        
                    except Exception as e:
                        print(f"处理图片失败 {img_path}: {e}")
                        skipped_images.append((img_path, f"处理失败: {e}"))
                
                self.processed_images = processed_images
                self.successful_paths = successful_paths
                self.skipped_images = skipped_images
                
            skipped_count = len(self.skipped_images)
            success_count = len(self.processed_images)
            
            if skipped_count > 0:
                self.update_status(f"处理完成，成功: {success_count}张，跳过: {skipped_count}张")
                # 启用查看被跳过图片的按钮
                self.root.after(0, lambda: self.show_skipped_button.config(state="normal"))
            else:
                self.update_status(f"处理完成，成功处理 {success_count} 张图片")
            
            return None
            
        except Exception as e:
            self.update_status(f"处理图片时出错: {e}")
            return None
    
    def update_after_processing(self):
        """处理完成后更新显示"""
        # 显示第一张图片
        if self.processed_images:
            self.current_index = 0
            self.update_display()
    
    def select_reference_image(self):
        """选择参考图片"""
        # 打开文件选择对话框
        ref_path = filedialog.askopenfilename(
            title="选择参考图片",
            filetypes=[("图片文件", "*.jpg *.jpeg *.png")],
            initialdir=self.folder_path
        )
        
        if ref_path:
            self.reference_image_path = ref_path
            self.ref_image_label.config(text=f"已选择: {os.path.basename(ref_path)}", fg="green")
            self.update_status(f"已选择参考图片: {os.path.basename(ref_path)}")
            
            # 更新稳定器设置
            self.stabilizer.force_reference_size = bool(self.force_reference_size.get())
            
            # 询问是否立即重新处理图片
            if messagebox.askyesno("确认", "是否立即使用此参考图片处理所有图片?"):
                self.reprocess_images()
        else:
            self.update_status("未选择参考图片")
            
    def reprocess_images(self):
        """根据当前设置重新处理图片"""
        # 检查是否已选择参考图片
        if not self.reference_image_path and self.force_reference_size.get() == 1:
            response = messagebox.askyesno("警告", 
                                         "您启用了强制参考图片尺寸，但尚未选择参考图片。\n是否先选择参考图片？")
            if response:
                self.select_reference_image()
                return
        
        # 更新稳定器设置
        eye_distance = self.eye_distance.get()
        preserve_bg = bool(self.preserve_bg.get())
        force_reference = bool(self.force_reference_size.get())
        
        self.stabilizer.preserve_background = preserve_bg
        self.stabilizer.force_reference_size = force_reference
        
        # 记录设置日志
        settings_info = f"眼睛间距: {eye_distance}%, 保留背景: {'是' if preserve_bg else '否'}, 强制参考尺寸: {'是' if force_reference else '否'}"
        if self.reference_image_path:
            settings_info += f", 参考图片: {os.path.basename(self.reference_image_path)}"
        self.update_status(f"使用新的设置重新处理 - {settings_info}")
            
        # 添加处理任务
        self.add_task(self.process_images_task, callback=self.update_after_processing)
        
    def save_current_image(self):
        """保存当前显示的图片"""
        if not self.processed_images or self.current_index >= len(self.processed_images):
            self.update_status("没有处理过的图片可以保存")
            return
            
        output_dir = os.path.join(self.folder_path, "aligned")
        os.makedirs(output_dir, exist_ok=True)
        
        # 获取原始文件名
        original_path = self.successful_paths[self.current_index] if self.current_index < len(self.successful_paths) else "unknown.jpg"
        base_name = os.path.basename(original_path)
        
        # 保存图片
        output_path = os.path.join(output_dir, f"aligned_{base_name}")
        cv2.imwrite(output_path, self.processed_images[self.current_index])
        self.update_status(f"已保存图片: aligned_{base_name}")
    
    def save_all_images_task(self):
        """保存所有处理过的图片的任务函数"""
        if not self.processed_images:
            self.update_status("没有处理过的图片可以保存")
            return None
            
        output_dir = os.path.join(self.folder_path, "aligned")
        os.makedirs(output_dir, exist_ok=True)
        
        count = 0
        total = len(self.processed_images)
        
        for i, img in enumerate(self.processed_images):
            try:
                # 获取原始文件名
                if i < len(self.successful_paths):
                    original_path = self.successful_paths[i]
                    base_name = os.path.basename(original_path)
                else:
                    base_name = f"unknown_{i}.jpg"
                
                # 保存图片
                output_path = os.path.join(output_dir, f"aligned_{base_name}")
                cv2.imwrite(output_path, img)
                count += 1
                
                # 更新进度
                progress = int((i + 1) / total * 100)
                self.root.after(0, lambda p=progress: self.update_progress(p))
                self.root.after(0, lambda p=i+1, t=total: 
                               self.update_status(f"保存进度: {p}/{t}"))
                
            except Exception as e:
                print(f"保存图片失败 {i}: {e}")
        
        self.update_status(f"已保存所有 {count} 张图片到: aligned 文件夹")
        return None
        
    def save_all_images(self):
        """保存所有处理过的图片"""
        self.add_task(self.save_all_images_task)
        
    def update_display(self):
        """更新显示的图片"""
        if not self.processed_images or self.current_index >= len(self.processed_images):
            self.update_status("没有图片可以显示")
            return
            
        # 获取当前图片
        img = self.processed_images[self.current_index]
        
        # 如果启用了调试模式且有调试图像，显示带关键点的图像
        if self.stabilizer.debug and len(self.debug_images) > self.current_index:
            debug_img = self.debug_images[self.current_index]
            img_rgb = cv2.cvtColor(debug_img, cv2.COLOR_BGR2RGB)
            
            # 显示调试状态
            self.update_status("调试模式：显示关键点")
        else:
            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        
        # 调整图像大小以适应显示区域
        h, w = img_rgb.shape[:2]
        max_height = 600  # 最大显示高度
        max_width = 600   # 最大显示宽度
        
        # 根据比例缩放
        scale = min(max_width/w, max_height/h)
        if scale < 1:  # 只有当图像太大时才缩小
            new_width = int(w * scale)
            new_height = int(h * scale)
            img_rgb = cv2.resize(img_rgb, (new_width, new_height), interpolation=cv2.INTER_AREA)
        
        # 转换为PIL图像并显示
        pil_img = Image.fromarray(img_rgb)
        tk_img = ImageTk.PhotoImage(image=pil_img)
        self.img_label.configure(image=tk_img)
        self.img_label.image = tk_img  # 防止垃圾回收
        
        # 更新计数器和标题
        self.counter_label.configure(text=f"{self.current_index+1}/{len(self.processed_images)}")
        self.root.title(f"头部对齐查看器 - {self.current_index+1}/{len(self.processed_images)}")
        
        # 更新状态显示
        if len(self.successful_paths) > self.current_index:
            filename = os.path.basename(self.successful_paths[self.current_index])
            self.update_status(f"当前显示: {filename}")
        
    def next_image(self):
        """显示下一张图片"""
        if not self.processed_images:
            return
        self.current_index = (self.current_index + 1) % len(self.processed_images)
        self.update_display()
        
    def prev_image(self):
        """显示上一张图片"""
        if not self.processed_images:
            return
        self.current_index = (self.current_index - 1) % len(self.processed_images)
        self.update_display()
        
    def show_skipped_images(self):
        """显示被跳过的图片及原因"""
        if not self.skipped_images:
            messagebox.showinfo("提示", "没有被跳过的图片")
            return
        
        # 创建一个新窗口
        skipped_window = Tk()
        skipped_window.title("被跳过的图片")
        skipped_window.geometry("600x400")
        
        # 创建一个Frame包含列表
        frame = Frame(skipped_window)
        frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # 创建列表标题
        Label(frame, text="文件名", font=("Arial", 10, "bold")).grid(row=0, column=0, sticky="w")
        Label(frame, text="跳过原因", font=("Arial", 10, "bold")).grid(row=0, column=1, sticky="w")
        
        # 添加分割线
        sep = ttk.Separator(frame, orient="horizontal")
        sep.grid(row=1, column=0, columnspan=2, sticky="ew", pady=5)
        
        # 添加滚动条
        scrollbar = Scrollbar(frame)
        scrollbar.grid(row=2, column=2, sticky="ns")
        
        # 创建Canvas用于滚动
        canvas = Canvas(frame, yscrollcommand=scrollbar.set)
        canvas.grid(row=2, column=0, columnspan=2, sticky="nsew")
        
        # 配置滚动条
        scrollbar.config(command=canvas.yview)
        
        # 在Canvas中创建一个Frame
        list_frame = Frame(canvas)
        canvas.create_window((0, 0), window=list_frame, anchor="nw")
        
        # 填充数据
        for i, (img_path, reason) in enumerate(self.skipped_images):
            filename = os.path.basename(img_path)
            Label(list_frame, text=filename, wraplength=250).grid(row=i, column=0, sticky="w", pady=2)
            Label(list_frame, text=reason, wraplength=300).grid(row=i, column=1, sticky="w", pady=2)
        
        # 更新Canvas滚动区域
        list_frame.update_idletasks()
        canvas.config(scrollregion=canvas.bbox("all"))
        
        # 设置Frame的行列权重
        frame.grid_rowconfigure(2, weight=1)
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_columnconfigure(1, weight=2)
        
        # 关闭按钮
        Button(skipped_window, text="关闭", command=skipped_window.destroy).pack(pady=10)
        
        # 运行窗口
        skipped_window.mainloop()
        
    def process_current_image_task(self):
        """处理当前图片的任务函数"""
        if not self.image_paths or self.current_index >= len(self.successful_paths):
            self.update_status("没有有效的当前图片")
            return None
            
        # 检查是否已选择参考图片
        if not self.reference_image_path and self.force_reference_size.get() == 1:
            self.update_status("警告：启用了强制参考图片尺寸，但未选择参考图片")
        
        # 获取当前图片路径
        current_path = self.successful_paths[self.current_index]
        self.update_status(f"重新处理当前图片: {os.path.basename(current_path)}")
        
        try:
            # 更新进度条
            self.update_progress(10)
            
            # 读取原始图片
            img = cv2.imread(current_path)
            if img is None:
                self.update_status(f"无法读取图片: {current_path}")
                return None
            
            # 如果启用了头部倾斜筛选，检查头部是否端正
            if self.filter_tilted.get():
                is_straight, tilt_info, reason = self.stabilizer.check_head_tilt(img)
                if not is_straight:
                    self.update_status(f"当前图片头部倾斜: {reason}")
                    return None
            
            # 更新进度条
            self.update_progress(30)
                
            # 更新稳定器设置
            self.stabilizer.preserve_background = bool(self.preserve_bg.get())
            self.stabilizer.force_reference_size = bool(self.force_reference_size.get())
            self.stabilizer.tilt_threshold = float(self.tilt_threshold.get())
            
            # 处理图片
            eye_distance = self.eye_distance.get()
            
            # 如果没有参考图片，使用眼睛间距设置
            if not self.reference_image_path:
                self.stabilizer.set_reference_eyes_position(eye_distance)
            
            # 更新进度条
            self.update_progress(50)
            
            # 根据是否启用调试模式选择不同的处理方法
            if self.stabilizer.debug:
                aligned, debug_img = self.stabilizer.align_and_crop_face(img, show_landmarks=True)
                
                # 更新处理结果
                self.processed_images[self.current_index] = aligned
                
                # 确保debug_images列表足够长
                while len(self.debug_images) <= self.current_index:
                    self.debug_images.append(None)
                    
                self.debug_images[self.current_index] = debug_img
            else:
                aligned = self.stabilizer.align_and_crop_face(img)
                self.processed_images[self.current_index] = aligned
            
            # 更新进度条
            self.update_progress(90)
            
            self.update_status(f"图片已重新处理: {os.path.basename(current_path)}")
            
            return (self.update_display, ())
            
        except Exception as e:
            self.update_status(f"处理图片失败: {e}")
            return None
        
    def process_current_image(self):
        """仅重新处理当前图片"""
        self.add_task(self.process_current_image_task)

    def run(self):
        """启动查看器"""
        self.root.mainloop()
    
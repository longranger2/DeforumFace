import streamlit as st
import cv2
import numpy as np
import os
import glob
from PIL import Image
import io
from head_stabilizer import HeadStabilizer

# 语言配置
LANGUAGES = {
    "中文": {
        # 页面基本信息
        "page_title": "头部对齐工具",
        "page_description": "用于创建\"瞬息宇宙\"风格的照片集合，确保所有照片中的人脸位置保持一致",
        
        # 侧边栏标题
        "file_settings": "📁 文件设置",
        "image_source": "图片获取方式",
        "upload_images": "上传图片",
        "specify_folder": "指定文件夹",
        "reference_settings": "🖼️ 参考图片设置",
        "reference_image": "参考图片",
        "upload_reference": "上传参考图片",
        "specify_reference_path": "指定参考图片路径",
        "processing_settings": "⚙️ 处理设置",
        "processing_mode": "处理模式",
        "video_export": "🎬 视频导出 (可选)",
        "operations": "🚀 操作",
        
        # 文件上传
        "select_images": "选择图片文件（支持多选）",
        "select_images_help": "可以一次选择多个图片文件",
        "clear_images": "清空所有图片",
        "clear_images_help": "清空已上传的图片，重新选择",
        "images_cleared": "已清空所有上传的图片",
        "folder_path": "图片文件夹路径",
        "folder_path_placeholder": "输入文件夹路径，如: /Users/username/photos",
        "folder_path_help": "指定包含图片的文件夹路径",
        "uploaded_count": "已上传 {} 张图片",
        "found_count": "找到 {} 张图片",
        "no_images_found": "在 {} 中未找到图片",
        "folder_not_exist": "文件夹路径不存在: {}",
        
        # 参考图片
        "upload_reference_help": "上传一张作为参考的图片",
        "reference_path": "参考图片路径",
        "reference_path_placeholder": "输入参考图片路径，如: /Users/username/ref.jpg",
        "reference_path_help": "指定一张参考图片的路径",
        "force_reference_size": "强制使用参考图片尺寸（推荐）",
        "force_reference_size_help": "使用参考图片的尺寸作为所有处理图片的输出尺寸",
        "reference_uploaded": "已上传参考图片: {}",
        "reference_selected": "已选择参考图片: {}",
        "reference_read_error": "无法读取参考图片",
        "reference_path_not_exist": "参考图片路径不存在: {}",
        
        # 处理模式
        "smart_mode": "智能模式 (推荐)",
        "custom_settings": "自定义设置",
        "mode_help": "智能模式使用最佳默认参数，适合大多数用户",
        "filter_tilted": "过滤倾斜头部的照片",
        "filter_tilted_help": "自动跳过头部明显倾斜的照片，推荐开启",
        "smart_mode_info": "💡 智能模式已为您优化所有参数，直接上传图片即可使用",
        "expert_mode_warning": "⚠️ 专家模式：请确保您了解这些参数的含义",
        
        # 专家模式参数
        "eye_distance": "眼睛间距",
        "eye_distance_desc": "决定人脸在画面中的大小比例，只有在参考图片没有设置的时候才会生效",
        "eye_distance_label": "眼睛间距百分比",
        "eye_distance_help": "眼睛间的距离占据图片宽度的百分比",
        "head_tilt_detection": "头部倾斜检测",
        "head_tilt_desc": "过滤掉头部不端正的照片",
        "enable_tilt_filter": "启用头部倾斜筛选",
        "enable_tilt_filter_help": "自动跳过头部倾斜的照片",
        "tilt_threshold": "倾斜阈值(度)",
        "tilt_threshold_help": "允许的最大头部倾斜角度",
        "other_options": "其他选项",
        "preserve_bg": "保留背景（不推荐）",
        "preserve_bg_help": "保留原始背景，但可能导致图片尺寸不一致",
        "debug_mode": "调试模式（显示关键点）",
        "debug_mode_help": "在图片上显示检测到的面部关键点",
        
        # 视频设置
        "video_description": "将处理后的图片制作成视频",
        "playback_speed": "播放速度",
        "playback_speed_help": "数值越高播放越快",
        "video_quality": "视频质量",
        "loop_playback": "来回循环播放",
        "loop_playback_help": "播放到最后会倒序回到开头",
        "filename": "文件名",
        "filename_placeholder": "输入视频文件名",
        
        # 操作按钮
        "process_all": "处理所有图片",
        "process_all_help": "根据当前设置处理所有图片",
        "previous": "上一张",
        "previous_help": "显示上一张图片",
        "next": "下一张",
        "next_help": "显示下一张图片",
        "save_all": "保存所有图片",
        "save_all_help": "将所有处理后的图片保存到程序目录",
        "export_video": "导出为视频",
        "export_video_help": "将所有处理后的图片导出为视频到程序目录",
        
        # 状态信息
        "display_count": "显示: {}/{}",
        "processing_progress": "处理进度: {}/{} - {}",
        "save_progress": "保存进度: {}/{} - {}",
        "export_progress": "导出视频进度: {}/{}",
        "start_export": "开始导出视频...",
        
        # 成功消息
        "all_images_saved": "✅ 所有图片已保存到当前目录",
        "video_exported": "✅ 视频已成功导出到当前目录",
        "reference_updated": "已更新输出尺寸为参考图片尺寸: {}",
        "reference_features_set": "从参考图片中提取的稳定面部特征已设置为对齐基准",
        "reference_position_set": "参考人脸关键点已设置",
        
        # 错误消息
        "no_images_to_process": "没有找到图片，请先选择文件夹或上传图片",
        "no_images_to_save": "没有处理过的图片可以保存",
        "no_images_to_export": "没有处理过的图片可以导出为视频",
        "invalid_filename": "请输入有效的文件名",
        "reference_read_failed": "无法读取参考图片，使用默认参考设置",
        "save_failed": "保存图片失败 {}: {}",
        "export_failed": "导出视频失败: {}",
        "processing_failed": "处理图片失败 {}: {}",
        "head_tilt_skipped": "头部倾斜",
        "image_read_error": "无法读取图片",
        
        # 提示信息
        "click_to_process": "请点击「处理所有图片」按钮开始处理",
        "ready_to_process": "准备就绪，点击侧边栏中的\"处理所有图片\"按钮开始处理",
        "select_images_first": "请先在侧边栏选择图片文件夹或上传图片",
        "use_sidebar": "使用侧边栏的\"文件设置\"部分上传图片或指定图片文件夹",
        
        # 其他
        "original_image": "原始图片: {}",
        "processed_image": "处理后的图片",
        "skipped_images": "被跳过的图片 ({} 张)",
        "skipped_images_title": "被跳过的图片",
        "no_skipped_images": "没有被跳过的图片",
        "original_unavailable": "原始图片无法显示",
        "version": "头部对齐工具 v2.1",
        "download_video": "下载视频 ({})",
        "low": "低",
        "medium": "中",
        "high": "高",
        "language": "🌐 语言",
    },
    
    "English": {
        # Basic page info
        "page_title": "Head Alignment Tool",
        "page_description": "Create 'Everything Everywhere All at Once' style photo collections with precisely aligned faces",
        
        # Sidebar titles
        "file_settings": "📁 File Settings",
        "image_source": "Image Source",
        "upload_images": "Upload Images",
        "specify_folder": "Specify Folder",
        "reference_settings": "🖼️ Reference Image Settings",
        "reference_image": "Reference Image",
        "upload_reference": "Upload Reference",
        "specify_reference_path": "Specify Reference Path",
        "processing_settings": "⚙️ Processing Settings",
        "processing_mode": "Processing Mode",
        "video_export": "🎬 Video Export (Optional)",
        "operations": "🚀 Operations",
        
        # File upload
        "select_images": "Select image files (multiple selection supported)",
        "select_images_help": "You can select multiple image files at once",
        "clear_images": "Clear All Images",
        "clear_images_help": "Clear all uploaded images, reselect",
        "images_cleared": "All uploaded images cleared",
        "folder_path": "Image folder path",
        "folder_path_placeholder": "Enter folder path, e.g.: /Users/username/photos",
        "folder_path_help": "Specify the folder path containing images",
        "uploaded_count": "Uploaded {} images",
        "found_count": "Found {} images",
        "no_images_found": "No images found in {}",
        "folder_not_exist": "Folder path does not exist: {}",
        
        # Reference image
        "upload_reference_help": "Upload a reference image",
        "reference_path": "Reference image path",
        "reference_path_placeholder": "Enter reference image path, e.g.: /Users/username/ref.jpg",
        "reference_path_help": "Specify a reference image path",
        "force_reference_size": "Force reference image size (recommended)",
        "force_reference_size_help": "Use reference image size as output size for all processed images",
        "reference_uploaded": "Reference image uploaded: {}",
        "reference_selected": "Reference image selected: {}",
        "reference_read_error": "Cannot read reference image",
        "reference_path_not_exist": "Reference image path does not exist: {}",
        
        # Processing modes
        "smart_mode": "Smart Mode (Recommended)",
        "custom_settings": "Custom Settings",
        "mode_help": "Smart mode uses optimal default parameters, suitable for most users",
        "filter_tilted": "Filter tilted head photos",
        "filter_tilted_help": "Automatically skip photos with obviously tilted heads, recommended",
        "smart_mode_info": "💡 Smart mode has optimized all parameters for you, just upload images to use",
        "expert_mode_warning": "⚠️ Expert mode: Please ensure you understand these parameters",
        
        # Expert mode parameters
        "eye_distance": "Eye Distance",
        "eye_distance_desc": "Determines face size ratio in the image, only effective when reference image is not set",
        "eye_distance_label": "Eye distance percentage",
        "eye_distance_help": "Distance between eyes as percentage of image width",
        "head_tilt_detection": "Head Tilt Detection",
        "head_tilt_desc": "Filter out photos with improper head orientation",
        "enable_tilt_filter": "Enable head tilt filtering",
        "enable_tilt_filter_help": "Automatically skip tilted head photos",
        "tilt_threshold": "Tilt threshold (degrees)",
        "tilt_threshold_help": "Maximum allowable head tilt angle",
        "other_options": "Other Options",
        "preserve_bg": "Preserve background (not recommended)",
        "preserve_bg_help": "Preserve original background, but may cause inconsistent image sizes",
        "debug_mode": "Debug mode (show landmarks)",
        "debug_mode_help": "Display detected facial landmarks on images",
        
        # Video settings
        "video_description": "Create video from processed images",
        "playback_speed": "Playback Speed",
        "playback_speed_help": "Higher values mean faster playback",
        "video_quality": "Video Quality",
        "loop_playback": "Loop playback",
        "loop_playback_help": "Reverse back to beginning after reaching the end",
        "filename": "Filename",
        "filename_placeholder": "Enter video filename",
        
        # Operation buttons
        "process_all": "Process All Images",
        "process_all_help": "Process all images with current settings",
        "previous": "Previous",
        "previous_help": "Show previous image",
        "next": "Next",
        "next_help": "Show next image",
        "save_all": "Save All Images",
        "save_all_help": "Save all processed images to program directory",
        "export_video": "Export as Video",
        "export_video_help": "Export all processed images as video to program directory",
        
        # Status info
        "display_count": "Display: {}/{}",
        "processing_progress": "Processing: {}/{} - {}",
        "save_progress": "Saving: {}/{} - {}",
        "export_progress": "Exporting video: {}/{}",
        "start_export": "Starting video export...",
        
        # Success messages
        "all_images_saved": "✅ All images saved to current directory",
        "video_exported": "✅ Video successfully exported to current directory",
        "reference_updated": "Output size updated to reference image size: {}",
        "reference_features_set": "Stable facial features from reference image set as alignment baseline",
        "reference_position_set": "Reference face landmarks set",
        
        # Error messages
        "no_images_to_process": "No images found, please select folder or upload images first",
        "no_images_to_save": "No processed images to save",
        "no_images_to_export": "No processed images to export as video",
        "invalid_filename": "Please enter a valid filename",
        "reference_read_failed": "Cannot read reference image, using default reference settings",
        "save_failed": "Failed to save image {}: {}",
        "export_failed": "Video export failed: {}",
        "processing_failed": "Failed to process image {}: {}",
        "head_tilt_skipped": "Head tilt",
        "image_read_error": "Cannot read image",
        
        # Info messages
        "click_to_process": "Please click 'Process All Images' button to start processing",
        "ready_to_process": "Ready, click 'Process All Images' button in sidebar to start processing",
        "select_images_first": "Please first select image folder or upload images in sidebar",
        "use_sidebar": "Use the 'File Settings' section in sidebar to upload images or specify image folder",
        
        # Others
        "original_image": "Original image: {}",
        "processed_image": "Processed image",
        "skipped_images": "Skipped images ({} total)",
        "skipped_images_title": "Skipped images",
        "no_skipped_images": "No skipped images",
        "original_unavailable": "Original image unavailable",
        "version": "Head Alignment Tool v2.1",
        "download_video": "Download video ({})",
        "low": "Low",
        "medium": "Medium",
        "high": "High",
        "language": "🌐 Language",
    }
}

def get_text(key, *args):
    """根据当前语言获取文本"""
    current_lang = st.session_state.get('language', '中文')
    text = LANGUAGES[current_lang].get(key, f"[Missing: {key}]")
    if args:
        return text.format(*args)
    return text

# 设置页面配置 - 保持最小化但必要的设置
st.set_page_config(
    page_title=get_text("page_title"),
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS样式
st.markdown("""
<style>
    .main {
        background-color: #222222;
        color: white;
    }
    .stButton button {
        width: 100%;
    }
    .stProgress .st-bo {
        background-color: #4CAF50;
    }
    h1, h2, h3 {
        color: white;
    }
    .success {
        color: #4CAF50;
    }
    .warning {
        color: #FF9800;
    }
    .error {
        color: #FF5722;
    }
    .info-text {
        color: #AAAAAA;
        font-size: 14px;
    }
    /* 隐藏Streamlit默认页脚 */
    footer {display: none !important;}
    /* 紧凑布局 */
    .block-container {padding-top: 3rem; padding-bottom: 0rem;}
    /* 紧凑版的侧边栏 */
    .css-1d391kg {padding-top: 1rem;}
    /* 减小标题大小 */
    h1 {font-size: 1.8rem !important; margin-bottom: 1rem !important; margin-top: 1rem !important;}
    /* 分隔线样式 */
    .divider {
        margin-top: 1rem;
        margin-bottom: 1rem;
        border-top: 1px solid #444;
        width: 100%;
    }
    /* 侧边栏分组标题 */
    .sidebar-section-title {
        font-weight: bold;
        margin-top: 0.8rem;
        margin-bottom: 0.5rem;
        color: #B0B0B0;
    }
    /* 折叠面板样式 */
    .streamlit-expanderHeader {
        font-weight: bold;
        background-color: #2E2E2E;
        border-radius: 4px;
    }
    .streamlit-expanderHeader:hover {
        background-color: #3E3E3E;
    }
    /* 文件上传区域样式 */
    .file-uploader {
        background-color: #2E2E2E;
        border-radius: 4px;
        padding: 1rem;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# 初始化session_state
if 'processed_images' not in st.session_state:
    st.session_state.processed_images = []
    st.session_state.successful_paths = []
    st.session_state.skipped_images = []
    st.session_state.debug_images = []
    st.session_state.current_index = 0
    st.session_state.stabilizer = None
    st.session_state.reference_image_path = None
    st.session_state.folder_path = None
    st.session_state.image_paths = []
    st.session_state.is_processed = False
    st.session_state.uploaded_files = []
    st.session_state.language = '中文'  # 默认语言
    st.session_state.uploader_key = 0  # 用于重置file_uploader
    st.session_state.cleared_status = False  # 用于显示清空成功消息

# 视频导出设置的默认值
if 'video_fps' not in st.session_state:
    st.session_state.video_fps = 4  # 修改为默认4fps以匹配新的选项
    st.session_state.video_quality = "高"
    st.session_state.video_loop = False
    st.session_state.video_filename = "aligned_video"

def initialize_stabilizer(output_size=(512, 512)):
    """初始化HeadStabilizer实例"""
    if st.session_state.stabilizer is None:
        st.session_state.stabilizer = HeadStabilizer(
            output_size=output_size,
            preserve_background=st.session_state.preserve_bg,
            force_reference_size=st.session_state.force_reference_size,
            tilt_threshold=st.session_state.tilt_threshold
        )
    else:
        # 更新已存在的实例
        st.session_state.stabilizer.preserve_background = st.session_state.preserve_bg
        st.session_state.stabilizer.force_reference_size = st.session_state.force_reference_size
        st.session_state.stabilizer.tilt_threshold = st.session_state.tilt_threshold

def load_image_from_path(image_path):
    """从路径加载图像，返回CV2和PIL格式"""
    cv_img = cv2.imread(image_path)
    if cv_img is None:
        return None, None
    
    rgb_img = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
    pil_img = Image.fromarray(rgb_img)
    return cv_img, pil_img

def load_image_from_bytes(image_bytes):
    """从二进制数据加载图像，返回CV2和PIL格式"""
    try:
        # 转换为numpy数组
        nparr = np.frombuffer(image_bytes, np.uint8)
        # 解码图像
        cv_img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if cv_img is None:
            return None, None
        
        # 转换为PIL格式
        rgb_img = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
        pil_img = Image.fromarray(rgb_img)
        return cv_img, pil_img
    except Exception as e:
        st.error(f"无法加载图像: {e}")
        return None, None

def process_images():
    """处理所有图片"""
    # 检查是否有图片可处理
    if not st.session_state.image_paths and not st.session_state.uploaded_files:
        st.error(get_text("no_images_to_process"))
        return
    
    # 初始化或更新稳定器
    initialize_stabilizer()
    
    # 清空结果
    st.session_state.processed_images = []
    st.session_state.successful_paths = []
    st.session_state.skipped_images = []
    st.session_state.debug_images = []
    
    # 设置参考图片
    if st.session_state.reference_image_path:
        ref_img = cv2.imread(st.session_state.reference_image_path)
        if ref_img is not None:
            st.session_state.stabilizer.set_reference_from_image(ref_img)
        else:
            st.warning(get_text("reference_read_failed"))
            st.session_state.stabilizer.set_reference_eyes_position(st.session_state.eye_distance)
    else:
        st.session_state.stabilizer.set_reference_eyes_position(st.session_state.eye_distance)
    
    # 创建进度条
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    # 处理从文件夹加载的图片
    total_files = len(st.session_state.image_paths) + len(st.session_state.uploaded_files)
    processed_images = []
    successful_paths = []
    debug_images = []
    skipped_images = []
    processed_count = 0
    
    # 首先处理从路径加载的图片
    for i, img_path in enumerate(st.session_state.image_paths):
        # 更新进度
        processed_count += 1
        progress = processed_count / total_files
        progress_bar.progress(progress)
        status_text.text(get_text("processing_progress", processed_count, total_files, os.path.basename(img_path)))
        
        try:
            img = cv2.imread(img_path)
            if img is None:
                skipped_images.append((img_path, get_text("image_read_error")))
                continue
            
            # 如果启用了头部倾斜筛选
            if st.session_state.filter_tilted:
                is_straight, tilt_info, reason = st.session_state.stabilizer.check_head_tilt(img)
                if not is_straight:
                    skipped_images.append((img_path, f"{get_text('head_tilt_skipped')}: {reason}"))
                    continue
            
            # 处理图片
            if st.session_state.debug_mode:
                aligned, debug_img = st.session_state.stabilizer.align_and_crop_face(img, show_landmarks=True)
                debug_images.append(debug_img)
            else:
                aligned = st.session_state.stabilizer.align_and_crop_face(img)
            
            processed_images.append(aligned)
            successful_paths.append(img_path)
            
        except Exception as e:
            skipped_images.append((img_path, get_text("processing_failed", "", str(e))))
    
    # 然后处理上传的图片
    for i, uploaded_file in enumerate(st.session_state.uploaded_files):
        # 更新进度
        processed_count += 1
        progress = processed_count / total_files
        progress_bar.progress(progress)
        status_text.text(get_text("processing_progress", processed_count, total_files, uploaded_file.name))
        
        try:
            # 读取上传的图片
            file_bytes = uploaded_file.getvalue()
            img, _ = load_image_from_bytes(file_bytes)
            
            if img is None:
                skipped_images.append((uploaded_file.name, get_text("image_read_error")))
                continue
            
            # 如果启用了头部倾斜筛选
            if st.session_state.filter_tilted:
                is_straight, tilt_info, reason = st.session_state.stabilizer.check_head_tilt(img)
                if not is_straight:
                    skipped_images.append((uploaded_file.name, f"{get_text('head_tilt_skipped')}: {reason}"))
                    continue
            
            # 处理图片
            if st.session_state.debug_mode:
                aligned, debug_img = st.session_state.stabilizer.align_and_crop_face(img, show_landmarks=True)
                debug_images.append(debug_img)
            else:
                aligned = st.session_state.stabilizer.align_and_crop_face(img)
            
            processed_images.append(aligned)
            successful_paths.append(uploaded_file.name)  # 存储文件名而不是路径
            
        except Exception as e:
            skipped_images.append((uploaded_file.name, get_text("processing_failed", "", str(e))))
    
    # 保存结果
    st.session_state.processed_images = processed_images
    st.session_state.successful_paths = successful_paths
    st.session_state.debug_images = debug_images
    st.session_state.skipped_images = skipped_images
    st.session_state.is_processed = True
    
    # 重置当前索引
    if processed_images:
        st.session_state.current_index = 0

def export_video():
    """导出处理后的图片为视频到程序运行目录"""
    if not st.session_state.processed_images:
        st.error(get_text("no_images_to_export"))
        return
    
    # 获取参数
    fps = st.session_state.video_fps
    quality = st.session_state.video_quality
    loop = st.session_state.video_loop
    filename = st.session_state.video_filename
    
    if not filename:
        st.error(get_text("invalid_filename"))
        return
    
    # 映射质量选项到编码器参数
    quality_map = {
        "低": {"codec": "XVID", "ext": "avi"},
        "中": {"codec": "MP4V", "ext": "mp4"},
        "高": {"codec": "H264", "ext": "mp4"}
    }
    
    codec_info = quality_map.get(quality, quality_map["高"])
    
    # 使用当前程序运行目录
    current_dir = os.getcwd()
    output_dir = os.path.join(current_dir, "deforum_videos")
    os.makedirs(output_dir, exist_ok=True)
    
    output_path = os.path.join(output_dir, f"{filename}.{codec_info['ext']}")
    
    # 创建进度条和状态显示
    progress_bar = st.progress(0)
    status_text = st.empty()
    status_text.text(get_text("start_export"))
    
    try:
        # 获取图像尺寸
        h, w = st.session_state.processed_images[0].shape[:2]
        
        # 设置编解码器
        if codec_info["codec"] == "H264":
            fourcc = cv2.VideoWriter_fourcc(*'avc1')  # H.264编码
        elif codec_info["codec"] == "MP4V":
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # MP4V编码
        else:
            fourcc = cv2.VideoWriter_fourcc(*'XVID')  # AVI编码
            
        # 创建VideoWriter对象
        video = cv2.VideoWriter(output_path, fourcc, fps, (w, h))
        
        # 准备图像序列
        images_to_write = st.session_state.processed_images.copy()
        
        # 如果启用循环，添加反向序列
        if loop:
            reversed_images = st.session_state.processed_images.copy()
            reversed_images.reverse()
            # 删除第一帧和最后一帧以避免重复
            if len(reversed_images) > 2:
                reversed_images = reversed_images[1:-1]
            images_to_write.extend(reversed_images)
        
        # 写入视频帧
        total_frames = len(images_to_write)
        for i, img in enumerate(images_to_write):
            video.write(img)
            # 更新进度
            progress = (i + 1) / total_frames
            progress_bar.progress(progress)
            status_text.text(get_text("export_progress", i+1, total_frames))
        
        # 释放视频写入器
        video.release()
        
        # 更新状态
        st.success(get_text("video_exported"))
        
        # 提供下载链接
        with open(output_path, "rb") as file:
            btn = st.download_button(
                label=get_text("download_video", codec_info['ext']),
                data=file,
                file_name=f"{filename}.{codec_info['ext']}",
                mime=f"video/{codec_info['ext']}"
            )
        
    except Exception as e:
        st.error(get_text("export_failed", str(e)))

def save_all_images():
    """保存所有处理过的图片到程序运行目录"""
    if not st.session_state.processed_images:
        st.error(get_text("no_images_to_save"))
        return
    
    # 使用当前程序运行目录
    current_dir = os.getcwd()
    output_dir = os.path.join(current_dir, "deforum_photos")
    os.makedirs(output_dir, exist_ok=True)
    
    # 创建进度条
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    count = 0
    total = len(st.session_state.processed_images)
    
    for i, img in enumerate(st.session_state.processed_images):
        try:
            # 更新进度
            progress = (i + 1) / total
            progress_bar.progress(progress)
            
            # 获取原始文件名
            if i < len(st.session_state.successful_paths):
                original_path = st.session_state.successful_paths[i]
                # 如果是上传的文件，original_path可能只是文件名
                base_name = os.path.basename(original_path) if os.path.isfile(original_path) else original_path
            else:
                base_name = f"unknown_{i}.jpg"
            
            # 保存图片
            output_path = os.path.join(output_dir, f"aligned_{base_name}")
            cv2.imwrite(output_path, img)
            count += 1
            
            status_text.text(get_text("save_progress", i+1, total, base_name))
            
        except Exception as e:
            st.error(get_text("save_failed", i, str(e)))
    
    st.success(get_text("all_images_saved"))

def show_current_image():
    """在主界面显示当前图片"""
    if not st.session_state.processed_images or st.session_state.current_index >= len(st.session_state.processed_images):
        return
    
    # 获取当前处理后的图片
    processed_img = st.session_state.processed_images[st.session_state.current_index]
    
    # 获取原始图片名称或路径
    current_path = st.session_state.successful_paths[st.session_state.current_index]
    
    # 确定是否为文件路径还是上传的文件名
    is_file_path = os.path.isfile(current_path) if isinstance(current_path, str) else False
    
    # 尝试加载原始图片用于显示
    original_pil = None
    if is_file_path:
        # 如果是文件路径，从文件加载
        _, original_pil = load_image_from_path(current_path)
    else:
        # 如果是上传的文件，尝试从session_state.uploaded_files找到对应的文件
        for uploaded_file in st.session_state.uploaded_files:
            if uploaded_file.name == current_path:
                _, original_pil = load_image_from_bytes(uploaded_file.getvalue())
                break
    
    # 处理后的图片
    if st.session_state.debug_mode and len(st.session_state.debug_images) > st.session_state.current_index:
        debug_img = st.session_state.debug_images[st.session_state.current_index]
        processed_rgb = cv2.cvtColor(debug_img, cv2.COLOR_BGR2RGB)
    else:
        processed_rgb = cv2.cvtColor(processed_img, cv2.COLOR_BGR2RGB)
    
    processed_pil = Image.fromarray(processed_rgb)
    
    # 显示图片
    col1, col2 = st.columns(2)
    
    with col1:
        if original_pil:
            st.image(original_pil, caption=get_text("original_image", os.path.basename(current_path) if isinstance(current_path, str) else current_path), use_container_width=True)
        else:
            st.write(get_text("original_unavailable"))
    
    with col2:
        st.image(processed_pil, caption=get_text("processed_image"), use_container_width=True)

def next_image():
    """显示下一张图片"""
    if not st.session_state.processed_images:
        return
    
    if st.session_state.current_index < len(st.session_state.processed_images) - 1:
        st.session_state.current_index += 1
    else:
        st.session_state.current_index = 0

def prev_image():
    """显示上一张图片"""
    if not st.session_state.processed_images:
        return
    
    if st.session_state.current_index > 0:
        st.session_state.current_index -= 1
    else:
        st.session_state.current_index = len(st.session_state.processed_images) - 1

def show_skipped_images():
    """显示被跳过的图片"""
    if not st.session_state.skipped_images:
        st.info(get_text("no_skipped_images"))
        return
    
    st.write(f"### {get_text('skipped_images_title', len(st.session_state.skipped_images))}")
    for img_path, reason in st.session_state.skipped_images:
        st.write(f"- **{os.path.basename(img_path) if isinstance(img_path, str) and os.path.isfile(img_path) else img_path}**: {reason}")

# ================ 主界面 ==================
st.title(get_text("page_title"))
st.write(f'<p class="info-text">{get_text("page_description")}</p>', unsafe_allow_html=True)

# 侧边栏部分 - 所有参数设置
with st.sidebar:
    # 语言切换
    language_col1, language_col2 = st.columns([3, 1])
    with language_col1:
        selected_language = st.selectbox(
            get_text("language"),
            options=["中文", "English"],
            index=0 if st.session_state.language == "中文" else 1,
            key="language_selector"
        )
    
    # 更新语言设置
    if selected_language != st.session_state.language:
        st.session_state.language = selected_language
        st.rerun()
    
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    
    # 文件选择部分
    with st.expander(get_text("file_settings"), expanded=True):
        st.markdown(f'<div class="sidebar-section-title">{get_text("image_source")}</div>', unsafe_allow_html=True)
        
        # 允许用户选择图片获取方式：上传图片或指定文件夹路径
        source_tab1, source_tab2 = st.tabs([get_text("upload_images"), get_text("specify_folder")])
        
        with source_tab1:
            
            # 显示清空成功消息
            if st.session_state.cleared_status:
                st.success(get_text("images_cleared"))
                st.session_state.cleared_status = False  # 重置状态
            
            uploaded_files = st.file_uploader(
                get_text("select_images"), 
                type=["jpg", "jpeg", "png"], 
                accept_multiple_files=True,
                help=get_text("select_images_help"),
                key=f"uploader_{st.session_state.uploader_key}"
            )
            st.markdown('</div>', unsafe_allow_html=True)
            
            if uploaded_files:
                st.session_state.uploaded_files = uploaded_files
                st.success(get_text("uploaded_count", len(uploaded_files)))
                
                # 添加清空按钮
                if st.button(
                    get_text("clear_images"),
                    help=get_text("clear_images_help"),
                    key=f"clear_uploaded_images_{st.session_state.uploader_key}"
                ):
                    # 只清空上传的文件
                    st.session_state.uploaded_files = []
                    st.session_state.uploader_key += 1
                    st.session_state.cleared_status = True
                    st.rerun()
        
        with source_tab2:
            folder_path = st.text_input(
                get_text("folder_path"), 
                value=st.session_state.folder_path if st.session_state.folder_path else "",
                placeholder=get_text("folder_path_placeholder"),
                help=get_text("folder_path_help")
            )
            
            if folder_path and folder_path != st.session_state.folder_path:
                if os.path.exists(folder_path):
                    st.session_state.folder_path = folder_path
                    # 查找所有图片
                    st.session_state.image_paths = glob.glob(os.path.join(folder_path, "*.jpg")) + \
                                                  glob.glob(os.path.join(folder_path, "*.jpeg")) + \
                                                  glob.glob(os.path.join(folder_path, "*.png"))
                    
                    if st.session_state.image_paths:
                        st.success(get_text("found_count", len(st.session_state.image_paths)))
                    else:
                        st.error(get_text("no_images_found", folder_path))
                else:
                    st.error(get_text("folder_not_exist", folder_path))
    
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    
    # 参考图片设置
    with st.expander(get_text("reference_settings"), expanded=True):
        st.markdown(f'<div class="sidebar-section-title">{get_text("reference_image")}</div>', unsafe_allow_html=True)
        
        # 也允许上传参考图片
        ref_tab1, ref_tab2 = st.tabs([get_text("upload_reference"), get_text("specify_reference_path")])
        
        with ref_tab1:
            uploaded_ref = st.file_uploader(
                get_text("upload_reference"), 
                type=["jpg", "jpeg", "png"],
                help=get_text("upload_reference_help")
            )
            
            if uploaded_ref:
                # 保存上传的参考图片到临时文件
                ref_bytes = uploaded_ref.getvalue()
                ref_cv, ref_pil = load_image_from_bytes(ref_bytes)
                
                if ref_cv is not None:
                    temp_dir = os.path.join(os.path.expanduser("~"), ".temp_ref_images")
                    os.makedirs(temp_dir, exist_ok=True)
                    temp_ref_path = os.path.join(temp_dir, f"ref_{uploaded_ref.name}")
                    cv2.imwrite(temp_ref_path, ref_cv)
                    
                    st.session_state.reference_image_path = temp_ref_path
                    if ref_pil:
                        st.image(ref_pil, caption=get_text("reference_image"), width=150)
                        st.success(get_text("reference_uploaded", uploaded_ref.name))
                else:
                    st.error(get_text("reference_read_error"))
        
        with ref_tab2:
            reference_path = st.text_input(
                get_text("reference_path"), 
                value=st.session_state.reference_image_path if st.session_state.reference_image_path and os.path.exists(st.session_state.reference_image_path) else "",
                placeholder=get_text("reference_path_placeholder"),
                help=get_text("reference_path_help")
            )
            
            if reference_path and reference_path != st.session_state.reference_image_path:
                if os.path.exists(reference_path):
                    st.session_state.reference_image_path = reference_path
                    ref_cv, ref_pil = load_image_from_path(reference_path)
                    if ref_pil:
                        st.image(ref_pil, caption=get_text("reference_image"), width=150)
                        st.success(get_text("reference_selected", os.path.basename(reference_path)))
                    else:
                        st.error(get_text("reference_read_error", reference_path))
                else:
                    st.error(get_text("reference_path_not_exist", reference_path))
        
        st.session_state.force_reference_size = st.checkbox(
            get_text("force_reference_size"), 
            value=True,
            help=get_text("force_reference_size_help")
        )
    
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    
    # 参数设置 - 大幅简化
    with st.expander(get_text("processing_settings"), expanded=True):
        # 简单模式选择
        st.markdown(f'<div class="sidebar-section-title">{get_text("processing_mode")}</div>', unsafe_allow_html=True)
        
        mode_choice = st.radio(
            get_text("processing_mode"),
            options=[get_text("smart_mode"), get_text("custom_settings")],
            help=get_text("mode_help")
        )
        
        if mode_choice == get_text("smart_mode"):
            # 智能模式 - 只显示最重要的选项
            st.session_state.eye_distance = 30
            st.session_state.filter_tilted = True
            st.session_state.tilt_threshold = 5
            st.session_state.preserve_bg = False
            st.session_state.debug_mode = False
            
            # 只保留头部倾斜筛选这一个重要选项
            st.session_state.filter_tilted = st.checkbox(
                get_text("filter_tilted"), 
                value=True,
                help=get_text("filter_tilted_help")
            )
            
            st.info(get_text("smart_mode_info"))
            
        else:
            # 自定义模式 - 显示所有参数
            st.warning(get_text("expert_mode_warning"))
            
            # 眼睛间距
            st.subheader(get_text("eye_distance"))
            st.caption(get_text("eye_distance_desc"))
            st.session_state.eye_distance = st.slider(
                get_text("eye_distance_label"), 
                min_value=15, 
                max_value=45, 
                value=30,
                help=get_text("eye_distance_help")
            )
            
            # 头部倾斜检测
            st.subheader(get_text("head_tilt_detection"))
            st.caption(get_text("head_tilt_desc"))
            st.session_state.filter_tilted = st.checkbox(
                get_text("enable_tilt_filter"), 
                value=True,
                help=get_text("enable_tilt_filter_help")
            )
            st.session_state.tilt_threshold = st.slider(
                get_text("tilt_threshold"), 
                min_value=1, 
                max_value=30, 
                value=5,
                help=get_text("tilt_threshold_help")
            )
            
            # 其他选项
            st.subheader(get_text("other_options"))
            st.session_state.preserve_bg = st.checkbox(
                get_text("preserve_bg"), 
                value=False,
                help=get_text("preserve_bg_help")
            )
            st.session_state.debug_mode = st.checkbox(
                get_text("debug_mode"), 
                value=False,
                help=get_text("debug_mode_help")
            )
    
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    
    # 视频导出设置
    with st.expander(get_text("video_export"), expanded=False):
        st.caption(get_text("video_description"))
        
        fps_options = [2, 4, 8, 16, 32, 64]
        st.session_state.video_fps = st.select_slider(
            get_text("playback_speed"), 
            options=fps_options, 
            value=st.session_state.video_fps,
            help=get_text("playback_speed_help")
        )
        
        quality_options = [get_text("low"), get_text("medium"), get_text("high")]
        current_quality_index = 0
        if st.session_state.video_quality == "中" or st.session_state.video_quality == "Medium":
            current_quality_index = 1
        elif st.session_state.video_quality == "高" or st.session_state.video_quality == "High":
            current_quality_index = 2
            
        selected_quality = st.radio(
            get_text("video_quality"), 
            options=quality_options, 
            index=current_quality_index,
            horizontal=True
        )
        
        # 更新质量设置（映射回内部格式）
        if selected_quality == get_text("low"):
            st.session_state.video_quality = "低"
        elif selected_quality == get_text("medium"):
            st.session_state.video_quality = "中"
        elif selected_quality == get_text("high"):
            st.session_state.video_quality = "高"
        
        st.session_state.video_loop = st.checkbox(
            get_text("loop_playback"), 
            value=st.session_state.video_loop,
            help=get_text("loop_playback_help")
        )
        
        st.session_state.video_filename = st.text_input(
            get_text("filename"), 
            value=st.session_state.video_filename,
            placeholder=get_text("filename_placeholder")
        )
    
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    
    # 操作按钮
    with st.expander(get_text("operations"), expanded=True):
        has_images = len(st.session_state.image_paths) > 0 or len(st.session_state.uploaded_files) > 0
        
        if st.button(
            get_text("process_all"), 
            type="primary", 
            disabled=not has_images,
            help=get_text("process_all_help")
        ):
            process_images()
        
        nav_col1, nav_col2 = st.columns(2)
        with nav_col1:
            if st.button(
                get_text("previous"), 
                disabled=not st.session_state.processed_images,
                help=get_text("previous_help")
            ):
                prev_image()
        
        with nav_col2:
            if st.button(
                get_text("next"), 
                disabled=not st.session_state.processed_images,
                help=get_text("next_help")
            ):
                next_image()
        
        action_col1, action_col2 = st.columns(2)
        with action_col1:
            if st.button(
                get_text("save_all"), 
                disabled=not st.session_state.processed_images,
                help=get_text("save_all_help")
            ):
                save_all_images()
        
        with action_col2:
            if st.button(
                get_text("export_video"), 
                disabled=not st.session_state.processed_images,
                help=get_text("export_video_help")
            ):
                export_video()
    
    # 版本信息
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    st.caption(get_text("version"))

# 主区域 - 仅显示图片和结果
if st.session_state.processed_images:
    st.write(f"#### {get_text('display_count', st.session_state.current_index + 1, len(st.session_state.processed_images))}")
    show_current_image()
    
    # 结果区导航按钮
    col1, col2, col3 = st.columns([1, 3, 1])
    with col1:
        if st.button(f"{get_text('previous')} ⬅️", disabled=not st.session_state.processed_images):
            prev_image()
    
    with col3:
        if st.button(f"{get_text('next')} ➡️", disabled=not st.session_state.processed_images):
            next_image()
else:
    if st.session_state.image_paths or st.session_state.uploaded_files:
        st.info(get_text('click_to_process'))
        st.markdown(f"""
        <div style="display: flex; justify-content: center; margin-top: 2rem;">
            <div style="text-align: center; max-width: 600px;">
                <img src="https://oss.streamlit.io/images/brand/streamlit-mark-color.png" width="100">
                <p style="margin-top: 1rem; color: #888;">{get_text('ready_to_process')}</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.info(get_text('select_images_first'))
        st.markdown(f"""
        <div style="display: flex; justify-content: center; margin-top: 2rem;">
            <div style="text-align: center; max-width: 600px;">
                <img src="https://oss.streamlit.io/images/brand/streamlit-mark-color.png" width="100">
                <p style="margin-top: 1rem; color: #888;">{get_text('use_sidebar')}</p>
            </div>
        </div>
        """, unsafe_allow_html=True)

# 显示跳过的图片
if st.session_state.skipped_images:
    with st.expander(get_text('skipped_images', len(st.session_state.skipped_images))):
        show_skipped_images() 
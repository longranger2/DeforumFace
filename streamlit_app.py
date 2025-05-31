import streamlit as st
import cv2
import numpy as np
import os
import glob
from PIL import Image
import io
from head_stabilizer import HeadStabilizer

# 设置页面配置 - 保持最小化但必要的设置
st.set_page_config(
    page_title="头部对齐工具",
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
        st.error("没有找到图片，请先选择文件夹或上传图片")
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
            st.warning(f"无法读取参考图片")
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
        status_text.text(f"处理进度: {processed_count}/{total_files} - {os.path.basename(img_path)}")
        
        try:
            img = cv2.imread(img_path)
            if img is None:
                skipped_images.append((img_path, "无法读取图片"))
                continue
            
            # 如果启用了头部倾斜筛选
            if st.session_state.filter_tilted:
                is_straight, tilt_info, reason = st.session_state.stabilizer.check_head_tilt(img)
                if not is_straight:
                    skipped_images.append((img_path, f"头部倾斜: {reason}"))
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
            skipped_images.append((img_path, f"处理失败: {str(e)}"))
    
    # 然后处理上传的图片
    for i, uploaded_file in enumerate(st.session_state.uploaded_files):
        # 更新进度
        processed_count += 1
        progress = processed_count / total_files
        progress_bar.progress(progress)
        status_text.text(f"处理进度: {processed_count}/{total_files} - {uploaded_file.name}")
        
        try:
            # 读取上传的图片
            file_bytes = uploaded_file.getvalue()
            img, _ = load_image_from_bytes(file_bytes)
            
            if img is None:
                skipped_images.append((uploaded_file.name, "无法读取图片"))
                continue
            
            # 如果启用了头部倾斜筛选
            if st.session_state.filter_tilted:
                is_straight, tilt_info, reason = st.session_state.stabilizer.check_head_tilt(img)
                if not is_straight:
                    skipped_images.append((uploaded_file.name, f"头部倾斜: {reason}"))
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
            skipped_images.append((uploaded_file.name, f"处理失败: {str(e)}"))
    
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
        st.error("没有处理过的图片可以导出为视频")
        return
    
    # 获取参数
    fps = st.session_state.video_fps
    quality = st.session_state.video_quality
    loop = st.session_state.video_loop
    filename = st.session_state.video_filename
    
    if not filename:
        st.error("请输入有效的文件名")
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
    status_text.text("开始导出视频...")
    
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
            status_text.text(f"导出视频进度: {i+1}/{total_frames}")
        
        # 释放视频写入器
        video.release()
        
        # 更新状态
        st.success(f"✅ 视频已成功导出到当前目录")
        
        # 提供下载链接
        with open(output_path, "rb") as file:
            btn = st.download_button(
                label=f"下载视频 ({codec_info['ext']})",
                data=file,
                file_name=f"{filename}.{codec_info['ext']}",
                mime=f"video/{codec_info['ext']}"
            )
        
    except Exception as e:
        st.error(f"导出视频失败: {str(e)}")

def save_all_images():
    """保存所有处理过的图片到程序运行目录"""
    if not st.session_state.processed_images:
        st.error("没有处理过的图片可以保存")
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
            
            status_text.text(f"保存进度: {i+1}/{total} - {base_name}")
            
        except Exception as e:
            st.error(f"保存图片失败 {i}: {str(e)}")
    
    st.success(f"✅ 所有图片已保存到当前目录")

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
            st.image(original_pil, caption=f"原始图片: {os.path.basename(current_path) if isinstance(current_path, str) else current_path}", use_container_width=True)
        else:
            st.write("原始图片无法显示")
    
    with col2:
        st.image(processed_pil, caption="处理后的图片", use_container_width=True)

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
        st.info("没有被跳过的图片")
        return
    
    st.write("### 被跳过的图片")
    for img_path, reason in st.session_state.skipped_images:
        st.write(f"- **{os.path.basename(img_path) if isinstance(img_path, str) and os.path.isfile(img_path) else img_path}**: {reason}")

# ================ 主界面 ==================
st.title("头部对齐工具")
st.write('<p class="info-text">用于创建"瞬息宇宙"风格的照片集合，确保所有照片中的人脸位置保持一致</p>', unsafe_allow_html=True)

# 侧边栏部分 - 所有参数设置
with st.sidebar:
    # 文件选择部分
    with st.expander("📁 文件设置", expanded=True):
        st.markdown('<div class="sidebar-section-title">图片获取方式</div>', unsafe_allow_html=True)
        
        # 允许用户选择图片获取方式：上传图片或指定文件夹路径
        source_tab1, source_tab2 = st.tabs(["上传图片", "指定文件夹"])
        
        with source_tab1:
            st.markdown('<div class="file-uploader">', unsafe_allow_html=True)
            uploaded_files = st.file_uploader(
                "选择图片文件（支持多选）", 
                type=["jpg", "jpeg", "png"], 
                accept_multiple_files=True,
                help="可以一次选择多个图片文件"
            )
            st.markdown('</div>', unsafe_allow_html=True)
            
            if uploaded_files:
                st.session_state.uploaded_files = uploaded_files
                st.success(f"已上传 {len(uploaded_files)} 张图片")
        
        with source_tab2:
            folder_path = st.text_input(
                "图片文件夹路径", 
                value=st.session_state.folder_path if st.session_state.folder_path else "",
                placeholder="输入文件夹路径，如: /Users/username/photos",
                help="指定包含图片的文件夹路径"
            )
            
            if folder_path and folder_path != st.session_state.folder_path:
                if os.path.exists(folder_path):
                    st.session_state.folder_path = folder_path
                    # 查找所有图片
                    st.session_state.image_paths = glob.glob(os.path.join(folder_path, "*.jpg")) + \
                                                  glob.glob(os.path.join(folder_path, "*.jpeg")) + \
                                                  glob.glob(os.path.join(folder_path, "*.png"))
                    
                    if st.session_state.image_paths:
                        st.success(f"找到 {len(st.session_state.image_paths)} 张图片")
                    else:
                        st.error(f"在 {folder_path} 中未找到图片")
                else:
                    st.error(f"文件夹路径不存在: {folder_path}")
    
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    
    # 参考图片设置
    with st.expander("🖼️ 参考图片设置", expanded=True):
        st.markdown('<div class="sidebar-section-title">参考图片</div>', unsafe_allow_html=True)
        
        # 也允许上传参考图片
        ref_tab1, ref_tab2 = st.tabs(["上传参考图片", "指定参考图片路径"])
        
        with ref_tab1:
            uploaded_ref = st.file_uploader(
                "上传参考图片", 
                type=["jpg", "jpeg", "png"],
                help="上传一张作为参考的图片"
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
                        st.image(ref_pil, caption="参考图片", width=150)
                        st.success(f"已上传参考图片: {uploaded_ref.name}")
                else:
                    st.error(f"无法读取参考图片")
        
        with ref_tab2:
            reference_path = st.text_input(
                "参考图片路径", 
                value=st.session_state.reference_image_path if st.session_state.reference_image_path and os.path.exists(st.session_state.reference_image_path) else "",
                placeholder="输入参考图片路径，如: /Users/username/ref.jpg",
                help="指定一张参考图片的路径"
            )
            
            if reference_path and reference_path != st.session_state.reference_image_path:
                if os.path.exists(reference_path):
                    st.session_state.reference_image_path = reference_path
                    ref_cv, ref_pil = load_image_from_path(reference_path)
                    if ref_pil:
                        st.image(ref_pil, caption="参考图片", width=150)
                        st.success(f"已选择参考图片: {os.path.basename(reference_path)}")
                    else:
                        st.error(f"无法读取参考图片: {reference_path}")
                else:
                    st.error(f"参考图片路径不存在: {reference_path}")
        
        st.session_state.force_reference_size = st.checkbox(
            "强制使用参考图片尺寸（推荐）", 
            value=True,
            help="使用参考图片的尺寸作为所有处理图片的输出尺寸"
        )
    
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    
    # 参数设置 - 大幅简化
    with st.expander("⚙️ 处理设置", expanded=True):
        # 简单模式选择
        st.markdown('<div class="sidebar-section-title">处理模式</div>', unsafe_allow_html=True)
        
        mode_choice = st.radio(
            "选择处理模式",
            options=["智能模式 (推荐)", "自定义设置"],
            help="智能模式使用最佳默认参数，适合大多数用户"
        )
        
        if mode_choice == "智能模式 (推荐)":
            # 智能模式 - 只显示最重要的选项
            st.session_state.eye_distance = 30
            st.session_state.filter_tilted = True
            st.session_state.tilt_threshold = 5
            st.session_state.preserve_bg = False
            st.session_state.debug_mode = False
            
            # 只保留头部倾斜筛选这一个重要选项
            st.session_state.filter_tilted = st.checkbox(
                "过滤倾斜头部的照片", 
                value=True,
                help="自动跳过头部明显倾斜的照片，推荐开启"
            )
            
            st.info("💡 智能模式已为您优化所有参数，直接上传图片即可使用")
            
        else:
            # 自定义模式 - 显示所有参数
            st.warning("⚠️ 专家模式：请确保您了解这些参数的含义")
            
            # 眼睛间距
            st.subheader("眼睛间距")
            st.caption("决定人脸在画面中的大小比例，只有在参考图片没有设置的时候才会生效")
            st.session_state.eye_distance = st.slider(
                "眼睛间距百分比", 
                min_value=15, 
                max_value=45, 
                value=30,
                help="眼睛间的距离占据图片宽度的百分比"
            )
            
            # 头部倾斜检测
            st.subheader("头部倾斜检测")
            st.caption("过滤掉头部不端正的照片")
            st.session_state.filter_tilted = st.checkbox(
                "启用头部倾斜筛选", 
                value=True,
                help="自动跳过头部倾斜的照片"
            )
            st.session_state.tilt_threshold = st.slider(
                "倾斜阈值(度)", 
                min_value=1, 
                max_value=30, 
                value=5,
                help="允许的最大头部倾斜角度"
            )
            
            # 其他选项
            st.subheader("其他选项")
            st.session_state.preserve_bg = st.checkbox(
                "保留背景（不推荐）", 
                value=False,
                help="保留原始背景，但可能导致图片尺寸不一致"
            )
            st.session_state.debug_mode = st.checkbox(
                "调试模式（显示关键点）", 
                value=False,
                help="在图片上显示检测到的面部关键点"
            )
    
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    
    # 视频导出设置
    with st.expander("🎬 视频导出 (可选)", expanded=False):
        st.caption("将处理后的图片制作成视频")
        
        fps_options = [2, 4, 8, 16, 32, 64]
        st.session_state.video_fps = st.select_slider(
            "播放速度", 
            options=fps_options, 
            value=st.session_state.video_fps,
            help="数值越高播放越快"
        )
        
        quality_options = ["低", "中", "高"]
        st.session_state.video_quality = st.radio(
            "视频质量", 
            options=quality_options, 
            index=quality_options.index(st.session_state.video_quality),
            horizontal=True
        )
        
        st.session_state.video_loop = st.checkbox(
            "来回循环播放", 
            value=st.session_state.video_loop,
            help="播放到最后会倒序回到开头"
        )
        
        st.session_state.video_filename = st.text_input(
            "文件名", 
            value=st.session_state.video_filename,
            placeholder="输入视频文件名"
        )
    
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    
    # 操作按钮
    with st.expander("🚀 操作", expanded=True):
        has_images = len(st.session_state.image_paths) > 0 or len(st.session_state.uploaded_files) > 0
        
        if st.button(
            "处理所有图片", 
            type="primary", 
            disabled=not has_images,
            help="根据当前设置处理所有图片"
        ):
            process_images()
        
        nav_col1, nav_col2 = st.columns(2)
        with nav_col1:
            if st.button(
                "上一张", 
                disabled=not st.session_state.processed_images,
                help="显示上一张图片"
            ):
                prev_image()
        
        with nav_col2:
            if st.button(
                "下一张", 
                disabled=not st.session_state.processed_images,
                help="显示下一张图片"
            ):
                next_image()
        
        action_col1, action_col2 = st.columns(2)
        with action_col1:
            if st.button(
                "保存所有图片", 
                disabled=not st.session_state.processed_images,
                help="将所有处理后的图片保存到程序目录"
            ):
                save_all_images()
        
        with action_col2:
            if st.button(
                "导出为视频", 
                disabled=not st.session_state.processed_images,
                help="将所有处理后的图片导出为视频到程序目录"
            ):
                export_video()
    
    # 版本信息
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    st.caption("头部对齐工具 v2.1")

# 主区域 - 仅显示图片和结果
if st.session_state.processed_images:
    st.write(f"#### 显示: {st.session_state.current_index + 1}/{len(st.session_state.processed_images)}")
    show_current_image()
    
    # 结果区导航按钮
    col1, col2, col3 = st.columns([1, 3, 1])
    with col1:
        if st.button("上一张 ⬅️", disabled=not st.session_state.processed_images):
            prev_image()
    
    with col3:
        if st.button("下一张 ➡️", disabled=not st.session_state.processed_images):
            next_image()
else:
    if st.session_state.image_paths or st.session_state.uploaded_files:
        st.info("请点击「处理所有图片」按钮开始处理")
        st.markdown("""
        <div style="display: flex; justify-content: center; margin-top: 2rem;">
            <div style="text-align: center; max-width: 600px;">
                <img src="https://oss.streamlit.io/images/brand/streamlit-mark-color.png" width="100">
                <p style="margin-top: 1rem; color: #888;">准备就绪，点击侧边栏中的"处理所有图片"按钮开始处理</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.info("请先在侧边栏选择图片文件夹或上传图片")
        st.markdown("""
        <div style="display: flex; justify-content: center; margin-top: 2rem;">
            <div style="text-align: center; max-width: 600px;">
                <img src="https://oss.streamlit.io/images/brand/streamlit-mark-color.png" width="100">
                <p style="margin-top: 1rem; color: #888;">使用侧边栏的"文件设置"部分上传图片或指定图片文件夹</p>
            </div>
        </div>
        """, unsafe_allow_html=True)

# 显示跳过的图片
if st.session_state.skipped_images:
    with st.expander(f"被跳过的图片 ({len(st.session_state.skipped_images)} 张)"):
        show_skipped_images() 
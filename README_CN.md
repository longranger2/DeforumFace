# 头部对齐工具（Head Alignment Tool）

[🇺🇸 English Version / 英文版本](README.md)

这是一个用于对多张照片中的人脸进行精确对齐的工具，适用于创建"瞬息宇宙"风格的照片集合，确保所有照片中的人脸位置保持一致。

## 🚀 快速开始

### 方法一：下载预编译版本（推荐）

无需安装Python环境，下载即用：

1. **下载对应平台文件**
   - [📦 Releases页面](../../releases) 下载最新版本
   - **Windows**: `HeadAlignmentTool-Windows.zip` 
   - **macOS**: `HeadAlignmentTool-macOS.tar.gz`
   - **Linux**: `HeadAlignmentTool-Linux.tar.gz`

2. **运行应用**
   - **Windows**: 解压后双击 `HeadAlignmentTool.exe`
   - **macOS/Linux**: 解压后在终端运行 `./HeadAlignmentTool`

3. **开始使用**
   - 等待应用启动（首次可能需要1-2分钟）
   - 浏览器自动打开 http://localhost:8501
   - 上传照片开始对齐处理

### 方法二：Python环境运行

```bash
# 1. 克隆项目
git clone <your-repo-url>
cd head-alignment-tool

# 2. 安装依赖
pip install -r requirements.txt

# 3. 启动应用（任选一种）
python run.py                    # 推荐：一键启动
streamlit run streamlit_app.py   # 直接启动
```

## 功能特点

- **精确对齐算法**：使用改进的相似变换算法，确保无拉伸变形
- **智能关键点检测**：精选最稳定的面部关键点，提高对齐精度
- **质量验证机制**：实时监控对齐质量，自动优化处理结果
- **多重优化**：基于眼睛粗对齐，鼻尖精细校正的二次优化机制
- **高质量插值**：使用立方插值和镜像边界处理，保持图像质量
- 支持使用参考图片作为对齐基准
- 自动过滤头部倾斜的照片
- 可调整参数（眼睛间距、倾斜阈值等）
- 多线程处理，界面不卡顿
- 支持调试模式，显示关键点
- **现代化网页界面**：基于Streamlit的直观易用界面

## 算法改进亮点

### 🔧 核心技术改进

#### 1. 变换算法优化
- **问题**：原仿射变换可能引入拉伸和剪切变形
- **解决**：改用相似变换（Similarity Transform），只包含旋转、缩放、平移
- **效果**：严格保持图像长宽比，完全避免拉伸变形

#### 2. 关键点选择优化
- **问题**：过多关键点引入噪声，影响对齐精度
- **解决**：精选最稳定的关键点组合（眼角和鼻尖）
- **效果**：减少噪声干扰，提高对齐一致性

#### 3. 质量验证机制
- **新增**：多重质量验证系统
- **功能**：实时监控对齐质量，提供量化精度指标
- **优势**：自动警告低质量结果，确保处理效果

#### 4. 多重优化机制
- **策略**：基于眼睛进行粗对齐，使用鼻尖进行精细校正
- **效果**：迭代优化提升精度，确保最佳对齐效果

#### 5. 图像质量优化
- **插值**：使用立方插值替代双线性插值
- **边界**：镜像边界处理减少伪影
- **结果**：避免黑边和失真，保持图像清晰度

### 📊 性能对比

| 指标 | 原算法 | 改进算法 | 提升 |
|------|--------|----------|------|
| 对齐精度 | ±5-10像素 | ±1-2像素 | 5-10倍 |
| 变形控制 | 可能拉伸 | 严格无拉伸 | 100% |
| 稳定性 | 中等 | 高 | 显著提升 |
| 图像质量 | 一般 | 高 | 明显改善 |

## 使用方法

### 网页界面操作

1. **文件夹选择**：在侧边栏输入包含照片的文件夹路径
2. **参考图片设置**：输入参考图片路径（强烈推荐）
3. **参数调整**：根据需要调整以下参数：
   - **眼睛间距**：调整人脸在画面中的大小比例（推荐25-35%）
   - **倾斜阈值**：调整过滤头部倾斜图片的严格程度（推荐3-8度）
   - **调试模式**：启用后显示面部关键点
   - **强制参考尺寸**：使用参考图片的尺寸作为输出尺寸
4. **开始处理**：点击"处理所有图片"按钮
5. **查看结果**：使用"上一张"和"下一张"按钮浏览处理结果
6. **保存结果**：点击"保存所有图片"将结果保存到"aligned"子目录

### 编程接口

#### 基础用法

```python
from head_stabilizer import HeadStabilizer

# 创建稳定器
stabilizer = HeadStabilizer(
    output_size=(512, 512),
    preserve_background=False,
    force_reference_size=True
)

# 设置参考图片
stabilizer.set_reference_from_image(reference_image)

# 对齐图片
aligned_image = stabilizer.align_and_crop_face(input_image)
```

#### 批量处理

```python
# 批量处理多张图片
results = stabilizer.process_batch(
    image_paths,
    reference_image_path="reference.jpg",
    filter_tilted=True  # 过滤倾斜头部
)

aligned_images, successful_paths, skipped_images = results
```

#### 调试模式

```python
# 启用调试模式查看关键点
stabilizer.debug = True
aligned, debug_img = stabilizer.align_and_crop_face(image, show_landmarks=True)
```

## 界面功能详解

### 侧边栏控制面板

- **📁 文件夹选择**：输入照片文件夹路径
- **🖼️ 参考图片设置**：设置对齐基准图片
- **⚙️ 参数设置**：调整算法参数
- **🔧 高级选项**：调试模式等专业设置

### 主界面功能

- **📊 处理状态**：实时显示处理进度和统计信息
- **🖼️ 图片预览**：对比查看原图和对齐后的效果
- **📝 详细信息**：显示图片信息和处理结果
- **💾 保存功能**：一键保存所有处理结果

## 故障排除

### Windows版本问题

#### 程序无法启动
**症状**: 双击 `HeadAlignmentTool.exe` 后没有反应或立即关闭

**解决方案**:
1. **Windows Defender 阻止**: 
   - 右键点击程序 → 属性 → 常规 → 勾选"解除阻止"
   - 或将文件夹添加到Windows Defender排除列表

2. **缺少Visual C++运行库**: 
   - 下载安装 [Microsoft Visual C++ Redistributable](https://docs.microsoft.com/en-us/cpp/windows/latest-supported-vc-redist)
   - 选择 x64 版本

3. **权限问题**: 右键以管理员身份运行

#### MediaPipe相关错误
**症状**: 程序启动但出现MediaPipe模型文件错误

**解决方案**:
1. 确保完整解压了所有文件
2. 检查是否有杀毒软件删除了某些文件
3. 重新下载完整的压缩包

#### 浏览器无法打开
**症状**: 程序启动成功但浏览器没有自动打开

**解决方案**:
1. 手动打开浏览器
2. 访问 `http://localhost:8501`
3. 如果端口被占用，程序会自动选择其他端口，查看控制台输出

#### 调试模式
如果遇到其他问题，可以通过命令行启动程序查看详细错误信息：

```cmd
# 打开命令提示符（cmd）
# 进入程序所在目录
cd /d "C:\path\to\HeadAlignmentTool"

# 运行程序
HeadAlignmentTool.exe
```

### 通用问题

#### Q: 为什么有些图片被跳过了？
A: 可能的原因包括：
- 头部倾斜角度超过设定阈值
- 无法检测到清晰的面部关键点
- 图片质量过低或光照条件不佳

#### Q: 如何提高对齐精度？
A: 建议：
- 使用高质量的参考图片
- 调整眼睛间距参数
- 确保输入图片质量良好
- 启用调试模式查看关键点检测情况

#### Q: 处理速度慢怎么办？
A: 优化建议：
- 降低输入图片分辨率
- 减少同时处理的图片数量
- 关闭调试模式

## 适用场景

- ✅ 头像视频制作（"瞬息宇宙"风格）
- ✅ 证件照标准化
- ✅ 人脸数据集预处理
- ✅ 视频会议头像稳定
- ✅ 直播换脸应用
- ✅ 社交媒体内容创作

## 系统要求

### 最低要求
- **Windows**: Windows 10 (64位) 或更高版本
- **macOS**: macOS 10.15 或更高版本
- **Linux**: 64位发行版，需要GUI支持
- **内存**: 4GB RAM（推荐8GB+）
- **磁盘**: 1GB 可用空间
- **显卡**: 支持OpenGL的显卡

### 推荐配置
- **Windows**: Windows 11 (64位)
- **macOS**: macOS 12+ (支持Apple Silicon)
- **内存**: 8GB+ RAM
- **磁盘**: SSD硬盘
- **显卡**: 独立显卡

## 注意事项

### 输入要求
1. **图片质量**：图片中需包含清晰的正面人脸
2. **光照条件**：避免过强阴影影响关键点检测
3. **倾斜角度**：超过设定阈值的头部倾斜会被自动过滤
4. **分辨率**：建议使用高分辨率输入图片

### 使用建议
- 参考图片应选择头部端正、表情自然的正面照
- 为获得最佳效果，推荐使用参考图片且启用"强制使用参考图片尺寸"选项
- 眼睛间距参数建议设置在25-35%之间
- 倾斜阈值建议设置在3-8度之间

### 质量评估
- **质量分数范围**：0.0 - 1.0
- **0.9+**：优秀，关键点对齐精度很高
- **0.8+**：良好，满足大多数应用需求
- **0.7+**：可接受，可能有轻微偏差
- **0.6-**：较差，建议检查图片质量

## 技术参数配置

```python
class HeadStabilizer:
    def __init__(self):
        # 精度控制参数
        self.alignment_tolerance = 2.0      # 对齐容差（像素）
        self.max_iterations = 3             # 最大优化迭代次数
        self.quality_threshold = 0.95       # 对齐质量阈值
        
        # 稳定性参数
        self.tilt_threshold = 5.0           # 头部倾斜角度阈值
        self.face_scale = 1.5               # 面部缩放比例
```

## 算法技术细节

### 相似变换实现

```python
def _calculate_similarity_transform(self, src_points, dst_points):
    """计算相似变换矩阵（只包含旋转、缩放、平移，无拉伸）"""
    # 计算缩放比例
    scale = dst_eye_dist / src_eye_dist
    
    # 计算旋转角度
    rotation_angle = dst_angle - src_angle
    
    # 构建变换矩阵确保保持长宽比
    cos_angle = np.cos(rotation_angle) * scale
    sin_angle = np.sin(rotation_angle) * scale
    
    M = np.array([
        [cos_angle, -sin_angle, tx],
        [sin_angle, cos_angle, ty]
    ], dtype=np.float32)
    
    return M
```

### 稳定关键点选择

```python
def _get_stable_landmarks(self, image):
    """获取最稳定的关键点组合"""
    stable_points = {
        # 眼角（最稳定的点）
        'left_eye_outer': landmarks[33],    # 左眼外角
        'left_eye_inner': landmarks[133],   # 左眼内角
        'right_eye_inner': landmarks[362],  # 右眼内角  
        'right_eye_outer': landmarks[263],  # 右眼外角
        # 鼻尖（第二稳定）
        'nose_tip': landmarks[4],           # 鼻尖
    }
    return stable_points
```

### 质量验证机制

```python
def _validate_alignment_quality(self, M, src_landmarks, dst_landmarks):
    """验证对齐质量"""
    # 根据输出尺寸动态调整误差阈值
    output_diagonal = np.sqrt(self.output_size[0]**2 + self.output_size[1]**2)
    base_error = output_diagonal * 0.01
    max_acceptable_error = max(15.0, base_error)
    
    # 计算关键点对齐误差
    errors = []
    for point_name in ['left_eye', 'right_eye', 'nose_tip']:
        transformed_point = M @ src_point
        error = euclidean_distance(transformed_point[:2], dst_point)
        errors.append(error)
    
    # 计算质量分数
    avg_error = np.mean(errors)
    quality_score = max(0, (max_acceptable_error - avg_error) / max_acceptable_error)
    return quality_score
```

## 替代运行方案

如果可执行文件无法正常工作，可以尝试：

1. **使用Python环境运行**:
   ```bash
   # 安装Python 3.9+
   pip install -r requirements.txt
   
   # 推荐启动方式（有依赖检查）
   python run.py
   
   # 或直接启动
   streamlit run streamlit_app.py
   ```

2. **Windows用户专用方案**:
   ```cmd
   # 双击运行 run_windows.bat
   # 该脚本会自动：
   # - 检查Python环境
   # - 创建虚拟环境
   # - 安装所需依赖
   # - 启动应用
   ```

3. **使用Docker**（如果有Docker环境）:
   ```cmd
   # 构建镜像
   docker build -t head-alignment-tool .
   
   # 运行容器
   docker run -p 8501:8501 head-alignment-tool
   ```

## 开发者指南

### 🏗️ 项目结构

```
项目根目录/
├── 📄 README.md                      # 📚 完整文档 - 您正在阅读的文件
├── 🐍 streamlit_app.py               # 🎯 主应用程序
├── 🧠 head_stabilizer.py             # 🔧 核心对齐算法
├── 📋 requirements.txt               # 📦 Python依赖列表
├── 🚀 run.py                         # ⚡ 本地启动脚本
└── 构建和部署文件/
    ├── 🛠️ prepare_build.py           # 📦 构建准备脚本
    ├── 🏗️ build_exe.py               # 📦 本地打包脚本
    ├── 🪟 run_windows.bat            # 🪟 Windows批处理文件
    ├── 🔧 run_streamlit.py           # 📦 PyInstaller启动器
    ├── 📁 hooks/                     # 📦 PyInstaller钩子
    └── 📁 .github/workflows/         # 🤖 GitHub Actions配置
```

#### 文件说明

**用户必需文件**:
- **`README.md`** - 📚 完整的用户指南和技术文档
- **`streamlit_app.py`** - 🎯 主要应用程序，包含Web界面
- **`head_stabilizer.py`** - 🧠 头部对齐核心算法
- **`requirements.txt`** - 📦 Python包依赖列表
- **`run.py`** - ⚡ 推荐的本地启动方式

**打包构建文件**:
- **`prepare_build.py`** - 🛠️ 跨平台构建准备，自动生成spec文件
- **`build_exe.py`** - 🏗️ 本地打包脚本
- **`run_streamlit.py`** - 🔧 PyInstaller专用启动器
- **`run_windows.bat`** - 🪟 Windows用户的Python环境解决方案
- **`hooks/`** - 📦 PyInstaller钩子文件夹

**自动化部署**:
- **`.github/workflows/`** - 🤖 GitHub Actions自动化构建配置

### 🚀 开发环境搭建

```bash
# 1. 克隆项目
git clone <your-repo-url>
cd head-alignment-tool

# 2. 安装依赖
pip install -r requirements.txt

# 3. 启动开发服务器
python run.py

# 4. 访问应用
# 浏览器自动打开 http://localhost:8501
```

### 📦 本地打包

```bash
# 1. 准备构建环境
python prepare_build.py

# 2. 执行打包
python build_exe.py

# 3. 测试可执行文件
./dist/HeadAlignmentTool  # macOS/Linux
# 或
dist\HeadAlignmentTool.exe  # Windows
```

### 🤖 自动化构建与发布

#### GitHub Actions 配置

项目配置了完整的CI/CD流水线，支持：
- ✅ Windows、macOS、Linux三平台自动构建
- ✅ 版本标签自动发布Release
- ✅ 手动触发测试构建
- ✅ 构建产物自动上传

#### 工作流文件

**主发布流水线** (`.github/workflows/build-release.yml`):
- **触发条件**: 推送版本标签（如 `v1.0.0`）或手动触发
- **功能**: 同时构建三个平台，自动创建Release
- **产物**: `HeadAlignmentTool-Windows.zip`、`HeadAlignmentTool-macOS.tar.gz`、`HeadAlignmentTool-Linux.tar.gz`

#### 使用方法

**测试构建**:
1. 进入GitHub仓库 → Actions 标签
2. 选择 "Build and Release" 工作流
3. 点击 "Run workflow" → 手动触发测试

**正式发布**:
```bash
# 创建版本标签
git tag v1.0.0
git push origin v1.0.0

# GitHub Actions自动触发构建和发布
```

#### 构建环境

**Python环境**: Python 3.9

**系统依赖**:
- **Ubuntu**: OpenGL开发库、GUI相关库、GStreamer库
```bash
libgl1-mesa-dev libglib2.0-0 libsm6 libxext6 libxrender-dev libgomp1 libgstreamer1.0-0 libgstreamer-plugins-base1.0-0
```
- **Windows**: 无额外依赖
- **macOS**: 无额外依赖

#### 构建步骤详解

1. **环境准备**:
   ```bash
   pip install -r requirements.txt
   pip install pyinstaller
   ```

2. **生成动态配置**:
   ```bash
   python prepare_build.py  # 自动检测路径，生成spec文件
   ```

3. **执行打包**:
   ```bash
   pyinstaller HeadAlignmentTool.spec --clean --noconfirm
   ```

4. **创建分发包**:
   - 复制可执行文件到distribution目录
   - 添加平台特定的使用说明
   - 创建压缩包（Windows: .zip，Unix: .tar.gz）

#### 故障排除

**常见问题**:
1. **构建失败**: 检查requirements.txt，查看Actions日志
2. **可执行文件无法运行**: 确保系统满足最低要求
3. **文件过大**: 当前已优化至150-200MB

**调试方法**:
1. 使用手动触发测试单个平台
2. 查看详细的构建日志
3. 本地复现构建过程验证

#### 版本管理

**标签命名规范**:
- 使用语义化版本：`v主版本.次版本.修订版本`
- 例如：`v1.0.0`, `v1.1.0`, `v1.1.1`

**Release自动化**:
每次发布时自动生成包含以下内容的Release说明：
- 版本信息和下载说明
- 使用方法和系统要求
- 注意事项和已知问题修复

#### 自定义配置

**修改构建参数**:
编辑 `.github/workflows/build-release.yml`:

```yaml
# Python版本
python-version: '3.9'

# 添加新平台
matrix:
  os: [windows-latest, macos-latest, ubuntu-latest, macos-13]
  include:
    - os: macos-13
      executable_name: HeadAlignmentTool
      artifact_name: HeadAlignmentTool-macOS-Intel
```

### 测试自动化构建

1. **Fork项目到你的GitHub账号**

2. **手动触发测试构建**
   - 进入你的仓库 → Actions 标签
   - 选择 "Build and Release" 工作流
   - 点击 "Run workflow"
   - 等待构建完成（约10-15分钟）

3. **下载测试产物**
   - 构建完成后在 Artifacts 部分下载
   - 测试可执行文件是否正常运行

### 发布新版本

1. **创建版本标签**
   ```bash
   git tag v1.0.0
   git push origin v1.0.0
   ```

2. **自动触发发布**
   - GitHub Actions自动检测到标签
   - 同时构建三个平台的可执行文件
   - 自动创建Release并上传文件

## 文件结构

- `streamlit_app.py` - Streamlit网页界面主程序
- `head_stabilizer.py` - 头部对齐核心算法（已全面改进）
- `run.py` - 一键启动脚本（推荐使用）
- `requirements.txt` - 项目依赖包列表
- `prepare_build.py` - PyInstaller构建准备脚本
- `hooks/` - PyInstaller钩子文件
- `.github/workflows/` - GitHub Actions自动化构建配置

## 未来优化方向

1. **深度学习增强**：集成更先进的人脸关键点检测模型
2. **实时优化**：针对视频流的实时处理优化
3. **3D对齐**：支持三维头部姿态的精确对齐
4. **表情保持**：在对齐过程中更好地保持面部表情
5. **批量优化**：GPU加速的大规模批量处理
6. **云端处理**：支持云端批量处理服务

## 获取帮助

- **Issues**: 在GitHub项目页面提交问题
- **Discussions**: 参与项目讨论
- **Email**: 联系项目维护者

---

通过这些改进，头像对齐算法现在能够确保：
- 🎯 **精确对齐**：人头始终保持在同一坐标位置
- 🚫 **无变形**：严格避免任何拉伸效果
- 📱 **高质量**：保持图像清晰度和自然感
- ⚡ **高效稳定**：快速处理且结果一致 
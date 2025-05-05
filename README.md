# 头部对齐工具（Head Alignment Tool）

这是一个用于对多张照片中的人脸进行精确对齐的工具，适用于创建"瞬息宇宙"风格的照片集合，确保所有照片中的人脸位置保持一致。

## 功能特点

- 自动检测人脸关键点并进行精确对齐
- 支持使用参考图片作为对齐基准
- 自动过滤头部倾斜的照片
- 可调整参数（眼睛间距、倾斜阈值等）
- 多线程处理，界面不卡顿
- 支持调试模式，显示关键点
- 提供两种用户界面：传统Tkinter和现代Streamlit网页界面

## 文件结构

- `main.py` - 程序入口点，处理命令行参数
- `head_stabilizer.py` - 头部对齐核心算法
- `head_alignment_viewer.py` - Tkinter图形界面组件
- `streamlit_app.py` - Streamlit网页界面

## 依赖库

- OpenCV
- NumPy
- Mediapipe
- Tkinter (Tkinter界面)
- PIL (Pillow)
- Streamlit (Streamlit界面)

## 安装依赖

### 基本依赖

```bash
pip install opencv-python numpy mediapipe pillow
```

### Streamlit界面依赖

```bash
pip install streamlit
```

## 使用方法

### Tkinter界面

#### 基本用法

```bash
python main.py --folder "照片文件夹路径"
```

#### 带参数的用法

```bash
python main.py --folder "照片文件夹路径" --reference "参考图片路径" --debug --size 800 600
```

#### 命令行参数

- `--folder`, `-f`: 要处理的图片文件夹路径
- `--reference`, `-r`: 参考图片路径（强烈推荐提供）
- `--debug`, `-d`: 启用调试模式，显示面部关键点
- `--size`, `-s`: 默认输出图像尺寸，例如: 512 512 (如提供参考图片则使用参考图片尺寸)
- `--keep-background`, `-k`: 保留背景（不推荐，可能导致尺寸不一致）

### Streamlit界面

#### 启动Streamlit应用

```bash
streamlit run streamlit_app.py
```

启动后，会自动打开浏览器访问本地Streamlit应用（通常是 http://localhost:8501）

## 操作指南

### Tkinter界面

1. 启动程序后，建议先选择一张参考图片
2. 调整参数（如需要）：
   - 眼睛间距：控制人脸在输出图像中的大小比例
   - 倾斜阈值：控制过滤头部倾斜照片的严格程度
3. 点击"重新处理所有图片"
4. 使用左右方向键或界面按钮浏览处理结果
5. 点击"保存所有图片"将结果保存到"aligned"文件夹

### Streamlit界面

1. 在侧边栏的"文件夹选择"中输入照片文件夹路径
2. 在"参考图片设置"中输入参考图片路径（推荐）
3. 根据需要在"参数设置"中调整参数：
   - 眼睛间距：调整人脸在画面中的大小比例
   - 倾斜阈值：调整过滤头部倾斜图片的严格程度 
   - 其他选项：如调试模式、保留背景等
4. 点击"重新处理所有图片"按钮开始处理
5. 使用"上一张"和"下一张"按钮浏览处理结果
6. 点击"保存所有图片"将结果保存到文件夹中的"aligned"子目录

## 注意事项

- 参考图片应选择头部端正、表情自然的正面照
- 为获得最佳效果，推荐使用参考图片且启用"强制使用参考图片尺寸"选项
- 不推荐启用"保留背景"选项，可能导致输出图片尺寸不一致
- Streamlit界面提供更现代的用户体验，推荐优先使用

## 快捷键

### Tkinter界面

- 左方向键：上一张图片
- 右方向键：下一张图片
- 空格键：下一张图片 
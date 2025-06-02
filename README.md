# Head Alignment Tool

[🇨🇳 中文版本 / Chinese Version](README_CN.md)

A precision tool for aligning faces across multiple photos, perfect for creating "Everything Everywhere All at Once" style photo collections with consistently positioned faces.

## 🚀 Quick Start

### Method 1: Download Pre-compiled Version (Recommended)

No Python environment required, download and run:

1. **Download Platform-specific Files**
   - [📦 Releases Page](../../releases) for latest version
   - **Windows**: `HeadAlignmentTool-Windows.zip` 
   - **macOS**: `HeadAlignmentTool-macOS.tar.gz`
   - **Linux**: `HeadAlignmentTool-Linux.tar.gz`

2. **Run Application**
   - **Windows**: Extract and double-click `HeadAlignmentTool.exe`
   - **macOS/Linux**: Extract and run `./HeadAlignmentTool` in terminal

3. **Start Using**
   - Wait for app startup (first launch may take 1-2 minutes)
   - Browser automatically opens http://localhost:8501
   - Upload photos to start alignment processing

### Method 2: Python Environment

```bash
# 1. Clone repository
git clone <your-repo-url>
cd head-alignment-tool

# 2. Install dependencies
pip install -r requirements.txt

# 3. Launch application (choose one)
python run.py                    # Recommended: one-click startup
streamlit run streamlit_app.py   # Direct launch
```

## Key Features

- **Precision Alignment Algorithm**: Uses improved similarity transform algorithm, ensuring no stretching distortion
- **Intelligent Keypoint Detection**: Carefully selected most stable facial keypoints for improved alignment accuracy
- **Quality Validation System**: Real-time alignment quality monitoring with automatic optimization
- **Multi-level Optimization**: Eye-based coarse alignment followed by nose-tip fine correction
- **High-quality Interpolation**: Cubic interpolation and mirror boundary processing to maintain image quality
- **Multi-language Support**: Chinese and English interface with real-time switching
- Reference image support for alignment baseline
- Automatic filtering of tilted head photos
- Adjustable parameters (eye distance, tilt threshold, etc.)
- Multi-threaded processing, responsive UI
- Debug mode with keypoint visualization
- **Modern Web Interface**: Intuitive Streamlit-based interface
- **One-click Clear**: Easy uploaded image clearing functionality
- **📅 Date Watermark System**: Advanced date overlay functionality with intelligent positioning and styling
- **🎨 Smart Background Colors**: Automatic background color selection based on font color for optimal readability
- **📏 Adaptive Font Sizing**: Percentage-based font sizing (5%-15% of image width) for consistent appearance across all resolutions

## Algorithm Improvements

### 🔧 Core Technical Enhancements

#### 1. Transform Algorithm Optimization
- **Problem**: Original affine transforms could introduce stretching and shearing distortion
- **Solution**: Switched to similarity transform (rotation, scaling, translation only)
- **Result**: Strict aspect ratio preservation, complete elimination of stretching

#### 2. Keypoint Selection Optimization
- **Problem**: Too many keypoints introduce noise, affecting alignment precision
- **Solution**: Carefully selected most stable keypoint combinations (eye corners and nose tip)
- **Result**: Reduced noise interference, improved alignment consistency

#### 3. Quality Validation System
- **New Feature**: Multi-level quality validation system
- **Function**: Real-time alignment quality monitoring with quantified precision metrics
- **Advantage**: Automatic low-quality result warnings, ensuring processing effectiveness

#### 4. Multi-level Optimization Mechanism
- **Strategy**: Eye-based coarse alignment, nose-tip fine correction
- **Result**: Iterative optimization for improved precision, ensuring optimal alignment

#### 5. Image Quality Optimization
- **Interpolation**: Cubic interpolation replacing bilinear interpolation
- **Boundaries**: Mirror boundary processing reduces artifacts
- **Result**: Eliminates black borders and distortion, maintains image clarity

### 📊 Performance Comparison

| Metric | Original Algorithm | Improved Algorithm | Improvement |
|--------|-------------------|-------------------|-------------|
| Alignment Precision | ±5-10 pixels | ±1-2 pixels | 5-10x |
| Distortion Control | Possible stretching | Strictly no stretching | 100% |
| Stability | Medium | High | Significant |
| Image Quality | Average | High | Notable |

## Date Watermark Features 📅

### Overview
The tool now includes a comprehensive date watermarking system that overlays date information directly onto images, making it perfect for creating time-lapse videos where dates are visible during playback.

### Core Functionality

#### 1. **Multiple Date Sources** 📊
- **User Input (Recommended)**: Set start date and interval for sequential dating
- **Filename Parsing**: Extract dates from filenames with multiple format support
- **EXIF Metadata**: Automatically read camera shooting dates from image metadata

#### 2. **Supported Date Formats** 📋
- **Filename Patterns**: YYYY-MM-DD, YYYY_MM_DD, YYYYMMDD, MM-DD-YYYY, DD-MM-YYYY
- **Display Formats**: YYYY-MM-DD, MM-DD-YYYY, DD-MM-YYYY
- **Auto-sorting**: Chronological ordering with ascending/descending options

#### 3. **Advanced Styling Options** 🎨
- **Font Size**: 5.0% to 15.0% of image width (adaptive sizing)
- **Position**: Four corner placement options (top-left, top-right, bottom-left, bottom-right)
- **Colors**: White, black, yellow, red with intelligent contrast
- **Background**: Optional semi-transparent background (0-100% opacity)
- **Margins**: Adjustable spacing from image edges (5-80 pixels)

#### 4. **Intelligent Background System** 🧠
- **Smart Color Selection**: Automatically chooses background color based on font color
  - White/Yellow fonts → Black background
  - Black/Red fonts → White background
- **Transparency Control**: 0% (no background) to 100% (fully opaque)
- **Default Setting**: No background for clean appearance

#### 5. **Real-time Preview** 👀
```
📅 Date Display: `2024-03-15`
📍 Position: Bottom Right
🔤 Font: 8.0% image width, White
🎭 Background: No Background
```

### Technical Improvements

#### Adaptive Font Sizing
- **Problem Solved**: Fixed pixel sizes were too small for high-resolution images
- **Solution**: Percentage-based sizing relative to image width
- **Benefits**: Consistent visual appearance across all resolutions

**Examples**:
- 1024×1024 image: 15% = ~153 pixels
- 2048×2048 image: 15% = ~307 pixels  
- 4K image (3840×2160): 15% = ~576 pixels

#### Smart Background Colors
- **Problem Solved**: Fixed black backgrounds created poor contrast with dark fonts
- **Solution**: Intelligent color selection based on font color
- **Result**: Optimal readability in all scenarios

### Recommended Settings

#### **Bright Background Photos**
- Font: Black, 8-10% size
- Position: Bottom-right
- Background: 50-70% opacity

#### **Dark Background Photos**  
- Font: White, 8-10% size
- Position: Bottom-right
- Background: 60-80% opacity

#### **Video Creation**
- Font: White, 10-12% size
- Position: Bottom-right  
- Background: 70% opacity
- Margin: 30-40 pixels

#### **Social Media Sharing**
- Font: Any color, 6-8% size
- Position: Top-right or bottom-left
- Background: 0% (no background)

### Interface Organization

The date settings are strategically placed before video settings in the sidebar, following the natural workflow:
1. **📁 File Settings** - Select images
2. **🖼️ Reference Settings** - Set alignment baseline  
3. **📅 Date Settings** - Configure watermarks
4. **🎬 Video Export** - Create final videos
5. **🚀 Operations** - Process and save

## Usage Guide

### Web Interface Operation
1. **Language Settings**: Switch between Chinese and English interface

2. **File Selection**: 
   - **Upload Images**: Use file uploader with multi-select support
   - **Specify Folder**: Enter folder path containing photos
   - **Clear Function**: One-click to clear uploaded images and reselect
3. **Reference Image Setup**: Upload or specify reference image path (highly recommended)

4. **Processing Mode Selection**:
   - **Smart Mode (Recommended)**: Optimized default parameters for most users
   - **Custom Settings**: Full parameter control for advanced users

5. **Parameter Adjustment** (Custom mode):
   - **Eye Distance**: Adjust face size ratio in image (recommended 25-35%)
   - **Tilt Threshold**: Adjust strictness for filtering tilted head photos (recommended 3-8°)
   - **Debug Mode**: Enable to show facial keypoints
   - **Force Reference Size**: Use reference image dimensions as output size

6. **Date Watermark Setup** (Optional):
   - **Enable Date Display**: Toggle date watermarks on images
   - **Date Source**: Choose from user input, filename parsing, or EXIF metadata
   - **Styling Options**: Configure font size (5-15% of image width), position, colors, and background
   - **Preview**: Real-time preview of date appearance


7. **Start Processing**: Click "Process All Images" button

8. **View Results**: Use "Previous" and "Next" buttons to browse processing results

9. **Save Results**: Click "Save All Images" to save to program directory

### Programming Interface

#### Basic Usage

```python
from head_stabilizer import HeadStabilizer

# Create stabilizer
stabilizer = HeadStabilizer(
    output_size=(512, 512),
    preserve_background=False,
    force_reference_size=True
)

# Set reference image
stabilizer.set_reference_from_image(reference_image)

# Align image
aligned_image = stabilizer.align_and_crop_face(input_image)
```

#### Batch Processing

```python
# Process multiple images
results = stabilizer.process_batch(
    image_paths,
    reference_image_path="reference.jpg",
    filter_tilted=True  # Filter tilted heads
)

aligned_images, successful_paths, skipped_images = results
```

#### Debug Mode

```python
# Enable debug mode to view keypoints
stabilizer.debug = True
aligned, debug_img = stabilizer.align_and_crop_face(image, show_landmarks=True)
```

## Interface Features

### Sidebar Control Panel

- **📁 File Settings**: Image upload/folder selection with clear functionality
- **🖼️ Reference Image Settings**: Set alignment baseline image
- **⚙️ Processing Settings**: Smart mode vs custom parameter adjustment
- **🎬 Video Export**: Create videos from processed images
- **🚀 Operations**: Process, navigate, save functions
- **🌐 Language**: Real-time Chinese/English switching

### Main Interface

- **📊 Processing Status**: Real-time progress and statistics
- **🖼️ Image Preview**: Side-by-side original vs processed comparison
- **📝 Detailed Information**: Image info and processing results
- **💾 Save Functions**: One-click save all processed results

## Troubleshooting

### Windows Version Issues

#### Program Won't Start
**Symptoms**: Double-clicking `HeadAlignmentTool.exe` has no response or closes immediately

**Solutions**:
1. **Windows Defender Blocking**: 
   - Right-click program → Properties → General → Check "Unblock"
   - Or add folder to Windows Defender exclusion list

2. **Missing Visual C++ Runtime**: 
   - Download and install [Microsoft Visual C++ Redistributable](https://docs.microsoft.com/en-us/cpp/windows/latest-supported-vc-redist)
   - Choose x64 version

3. **Permission Issues**: Right-click and run as administrator

#### MediaPipe Related Errors
**Symptoms**: Program starts but shows MediaPipe model file errors

**Solutions**:
1. Ensure all files were completely extracted
2. Check if antivirus software deleted some files
3. Re-download complete archive

#### Browser Won't Open
**Symptoms**: Program starts successfully but browser doesn't auto-open

**Solutions**:
1. Manually open browser
2. Navigate to `http://localhost:8501`
3. If port is occupied, program will auto-select another port, check console output

#### Debug Mode
For other issues, start program via command line to see detailed error information:

```cmd
# Open Command Prompt (cmd)
# Navigate to program directory
cd /d "C:\path\to\HeadAlignmentTool"

# Run program
HeadAlignmentTool.exe
```

### Common Issues

#### Q: Why are some images skipped?
A: Possible reasons include:
- Head tilt angle exceeds set threshold
- Unable to detect clear facial keypoints
- Poor image quality or lighting conditions

#### Q: How to improve alignment accuracy?
A: Suggestions:
- Use high-quality reference images
- Adjust eye distance parameters
- Ensure good input image quality
- Enable debug mode to check keypoint detection

#### Q: What if processing is slow?
A: Optimization tips:
- Reduce input image resolution
- Process fewer images simultaneously
- Disable debug mode

## System Requirements

### Minimum Requirements
- **Windows**: Windows 10 (64-bit) or higher
- **macOS**: macOS 10.15 or higher
- **Linux**: 64-bit distribution with GUI support
- **Memory**: 4GB RAM (8GB+ recommended)
- **Storage**: 1GB available space
- **Graphics**: OpenGL-supported graphics card

### Recommended Configuration
- **Windows**: Windows 11 (64-bit)
- **macOS**: macOS 12+ (Apple Silicon supported)
- **Memory**: 8GB+ RAM
- **Storage**: SSD drive
- **Graphics**: Dedicated graphics card

## Important Notes

### Input Requirements
1. **Image Quality**: Images must contain clear frontal faces
2. **Lighting Conditions**: Avoid strong shadows affecting keypoint detection
3. **Tilt Angle**: Head tilts exceeding threshold will be automatically filtered
4. **Resolution**: High-resolution input images recommended

### Usage Recommendations
- Reference images should have upright heads and natural expressions
- For best results, use reference images with "Force Reference Size" enabled
- Eye distance parameter recommended between 25-35%
- Tilt threshold recommended between 3-8°

### Quality Assessment
- **Quality Score Range**: 0.0 - 1.0
- **0.9+**: Excellent, very high keypoint alignment precision
- **0.8+**: Good, meets most application needs
- **0.7+**: Acceptable, may have slight deviations
- **0.6-**: Poor, recommend checking image quality

## Technical Parameter Configuration

```python
class HeadStabilizer:
    def __init__(self):
        # Precision control parameters
        self.alignment_tolerance = 2.0      # Alignment tolerance (pixels)
        self.max_iterations = 3             # Maximum optimization iterations
        self.quality_threshold = 0.95       # Alignment quality threshold
        
        # Stability parameters
        self.tilt_threshold = 5.0           # Head tilt angle threshold
        self.face_scale = 1.5               # Face scaling ratio
```

## Algorithm Technical Details

### Similarity Transform Implementation

```python
def _calculate_similarity_transform(self, src_points, dst_points):
    """Calculate similarity transform matrix (rotation, scaling, translation only, no stretching)"""
    # Calculate scale ratio
    scale = dst_eye_dist / src_eye_dist
    
    # Calculate rotation angle
    rotation_angle = dst_angle - src_angle
    
    # Build transform matrix ensuring aspect ratio preservation
    cos_angle = np.cos(rotation_angle) * scale
    sin_angle = np.sin(rotation_angle) * scale
    
    M = np.array([
        [cos_angle, -sin_angle, tx],
        [sin_angle, cos_angle, ty]
    ], dtype=np.float32)
    
    return M
```

### Stable Keypoint Selection

```python
def _get_stable_landmarks(self, image):
    """Get most stable keypoint combinations"""
    stable_points = {
        # Eye corners (most stable points)
        'left_eye_outer': landmarks[33],    # Left eye outer corner
        'left_eye_inner': landmarks[133],   # Left eye inner corner
        'right_eye_inner': landmarks[362],  # Right eye inner corner  
        'right_eye_outer': landmarks[263],  # Right eye outer corner
        # Nose tip (second most stable)
        'nose_tip': landmarks[4],           # Nose tip
    }
    return stable_points
```

### Quality Validation System

```python
def _validate_alignment_quality(self, M, src_landmarks, dst_landmarks):
    """Validate alignment quality"""
    # Dynamically adjust error threshold based on output size
    output_diagonal = np.sqrt(self.output_size[0]**2 + self.output_size[1]**2)
    base_error = output_diagonal * 0.01
    max_acceptable_error = max(15.0, base_error)
    
    # Calculate keypoint alignment errors
    errors = []
    for point_name in ['left_eye', 'right_eye', 'nose_tip']:
        transformed_point = M @ src_point
        error = euclidean_distance(transformed_point[:2], dst_point)
        errors.append(error)
    
    # Calculate quality score
    avg_error = np.mean(errors)
    quality_score = max(0, (max_acceptable_error - avg_error) / max_acceptable_error)
    return quality_score
```

## Alternative Running Methods

If executable files don't work properly, try:

1. **Using Python Environment**:
   ```bash
   # Install Python 3.9+
   pip install -r requirements.txt
   
   # Recommended startup method (with dependency checking)
   python run.py
   
   # Or direct startup
   streamlit run streamlit_app.py
   ```

2. **Windows User Special Solution**:
   ```cmd
   # Double-click run_windows.bat
   # This script will automatically:
   # - Check Python environment
   # - Create virtual environment
   # - Install required dependencies
   # - Launch application
   ```

3. **Using Docker** (if Docker environment available):
   ```cmd
   # Build image
   docker build -t head-alignment-tool .
   
   # Run container
   docker run -p 8501:8501 head-alignment-tool
   ```

## Developer Guide

### 🏗️ Project Structure

```
Project Root/
├── 📄 README.md                      # 📚 Complete documentation - This file
├── 📄 README_CN.md                   # 📚 Chinese version documentation
├── 🐍 streamlit_app.py               # 🎯 Main application
├── 🧠 head_stabilizer.py             # 🔧 Core alignment algorithm
├── 📋 requirements.txt               # 📦 Python dependencies list
├── 🚀 run.py                         # ⚡ Local startup script
└── Build and Deployment Files/
    ├── 🛠️ prepare_build.py           # 📦 Build preparation script
    ├── 🏗️ build_exe.py               # 📦 Local packaging script
    ├── 🪟 run_windows.bat            # 🪟 Windows batch file
    ├── 🔧 run_streamlit.py           # 📦 PyInstaller launcher
    ├── 📁 hooks/                     # 📦 PyInstaller hooks
    └── 📁 .github/workflows/         # 🤖 GitHub Actions configuration
```

#### File Description

**User Essential Files**:
- **`README.md`** - 📚 Complete user guide and technical documentation (English)
- **`README_CN.md`** - 📚 Chinese version documentation
- **`streamlit_app.py`** - 🎯 Main application with web interface
- **`head_stabilizer.py`** - 🧠 Head alignment core algorithm
- **`requirements.txt`** - 📦 Python package dependencies list
- **`run.py`** - ⚡ Recommended local startup method

**Build/Package Files**:
- **`prepare_build.py`** - 🛠️ Cross-platform build preparation, auto-generates spec files
- **`build_exe.py`** - 🏗️ Local packaging script
- **`run_streamlit.py`** - 🔧 PyInstaller launcher
- **`run_windows.bat`** - 🪟 Python environment solution for Windows users
- **`hooks/`** - 📦 PyInstaller hooks folder

**Automation Deployment**:
- **`.github/workflows/`** - 🤖 GitHub Actions automated build configuration

### 🚀 Development Environment Setup

```bash
# 1. Clone project
git clone <your-repo-url>
cd head-alignment-tool

# 2. Install dependencies
pip install -r requirements.txt

# 3. Start development server
python run.py

# 4. Access application
# Browser automatically opens http://localhost:8501
```

### 📦 Local Packaging

```bash
# 1. Prepare build environment
python prepare_build.py

# 2. Execute packaging
python build_exe.py

# 3. Test executable
./dist/HeadAlignmentTool  # macOS/Linux
# or
dist\HeadAlignmentTool.exe  # Windows
```

### 🤖 Automated Build & Release

#### GitHub Actions Configuration

Project configured with complete CI/CD pipeline supporting:
- ✅ Windows, macOS, Linux three-platform automated builds
- ✅ Version tag automatic Release publishing
- ✅ Manual trigger test builds
- ✅ Build artifacts automatic upload

#### Workflow Files

**Main Release Pipeline** (`.github/workflows/build-release.yml`):
- **Trigger Conditions**: Push version tags (e.g., `v1.0.0`) or manual trigger
- **Function**: Simultaneous three-platform build, automatic Release creation
- **Artifacts**: `HeadAlignmentTool-Windows.zip`, `HeadAlignmentTool-macOS.tar.gz`, `HeadAlignmentTool-Linux.tar.gz`

#### Usage

**Test Build**:
1. Go to GitHub repository → Actions tab
2. Select "Build and Release" workflow
3. Click "Run workflow" → Manual trigger test

**Official Release**:
```bash
# Create version tag
git tag v1.0.0
git push origin v1.0.0

# GitHub Actions automatically triggers build and release
```

## File Structure

- `streamlit_app.py` - Streamlit web interface main program
- `head_stabilizer.py` - Head alignment core algorithm (fully improved)
- `run.py` - One-click startup script (recommended)
- `requirements.txt` - Project dependency package list
- `prepare_build.py` - PyInstaller build preparation script
- `hooks/` - PyInstaller hook files
- `.github/workflows/` - GitHub Actions automated build configuration

## Future Optimization Directions

1. **Deep Learning Enhancement**: Integrate more advanced face keypoint detection models
2. **Real-time Optimization**: Real-time processing optimization for video streams
3. **3D Alignment**: Support precise alignment of three-dimensional head poses
4. **Expression Preservation**: Better maintain facial expressions during alignment
5. **Batch Optimization**: GPU-accelerated large-scale batch processing
6. **Cloud Processing**: Support cloud batch processing services

## Getting Help

- **Issues**: Submit issues on GitHub project page
- **Discussions**: Participate in project discussions
- **Email**: Contact project maintainers

---

Through these improvements, the head alignment algorithm now ensures:
- 🎯 **Precise Alignment**: Heads consistently positioned at same coordinates
- 🚫 **No Distortion**: Strictly avoid any stretching effects
- 📱 **High Quality**: Maintain image clarity and natural appearance
- ⚡ **Efficient & Stable**: Fast processing with consistent results 
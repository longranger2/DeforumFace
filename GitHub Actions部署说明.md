# GitHub Actions 自动化部署说明

## 概述

本项目配置了GitHub Actions自动化工作流，可以自动构建Windows、macOS和Linux三个平台的可执行文件，并在创建版本标签时自动发布Release。

## 工作流文件

### 1. 主要发布工作流 (`.github/workflows/build-release.yml`)

**触发条件：**
- 推送版本标签（如 `v1.0.0`）
- 手动触发

**功能：**
- 同时构建Windows、macOS、Linux三个平台
- 自动创建GitHub Release
- 上传可执行文件到Release

### 2. 测试构建工作流 (`.github/workflows/test-build.yml`)

**触发条件：**
- 仅手动触发

**功能：**
- 选择单个平台进行测试构建
- 验证构建过程是否正常
- 上传构建产物作为临时文件

## 使用方法

### 测试构建

1. 进入GitHub仓库页面
2. 点击 "Actions" 标签
3. 选择 "Test Build" 工作流
4. 点击 "Run workflow"
5. 选择要测试的平台（ubuntu-latest/windows-latest/macos-latest）
6. 点击 "Run workflow" 确认

### 正式发布

#### 方法1：创建版本标签（推荐）

```bash
# 本地创建并推送标签
git tag v1.0.0
git push origin v1.0.0
```

#### 方法2：手动触发

1. 进入GitHub仓库页面
2. 点击 "Actions" 标签
3. 选择 "Build and Release" 工作流
4. 点击 "Run workflow"
5. 点击 "Run workflow" 确认

## 构建产物

### 文件格式

- **Windows**: `HeadAlignmentTool-Windows.zip`
  - 包含 `HeadAlignmentTool.exe` 和使用说明
  
- **macOS**: `HeadAlignmentTool-macOS.tar.gz`
  - 包含 `HeadAlignmentTool` 可执行文件和使用说明
  
- **Linux**: `HeadAlignmentTool-Linux.tar.gz`
  - 包含 `HeadAlignmentTool` 可执行文件和使用说明

### 下载方式

1. **从Release页面下载**（推荐）
   - 进入仓库的 "Releases" 页面
   - 选择最新版本
   - 下载对应平台的文件

2. **从Actions页面下载**
   - 进入 "Actions" 页面
   - 选择对应的工作流运行
   - 在 "Artifacts" 部分下载

## 构建过程详解

### 环境准备

1. **Python环境**: Python 3.9
2. **系统依赖**:
   - Ubuntu: OpenGL、GUI相关库
   - Windows: 无额外依赖
   - macOS: 无额外依赖

### 构建步骤

1. **安装依赖**
   ```bash
   pip install -r requirements.txt
   pip install pyinstaller
   ```

2. **创建Hook文件**
   - 自动生成 `hooks/hook-streamlit.py`
   - 处理Streamlit的动态导入

3. **生成Spec文件**
   - 动态获取site-packages路径
   - 配置所有必要的数据文件和隐藏导入

4. **执行打包**
   ```bash
   pyinstaller HeadAlignmentTool.spec --clean --noconfirm
   ```

5. **创建分发包**
   - 复制可执行文件
   - 添加使用说明
   - 创建压缩包

## 故障排除

### 常见问题

1. **构建失败**
   - 检查 `requirements.txt` 是否包含所有依赖
   - 查看Actions日志中的错误信息

2. **可执行文件无法运行**
   - 确保目标系统满足最低要求
   - 检查是否缺少系统依赖

3. **文件过大**
   - 当前配置已优化，单个文件约150-200MB
   - 可以通过排除不必要的模块进一步优化

### 调试方法

1. **使用测试工作流**
   - 先用测试工作流验证单个平台
   - 确认无误后再进行正式发布

2. **查看构建日志**
   - Actions页面提供详细的构建日志
   - 可以定位具体的错误位置

3. **本地测试**
   - 在本地环境复现构建过程
   - 使用相同的Python版本和依赖

## 自定义配置

### 修改构建参数

编辑 `.github/workflows/build-release.yml` 文件：

1. **Python版本**
   ```yaml
   python-version: '3.9'  # 修改为需要的版本
   ```

2. **PyInstaller选项**
   ```yaml
   # 在spec文件生成部分修改
   upx=True,  # 是否使用UPX压缩
   console=True,  # 是否显示控制台
   ```

3. **包含的文件**
   ```yaml
   # 在datas部分添加额外文件
   ('config.json', '.'),
   ```

### 添加新平台

在matrix部分添加新的操作系统：

```yaml
matrix:
  os: [windows-latest, macos-latest, ubuntu-latest, macos-13]
  include:
    - os: macos-13
      executable_name: HeadAlignmentTool
      artifact_name: HeadAlignmentTool-macOS-Intel
```

## 版本管理

### 标签命名规范

- 使用语义化版本：`v主版本.次版本.修订版本`
- 例如：`v1.0.0`, `v1.1.0`, `v1.1.1`

### Release说明

每次发布时，GitHub Actions会自动生成包含以下内容的Release说明：
- 版本信息
- 下载说明
- 使用方法
- 系统要求
- 注意事项

## 安全注意事项

1. **GITHUB_TOKEN**: 自动提供，无需手动配置
2. **私有仓库**: 确保Actions有足够的权限
3. **依赖安全**: 定期更新依赖版本，避免安全漏洞

## 性能优化

1. **缓存依赖**: 可以添加pip缓存以加速构建
2. **并行构建**: 当前已配置矩阵并行构建
3. **构建时间**: 单个平台约10-15分钟

## 维护建议

1. **定期测试**: 每月至少运行一次测试构建
2. **依赖更新**: 定期更新Python依赖版本
3. **文档更新**: 保持使用说明与实际功能同步 
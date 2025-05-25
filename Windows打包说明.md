# Windows平台打包说明

## 🪟 为Windows用户打包

### 准备工作
1. **Windows系统要求**：
   - Windows 10/11 (64位)
   - Python 3.9+ 
   - 至少4GB内存

### 打包步骤

#### 1. 安装Python环境
```cmd
# 下载并安装Python 3.9+
# 确保勾选"Add Python to PATH"
```

#### 2. 创建虚拟环境
```cmd
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
venv\Scripts\activate
```

#### 3. 安装依赖
```cmd
# 安装项目依赖
pip install -r requirements.txt

# 安装PyInstaller
pip install pyinstaller
```

#### 4. 修改spec文件
创建Windows版本的spec文件 `HeadAlignmentTool_Windows.spec`：

```python
# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_data_files, copy_metadata
import platform

block_cipher = None

# 收集Streamlit数据文件和元数据
datas = copy_metadata("streamlit")

# Windows路径 - 需要根据实际Python安装路径修改
python_path = "C:\\Users\\YourUsername\\AppData\\Local\\Programs\\Python\\Python39"
site_packages = f"{python_path}\\Lib\\site-packages"

# 添加应用文件和streamlit必要文件
datas += [
    ('streamlit_app.py', '.'),
    ('head_stabilizer.py', '.'),
    ('requirements.txt', '.'),
    # Windows路径格式
    (f'{site_packages}\\streamlit\\static', '.\\streamlit\\static'),
    (f'{site_packages}\\streamlit\\runtime', '.\\streamlit\\runtime'),
    (f'{site_packages}\\mediapipe\\modules', '.\\mediapipe\\modules'),
]

# 收集MediaPipe的数据文件
datas += collect_data_files("mediapipe")

a = Analysis(
    ['run_streamlit.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=[
        'streamlit',
        'streamlit.web.cli',
        'streamlit.web.server',
        'streamlit.runtime.scriptrunner.script_runner',
        'streamlit.runtime.scriptrunner.magic_funcs',
        'streamlit.runtime.state',
        'streamlit.runtime.caching',
        'streamlit.runtime.uploaded_file_manager',
        'streamlit.components.v1',
        'streamlit.delta_generator',
        'tornado',
        'tornado.web',
        'tornado.websocket',
        'tornado.ioloop',
        'cv2',
        'mediapipe',
        'mediapipe.python',
        'mediapipe.python.solutions',
        'mediapipe.python.solutions.face_mesh',
        'mediapipe.python.solution_base',
        'numpy',
        'PIL',
        'PIL.Image',
        'PIL.ImageOps',
        'PIL.ImageEnhance',
        'PIL.ImageFilter',
    ],
    hookspath=['./hooks'],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'tkinter',
        'PyQt5',
        'PyQt6',
        'PySide2',
        'PySide6',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='HeadAlignmentTool',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Windows下设为False隐藏控制台
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)
```

#### 5. 执行打包
```cmd
# 激活虚拟环境
venv\Scripts\activate

# 打包
pyinstaller HeadAlignmentTool_Windows.spec --clean
```

#### 6. 测试
```cmd
# 测试可执行文件
cd dist
HeadAlignmentTool.exe
```

### 预期结果
- 生成 `dist/HeadAlignmentTool.exe`
- 文件大小约200-300MB
- 双击即可运行，无需Python环境

## 🔧 Windows特殊注意事项

1. **路径分隔符**：Windows使用`\`而不是`/`
2. **控制台窗口**：可设置`console=False`隐藏黑色窗口
3. **防病毒软件**：可能需要添加到白名单
4. **权限问题**：可能需要管理员权限运行

## 📦 分发建议

### 创建安装包
可以使用NSIS或Inno Setup创建Windows安装程序：

```nsis
; 示例NSIS脚本
!define APP_NAME "头部对齐工具"
!define APP_VERSION "1.0"

Name "${APP_NAME}"
OutFile "HeadAlignmentTool_Setup.exe"
InstallDir "$PROGRAMFILES\${APP_NAME}"

Section "MainSection" SEC01
    SetOutPath "$INSTDIR"
    File "dist\HeadAlignmentTool.exe"
    CreateShortCut "$DESKTOP\${APP_NAME}.lnk" "$INSTDIR\HeadAlignmentTool.exe"
SectionEnd
``` 
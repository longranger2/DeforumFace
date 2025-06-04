#!/usr/bin/env python3
"""
Build environment preparation script
Creates PyInstaller spec file and hook configuration for GitHub Actions
"""

import os
import site
import platform
import sys

def find_site_packages():
    """Find the correct site-packages directory across platforms"""
    # Try multiple methods to find site-packages
    candidates = []
    
    # Method 1: site.getsitepackages()
    try:
        candidates.extend(site.getsitepackages())
    except:
        pass
    
    # Method 2: site.getusersitepackages()
    try:
        candidates.append(site.getusersitepackages())
    except:
        pass
    
    # Method 3: Check common locations
    python_root = sys.prefix
    candidates.extend([
        os.path.join(python_root, 'lib', 'site-packages'),
        os.path.join(python_root, 'Lib', 'site-packages'),
        os.path.join(python_root, 'site-packages'),
    ])
    
    # Find the first candidate that actually contains streamlit
    for candidate in candidates:
        if os.path.exists(candidate):
            streamlit_path = os.path.join(candidate, 'streamlit')
            if os.path.exists(streamlit_path):
                print(f"Found site-packages with streamlit: {candidate}")
                return candidate
    
    # If none found, return the first existing path
    for candidate in candidates:
        if os.path.exists(candidate):
            print(f"Using site-packages (no streamlit found): {candidate}")
            return candidate
    
    # Fallback
    print("Warning: Could not find site-packages, using sys.prefix")
    return sys.prefix

def get_windows_mediapipe_binaries():
    """Get Windows-specific MediaPipe binary files"""
    binaries = []
    site_packages = find_site_packages()
    
    # MediaPipe binary files for Windows
    mediapipe_path = os.path.join(site_packages, 'mediapipe')
    if os.path.exists(mediapipe_path):
        # Look for DLL files
        for root, dirs, files in os.walk(mediapipe_path):
            for file in files:
                if file.endswith(('.dll', '.pyd')):
                    full_path = os.path.join(root, file)
                    rel_path = os.path.relpath(full_path, site_packages)
                    binaries.append((full_path, os.path.dirname(rel_path)))
                    print(f"[BINARY] Found: {rel_path}")
    
    return binaries

def main():
    # Ensure hooks directory exists
    if not os.path.exists('hooks'):
        print("Creating hooks directory...")
        os.makedirs('hooks')
    
    # Create simple, effective hooks
    print("Creating hook files...")
    
    # Streamlit hook - keep it simple
    streamlit_hook_content = """from PyInstaller.utils.hooks import collect_data_files, collect_submodules

datas = collect_data_files('streamlit')
hiddenimports = collect_submodules('streamlit')
"""
    with open('hooks/hook-streamlit.py', 'w', encoding='utf-8') as f:
        f.write(streamlit_hook_content)
    
    # MediaPipe hook - 让PyInstaller自动处理，避免手动路径操作
    mediapipe_hook_content = """from PyInstaller.utils.hooks import collect_data_files, collect_submodules

# 收集MediaPipe子模块
hiddenimports = collect_submodules('mediapipe')

# 只使用自动收集，避免重复
# 这是推荐的方法，PyInstaller会自动处理路径
datas = collect_data_files('mediapipe')

# 添加必要的隐藏导入
additional_hiddenimports = [
    'mediapipe.python._framework_bindings',
    'mediapipe.python.solutions.face_mesh',
    'mediapipe.python.solutions.drawing_utils',
    'mediapipe.python.solutions.drawing_styles',
    'google.protobuf.pyext._message',
]

hiddenimports.extend(additional_hiddenimports)

print(f"[MEDIAPIPE HOOK] 收集到 {len(datas)} 个数据文件")
print(f"[MEDIAPIPE HOOK] 包含 {len(hiddenimports)} 个隐藏导入")
"""
    with open('hooks/hook-mediapipe.py', 'w', encoding='utf-8') as f:
        f.write(mediapipe_hook_content)
    
    # Get site-packages path
    site_packages = find_site_packages()
    print(f'Site packages: {site_packages}')
    print(f'Platform: {platform.system()}')
    
    # 最小化数据文件列表，只包含核心应用文件
    critical_paths = [
        ('streamlit_app.py', '.'),
        ('head_stabilizer.py', '.'),
    ]
    
    # 只添加确实需要的Streamlit文件
    streamlit_static = os.path.join(site_packages, 'streamlit', 'static')
    if os.path.exists(streamlit_static):
        critical_paths.append((streamlit_static, 'streamlit/static'))
        print(f"[EXISTS] streamlit/static")
    
    streamlit_runtime = os.path.join(site_packages, 'streamlit', 'runtime')
    if os.path.exists(streamlit_runtime):
        critical_paths.append((streamlit_runtime, 'streamlit/runtime'))
        print(f"[EXISTS] streamlit/runtime")
    
    # MediaPipe完全由hook处理，不在这里手动添加
    print("[INFO] MediaPipe files will be handled automatically by hook")
    
    # Convert datas to spec format
    datas_str = ",\n        ".join([f"(r'{src}', r'{dst}')" for src, dst in critical_paths])
    
    # Get Windows-specific binaries
    binaries_list = []
    if platform.system() == 'Windows':
        binaries_list = get_windows_mediapipe_binaries()
    
    binaries_str = ""
    if binaries_list:
        binaries_str = ",\n        ".join([f"(r'{src}', r'{dst}')" for src, dst in binaries_list])
        binaries_str = f"[\n        {binaries_str}\n    ]"
    else:
        binaries_str = "[]"
    
    # 简化隐藏导入列表
    hidden_imports = [
        'streamlit',
        'streamlit.web.cli',
        'mediapipe',
        'cv2',
        'numpy',
        'PIL',
        'PIL.Image',
        'PIL.ImageDraw',
        'PIL.ImageFont',
    ]
    
    # Windows特定导入
    if platform.system() == 'Windows':
        hidden_imports.extend([
            'mediapipe.python._framework_bindings',
            'google.protobuf.pyext._message',
        ])
    
    hidden_imports_str = ",\n        ".join([f"'{imp}'" for imp in hidden_imports])
    
    # Create simplified PyInstaller spec file
    spec_content = f"""# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['run_streamlit.py'],
    pathex=[],
    binaries={binaries_str},
    datas=[
        {datas_str},
    ],
    hiddenimports=[
        {hidden_imports_str},
    ],
    hookspath=['hooks'],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='HeadAlignmentTool',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
"""
    
    # Write spec file
    with open('HeadAlignmentTool.spec', 'w', encoding='utf-8') as f:
        f.write(spec_content)
    print('[SUCCESS] Build environment prepared successfully')
    
    # Verify spec file was created
    if os.path.exists('HeadAlignmentTool.spec'):
        spec_size = os.path.getsize('HeadAlignmentTool.spec')
        print(f'[SUCCESS] Spec file created ({spec_size} bytes)')

if __name__ == '__main__':
    main() 
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
    # Ensure hooks directory exists (usually already exists)
    if not os.path.exists('hooks'):
        print("Creating hooks directory...")
        os.makedirs('hooks')
        
        # Only create basic hook file if hooks directory doesn't exist
        print("Creating basic hook file...")
        hook_content = """from PyInstaller.utils.hooks import collect_data_files, collect_submodules

datas = collect_data_files('streamlit')
hiddenimports = collect_submodules('streamlit')
"""
        with open('hooks/hook-streamlit.py', 'w', encoding='utf-8') as f:
            f.write(hook_content)
    else:
        print("Using existing hooks directory and files")
    
    # Get site-packages path with better detection
    site_packages = find_site_packages()
    print(f'Site packages: {site_packages}')
    print(f'Platform: {platform.system()}')
    
    # Check critical paths and build datas list dynamically
    critical_paths = [
        ('streamlit_app.py', '.'),
        ('head_stabilizer.py', '.'),
    ]
    
    # Check for streamlit static files
    streamlit_static = os.path.join(site_packages, 'streamlit', 'static')
    if os.path.exists(streamlit_static):
        critical_paths.append((streamlit_static, 'streamlit/static'))
        print(f"[EXISTS] streamlit/static: {streamlit_static}")
    else:
        print(f"[MISSING] streamlit/static: {streamlit_static}")
    
    # Check for streamlit runtime files
    streamlit_runtime = os.path.join(site_packages, 'streamlit', 'runtime')
    if os.path.exists(streamlit_runtime):
        critical_paths.append((streamlit_runtime, 'streamlit/runtime'))
        print(f"[EXISTS] streamlit/runtime: {streamlit_runtime}")
    else:
        print(f"[MISSING] streamlit/runtime: {streamlit_runtime}")
    
    # Check for mediapipe modules
    mediapipe_modules = os.path.join(site_packages, 'mediapipe', 'modules')
    if os.path.exists(mediapipe_modules):
        critical_paths.append((mediapipe_modules, 'mediapipe/modules'))
        print(f"[EXISTS] mediapipe/modules: {mediapipe_modules}")
    else:
        print(f"[MISSING] mediapipe/modules: {mediapipe_modules}")
    
    # Windows-specific MediaPipe data files
    if platform.system() == 'Windows':
        mediapipe_data = os.path.join(site_packages, 'mediapipe', 'python', 'solutions')
        if os.path.exists(mediapipe_data):
            critical_paths.append((mediapipe_data, 'mediapipe/python/solutions'))
            print(f"[EXISTS] mediapipe/python/solutions: {mediapipe_data}")
    
    # Convert datas to spec format with proper path escaping
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
    
    # Enhanced hidden imports for Windows
    hidden_imports = [
        'streamlit',
        'streamlit.web.cli',
        'streamlit.runtime.scriptrunner.magic_funcs',
        'streamlit.runtime.caching.cache_data_api',
        'streamlit.runtime.metrics_util',
        'streamlit.components.v1.components',
        'streamlit.external.langchain',
        'mediapipe',
        'mediapipe.python',
        'mediapipe.python.solutions',
        'mediapipe.python.solutions.face_mesh',
        'mediapipe.python.solutions.drawing_utils',
        'mediapipe.python.solutions.drawing_styles',
        'cv2',
        'numpy',
        'PIL',
        'PIL.Image',
        'PIL.ImageDraw',
        'PIL.ImageFont',
    ]
    
    # Windows-specific imports
    if platform.system() == 'Windows':
        hidden_imports.extend([
            'mediapipe.python._framework_bindings',
            'google.protobuf',
            'google.protobuf.internal',
            'google.protobuf.pyext',
            'google.protobuf.pyext._message',
        ])
    
    hidden_imports_str = ",\n        ".join([f"'{imp}'" for imp in hidden_imports])
    
    # Create PyInstaller spec file with proper cross-platform path handling
    spec_content = f"""# -*- mode: python ; coding: utf-8 -*-
import os
import site
import platform

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
    
    # Write spec file with UTF-8 encoding
    try:
        with open('HeadAlignmentTool.spec', 'w', encoding='utf-8') as f:
            f.write(spec_content)
        print('[SUCCESS] Build environment prepared successfully')
    except UnicodeEncodeError as e:
        print(f'[ERROR] Encoding error: {e}')
        # Fallback: write with platform default encoding
        with open('HeadAlignmentTool.spec', 'w') as f:
            f.write(spec_content)
        print('[SUCCESS] Build environment prepared with fallback encoding')
    
    if os.path.exists('hooks/hook-streamlit.py'):
        print('[SUCCESS] Using existing hooks/hook-streamlit.py file')
    
    # Verify spec file was created
    if os.path.exists('HeadAlignmentTool.spec'):
        spec_size = os.path.getsize('HeadAlignmentTool.spec')
        print(f'[SUCCESS] Spec file created ({spec_size} bytes)')
    
    # Check if dist directory exists and show contents
    if os.path.exists('dist'):
        print('[INFO] Contents of dist directory:')
        for item in os.listdir('dist'):
            print(f'  - {item}')

if __name__ == '__main__':
    main() 
#!/usr/bin/env python3
"""
Build environment preparation script
Creates PyInstaller spec file and hook configuration for GitHub Actions
"""

import os
import site
import platform

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
    
    # Get site-packages path
    site_packages = site.getsitepackages()[0]
    print(f'Site packages: {site_packages}')
    print(f'Platform: {platform.system()}')
    
    # Normalize path separators for cross-platform compatibility
    # Convert to forward slashes and escape properly for Python strings
    site_packages_escaped = site_packages.replace('\\', '\\\\')
    
    # Create PyInstaller spec file with proper cross-platform path handling
    spec_content = f"""# -*- mode: python ; coding: utf-8 -*-
import os
import site

# Cross-platform site-packages path
site_packages = r"{site_packages}"

block_cipher = None

a = Analysis(
    ['run_streamlit.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('streamlit_app.py', '.'),
        ('head_stabilizer.py', '.'),
        (os.path.join(site_packages, 'streamlit', 'static'), 'streamlit/static'),
        (os.path.join(site_packages, 'streamlit', 'runtime'), 'streamlit/runtime'),
        (os.path.join(site_packages, 'mediapipe', 'modules'), 'mediapipe/modules'),
    ],
    hiddenimports=[
        'streamlit',
        'streamlit.web.cli',
        'streamlit.runtime.scriptrunner.magic_funcs',
        'streamlit.runtime.caching.cache_data_api',
        'streamlit.runtime.metrics_util',
        'streamlit.components.v1.components',
        'streamlit.external.langchain',
        'mediapipe',
        'cv2',
        'numpy',
        'PIL',
        'PIL.Image',
        'PIL.ImageDraw',
        'PIL.ImageFont',
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
        print('✅ Build environment prepared successfully')
    except UnicodeEncodeError as e:
        print(f'❌ Encoding error: {e}')
        # Fallback: write with platform default encoding
        with open('HeadAlignmentTool.spec', 'w') as f:
            f.write(spec_content)
        print('✅ Build environment prepared with fallback encoding')
    
    if os.path.exists('hooks/hook-streamlit.py'):
        print('✅ Using existing hooks/hook-streamlit.py file')
    
    # Verify spec file was created
    if os.path.exists('HeadAlignmentTool.spec'):
        spec_size = os.path.getsize('HeadAlignmentTool.spec')
        print(f'✅ Spec file created ({spec_size} bytes)')
    
    # Check if dist directory exists and show contents
    if os.path.exists('dist'):
        print('📁 Contents of dist directory:')
        for item in os.listdir('dist'):
            print(f'  - {item}')

if __name__ == '__main__':
    main() 
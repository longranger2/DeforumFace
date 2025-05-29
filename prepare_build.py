#!/usr/bin/env python3
"""
构建环境准备脚本
为GitHub Actions创建PyInstaller spec文件和hook配置
"""

import os
import site

def main():
    # 确保hooks目录存在（通常已经存在）
    if not os.path.exists('hooks'):
        print("Creating hooks directory...")
        os.makedirs('hooks')
        
        # 只有在hooks目录不存在时才创建基本的hook文件
        print("Creating basic hook file...")
        hook_content = """from PyInstaller.utils.hooks import collect_data_files, collect_submodules

datas = collect_data_files('streamlit')
hiddenimports = collect_submodules('streamlit')
"""
        with open('hooks/hook-streamlit.py', 'w') as f:
            f.write(hook_content)
    else:
        print("Using existing hooks directory and files")
    
    # 获取site-packages路径
    site_packages = site.getsitepackages()[0]
    print(f'Site packages: {site_packages}')
    
    # 创建PyInstaller spec文件
    spec_content = f"""# -*- mode: python ; coding: utf-8 -*-
import os
import site

# 获取site-packages路径
site_packages = r'{site_packages}'

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
    
    with open('HeadAlignmentTool.spec', 'w') as f:
        f.write(spec_content)
    
    print('✅ Build environment prepared successfully')
    if os.path.exists('hooks/hook-streamlit.py'):
        print('✅ Using existing hooks/hook-streamlit.py file')
    
    # 验证可执行文件是否存在的辅助函数
    if os.path.exists('dist'):
        print('📁 Contents of dist directory:')
        for item in os.listdir('dist'):
            print(f'  - {item}')

if __name__ == '__main__':
    main() 
# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_data_files, copy_metadata
import platform

block_cipher = None

# 收集Streamlit数据文件和元数据
datas = copy_metadata("streamlit")

# 添加应用文件和streamlit必要文件
datas += [
    ('streamlit_app.py', '.'),
    ('head_stabilizer.py', '.'),
    ('requirements.txt', '.'),
    # 添加streamlit的static和runtime文件
    ('/Users/loneranger/Project/DeforumAI/deforumai/lib/python3.9/site-packages/streamlit/static', './streamlit/static'),
    ('/Users/loneranger/Project/DeforumAI/deforumai/lib/python3.9/site-packages/streamlit/runtime', './streamlit/runtime'),
    # 添加MediaPipe的modules文件
    ('/Users/loneranger/Project/DeforumAI/deforumai/lib/python3.9/site-packages/mediapipe/modules', './mediapipe/modules'),
]

# 收集MediaPipe的数据文件
datas += collect_data_files("mediapipe")

# 系统特定设置
system = platform.system().lower()

a = Analysis(
    ['run_streamlit.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=[
        # Streamlit核心模块
        'streamlit',
        'streamlit.web.cli',
        'streamlit.web.server',
        'streamlit.web.server.server',
        'streamlit.runtime.scriptrunner.script_runner',
        'streamlit.runtime.scriptrunner.magic_funcs',  # 添加缺失的模块
        'streamlit.runtime.state',
        'streamlit.runtime.caching',
        'streamlit.runtime.uploaded_file_manager',
        'streamlit.components.v1',
        'streamlit.delta_generator',
        'streamlit.elements',
        'streamlit.elements.form',
        'streamlit.elements.button',
        'streamlit.elements.selectbox',
        'streamlit.elements.slider',
        'streamlit.elements.text_input',
        'streamlit.elements.file_uploader',
        'streamlit.elements.image',
        'streamlit.elements.markdown',
        'streamlit.elements.columns',
        'streamlit.elements.container',
        'streamlit.elements.empty',
        'streamlit.elements.progress',
        'streamlit.elements.spinner',
        'streamlit.elements.success',
        'streamlit.elements.error',
        'streamlit.elements.warning',
        'streamlit.elements.info',
        'streamlit.elements.exception',
        'streamlit.elements.json',
        'streamlit.elements.code',
        'streamlit.elements.text',
        'streamlit.elements.title',
        'streamlit.elements.header',
        'streamlit.elements.subheader',
        'streamlit.elements.caption',
        'streamlit.elements.metric',
        'streamlit.elements.balloons',
        'streamlit.elements.snow',
        
        # Web服务器相关
        'tornado',
        'tornado.web',
        'tornado.websocket',
        'tornado.ioloop',
        'tornado.httpserver',
        'tornado.netutil',
        'tornado.platform',
        'tornado.platform.asyncio',
        
        # 图像处理
        'cv2',
        'mediapipe',
        'mediapipe.python',
        'mediapipe.python.solutions',
        'mediapipe.python.solutions.face_mesh',
        'mediapipe.python.solutions.drawing_utils',
        'mediapipe.python.solutions.drawing_styles',
        'mediapipe.python.solution_base',
        'numpy',
        'PIL',
        'PIL.Image',
        'PIL.ImageOps',
        'PIL.ImageEnhance',
        'PIL.ImageFilter',
        
        # 数据处理
        'pandas',
        'pandas.core',
        'pandas.core.frame',
        'pandas.core.series',
        
        # 绘图
        'matplotlib',
        'matplotlib.pyplot',
        'plotly',
        'plotly.graph_objects',
        'plotly.express',
        'altair',
        
        # 系统和网络
        'psutil',
        'socket',
        'webbrowser',
        'subprocess',
        'pathlib',
        'time',
        'traceback',
        'threading',
        'queue',
        'json',
        'base64',
        'io',
        'tempfile',
        'glob',
        'math',
        'collections',
        'itertools',
        'functools',
        'typing',
        'dataclasses',
        'enum',
        'datetime',
        'uuid',
        'hashlib',
        'urllib',
        'urllib.parse',
        'urllib.request',
        'requests',
        'click',
        'toml',
        'watchdog',
        'watchdog.observers',
        'watchdog.events',
        'blinker',
        'cachetools',
        'packaging',
        'packaging.version',
        'packaging.requirements',
        'protobuf',
        'pyarrow',
        'tzlocal',
        'validators',
        'gitpython',
        'pydeck',
        'pympler',
        'rich',
        'semver',
        'tenacity',
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
        'IPython',
        'jupyter',
        'notebook',
        'sphinx',
        'pytest',
        'setuptools',
        'distutils',
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
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
) 
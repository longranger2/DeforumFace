#!/usr/bin/env python3
"""
PyInstaller hook for MediaPipe
Handles MediaPipe data files and dependencies properly
"""

from PyInstaller.utils.hooks import collect_data_files, collect_submodules

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
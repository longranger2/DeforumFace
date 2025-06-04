#!/usr/bin/env python3
"""
PyInstaller hook for MediaPipe
Handles MediaPipe data files and dependencies properly
"""

from PyInstaller.utils.hooks import collect_data_files, collect_submodules

# Collect MediaPipe submodules
hiddenimports = collect_submodules('mediapipe')

# Use automatic collection only to avoid duplicates
# This is the recommended approach, PyInstaller handles paths automatically
datas = collect_data_files('mediapipe')

# Add necessary hidden imports
additional_hiddenimports = [
    'mediapipe.python._framework_bindings',
    'mediapipe.python.solutions.face_mesh',
    'mediapipe.python.solutions.drawing_utils',
    'mediapipe.python.solutions.drawing_styles',
    'google.protobuf.pyext._message',
]

hiddenimports.extend(additional_hiddenimports)

print(f"[MEDIAPIPE HOOK] Collected {len(datas)} data files")
print(f"[MEDIAPIPE HOOK] Included {len(hiddenimports)} hidden imports") 
from PyInstaller.utils.hooks import collect_data_files, collect_submodules, collect_dynamic_libs
import os
import platform

# Collect all MediaPipe data files
datas = collect_data_files('mediapipe')

# Collect all MediaPipe submodules
hiddenimports = collect_submodules('mediapipe')

# Windows-specific handling
if platform.system() == 'Windows':
    # Add Windows-specific hidden imports
    hiddenimports.extend([
        'mediapipe.python._framework_bindings',
        'google.protobuf',
        'google.protobuf.internal',
        'google.protobuf.pyext',
        'google.protobuf.pyext._message',
        'mediapipe.calculators',
        'mediapipe.framework',
        'mediapipe.gpu',
    ])
    
    # Collect dynamic libraries (DLLs)
    binaries = collect_dynamic_libs('mediapipe')
    
    # Try to find specific MediaPipe model files
    try:
        import mediapipe as mp
        mp_path = os.path.dirname(mp.__file__)
        
        # Look for model files
        for root, dirs, files in os.walk(mp_path):
            for file in files:
                if file.endswith(('.binarypb', '.tflite', '.pb')):
                    full_path = os.path.join(root, file)
                    rel_path = os.path.relpath(full_path, mp_path)
                    datas.append((full_path, f'mediapipe/{rel_path}'))
    except ImportError:
        pass

# Add essential MediaPipe modules
hiddenimports.extend([
    'mediapipe.python.solutions.face_mesh',
    'mediapipe.python.solutions.drawing_utils',
    'mediapipe.python.solutions.drawing_styles',
    'mediapipe.python.solution_base',
]) 
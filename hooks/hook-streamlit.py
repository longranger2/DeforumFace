from PyInstaller.utils.hooks import collect_data_files, collect_submodules, copy_metadata

# Copy streamlit metadata - this is critical for runtime to find version info
datas = copy_metadata("streamlit")

# Collect streamlit data files
datas += collect_data_files("streamlit")

# Collect all streamlit submodules automatically
hiddenimports = collect_submodules("streamlit")

print(f"[STREAMLIT HOOK] Collected {len(datas)} data files")
print(f"[STREAMLIT HOOK] Included {len(hiddenimports)} hidden imports")

# Add essential streamlit modules
essential_imports = [
    'streamlit.web.cli',
    'streamlit.web.server',
    'streamlit.web.server.server',
    'streamlit.runtime.scriptrunner.script_runner',
    'streamlit.runtime.state',
    'streamlit.runtime.caching',
    'streamlit.runtime.uploaded_file_manager',
    'streamlit.components.v1',
    'streamlit.delta_generator',
]

hiddenimports.extend(essential_imports)

# 添加隐藏导入
hiddenimports += [
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
] 
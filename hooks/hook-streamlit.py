from PyInstaller.utils.hooks import copy_metadata, collect_data_files

# 复制Streamlit的元数据
datas = copy_metadata("streamlit")

# 收集Streamlit的数据文件
datas += collect_data_files("streamlit")

# 添加隐藏导入
hiddenimports = [
    'streamlit.web.cli',
    'streamlit.web.server',
    'streamlit.web.server.server',
    'streamlit.runtime.scriptrunner.script_runner',
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
] 
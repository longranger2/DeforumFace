#!/usr/bin/env python3
"""
Streamlit应用启动器 - 用于PyInstaller打包
参考: https://ploomber.io/blog/streamlit_exe/
"""

import streamlit.web.cli as stcli
import os
import sys


if __name__ == "__main__":
    # 判断当前路径是打包后启动的临时文件路径，还是平时直接运行脚本的路径
    if getattr(sys, 'frozen', False):
        current_dir = sys._MEIPASS
    else:
        current_dir = os.path.dirname(os.path.abspath(__file__))
    
    file_path = os.path.join(current_dir, "streamlit_app.py")
    
    # 设置Streamlit命令行参数
    sys.argv = [
        "streamlit", 
        "run", 
        file_path,
        "--server.enableCORS=true", 
        "--server.enableXsrfProtection=false", 
        "--global.developmentMode=false", 
        "--client.toolbarMode=minimal"
    ]
    
    # 启动Streamlit
    sys.exit(stcli.main()) 
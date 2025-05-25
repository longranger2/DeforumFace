#!/usr/bin/env python3
"""
头部对齐工具启动脚本
Head Alignment Tool Launcher
"""

import subprocess
import sys
import os

def check_dependencies():
    """检查必要的依赖是否已安装"""
    try:
        import streamlit
        import cv2
        import mediapipe
        import numpy
        from PIL import Image
        print("✅ 所有依赖已安装")
        return True
    except ImportError as e:
        print(f"❌ 缺少依赖: {e}")
        print("请运行: pip install -r requirements.txt")
        return False

def main():
    """主函数"""
    print("🚀 头部对齐工具启动器")
    print("=" * 40)
    
    # 检查依赖
    if not check_dependencies():
        sys.exit(1)
    
    # 检查streamlit_app.py是否存在
    if not os.path.exists("streamlit_app.py"):
        print("❌ 找不到 streamlit_app.py 文件")
        sys.exit(1)
    
    print("🌐 启动Streamlit应用...")
    print("📝 应用将在浏览器中自动打开")
    print("🔗 如果没有自动打开，请访问: http://localhost:8501")
    print("⏹️  按 Ctrl+C 停止应用")
    print("=" * 40)
    
    try:
        # 启动Streamlit应用
        subprocess.run([sys.executable, "-m", "streamlit", "run", "streamlit_app.py"], check=True)
    except KeyboardInterrupt:
        print("\n👋 应用已停止")
    except subprocess.CalledProcessError as e:
        print(f"❌ 启动失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 
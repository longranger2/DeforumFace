#!/usr/bin/env python3
"""
头部对齐工具打包脚本 - 简化版
参考: https://ploomber.io/blog/streamlit_exe/
"""

import os
import sys
import subprocess
import shutil
import platform

def check_pyinstaller():
    """检查PyInstaller是否已安装"""
    try:
        import PyInstaller
        print("✅ PyInstaller已安装")
        return True
    except ImportError:
        print("❌ PyInstaller未安装，正在安装...")
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"], check=True)
            print("✅ PyInstaller安装成功")
            return True
        except subprocess.CalledProcessError:
            print("❌ PyInstaller安装失败")
            return False

def check_dependencies():
    """检查项目依赖"""
    print("🔍 检查项目依赖...")
    required_files = ["streamlit_app.py", "head_stabilizer.py", "requirements.txt", "run_streamlit.py"]
    
    for file in required_files:
        if not os.path.exists(file):
            print(f"❌ 缺少文件: {file}")
            return False
        print(f"✅ 找到文件: {file}")
    
    return True

def build_with_pyinstaller():
    """使用PyInstaller构建应用"""
    print("🔨 开始使用PyInstaller构建应用...")
    
    try:
        # 第一步：生成初始spec文件
        print("📝 生成初始spec文件...")
        subprocess.run([
            sys.executable, "-m", "PyInstaller",
            "--onefile",
            "--additional-hooks-dir=./hooks",
            "run_streamlit.py",
            "--clean"
        ], check=True)
        
        print("✅ 初始构建完成")
        
        # 第二步：使用自定义spec文件重新构建
        if os.path.exists("HeadAlignmentTool.spec"):
            print("📝 使用自定义spec文件重新构建...")
            subprocess.run([
                sys.executable, "-m", "PyInstaller",
                "HeadAlignmentTool.spec",
                "--clean"
            ], check=True)
        
        print("✅ 应用构建成功！")
        
        # 检查输出文件
        system = platform.system().lower()
        if system == "windows":
            exe_path = "dist/HeadAlignmentTool.exe"
        else:
            exe_path = "dist/HeadAlignmentTool"
        
        if os.path.exists(exe_path):
            file_size = os.path.getsize(exe_path) / (1024 * 1024)  # MB
            print(f"📦 应用文件: {exe_path}")
            print(f"📏 文件大小: {file_size:.1f} MB")
            print(f"🎯 用户只需双击 {os.path.basename(exe_path)} 即可运行")
            return True
        else:
            print("❌ 未找到构建的应用文件")
            return False
            
    except subprocess.CalledProcessError as e:
        print(f"❌ 构建失败: {e}")
        return False

def cleanup():
    """清理临时文件"""
    print("🧹 清理临时文件...")
    temp_files = ["run_streamlit.spec"]
    temp_dirs = ["build", "__pycache__"]
    
    for file in temp_files:
        if os.path.exists(file):
            os.remove(file)
            print(f"🗑️  删除文件: {file}")
    
    for dir in temp_dirs:
        if os.path.exists(dir):
            shutil.rmtree(dir)
            print(f"🗑️  删除目录: {dir}")

def main():
    """主函数"""
    print("🚀 头部对齐工具打包器 (简化版)")
    print("参考: https://ploomber.io/blog/streamlit_exe/")
    print("=" * 50)
    
    # 检查依赖
    if not check_pyinstaller():
        return
    
    if not check_dependencies():
        return
    
    # 构建应用
    if build_with_pyinstaller():
        print("\n🎉 打包完成！")
        print("📦 在 dist/ 目录中找到可执行文件")
        print("💡 提示：首次运行可能需要几秒钟启动时间")
    else:
        print("\n❌ 打包失败")
    
    # 清理临时文件
    cleanup()

if __name__ == "__main__":
    main() 
@echo off
chcp 65001 >nul
echo.
echo ==========================================
echo    头部对齐工具 - Windows启动脚本
echo ==========================================
echo.

REM 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 错误：未找到Python
    echo.
    echo 请先安装Python 3.9或更高版本：
    echo 1. 访问 https://www.python.org/downloads/
    echo 2. 下载并安装Python
    echo 3. 安装时勾选 "Add Python to PATH"
    echo.
    pause
    exit /b 1
)

echo ✅ Python已安装
python --version

REM 检查虚拟环境
if not exist "venv" (
    echo.
    echo 📦 创建虚拟环境...
    python -m venv venv
    if errorlevel 1 (
        echo ❌ 创建虚拟环境失败
        pause
        exit /b 1
    )
)

REM 激活虚拟环境
echo.
echo 🔧 激活虚拟环境...
call venv\Scripts\activate.bat

REM 检查依赖是否安装
echo.
echo 📋 检查依赖...
pip show streamlit >nul 2>&1
if errorlevel 1 (
    echo 📥 安装依赖包...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo ❌ 依赖安装失败
        pause
        exit /b 1
    )
)

REM 检查主要文件
if not exist "streamlit_app.py" (
    echo ❌ 错误：找不到 streamlit_app.py 文件
    echo 请确保在正确的项目目录中运行此脚本
    pause
    exit /b 1
)

if not exist "head_stabilizer.py" (
    echo ❌ 错误：找不到 head_stabilizer.py 文件
    pause
    exit /b 1
)

echo.
echo 🚀 启动头部对齐工具...
echo.
echo 📝 应用将在浏览器中自动打开
echo 🔗 如果没有自动打开，请访问: http://localhost:8501
echo ⏹️  按 Ctrl+C 停止应用
echo.
echo ==========================================

REM 启动Streamlit应用
streamlit run streamlit_app.py

echo.
echo 👋 应用已停止
pause 
# Windows版本故障排除指南

## 常见问题及解决方案

### 1. 程序无法启动

**症状**: 双击 `HeadAlignmentTool.exe` 后没有反应或立即关闭

**可能原因及解决方案**:

#### A. Windows Defender 阻止
- **解决方案**: 
  1. 右键点击 `HeadAlignmentTool.exe`
  2. 选择"属性" → "常规"
  3. 勾选"解除阻止"
  4. 或者将文件夹添加到Windows Defender排除列表

#### B. 缺少Visual C++运行库
- **解决方案**: 下载安装 Microsoft Visual C++ Redistributable
  - [下载链接](https://docs.microsoft.com/en-us/cpp/windows/latest-supported-vc-redist)
  - 选择 x64 版本

#### C. 权限问题
- **解决方案**: 右键以管理员身份运行

### 2. MediaPipe相关错误

**症状**: 程序启动但出现MediaPipe模型文件错误

**解决方案**:
1. 确保完整解压了所有文件
2. 检查是否有杀毒软件删除了某些文件
3. 重新下载完整的压缩包

### 3. 浏览器无法打开

**症状**: 程序启动成功但浏览器没有自动打开

**解决方案**:
1. 手动打开浏览器
2. 访问 `http://localhost:8501`
3. 如果端口被占用，程序会自动选择其他端口，查看控制台输出

### 4. 性能问题

**症状**: 程序运行缓慢或卡顿

**解决方案**:
1. 确保系统内存充足（建议8GB+）
2. 关闭其他占用资源的程序
3. 使用较小的图片进行测试

### 5. 调试模式

如果遇到其他问题，可以通过命令行启动程序查看详细错误信息：

```cmd
# 打开命令提示符（cmd）
# 进入程序所在目录
cd /d "C:\path\to\HeadAlignmentTool"

# 运行程序
HeadAlignmentTool.exe
```

### 6. 系统要求

**最低要求**:
- Windows 10 (64位) 或更高版本
- 4GB RAM（推荐8GB+）
- 1GB 可用磁盘空间
- 支持OpenGL的显卡

**推荐配置**:
- Windows 11 (64位)
- 8GB+ RAM
- SSD硬盘
- 独立显卡

### 7. 联系支持

如果以上方案都无法解决问题，请：

1. 记录详细的错误信息
2. 提供系统配置信息
3. 在GitHub项目页面提交Issue
4. 或发送邮件至项目维护者

### 8. 替代方案

如果可执行文件无法正常工作，可以尝试：

1. **使用Python环境运行**:
   ```cmd
   # 安装Python 3.9+
   # 安装依赖
   pip install -r requirements.txt
   
   # 运行应用
   streamlit run streamlit_app.py
   ```

2. **使用Docker**（如果有Docker环境）:
   ```cmd
   # 构建镜像
   docker build -t head-alignment-tool .
   
   # 运行容器
   docker run -p 8501:8501 head-alignment-tool
   ```

## 版本历史

### v1.1.0
- 修复了Windows版本的MediaPipe依赖问题
- 改进了跨平台路径处理
- 增强了错误诊断和调试信息

### v1.0.0
- 初始版本发布 
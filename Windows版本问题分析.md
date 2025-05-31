# Windows版本问题分析与解决方案

## 问题原因分析

### 1. 硬编码路径问题
**问题**: 之前的 `HeadAlignmentTool.spec` 文件包含硬编码的macOS路径：
```python
'/Users/loneranger/Project/DeforumAI/deforumai/lib/python3.9/site-packages/streamlit/static'
```

**影响**: Windows系统无法找到这些路径，导致关键文件缺失

**解决方案**: 
- 删除硬编码的spec文件
- 使用 `prepare_build.py` 动态生成跨平台spec文件
- 自动检测当前系统的site-packages路径

### 2. MediaPipe Windows兼容性
**问题**: MediaPipe在Windows上需要额外的DLL文件和特定的导入模块

**影响**: 程序启动时出现MediaPipe相关错误

**解决方案**:
- 创建专门的 `hooks/hook-mediapipe.py`
- 添加Windows特定的隐藏导入
- 自动收集MediaPipe的DLL文件
- 包含protobuf相关模块

### 3. 路径分隔符问题
**问题**: Windows使用反斜杠(\)，Unix系统使用正斜杠(/)

**解决方案**: 在spec文件生成时使用原始字符串(r'')处理路径

## 修复内容

### 1. 更新 `prepare_build.py`
- 添加 `get_windows_mediapipe_binaries()` 函数
- 增强Windows特定的隐藏导入
- 改进路径处理和错误检测
- 添加详细的调试输出

### 2. 创建 `hooks/hook-mediapipe.py`
- 自动收集MediaPipe数据文件
- 处理Windows特定的DLL依赖
- 添加必要的隐藏导入模块

### 3. 更新GitHub Actions
- 添加Windows特定的调试步骤
- 增强错误诊断信息
- 改进构建测试流程

### 4. 创建故障排除文档
- `Windows故障排除.md` - 用户指南
- 包含常见问题和解决方案
- 提供替代运行方案

## 技术细节

### Windows特定的隐藏导入
```python
if platform.system() == 'Windows':
    hidden_imports.extend([
        'mediapipe.python._framework_bindings',
        'google.protobuf',
        'google.protobuf.internal',
        'google.protobuf.pyext',
        'google.protobuf.pyext._message',
    ])
```

### 动态路径检测
```python
def find_site_packages():
    candidates = []
    candidates.extend(site.getsitepackages())
    candidates.append(site.getusersitepackages())
    # 检测包含streamlit的路径
    for candidate in candidates:
        if os.path.exists(os.path.join(candidate, 'streamlit')):
            return candidate
```

### MediaPipe二进制文件收集
```python
def get_windows_mediapipe_binaries():
    for root, dirs, files in os.walk(mediapipe_path):
        for file in files:
            if file.endswith(('.dll', '.pyd')):
                # 收集DLL和PYD文件
```

## 预期效果

### 修复后的Windows版本应该：
1. ✅ 正确检测Windows系统的Python环境
2. ✅ 自动包含所有必要的MediaPipe文件
3. ✅ 处理Windows特定的路径和依赖
4. ✅ 提供详细的错误诊断信息
5. ✅ 与macOS/Linux版本功能一致

### 用户体验改进：
1. 🚀 更快的启动速度
2. 🛡️ 更好的错误处理
3. 📚 完整的故障排除文档
4. 🔧 多种运行方案选择

## 测试建议

### 下次发布时测试：
1. 在Windows 10/11上测试可执行文件
2. 验证MediaPipe功能正常
3. 检查浏览器自动打开
4. 测试图片处理功能
5. 验证错误处理机制

### 如果仍有问题：
1. 查看GitHub Actions的构建日志
2. 检查Windows特定的调试输出
3. 参考 `Windows故障排除.md`
4. 考虑添加更多Windows特定的依赖 
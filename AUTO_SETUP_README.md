# Task-Star 自动环境配置使用说明

## 📋 功能概述

`auto_setup.py` 是一个全自动的环境配置脚本，可以一键完成 Task-Star 程序运行环境的检测和配置。

## ✨ 主要功能

### 1. **自动环境检测**
- ✅ 检测 Python 版本（要求 >= 3.8）
- ✅ 检测已安装的 Python 包
- ✅ 检测缺失的依赖包
- ✅ 检测 Chrome 浏览器是否安装
- ✅ 检测配置文件是否存在

### 2. **自动依赖安装**
- ✅ 自动升级 pip
- ✅ 自动安装缺失的依赖包
- ✅ 支持批量安装
- ✅ 支持版本要求检查

### 3. **配置文件管理**
- ✅ 自动检测配置文件
- ✅ 自动从默认配置复制
- ✅ 验证配置文件格式

### 4. **完善的错误处理**
- ✅ 详细的错误日志
- ✅ 安装失败自动重试建议
- ✅ 完整的错误堆栈跟踪

### 5. **详细的日志记录**
- ✅ 实时控制台输出（彩色）
- ✅ 详细日志文件保存
- ✅ 配置过程计时
- ✅ 成功/失败统计

## 🚀 快速开始

### 方法一：运行自动配置脚本（推荐）

```bash
# 运行自动配置脚本
python auto_setup.py
```

脚本会自动完成以下步骤：
1. 检查 Python 版本
2. 升级 pip
3. 检测并安装缺失的依赖包
4. 检测 Chrome 浏览器
5. 检查配置文件
6. 输出配置结果

### 方法二：手动安装依赖

```bash
# 使用 requirements.txt 安装
pip install -r requirements.txt

# 或使用 pyproject.toml 安装（开发模式）
pip install -e .
```

## 📝 配置脚本说明

### 命令行使用

```bash
# 基本使用
python auto_setup.py

# 查看帮助（脚本内无参数，直接运行即可）
python auto_setup.py
```

### 输出说明

脚本会输出以下信息：

1. **彩色控制台输出**
   - 🟢 绿色 ✅ 表示成功
   - 🔴 红色 ❌ 表示失败
   - 🟡 黄色 ⚠️ 表示警告
   - 🔵 蓝色 ℹ️ 表示信息
   - 🔵 蓝色 🔄 表示进行中

2. **日志文件**
   - 文件名: `auto_setup.log`
   - 包含详细的配置过程
   - 记录所有错误和警告
   - 用于问题排查

### 配置检查项

脚本会检查以下项目：

| 检查项 | 说明 | 必需 |
|--------|------|------|
| Python 版本 | 检查 Python 版本是否 >= 3.8 | ✅ |
| pip 升级 | 自动升级 pip 到最新版本 | ✅ |
| 依赖包 | 检查并安装缺失的依赖包 | ✅ |
| Chrome 浏览器 | 检查 Google Chrome 是否已安装 | ⚠️ |
| 配置文件 | 检查 config/config.yaml 是否存在 | ✅ |

**说明**: ⚠️ 标记的项目表示非必需（Chrome 浏览器建议安装，但不会阻止程序运行）

## 🔧 依赖包说明

### 必需的依赖包

| 包名 | 版本要求 | 用途 |
|------|---------|------|
| selenium | >=4.15.0 | Web 自动化框架 |
| webdriver-manager | >=4.0.1 | ChromeDriver 自动管理 |
| pyyaml | >=6.0 | YAML 配置文件解析 |
| customtkinter | >=5.2.1 | 现代 GUI 框架 |
| pillow | >=10.0.0 | 图像处理 |

### 依赖包详细说明

#### selenium
- **用途**: 用于自动化浏览器操作
- **下载**: https://pypi.org/project/selenium/
- **文档**: https://selenium-python.readthedocs.io/

#### webdriver-manager
- **用途**: 自动下载和管理 ChromeDriver
- **下载**: https://pypi.org/project/webdriver-manager/
- **说明**: 程序首次运行时会自动下载匹配的 ChromeDriver

#### pyyaml
- **用途**: 解析 YAML 配置文件
- **下载**: https://pypi.org/project/PyYAML/

#### customtkinter
- **用途**: 提供现代化的 GUI 界面
- **下载**: https://pypi.org/project/customtkinter/
- **说明**: 基于 tkinter 的增强版本

#### pillow
- **用途**: 图像处理（可选）
- **下载**: https://pypi.org/project/Pillow/

## 📊 日志文件说明

### 日志文件位置
- 文件名: `auto_setup.log`
- 位置: 脚本运行的当前目录

### 日志内容

日志文件包含：
1. 配置开始时间
2. 系统信息
3. Python 版本信息
4. 每个检查项的详细结果
5. 安装过程的详细输出
6. 错误和警告信息
7. 配置完成时间
8. 统计信息

### 日志格式

```
[2026-03-03 10:30:45] [INFO] 检测 Python 版本...
[2026-03-03 10:30:45] [SUCCESS] Python 版本符合要求 (3.10.0)
[2026-03-03 10:30:46] [INFO] 检测已安装的 Python 包...
[2026-03-03 10:30:47] [WARNING] selenium (4.15.0) - 未安装
...
```

## ⚙️ 高级配置

### 修改依赖包版本

如果需要修改依赖包的版本要求，编辑 `auto_setup.py` 文件：

```python
class EnvironmentChecker:
    REQUIRED_PACKAGES = {
        'selenium': '4.15.0',      # 修改这里
        'webdriver_manager': '4.0.1',
        # ...
    }
```

### 修改 Python 版本要求

```python
class EnvironmentChecker:
    REQUIRED_PYTHON_VERSION = (3, 8)  # 修改最低版本要求
```

### 自定义 Chrome 检测路径

如果 Chrome 安装在非标准位置，编辑 `check_chrome_browser` 方法：

```python
def check_chrome_browser(self) -> bool:
    # 在这里添加自定义路径
    chrome_paths = [
        r"C:\Your\Custom\Path\chrome.exe",
        # ...
    ]
```

## 🐛 常见问题

### Q1: pip 安装失败

**问题**: 安装包时出现错误

**解决方案**:
```bash
# 升级 pip
python -m pip install --upgrade pip

# 使用国内镜像源
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 或配置永久镜像源
pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
```

### Q2: 网络超时

**问题**: 下载包时超时

**解决方案**:
```bash
# 增加超时时间
pip install --timeout 600 <包名>

# 或分批安装
pip install selenium
pip install webdriver_manager
```

### Q3: 权限错误

**问题**: 安装时提示权限不足

**解决方案**:
```bash
# 使用用户模式安装
pip install --user <包名>

# 或使用虚拟环境
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac
pip install -r requirements.txt
```

### Q4: Chrome 未检测到

**问题**: 脚本提示未检测到 Chrome

**解决方案**:
1. 确认已安装 Google Chrome
2. 检查 Chrome 安装路径
3. 修改 `check_chrome_browser` 方法添加自定义路径

### Q5: Python 版本过低

**问题**: Python 版本不符合要求

**解决方案**:
1. 升级 Python 到 3.8 或更高版本
2. 下载地址: https://www.python.org/downloads/

## 📚 使用示例

### 示例 1: 首次安装

```bash
# 1. 运行自动配置脚本
python auto_setup.py

# 2. 查看输出，确认所有检查通过
# 3. 修改 config/config.yaml
# 4. 运行程序
python main.py
```

### 示例 2: 检查环境

```bash
# 只检查环境，不安装（修改脚本跳过安装步骤）
python auto_setup.py
```

### 示例 3: 查看详细日志

```bash
# 运行配置脚本
python auto_setup.py

# 查看详细日志
type auto_setup.log  # Windows
# cat auto_setup.log  # Linux/Mac
```

## 🎯 最佳实践

### 1. 使用虚拟环境

```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# 运行自动配置
python auto_setup.py
```

### 2. 定期更新依赖

```bash
# 更新所有包
pip install --upgrade -r requirements.txt

# 或重新运行自动配置
python auto_setup.py
```

### 3. 备份配置

```bash
# 备份配置文件
copy config\config.yaml config\config.yaml.backup
```

## 📞 技术支持

如果遇到问题：

1. 查看 `auto_setup.log` 日志文件
2. 检查本说明的"常见问题"部分
3. 确认网络连接正常
4. 确认 Python 和 pip 版本

## 📄 许可证

MIT License

## 👥 贡献

欢迎提交问题和改进建议！

---

**祝您使用愉快！** 🎉

# Task-Star 问卷星自动填写工具

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

问卷星（问卷星）自动填写工具，基于 Selenium 实现自动化批量填写问卷。

## ✨ 特性

- 🚀 **快速启动** - 3 秒启动，无需复杂配置
- 📝 **支持多种题型** - 单选题、多选题、填空题、下拉选择题
- 🎲 **随机填写** - 智能随机选择，模拟真实用户行为
- 🔄 **批量填写** - 支持自定义填写次数
- ⏱️ **智能间隔** - 可设置提交间隔时间，避免被封禁
- 📊 **实时日志** - 详细记录填写过程和统计信息

## 📦 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

或使用国内镜像：

```bash
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 2. 安装 Chrome 浏览器

确保已安装 Google Chrome 浏览器：[下载链接](https://www.google.com/chrome/)

### 3. 运行脚本

#### 方法 A：使用简单脚本（推荐）

```bash
python simple_fill.py
```

#### 方法 B：使用完整项目

```bash
# 修改配置文件 config/config.yaml
python main.py -t 100
```

## 📖 使用说明

### 简单脚本模式

编辑 `simple_fill.py` 修改配置：

```python
# 修改 URL
url = "https://v.wjx.cn/vm/w7MiF02.aspx#"

# 修改填写次数和间隔
filler.run(times=100, interval=5)
```

### 配置文件模式

编辑 `config/config.yaml`：

```yaml
general:
  questionnaire_url: "https://v.wjx.cn/vm/w7MiF02.aspx#"
  fill_times: 100
  interval_seconds: 5
  headless: false
  auto_submit: true
  retry_count: 3

strategy:
  multi_choice:
    min_select: 2
    max_select: 3
  fill_blanks:
    9: ["答案 1", "答案 2", "答案 3"]
```

### 命令行参数

```bash
# 填写 100 次
python main.py -t 100

# 后台运行
python main.py --headless

# 后台填写 50 次
python main.py -t 50 --headless

# 查看帮助
python main.py -h
```

## 📁 项目结构

```
task-star/
├── config/
│   ├── config.yaml          # 用户配置文件
│   ├── default_config.yaml  # 默认配置模板
│   └── selectors.yaml       # CSS 选择器配置
├── src/
│   └── task_star/
│       ├── __init__.py      # 包初始化
│       ├── browser.py       # 浏览器管理
│       ├── config.py        # 配置加载
│       ├── core_logic.py    # 核心逻辑
│       ├── utils.py         # 工具函数
│       └── exceptions.py    # 异常定义
├── simple_fill.py           # 简单脚本（推荐）
├── main.py                  # 主入口
├── auto_setup.py            # 自动环境配置
├── requirements.txt         # 依赖包列表
├── README.md                # 项目说明
├── LICENSE                  # MIT 许可证
└── .gitignore              # Git 忽略文件
```

## 🔧 常见问题

### 1. ChromeDriver 版本不匹配

```bash
pip install --upgrade webdriver-manager
```

或手动下载匹配的 ChromeDriver：[下载链接](https://chromedriver.chromium.org/)

### 2. 未找到 Chrome 浏览器

安装 Chrome 浏览器：https://www.google.com/chrome/

### 3. 页面加载超时

- 检查网络连接
- 增加超时时间：`page_timeout: 60`
- 检查问卷链接是否有效

### 4. 检测到验证码

程序会自动暂停，等待手动完成验证码后继续执行。

## ⚠️ 注意事项

1. **合理使用** - 请设置适当的填写次数（建议 10-100 次）
2. **间隔时间** - 建议设置 3-10 秒的提交间隔
3. **网络稳定** - 确保网络连接稳定
4. **合法使用** - 本工具仅供学习研究使用，请勿用于非法用途
5. **风险自担** - 使用本工具产生的后果由使用者自行承担

## 📊 性能对比

| 模式 | 启动时间 | 单份耗时 | 100 份总耗时 |
|------|----------|----------|--------------|
| 简单脚本 | 3 秒 | 8-12 秒 | 12-18 分钟 |
| 完整项目 | 5 秒 | 10-15 秒 | 15-20 分钟 |

## 🛠️ 开发环境

- Python 3.8+
- Selenium 4.15.0+
- ChromeDriver（自动管理）
- Chrome 浏览器

## 📝 更新日志

### v1.0.0 (2026-03-08)

- ✨ 初始版本发布
- 🚀 支持单选题、多选题、填空题、下拉选择题
- 🎯 支持批量填写和随机答案
- 📝 完善的文档和示例

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🙏 致谢

- [Selenium](https://www.selenium.dev/) - Web 自动化框架
- [webdriver-manager](https://github.com/SergeyPirogov/webdriver_manager) - ChromeDriver 管理工具
- [问卷星](https://www.wjx.cn/) - 问卷平台

## 📧 联系方式

如有问题或建议，请提交 Issue 或联系作者。

---

**⚠️ 免责声明**：本工具仅供学习和研究使用。使用本工具时应遵守相关法律法规和网站使用条款。作者不对使用本工具产生的任何后果负责。

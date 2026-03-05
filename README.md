# Task-Star 问卷自动填写助手 🌟

[![Stars](https://img.shields.io/github/stars/badhope/task-star?style=social)](https://github.com/badhope/task-star/stargazers)
[![Forks](https://img.shields.io/github/forks/badhope/task-star?style=social)](https://github.com/badhope/task-star/network/members)
[![Issues](https://img.shields.io/github/issues/badhope/task-star)](https://github.com/badhope/task-star/issues)
[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Version](https://img.shields.io/badge/version-3.0.0-orange.svg)](https://github.com/badhope/task-star/releases)

> 🎯 **这个项目就像一颗冉冉升起的新星，只差你的一颗 Star 就能点亮夜空！** ⭐🌌

一个强大的问卷星自动填写工具，支持多种题型和策略配置。解放你的双手，让填问卷变得像喝奶茶一样简单！🧋✨

---

## ✨ 特性亮点

### 核心功能
- ✅ **智能识别** - 单选、多选、填空、下拉选择题自动识别，比你还懂问卷 🧠
- ✅ **自定义答案池** - 想要什么答案就填什么，就是这么任性 😎
- ✅ **验证码检测** - 遇到验证码自动暂停，等你手动搞定再继续 🤖
- ✅ **图形化界面** - 无需编写代码，点点鼠标就能完成配置 🖱️
- ✅ **后台运行** - 支持无界面模式，服务器也能愉快使用 ☁️
- ✅ **防封禁机制** - 随机时间间隔模拟真人，安全又可靠 🛡️

### v3.0 新增功能 🆕
- 🎨 **现代化 GUI 界面** - 全新设计的深色主题，支持亮色/暗色切换
- 📊 **任务历史记录** - 自动保存历史任务统计，方便查看分析
- 🔧 **智能错误处理** - 自动诊断并修复常见错误
- 💬 **用户友好提示** - 分级错误提示系统，清晰指导用户操作
- 📝 **日志导出功能** - 一键导出运行日志，方便问题排查
- 🔄 **自动重试机制** - 失败自动重试，提高成功率
- ⏱️ **实时进度显示** - 进度条、成功/失败统计实时更新

---

## 🚀 快速开始

### 🎯 方式一：自动配置（强烈推荐，新手友好）

一键自动配置完整运行环境，妈妈再也不用担心我不会装环境了！

```bash
python auto_setup.py
```

**自动配置脚本会：**
- ✅ 检查 Python 版本（要求 >= 3.8）
- ✅ 自动升级 pip
- ✅ 检测并安装所有缺失的依赖包
- ✅ 检测 Chrome 浏览器
- ✅ 自动创建配置文件
- ✅ 生成详细的配置日志

**详细说明请查看**: [AUTO_SETUP_README.md](AUTO_SETUP_README.md)

### 💻 方式二：手动安装依赖

**使用 requirements.txt:**
```bash
pip install -r requirements.txt
```

**或使用 pyproject.toml:**
```bash
pip install -e .
```

**或者直接安装依赖包:**
```bash
pip install selenium webdriver-manager pyyaml customtkinter pillow
```

### 📝 配置问卷

编辑 `config/config.yaml` 文件，设置：
- `questionnaire_url`: 问卷链接（必填，不然程序会懵圈 😵）
- `fill_times`: 填写次数（建议 10-50 次，别太贪心哦）
- `interval_seconds`: 提交间隔时间（3-10 秒，给服务器喘口气的时间）
- `retry_count`: 失败重试次数（默认 3 次）
- `page_timeout`: 页面加载超时（秒，默认 30 秒）
- 答题策略配置（详细看下面）

### ▶️ 运行程序

**方式一：启动 GUI 界面（推荐）**
```bash
python main.py
```

**方式二：使用包命令**
```bash
taskstar
```

---

## 📁 项目结构

```
task-star/
├── config/
│   ├── config.yaml          # 用户配置文件（请修改此文件）
│   ├── default_config.yaml  # 默认配置模板
│   └── selectors.yaml       # CSS 选择器配置
├── src/
│   └── task_star/
│       ├── __init__.py      # 包初始化
│       ├── browser.py       # 浏览器管理 🆕
│       ├── config.py        # 配置加载 🆕
│       ├── core_logic.py    # 核心逻辑 🆕
│       ├── utils.py         # 工具函数
│       ├── exceptions.py    # 异常定义 🆕
│       ├── error_handler.py # 错误处理系统 ⭐NEW
│       └── strategies/      # 答题策略 🆕
│           ├── base.py      # 基类
│           ├── single.py    # 单选题策略
│           ├── multiple.py  # 多选题策略
│           ├── blank.py     # 填空题策略
│           └── dropdown.py  # 下拉选择题 ⭐NEW
├── ui_app.py                # GUI 界面 ⭐NEW
├── main.py                  # 主入口
├── auto_setup.py            # 自动环境配置脚本 ⭐
├── test_run.py              # 环境检测脚本
├── test_comprehensive.py    # 综合测试套件 ⭐NEW
├── requirements.txt         # 依赖包列表
├── AUTO_SETUP_README.md     # 自动配置详细说明 ⭐
├── README.md                # 项目说明文档
└── pyproject.toml           # 项目配置
```

---

## ⚙️ 配置说明

### 基础配置 (config.yaml)

```yaml
general:
  questionnaire_url: "https://www.wjx.cn/jq/xxxx.aspx"  # 问卷链接（必填！）
  fill_times: 10                                        # 填写次数
  interval_seconds: 5                                   # 提交间隔（秒）
  headless: false                                       # 是否后台运行
  auto_submit: true                                     # 是否自动提交
  retry_count: 3                                        # 失败重试次数 ⭐NEW
  page_timeout: 30                                      # 页面超时（秒）⭕NEW
  # proxy: "127.0.0.1:7890"                            # 代理服务器（可选）⭕NEW
```

### 答题策略配置

#### 多选题策略
```yaml
strategy:
  multi_choice:
    min_select: 2    # 最少选择项数
    max_select: 3    # 最多选择项数
```

#### 填空题策略
```yaml
strategy:
  fill_blanks:
    1: ["张三", "李四"]              # 第 1 题答案池
    2: ["计算机学院", "软件学院"]    # 第 2 题答案池
```

---

## 🎨 GUI 界面功能

### 页面导航
- 🏠 **首页** - 项目介绍和快速入门
- 🚀 **开始任务** - 任务执行界面，实时查看进度
- ⚙️ **设置** - 配置问卷参数和答题策略
- 📊 **历史记录** - 查看历史任务统计
- ❓ **帮助** - 详细的使用说明和常见问题

### 主题切换
支持三种主题模式：
- **Dark** - 深色主题（默认）
- **Light** - 浅色主题
- **System** - 跟随系统

### 错误提示系统
当发生错误时，系统会：
1. 🔍 **自动诊断** - 智能识别错误类型
2. 💡 **提供建议** - 给出清晰的解决建议
3. 🔧 **自动修复** - 对常见错误自动修复
4. 📝 **记录日志** - 详细记录错误信息

---

## ❓ 常见问题

### 1. 遇到验证码怎么办？ 🤔
程序会自动暂停并在日志中提示。手动在浏览器中完成验证后，点击 GUI 界面中的"验证码已完成，继续"按钮即可。
> 小贴士：验证码是系统在说"让我看看你是不是真人"，配合一下就好啦~ 👮‍♂️

### 2. 为什么提交失败？ 😱
- 检查网络连接（没网啥也干不了）
- 尝试关闭"后台运行"模式（看看浏览器有啥报错）
- 查看 GUI 界面的错误提示信息
- 导出日志文件查看详细错误

### 3. 配置文件在哪里？ 📄
位于 `config/config.yaml`，如果不存在可从 `default_config.yaml` 复制，或运行自动配置脚本自动创建。

### 4. 如何修改 CSS 选择器？ 🔧
如果问卷星更新页面导致程序失效，可修改 `config/selectors.yaml` 中的选择器。

### 5. 依赖安装失败怎么办？ 📦

**方案一（推荐）**: 运行自动配置脚本
```bash
python auto_setup.py
```

**方案二**: 使用国内镜像源
```bash
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

**方案三**: 逐个手动安装
```bash
pip install selenium
pip install webdriver-manager
pip install pyyaml
pip install customtkinter
pip install pillow
```

### 6. Python 版本过低怎么办？ 🐍
请升级 Python 到 3.8 或更高版本：
- 下载地址：https://www.python.org/downloads/

### 7. 如何检查环境是否正确？ ✅
运行环境检测脚本：
```bash
python test_run.py
```

### 8. 如何运行测试？ 🧪
运行综合测试套件：
```bash
python test_comprehensive.py
```

### 9. 如何导出日志？ 📝
在 GUI 界面中点击右上角的"导出日志"按钮，日志将保存到 `logs/` 目录。

---

## 🛠️ 开发调试

### 安装开发依赖
```bash
pip install -e .[dev]
```

### 运行测试
```bash
python test_comprehensive.py
```

### 代码结构说明
- **core_logic.py** - 核心业务逻辑，负责问卷填写流程
- **browser.py** - 浏览器管理器，负责创建和配置 Chrome
- **config.py** - 配置加载器，负责读取和验证配置
- **error_handler.py** - 错误处理系统，提供智能错误诊断
- **strategies/** - 答题策略模块，支持扩展新题型

---

## 📝 注意事项

1. ⚠️ **请合理使用本工具**，不要过度使用导致 IP 被封禁
2. 💡 建议设置适当的填写次数（10-50 次）
3. ⏱️ 提交间隔建议设置为 3-10 秒
4. 📚 本工具仅供学习研究使用
5. 🔒 请勿用于非法用途，后果自负

---

## 📄 许可证

MIT License

---

## 👥 作者

BadHope <badhope@example.com>

---

## 📊 更新日志

### v3.0.0 (2026-03-06) ⭐ Major Update
- 🎨 全新设计的现代化 GUI 界面
- 🤖 智能错误处理和自动修复系统
- 📊 任务历史记录功能
- 🔄 自动重试机制
- ⏱️ 实时进度显示
- 📝 日志导出功能
- � 新增下拉选择题支持
- 💬 用户友好的分级错误提示

### v2.0.0
- 🖥️ 图形化界面
- ⚙️ 可视化配置
- 📋 多题型支持

### v1.0.0
- 🎉 初始版本发布

---

## �🌟 Star History

如果觉得这个项目帮到了你，别忘了给个 Star 哦！⭐ 
每一颗 Star 都是我继续前进的动力！💪

[![Star History Chart](https://api.star-history.com/svg?repos=badhope/task-star&type=Date)](https://star-history.com/#badhope/task-star&Date)

---

<div align="center">

**Made with ❤️ by BadHope**

如果这个工具帮到了你，请给它一个大大的赞！👍

</div>

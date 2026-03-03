# Task-Star 问卷自动填写助手

一个强大的问卷星自动填写工具，支持多种题型和策略配置。

## ✨ 特性

- ✅ 支持单选、多选、填空题自动识别
- ✅ 支持自定义答案池
- ✅ 支持验证码暂停机制
- ✅ 图形化配置，无需编写代码
- ✅ 支持后台运行模式

## 🚀 快速开始

### 🎯 方式一：自动配置（推荐，适合新手）

一键自动配置完整运行环境：

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

**或直接安装依赖包:**
```bash
pip install selenium webdriver-manager pyyaml customtkinter pillow
```

### 2. 配置问卷

编辑 `config/config.yaml` 文件，设置：
- `questionnaire_url`: 问卷链接
- `fill_times`: 填写次数
- `interval_seconds`: 提交间隔时间
- 答题策略配置

### 3. 运行程序

**方式一：直接运行（推荐）**
```bash
python main.py
```

**方式二：使用包命令**
```bash
taskstar
```

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
│       ├── browser.py       # 浏览器管理
│       ├── config.py        # 配置加载
│       ├── core_logic.py    # 核心逻辑
│       ├── utils.py         # 工具函数
│       ├── exceptions.py    # 异常定义
│       └── strategies/      # 答题策略
│           ├── base.py      # 基类
│           ├── single.py    # 单选题策略
│           ├── multiple.py  # 多选题策略
│           └── blank.py     # 填空题策略
├── ui_app.py                # GUI 界面
├── main.py                  # 主入口
├── auto_setup.py            # 自动环境配置脚本 ⭐
├── test_run.py              # 环境检测脚本
├── requirements.txt         # 依赖包列表
├── AUTO_SETUP_README.md     # 自动配置详细说明 ⭐
├── README.md                # 项目说明文档
└── pyproject.toml           # 项目配置
```

## ⚙️ 配置说明

### 基础配置 (config.yaml)

```yaml
general:
  questionnaire_url: "https://www.wjx.cn/jq/xxxx.aspx"  # 问卷链接
  fill_times: 10                                        # 填写次数
  interval_seconds: 5                                   # 提交间隔（秒）
  headless: false                                       # 是否后台运行
  auto_submit: true                                     # 是否自动提交
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

## ❓ 常见问题

### 1. 遇到验证码怎么办？
程序会自动暂停并在日志中提示。手动在浏览器中完成验证后，程序会继续执行。

### 2. 为什么提交失败？
- 检查网络连接
- 尝试关闭"后台运行"模式
- 查看浏览器是否有报错信息

### 3. 配置文件在哪里？
位于 `config/config.yaml`，如果不存在可从 `default_config.yaml` 复制，或运行自动配置脚本自动创建。

### 4. 如何修改 CSS 选择器？
如果问卷星更新页面导致程序失效，可修改 `config/selectors.yaml` 中的选择器。

### 5. 依赖安装失败怎么办？
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

### 6. Python 版本过低怎么办？
请升级 Python 到 3.8 或更高版本：
- 下载地址: https://www.python.org/downloads/

### 7. 如何检查环境是否正确？
运行环境检测脚本：
```bash
python test_run.py
```

## 🛠️ 开发调试

### 安装开发依赖
```bash
pip install -e .[dev]
```

### 运行测试
```bash
python -m pytest tests/
```

## 📝 注意事项

1. 请合理使用本工具，不要过度使用导致 IP 被封禁
2. 建议设置适当的填写次数（10-50 次）
3. 提交间隔建议设置为 3-10 秒
4. 本工具仅供学习研究使用

## 📄 许可证

MIT License

## 👥 作者

Your Name <your.email@example.com>

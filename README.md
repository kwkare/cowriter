<img align="left" style="margin: 0 0 4px 0;" src="https://raw.githubusercontent.com/YOUR_USERNAME/cowriter/main/setup/cowriter_readme.png">

# CoWriter · 共笔

**AI 辅助小说写作编辑器** | 基于 novelWriter 衍生

> CoWriter 是 novelWriter 的一个分支，在其优秀的纯文本写作编辑器基础上，融入了 **AI 辅助写作** 能力。与 AI 共笔，行文更从容。

---

## 特色功能

### ✍️ AI 辅助写作
- **续写**（Continue）：在光标处让 AI 继续写出下文
- **改写**（Rewrite）：选中文本 → AI 润色/重写
- **扩写**（Expand）：把简略的描述展开为细腻的段落
- **AI 聊天**（AI Chat）：侧边栏 AI 对话窗口，边聊边写
- **头脑风暴**：根据大纲/情节生成创意建议

### 🔌 多模型支持
| 模型 | 类型 | 特点 |
|------|------|------|
| **OpenAI** (GPT-4o/GPT-4) | 云端 API | 最强文字能力 |
| **Anthropic** (Claude) | 云端 API | 长上下文，风格细腻 |
| **Ollama** (Qwen2.5/Llama 等) | **本地运行** | 免费、隐私安全 |

### 📝 继承 novelWriter 的全部能力
- 纯文本编辑器，类 Markdown 格式
- 分章节/分场景管理
- 角色/地点/笔记管理
- 大纲视图与写作统计
- 多主题支持
- 导出为 ODT/HTML/DOCX/Markdown

---

## 快速开始

### 安装

```bash
# 克隆仓库
git clone https://github.com/YOUR_USERNAME/cowriter.git
cd cowriter

# 推荐使用 PDM 安装
pdm install

# 或者用 pip
pip install -e .
```

### 运行

```bash
# 方式一
pdm run cowriter

# 方式二
python -m cowriter

# 方式三（根目录脚本）
python CoWriter.py
```

### 配置 AI

1. 启动 CoWriter
2. 进入 **Preferences → AI Assistant**
3. 选择 Provider（OpenAI / Anthropic / Ollama）
4. 填入 API Key（云端模型）或保持默认（本地 Ollama）
5. 开始写作！🎉

---

## 项目结构

```
cowriter/
├── ai/                  # AI 模块（新增）
│   ├── provider.py      #   Provider 抽象层
│   ├── completion.py    #   续写/改写引擎
│   ├── chat.py          #   AI 对话会话
│   ├── prompts.py       #   Prompt 模板
│   └── settings.py      #   AI 配置模型
├── core/                # 核心逻辑（继承 novelWriter）
├── gui/                 # GUI 组件（继承 + 新增 AI 面板）
├── extensions/          # 扩展组件
├── formats/             # 导出格式
├── tools/               # 工具
└── ...                  # 其余继承自 novelWriter
```

---

## 与 novelWriter 的关系

CoWriter 是 [novelWriter](https://novelwriter.io) 的 **GPLv3 分支**。

- **致敬原作者**：novelWriter 是由 [Veronica Berglyd Olsen](https://github.com/vkbo) 精心维护的优秀项目
- **尊重原项目态度**：novelWriter 坚持「100% free of AI slop」，因此 CoWriter 作为一个 AI 增强分支，与 upstream 保持独立发展
- **上游更新**：我们会定期从 novelWriter 合并更新

---

## 许可证

GNU General Public License v3.0 (GPLv3) — 与 novelWriter 一致。

---

*与 AI 共笔，共织锦绣文章。*

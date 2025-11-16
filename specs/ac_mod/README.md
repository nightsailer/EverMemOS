# memory_layer 模块文档索引

本目录包含 memory_layer 所有子模块的 ac_mod 文档。

## 文档列表

| 文档 | 模块路径 | 行数 | 说明 |
|------|---------|------|------|
| [memory_layer.ac.mod.md](./memory_layer.ac.mod.md) | `src/memory_layer/` | 345 | 记忆管理核心层（MemoryManager、Types、LLM集成） |
| [memory_layer.cluster_manager.ac.mod.md](./memory_layer.cluster_manager.ac.mod.md) | `src/memory_layer/cluster_manager/` | 408 | MemCell 聚类管理器（向量聚类、Storage） |
| [memory_layer.profile_manager.ac.mod.md](./memory_layer.profile_manager.ac.mod.md) | `src/memory_layer/profile_manager/` | 520 | 用户画像管理器（Discriminator、自动提取） |
| [memory_layer.llm.ac.mod.md](./memory_layer.llm.ac.mod.md) | `src/memory_layer/llm/` | 483 | LLM Provider 协议和实现（OpenAI/OpenRouter） |
| [memory_layer.memory_extractor.group_profile.ac.mod.md](./memory_layer.memory_extractor.group_profile.ac.mod.md) | `src/memory_layer/memory_extractor/group_profile/` | 501 | 群组画像提取工具包（4个文件） |
| [memory_layer.memory_extractor.profile_memory.ac.mod.md](./memory_layer.memory_extractor.profile_memory.ac.mod.md) | `src/memory_layer/memory_extractor/profile_memory/` | 542 | 个人画像提取工具包（11个文件） |
| [memory_layer.prompts.ac.mod.md](./memory_layer.prompts.ac.mod.md) | `src/memory_layer/prompts/` | 332 | 多语言提示词模板包（en/zh/eval） |
| [memory_layer.prompts.en.ac.mod.md](./memory_layer.prompts.en.ac.mod.md) | `src/memory_layer/prompts/en/` | 298 | 英文提示词（11个文件） |
| [memory_layer.prompts.zh.ac.mod.md](./memory_layer.prompts.zh.ac.mod.md) | `src/memory_layer/prompts/zh/` | 202 | 中文提示词（11个文件） |
| [memory_layer.prompts.eval.ac.mod.md](./memory_layer.prompts.eval.ac.mod.md) | `src/memory_layer/prompts/eval/` | 236 | 评估提示词（6个文件） |

**总计**: 10 个文档，3867 行

## 快速导航

### 核心模块
- [memory_layer](./memory_layer.ac.mod.md) - 记忆管理核心层
- [llm](./memory_layer.llm.ac.mod.md) - LLM Provider 抽象

### 管理器
- [cluster_manager](./memory_layer.cluster_manager.ac.mod.md) - MemCell 聚类
- [profile_manager](./memory_layer.profile_manager.ac.mod.md) - 用户画像管理

### 提取器工具
- [group_profile](./memory_layer.memory_extractor.group_profile.ac.mod.md) - 群组画像工具
- [profile_memory](./memory_layer.memory_extractor.profile_memory.ac.mod.md) - 个人画像工具

### 提示词
- [prompts](./memory_layer.prompts.ac.mod.md) - 多语言提示词
- [prompts.en](./memory_layer.prompts.en.ac.mod.md) - 英文提示词
- [prompts.zh](./memory_layer.prompts.zh.ac.mod.md) - 中文提示词
- [prompts.eval](./memory_layer.prompts.eval.ac.mod.md) - 评估提示词

## 文档特性

所有文档包含：
- ✅ 模块位置和目录结构
- ✅ 快速开始示例
- ✅ 核心组件详解
- ✅ Mermaid 依赖图
- ✅ Grep 验证的依赖关系
- ✅ 可运行的测试命令
- ✅ 实际场景示例

## 遵循规范

- **ac_mod.md**: 模块文档编写标准
- **doc_rules.md**: 紧凑格式原则（token 优化）

# memory_layer.prompts.zh

中文提示词模板包，与英文版功能对齐，包含对话处理、Episode 记忆、Profile 画像等 11 个模块

## 模块位置

**源码路径**: `src/memory_layer/prompts/zh/`
**文档路径**: `specs/ac_mod/memory_layer.prompts.zh.ac.mod.md`
**模块类型**: 包模块

## 文件结构

```
src/memory_layer/prompts/zh/
├── __init__.py                                    # 空文件
├── conv_prompts.py                                # 对话处理（边界检测、摘要）
├── episode_mem_prompts.py                         # Episode 记忆生成
├── event_log_prompts.py                           # 事件日志提取
├── group_profile_prompts.py                       # Group Profile 画像（内容、行为分析）
├── group_profile_merge_prompts.py                 # Group Profile 合并
├── profile_mem_prompts.py                         # Profile 画像（完整版）
├── profile_mem_part1_prompts.py                   # Profile 画像（Part1：基础）
├── profile_mem_part2_prompts.py                   # Profile 画像（Part2：项目）
├── profile_mem_part3_prompts.py                   # Profile 画像（Part3：价值观）
├── profile_mem_evidence_completion_prompt.py      # 证据补全
└── semantic_mem_prompts.py                        # 语义记忆生成
```

## 快速开始

```python
# 设置中文环境
import os
os.environ['MEMORY_LANGUAGE'] = 'zh'

# 导入（自动加载中文提示词）
from memory_layer.prompts import (
    CONV_BOUNDARY_DETECTION_PROMPT,
    EPISODE_GENERATION_PROMPT,
    CONVERSATION_PROFILE_PART1_EXTRACTION_PROMPT
)

# 使用中文提示词
prompt = CONV_BOUNDARY_DETECTION_PROMPT.format(
    conversation_history="Alice: 你好\nBob: 嗨",
    time_gap_info="5分钟",
    new_messages="Alice: 项目进展如何？"
)
```

## 提示词模块详解

**与英文版完全对应**，模块功能和输出格式相同，仅语言不同。

### 核心差异

| 方面 | 英文版 | 中文版 |
|------|--------|--------|
| 语言 | English | 中文 |
| 字段名 | `hard_skills` | `hard_skills`（保持不变） |
| 输出格式 | JSON（英文值） | JSON（中文值） |
| 示例 | `{"value": "Python"}` | `{"value": "Python开发"}` |

### 提示词列表

1. **conv_prompts.py**: 对话处理
   - `CONV_BOUNDARY_DETECTION_PROMPT`
   - `CONV_SUMMARY_PROMPT`

2. **episode_mem_prompts.py**: Episode 记忆
   - `EPISODE_GENERATION_PROMPT`
   - `GROUP_EPISODE_GENERATION_PROMPT`
   - `DEFAULT_CUSTOM_INSTRUCTIONS`

3. **profile_mem_part1_prompts.py**: 基础画像
   - `CONVERSATION_PROFILE_PART1_EXTRACTION_PROMPT`

4. **profile_mem_part2_prompts.py**: 项目画像
   - `CONVERSATION_PROFILE_PART2_EXTRACTION_PROMPT`

5. **profile_mem_part3_prompts.py**: 价值观系统
   - `CONVERSATION_PROFILE_PART3_EXTRACTION_PROMPT`

6. **group_profile_prompts.py**: Group Profile
   - `CONTENT_ANALYSIS_PROMPT`
   - `BEHAVIOR_ANALYSIS_PROMPT`

7. **semantic_mem_prompts.py**: 语义记忆
   - `get_semantic_generation_prompt()`
   - `get_group_semantic_generation_prompt()`

8. **event_log_prompts.py**: 事件日志
   - `EVENT_LOG_PROMPT`

详细功能说明参考：`specs/ac_mod/memory_layer.prompts.en.ac.mod.md`

## 依赖关系说明

### 对其他模块的依赖

**无外部依赖**（纯提示词文本）

### 被依赖关系

通过 Grep 验证：
```bash
grep -rn "from \.zh\." src/memory_layer/prompts/__init__.py
```

**结果**：
- `memory_layer/prompts/__init__.py`: 当 `MEMORY_LANGUAGE=zh` 时导入

**文档引用**：
- `specs/ac_mod/memory_layer.prompts.ac.mod.md`（父包）

## 可运行的测试命令

```bash
# 1. 设置中文环境
export MEMORY_LANGUAGE=zh

# 2. 验证导入
python -c "
from memory_layer.prompts import CONV_BOUNDARY_DETECTION_PROMPT
print(f'✅ ZH prompts loaded: {len(CONV_BOUNDARY_DETECTION_PROMPT)} chars')
"

# 3. 验证格式化
python -c "
from memory_layer.prompts import EPISODE_GENERATION_PROMPT
prompt = EPISODE_GENERATION_PROMPT.format(
    conversation_text='测试对话',
    custom_instructions=''
)
print(f'✅ Formatted prompt: {len(prompt)} chars')
"

# 4. 对比英文版长度
python -c "
import os
os.environ['MEMORY_LANGUAGE'] = 'en'
from memory_layer.prompts.en.conv_prompts import CONV_BOUNDARY_DETECTION_PROMPT as EN
os.environ['MEMORY_LANGUAGE'] = 'zh'
from memory_layer.prompts.zh.conv_prompts import CONV_BOUNDARY_DETECTION_PROMPT as ZH
print(f'✅ EN: {len(EN)} chars, ZH: {len(ZH)} chars')
"
```

## 示例场景

### 场景 1: 中文对话处理

```python
import os
os.environ['MEMORY_LANGUAGE'] = 'zh'

from memory_layer.prompts import CONV_BOUNDARY_DETECTION_PROMPT

prompt = CONV_BOUNDARY_DETECTION_PROMPT.format(
    conversation_history="Alice: 早上好\nBob: 你好",
    time_gap_info="3分钟",
    new_messages="Alice: 今天的会议准备好了吗？"
)

response = await llm_provider.generate(prompt, temperature=0.0)
# 返回中文结果
```

### 场景 2: 中文画像提取

```python
from memory_layer.prompts import CONVERSATION_PROFILE_PART1_EXTRACTION_PROMPT

prompt = CONVERSATION_PROFILE_PART1_EXTRACTION_PROMPT.format(
    conversation_text="Alice: 我是一名Python开发工程师，有5年经验",
    user_id="alice",
    existing_profile="{}"
)

response = await llm_provider.generate(prompt, temperature=0.3)
# 返回中文画像
```

## 中文提示词优化建议

**语言风格**：
- 使用自然的中文表达
- 避免直译英文

**文化适配**：
- 考虑中文沟通习惯
- 适配中文语境

**术语统一**：
- 保持专业术语一致
- 使用行业标准翻译

## 扩展阅读

- **父包文档**：`specs/ac_mod/memory_layer.prompts.ac.mod.md`
- **英文提示词**：`specs/ac_mod/memory_layer.prompts.en.ac.mod.md`
- **Memory Extractors**：`specs/ac_mod/memory_layer.memory_extractor.ac.mod.md`

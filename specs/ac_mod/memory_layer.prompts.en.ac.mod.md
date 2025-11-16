# memory_layer.prompts.en

英文提示词模板包，包含对话处理、Episode 记忆、Profile 画像、Group Profile、语义记忆、事件日志等 11 个模块

## 模块位置

**源码路径**: `src/memory_layer/prompts/en/`
**文档路径**: `specs/ac_mod/memory_layer.prompts.en.ac.mod.md`
**模块类型**: 包模块

## 文件结构

```
src/memory_layer/prompts/en/
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
from memory_layer.prompts.en import (
    conv_prompts,
    episode_mem_prompts,
    profile_mem_part1_prompts,
    group_profile_prompts,
    semantic_mem_prompts,
    event_log_prompts
)

# 对话边界检测
boundary_prompt = conv_prompts.CONV_BOUNDARY_DETECTION_PROMPT.format(
    conversation_history="...",
    time_gap_info="...",
    new_messages="..."
)

# Episode 生成
episode_prompt = episode_mem_prompts.EPISODE_GENERATION_PROMPT.format(
    conversation_text="...",
    custom_instructions="..."
)

# Profile 提取（Part1）
profile_prompt = profile_mem_part1_prompts.CONVERSATION_PROFILE_PART1_EXTRACTION_PROMPT.format(
    conversation_text="...",
    user_id="alice",
    existing_profile="{}"
)
```

## 提示词模块详解

### 1. conv_prompts.py

**提示词**：
- `CONV_BOUNDARY_DETECTION_PROMPT`: 对话边界检测，判断是否开启新 Episode
- `CONV_SUMMARY_PROMPT`: 对话摘要生成

**输出格式**：
```json
{
  "start_new_episode": true,
  "reason": "Topic changed from greeting to project discussion"
}
```

### 2. episode_mem_prompts.py

**提示词**：
- `EPISODE_GENERATION_PROMPT`: 个人 Episode 记忆生成
- `GROUP_EPISODE_GENERATION_PROMPT`: 群组 Episode 记忆生成
- `DEFAULT_CUSTOM_INSTRUCTIONS`: 默认自定义指令

**输出格式**：
```json
{
  "episode": "Alice shared project progress...",
  "subject": "Project Update Discussion"
}
```

### 3. profile_mem_part1_prompts.py

**提示词**：
- `CONVERSATION_PROFILE_PART1_EXTRACTION_PROMPT`: 基础画像提取

**提取字段**：
- `hard_skills`: 硬技能
- `soft_skills`: 软技能
- `way_of_decision_making`: 决策方式
- `personality`: 性格特质
- `user_goal`: 用户目标
- `work_responsibility`: 工作职责
- `working_habit_preference`: 工作习惯
- `interests`: 兴趣爱好
- `tendency`: 倾向

### 4. profile_mem_part2_prompts.py

**提示词**：
- `CONVERSATION_PROFILE_PART2_EXTRACTION_PROMPT`: 项目画像提取

**提取字段**：
- `projects_participated`: 参与项目（ProjectInfo 列表）

### 5. profile_mem_part3_prompts.py

**提示词**：
- `CONVERSATION_PROFILE_PART3_EXTRACTION_PROMPT`: 价值观系统提取

**提取字段**：
- `motivation_system`: 动机系统
- `fear_system`: 恐惧系统
- `value_system`: 价值观系统
- `humor_use`: 幽默使用
- `colloquialism`: 口语化表达

### 6. group_profile_prompts.py

**提示词**：
- `CONTENT_ANALYSIS_PROMPT`: 内容分析（话题、摘要、主题）
- `BEHAVIOR_ANALYSIS_PROMPT`: 行为分析（角色分配）

**输出格式**：
```json
{
  "topics": [{"topic": "...", "description": "...", "evidences": [...]}],
  "roles": {
    "技术负责人": [{"speaker": "alice", "evidences": [...], "confidence": "strong"}]
  },
  "summary": "...",
  "subject": "..."
}
```

### 7. semantic_mem_prompts.py

**提示词**：
- `get_semantic_generation_prompt()`: 语义记忆生成（函数）
- `get_group_semantic_generation_prompt()`: 群组语义记忆生成（函数）

**输出格式**：
```json
[
  {
    "content": "Alice is skilled in Python",
    "evidence": "Alice: I use Python daily",
    "start_time": "2024-11-01",
    "end_time": "2024-11-16"
  }
]
```

### 8. event_log_prompts.py

**提示词**：
- `EVENT_LOG_PROMPT`: 事件日志提取

**输出格式**：
```json
{
  "events": [
    {"time": "2024-11-16T10:00:00", "action": "discussed", "object": "project plan"}
  ]
}
```

### 9. profile_mem_prompts.py

**提示词**：
- `CONVERSATION_PROFILE_EXTRACTION_PROMPT`: 完整画像提取（一次性提取所有字段，已弃用，推荐使用 Part1/2/3）

### 10. profile_mem_evidence_completion_prompt.py

**提示词**：
- `CONVERSATION_PROFILE_EVIDENCE_COMPLETION_PROMPT`: 证据补全

### 11. group_profile_merge_prompts.py

**提示词**：
- Group Profile 合并相关提示词

## 依赖关系说明

### 对其他模块的依赖

**无外部依赖**（纯提示词文本）

### 被依赖关系

通过 Grep 验证：
```bash
grep -rn "from \.en\." src/memory_layer/prompts/__init__.py
```

**结果**：
- `memory_layer/prompts/__init__.py`: 当 `MEMORY_LANGUAGE=en` 时导入

**文档引用**：
- `specs/ac_mod/memory_layer.prompts.ac.mod.md`（父包）

## 可运行的测试命令

```bash
# 1. 验证导入
python -c "
from memory_layer.prompts.en import conv_prompts, episode_mem_prompts
print('✅ EN prompts loaded')
"

# 2. 验证提示词内容
python -c "
from memory_layer.prompts.en.conv_prompts import CONV_BOUNDARY_DETECTION_PROMPT
print(f'✅ CONV_BOUNDARY_DETECTION_PROMPT: {len(CONV_BOUNDARY_DETECTION_PROMPT)} chars')
"

# 3. 验证格式化
python -c "
from memory_layer.prompts.en.conv_prompts import CONV_BOUNDARY_DETECTION_PROMPT
prompt = CONV_BOUNDARY_DETECTION_PROMPT.format(
    conversation_history='test',
    time_gap_info='5 min',
    new_messages='hello'
)
print(f'✅ Formatted prompt: {len(prompt)} chars')
"
```

## 示例场景

### 场景 1: 对话边界检测

```python
from memory_layer.prompts.en.conv_prompts import CONV_BOUNDARY_DETECTION_PROMPT

prompt = CONV_BOUNDARY_DETECTION_PROMPT.format(
    conversation_history="Alice: Hi\nBob: Hello",
    time_gap_info="2 minutes",
    new_messages="Alice: How's the project?"
)

response = await llm_provider.generate(prompt, temperature=0.0)
result = json.loads(response)
# {"start_new_episode": false, "reason": "Continuation of greeting"}
```

### 场景 2: Profile 提取（分阶段）

```python
from memory_layer.prompts.en.profile_mem_part1_prompts import CONVERSATION_PROFILE_PART1_EXTRACTION_PROMPT

prompt = CONVERSATION_PROFILE_PART1_EXTRACTION_PROMPT.format(
    conversation_text="Alice: I'm a Python developer with 5 years experience",
    user_id="alice",
    existing_profile="{}"
)

response = await llm_provider.generate(prompt, temperature=0.3)
profile = json.loads(response)
# {"hard_skills": [{"value": "Python", "level": "高级", "evidences": [...]}], ...}
```

## 提示词工程最佳实践

**结构化约束**：
- JSON Schema 定义
- 明确字段类型
- 示例输出

**上下文优化**：
- 关键信息前置
- 限制上下文长度（4000 tokens）
- 使用分隔符（`---`, `###`）

**Few-shot 示例**：
- 2-3 个代表性示例
- 覆盖边界情况

**Temperature 设置**：
- 提取任务：0.0-0.3
- 生成任务：0.5-0.7

## 扩展阅读

- **父包文档**：`specs/ac_mod/memory_layer.prompts.ac.mod.md`
- **中文提示词**：`specs/ac_mod/memory_layer.prompts.zh.ac.mod.md`
- **Memory Extractors**：`specs/ac_mod/memory_layer.memory_extractor.ac.mod.md`

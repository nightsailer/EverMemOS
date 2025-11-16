# memory_layer.prompts.eval

评估场景提示词模板包，用于 A/B 测试、评估实验，与生产提示词（en/zh）隔离

## 模块位置

**源码路径**: `src/memory_layer/prompts/eval/`
**文档路径**: `specs/ac_mod/memory_layer.prompts.eval.ac.mod.md`
**模块类型**: 包模块

## 文件结构

```
src/memory_layer/prompts/eval/
├── __init__.py                 # 空文件
├── conv_prompts.py             # 对话处理评估
├── episode_mem_prompts.py      # Episode 记忆评估
├── event_log_prompts.py        # 事件日志评估
├── group_profile_prompts.py    # Group Profile 评估
├── email_prompts.py            # 邮件处理评估
└── linkdoc_prompts.py          # 文档链接评估
```

## 快速开始

```python
# 直接导入评估提示词（不受 MEMORY_LANGUAGE 影响）
from memory_layer.prompts.eval import (
    conv_prompts,
    episode_mem_prompts,
    email_prompts
)

# 使用评估版本
eval_prompt = conv_prompts.CONV_BOUNDARY_DETECTION_PROMPT
production_prompt = memory_layer.prompts.CONV_BOUNDARY_DETECTION_PROMPT

# A/B 测试
result_eval = await llm.generate(eval_prompt.format(...))
result_prod = await llm.generate(production_prompt.format(...))

# 对比结果
compare_results(result_eval, result_prod)
```

## 提示词模块详解

### 1. conv_prompts.py

**提示词**：
- `CONV_BOUNDARY_DETECTION_PROMPT`: 对话边界检测（评估版）

**用途**：
- 测试新的边界检测算法
- 对比不同 prompt 设计

### 2. episode_mem_prompts.py

**提示词**：
- `EPISODE_GENERATION_PROMPT`: Episode 生成（评估版）

**用途**：
- 评估不同 Episode 生成策略
- 测试上下文长度影响

### 3. event_log_prompts.py

**提示词**：
- `EVENT_LOG_PROMPT`: 事件日志提取（评估版）

**用途**：
- 测试事件提取准确性
- 评估时间戳解析

### 4. group_profile_prompts.py

**提示词**：
- Group Profile 相关评估提示词

**用途**：
- 评估角色分配准确性
- 测试话题提取效果

### 5. email_prompts.py

**提示词**：
- 邮件处理相关提示词

**用途**：
- 评估邮件内容提取
- 测试邮件分类

### 6. linkdoc_prompts.py

**提示词**：
- 文档链接处理提示词

**用途**：
- 评估文档理解能力
- 测试链接提取

## 使用场景

### 场景 1: A/B 测试

```python
from memory_layer.prompts import CONV_BOUNDARY_DETECTION_PROMPT as PROD_PROMPT
from memory_layer.prompts.eval.conv_prompts import CONV_BOUNDARY_DETECTION_PROMPT as EVAL_PROMPT

async def ab_test(conversation_data):
    # 生产版本
    prod_result = await llm.generate(PROD_PROMPT.format(**conversation_data))

    # 评估版本
    eval_result = await llm.generate(EVAL_PROMPT.format(**conversation_data))

    # 对比
    return {
        "prod": prod_result,
        "eval": eval_result,
        "accuracy_prod": evaluate_accuracy(prod_result),
        "accuracy_eval": evaluate_accuracy(eval_result)
    }
```

### 场景 2: 批量评估

```python
from memory_layer.prompts.eval import episode_mem_prompts

test_cases = load_test_cases()  # 加载测试数据

results = []
for case in test_cases:
    prompt = episode_mem_prompts.EPISODE_GENERATION_PROMPT.format(
        conversation_text=case["text"],
        custom_instructions=""
    )

    result = await llm.generate(prompt)
    results.append({
        "case_id": case["id"],
        "result": result,
        "ground_truth": case["expected"],
        "score": calculate_score(result, case["expected"])
    })

# 统计评估结果
avg_score = sum(r["score"] for r in results) / len(results)
```

### 场景 3: 新功能测试

```python
from memory_layer.prompts.eval.email_prompts import EMAIL_PARSING_PROMPT

# 测试新的邮件解析功能
email_data = {
    "subject": "Project Update",
    "body": "...",
    "sender": "alice@example.com"
}

prompt = EMAIL_PARSING_PROMPT.format(**email_data)
result = await llm.generate(prompt)

# 验证结果
assert "subject" in result
assert "sender" in result
```

## 评估最佳实践

**测试数据准备**：
- 准备多样化测试集
- 包含边界情况
- 标注真实标签

**评估指标**：
- 准确率（Accuracy）
- 召回率（Recall）
- F1 分数
- 成本（Token 消耗）

**版本管理**：
- 使用 Git 跟踪提示词变更
- 记录评估结果
- 保留历史版本

**隔离原则**：
- eval 提示词不影响生产
- 独立测试环境
- 避免交叉污染

## 依赖关系说明

### 对其他模块的依赖

**无外部依赖**（纯提示词文本）

### 被依赖关系

**独立使用**（不被生产代码依赖）

**文档引用**：
- `specs/ac_mod/memory_layer.prompts.ac.mod.md`（父包）

## 可运行的测试命令

```bash
# 1. 验证导入
python -c "
from memory_layer.prompts.eval import conv_prompts, episode_mem_prompts
print('✅ Eval prompts loaded')
"

# 2. 验证独立性（不受 MEMORY_LANGUAGE 影响）
export MEMORY_LANGUAGE=zh
python -c "
from memory_layer.prompts.eval.conv_prompts import CONV_BOUNDARY_DETECTION_PROMPT
print(f'✅ Eval prompt (independent): {len(CONV_BOUNDARY_DETECTION_PROMPT)} chars')
"

# 3. 对比生产版本
python -c "
from memory_layer.prompts import EPISODE_GENERATION_PROMPT as PROD
from memory_layer.prompts.eval.episode_mem_prompts import EPISODE_GENERATION_PROMPT as EVAL
print(f'✅ Prod: {len(PROD)} chars, Eval: {len(EVAL)} chars')
"
```

## 扩展阅读

- **父包文档**：`specs/ac_mod/memory_layer.prompts.ac.mod.md`
- **英文提示词**：`specs/ac_mod/memory_layer.prompts.en.ac.mod.md`
- **中文提示词**：`specs/ac_mod/memory_layer.prompts.zh.ac.mod.md`

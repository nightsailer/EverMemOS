# core.observation.tracing

追踪日志装饰器，为方法自动添加执行追踪日志（开始、结束、耗时、参数、结果）

## 模块位置

**源码路径**: `src/core/observation/tracing/`
**文档路径**: `specs/ac_mod/core.observation.tracing.ac.mod.md`
**模块类型**: 包模块

## 目录结构

```
src/core/observation/tracing/
├── __init__.py
└── decorators.py                   # 追踪装饰器
```

## 快速开始

### 基本使用

```python
from core.observation.tracing.decorators import trace_logger

@trace_logger(operation_name="用户查询")
async def get_user(user_id: int):
    # 业务逻辑
    return {"id": user_id, "name": "Alice"}

# 调用后自动记录：
# [trace] 用户查询 - 开始处理
# [trace] 用户查询 - 处理完成 (耗时: 15.32ms)
```

### 记录参数和结果

```python
@trace_logger(
    operation_name="创建订单",
    include_args=True,
    include_result=True,
    log_level="info"
)
async def create_order(user_id: int, amount: float):
    return {"order_id": "123", "amount": amount}

# 输出：
# [trace] 创建订单 - 开始处理 | 参数: (user_id=1, amount=99.9)
# [trace] 创建订单 - 处理完成 (耗时: 25ms) | 结果: {'order_id': '123', 'amount': 99.9}
```

### 同步函数支持

```python
@trace_logger(operation_name="同步计算")
def calculate_sum(a: int, b: int):
    return a + b

# 同时支持异步和同步函数
```

## 核心组件详解

### 1. @trace_logger装饰器

**功能**: 为函数添加追踪日志

**参数**:
- `operation_name`: 操作名称（可选），默认使用函数名
- `include_args`: 是否记录函数参数（默认False）
- `include_result`: 是否记录返回值（默认False）
- `log_level`: 日志级别（默认"debug"）
  - 可选: "debug", "info", "warning", "error"

**日志格式**:
```
[trace] {operation_name} - 开始处理 | 参数: {...}
[trace] {operation_name} - 处理完成 (耗时: {duration}ms) | 结果: {...}
[trace] {operation_name} - 处理失败 (耗时: {duration}ms) | 错误: {...}
```

### 2. 性能优化

**日志级别检查**:
- 装饰器会先检查日志级别是否启用
- 如果日志级别未启用，直接执行函数，避免性能损耗
- 不会计算耗时、格式化参数等

**示例**:
```python
# 如果logger.level > DEBUG，以下装饰器不会有任何性能开销
@trace_logger(log_level="debug")
async def high_frequency_function():
    pass
```

### 3. 异常处理

**异常追踪**:
- 捕获异常并记录错误日志
- 自动包含耗时信息
- 重新抛出原始异常

**日志输出**:
```python
@trace_logger()
async def risky_operation():
    raise ValueError("Something went wrong")

# 输出:
# [trace] risky_operation - 开始处理
# [trace] risky_operation - 处理失败 (耗时: 2ms) | 错误: Something went wrong
# (异常被重新抛出)
```

### 4. 参数和结果格式化

**内部辅助函数**:
- `_format_args(args, kwargs)`: 格式化参数
- `_format_result(result)`: 格式化结果
- `_is_log_level_enabled(logger, level)`: 检查日志级别
- `_log_message(logger, level, message)`: 记录日志

## Mermaid 依赖图

```mermaid
graph TB
    TraceLogger[@trace_logger<br/>追踪装饰器]
    Logging[logging<br/>Python日志]

    TraceLogger --> Logging

    classDef coreClass fill:#e1f5fe,stroke:#0277bd,stroke-width:2px
    classDef depClass fill:#f3e5f5,stroke:#7b1fa2,stroke-width:1px

    class TraceLogger coreClass
    class Logging depClass
```

## 依赖关系说明

### 对其他模块的依赖

- `logging` - Python标准日志库
- `functools` - wraps装饰器
- `time` - 时间测量

### 被依赖关系

- 业务逻辑模块（需要追踪的函数）
- Service层
- Repository层

## 可以验证模块可运行的测试命令

```bash
# 检查模块导入
python -c "from core.observation.tracing.decorators import trace_logger; print('OK')"

# 测试追踪功能
python -c "
import asyncio
import logging
from core.observation.tracing.decorators import trace_logger

logging.basicConfig(level=logging.DEBUG)

@trace_logger(operation_name='测试操作', include_args=True, include_result=True)
async def test_func(x, y):
    return x + y

async def main():
    result = await test_func(10, 20)
    print('结果:', result)

asyncio.run(main())
"

# 运行测试
pytest src/ -v -k tracing
```

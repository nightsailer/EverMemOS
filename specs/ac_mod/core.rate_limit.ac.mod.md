# core.rate_limit

基于aiolimiter的异步限流装饰器，支持函数级别请求频率控制

## 模块位置

**源码路径**: `src/core/rate_limit/`
**文档路径**: `specs/ac_mod/core.rate_limit.ac.mod.md`
**模块类型**: 包模块

## 目录结构

```
src/core/rate_limit/
├── __init__.py
└── rate_limiter.py                 # 限流装饰器和管理器
```

## 快速开始

### 基本使用

```python
from core.rate_limit.rate_limiter import rate_limit

# 全局限流：3次/10秒
@rate_limit(max_rate=3, time_period=10)
async def api_call():
    print("API调用")
    return {"status": "ok"}

# 调用
await api_call()  # 正常执行
await api_call()  # 正常执行
await api_call()  # 正常执行
await api_call()  # 等待直到窗口刷新
```

### 用户级别限流

```python
# 为不同用户单独限流
@rate_limit(
    max_rate=5,
    time_period=60,
    key_func=lambda user_id: f"user_{user_id}"
)
async def user_action(user_id: str):
    print(f"用户 {user_id} 执行操作")

# 每个用户有独立的限流计数
await user_action("alice")  # Alice的计数
await user_action("bob")    # Bob的计数
```

### 复杂key函数

```python
# 基于多个参数生成限流key
@rate_limit(
    max_rate=10,
    time_period=60,
    key_func=lambda user_id, resource_type: f"{user_id}_{resource_type}"
)
async def access_resource(user_id: str, resource_type: str):
    pass
```

## 核心组件详解

### 1. @rate_limit装饰器

**功能**: 异步函数限流装饰器

**参数**:
- `max_rate`: 时间窗口内允许的最大请求数（默认3）
- `time_period`: 时间窗口大小，秒（默认10）
- `key_func`: 可选，键函数，用于为不同参数生成不同的限流键

**工作原理**:
1. 根据key_func生成限流器标识
2. 获取或创建对应的AsyncLimiter实例
3. 调用前等待限流器许可
4. 执行函数

### 2. RateLimitManager

**功能**: 限流器管理器

**主要方法**:
- `get_limiter(key, max_rate, time_period)`: 获取或创建限流器

**特性**:
- 单例模式（全局_rate_limit_manager实例）
- 缓存限流器实例
- 自动管理多个限流器

### 3. 限流策略

**时间窗口**:
- 滑动窗口算法
- 基于aiolimiter实现

**等待行为**:
- 超过限流时自动等待
- 无超时机制（会一直等待）

## Mermaid 依赖图

```mermaid
graph TB
    RateLimitDecorator[@rate_limit<br/>限流装饰器]
    RateLimitManager[RateLimitManager<br/>限流管理器]
    AsyncLimiter[AsyncLimiter<br/>aiolimiter]

    RateLimitDecorator --> RateLimitManager
    RateLimitManager --> AsyncLimiter

    classDef coreClass fill:#e1f5fe,stroke:#0277bd,stroke-width:2px
    classDef depClass fill:#f3e5f5,stroke:#7b1fa2,stroke-width:1px

    class RateLimitDecorator,RateLimitManager coreClass
    class AsyncLimiter depClass
```

## 依赖关系说明

### 对其他模块的依赖

- `aiolimiter` - AsyncLimiter限流库
- `functools` - wraps装饰器

### 被依赖关系

- API接口模块
- 外部服务调用模块

## 可以验证模块可运行的测试命令

```bash
# 检查模块导入
python -c "from core.rate_limit.rate_limiter import rate_limit; print('OK')"

# 测试限流功能
python -c "
import asyncio
from core.rate_limit.rate_limiter import rate_limit

@rate_limit(max_rate=2, time_period=5)
async def test():
    print('Call')

async def main():
    await test()
    await test()
    print('第3次调用会等待')
    await test()

asyncio.run(main())
"

# 运行测试
pytest src/ -v -k rate_limit
```

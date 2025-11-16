# core.asynctasks

基于ARQ的异步任务管理器，支持任务队列、重试、超时和用户上下文传递

## 模块位置

**源码路径**: `src/core/asynctasks/`
**文档路径**: `specs/ac_mod/core.asynctasks.ac.mod.md`
**模块类型**: 包模块

## 目录结构

```
src/core/asynctasks/
├── __init__.py
├── task_manager.py                 # 任务管理器
└── examples/
    └── hello_word_job.py          # 示例任务
```

## 快速开始

### 基本使用

```python
from core.asynctasks.task_manager import TaskManager, task, RetryConfig
from core.di import get_bean_by_type

# 定义任务
@task(
    name="send_email",
    timeout=30.0,
    retry_config=RetryConfig(max_retries=3, retry_delay=2.0)
)
async def send_email_task(email: str, subject: str):
    # 任务逻辑
    print(f"发送邮件到 {email}: {subject}")
    return {"status": "sent"}

# 提交任务
task_manager = get_bean_by_type(TaskManager)
task_id = await task_manager.enqueue("send_email", email="user@example.com", subject="Hello")

# 查询任务状态
result = await task_manager.get_task_result(task_id)
print(result.status, result.result)
```

### 自动发现任务

```python
# 任务自动从指定包中发现
# 在TaskManager初始化时配置
task_manager = TaskManager(
    redis_settings=redis_settings,
    task_packages=["tasks", "jobs"]  # 扫描这些包中的@task装饰器
)
```

## 核心组件详解

### 1. TaskManager

**功能**: 异步任务管理器，基于ARQ实现

**初始化参数**:
- `redis_settings`: Redis连接配置
- `task_packages`: 任务包列表，自动扫描任务

**主要方法**:
- `enqueue(task_name, *args, **kwargs)`: 提交任务到队列
- `get_task_result(task_id)`: 查询任务结果
- `register_task(task_func, ...)`: 注册任务函数
- `start_worker()`: 启动任务Worker

### 2. @task装饰器

**功能**: 声明异步任务

**参数**:
- `name`: 任务名称（必填）
- `timeout`: 超时时间（秒）
- `retry_config`: 重试配置

**特性**:
- 自动传递用户上下文
- 支持异步函数
- ARQ兼容

### 3. TaskStatus枚举

```python
class TaskStatus(Enum):
    PENDING = "pending"       # 等待执行
    RUNNING = "running"       # 正在执行
    SUCCESS = "success"       # 执行成功
    FAILED = "failed"         # 执行失败
    CANCELLED = "cancelled"   # 已取消
```

### 4. RetryConfig

**重试配置**:
- `max_retries`: 最大重试次数
- `retry_delay`: 重试延迟（秒）
- `exponential_backoff`: 指数退避
- `max_retry_delay`: 最大重试延迟

### 5. TaskResult

**任务结果数据类**:
- `task_id`: 任务ID
- `status`: 任务状态
- `result`: 返回值
- `error`: 错误信息
- `created_at/started_at/finished_at`: 时间戳
- `user_context`: 用户上下文

## Mermaid 依赖图

```mermaid
graph TB
    TaskManager[TaskManager<br/>任务管理器]
    TaskDecorator[@task<br/>任务装饰器]
    ARQ[ARQ<br/>任务队列]

    Context[core.context]
    DI[core.di]
    Redis[Redis]

    TaskManager --> TaskDecorator
    TaskManager --> ARQ
    TaskManager --> Context
    TaskManager --> DI
    ARQ --> Redis

    classDef coreClass fill:#e1f5fe,stroke:#0277bd,stroke-width:2px
    classDef depClass fill:#f3e5f5,stroke:#7b1fa2,stroke-width:1px

    class TaskManager,TaskDecorator coreClass
    class ARQ,Context,DI,Redis depClass
```

## 依赖关系说明

### 对其他模块的依赖

- `arq` - 异步任务队列库
- `core.context.context` - 用户上下文管理
- `core.context.context_manager` - 上下文管理器
- `core.di` - 依赖注入
- `specs/ac_mod/core.observation.logging.ac.mod.md` - 日志
- `core.authorize.enums` - 角色枚举

### 被依赖关系

- 应用层任务定义模块
- 后台作业处理模块

## 可以验证模块可运行的测试命令

```bash
# 检查模块导入
python -c "from core.asynctasks.task_manager import TaskManager, task; print('OK')"

# 运行示例任务
python -m core.asynctasks.examples.hello_word_job

# 运行测试
pytest src/ -v -k asynctasks
```

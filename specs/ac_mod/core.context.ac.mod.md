# core.context

基于Python contextvars的异步上下文管理，提供数据库会话、用户信息、应用信息的跨异步调用传递。

## 模块位置

**源码路径**: `src/core/context/`
**文档路径**: `specs/ac_mod/core.context.ac.mod.md`
**模块类型**: 包模块

## 目录结构

```
src/core/context/
├── __init__.py                 # 包初始化（空）
├── context.py                  # 上下文变量定义及基础操作函数
└── context_manager.py          # 管理器类和装饰器实现
```

## 快速开始

### 基本使用 - 数据库会话

```python
from core.context.context_manager import with_database_session
from core.context.context import get_current_session

@with_database_session(auto_commit=True)
async def create_user(name: str):
    session = get_current_session()
    # 使用session进行数据库操作
    # 函数结束自动提交或回滚
    pass
```

### 基本使用 - 用户上下文

```python
from core.context.context_manager import with_user_context
from core.context.context import get_current_user_info

@with_user_context()
async def get_user_profile():
    user_info = get_current_user_info()
    user_id = user_info['user_id']
    return user_id
```

### 基本使用 - 完整上下文

```python
from core.context.context_manager import with_full_context

@with_full_context(auto_commit=True)
async def process_order():
    # 同时拥有数据库会话和用户信息
    session = get_current_session()
    user_info = get_current_user_info()
    # 业务逻辑
    pass
```

### 管理器方式使用

```python
from core.di.utils import get_bean_by_type
from core.context.context_manager import ContextManager

async def example():
    ctx_mgr = get_bean_by_type(ContextManager)

    # 方式1：使用完整上下文运行函数
    result = await ctx_mgr.run_with_full_context(
        my_func,
        user_data={'user_id': 123},
        auto_commit=True
    )

    # 方式2：仅使用数据库会话
    result = await ctx_mgr.run_with_database_only(
        my_func,
        force_new_session=True
    )
```

## 核心组件详解

### 1. 上下文变量（context.py）

**ContextVar 定义**:
- `db_session_context`: 存储AsyncSession数据库会话
- `user_info_context`: 存储用户信息字典
- `app_info_context`: 存储应用信息（如task_id）

**基础函数**:
- `get_current_session()`: 获取当前数据库会话，未设置抛RuntimeError
- `set_current_session(session)`: 设置会话，返回Token
- `clear_current_session(token)`: 清除会话
- `get_current_user_info()`: 获取用户信息，返回Optional[UserInfo]
- `set_current_user_info(user_info)`: 设置用户信息
- `get_current_app_info()`: 获取应用信息
- `set_current_app_info(app_info)`: 设置应用信息

### 2. DatabaseSessionManager

**功能**: 管理数据库会话生命周期

**主要方法**:
- `run_with_session(func, *args, session=None, auto_commit=True, force_new_session=False, **kwargs)`
  - 优先使用传入session，次选当前上下文session，最后创建新session
  - force_new_session=True 强制创建新会话（避免并发冲突）
  - auto_commit=True 成功时自动提交，失败自动回滚
  - 自动管理会话的创建、设置、提交、回滚、清理、关闭

### 3. UserContextManager

**功能**: 管理用户上下文

**主要方法**:
- `run_with_user_context(func, *args, user_data=None, auto_inherit=True, **kwargs)`
  - auto_inherit=True 自动继承当前用户上下文
  - 自动设置和清理用户上下文

### 4. ContextManager

**功能**: 组合DB会话和用户上下文的综合管理器

**主要方法**:
- `run_with_full_context()`: 同时提供数据库会话和用户上下文
- `run_with_database_only()`: 仅提供数据库会话
- `run_with_user_only()`: 仅提供用户上下文
- `copy_current_context()`: 复制当前上下文副本
- `get_current_context_data()`: 获取当前上下文数据快照

### 5. 装饰器

**@with_full_context(user_data=None, session=None, auto_commit=True, auto_inherit_user=True)**
- 为异步函数注入完整上下文

**@with_database_session(session=None, auto_commit=True, force_new_session=False)**
- 为异步函数注入数据库会话

**@with_user_context(user_data=None, auto_inherit=True)**
- 为异步函数注入用户上下文

## Mermaid 依赖图

```mermaid
graph TB
    subgraph 核心上下文
        CV[ContextVar变量<br/>db_session/user_info/app_info]
        CF[上下文函数<br/>get/set/clear]
    end

    subgraph 管理器层
        DSM[DatabaseSessionManager<br/>会话生命周期管理]
        UCM[UserContextManager<br/>用户上下文管理]
        CM[ContextManager<br/>综合管理器]
    end

    subgraph 装饰器层
        WDB[@with_database_session]
        WUC[@with_user_context]
        WFC[@with_full_context]
    end

    subgraph 使用层
        MW[Middleware<br/>请求级上下文]
        SVC[Service<br/>业务逻辑]
        AUD[AuditBase<br/>审计跟踪]
    end

    CV --> CF
    CF --> DSM
    CF --> UCM
    DSM --> CM
    UCM --> CM
    CM --> WDB
    CM --> WUC
    CM --> WFC
    WDB --> SVC
    WUC --> SVC
    WFC --> SVC
    CF --> MW
    MW --> SVC
    SVC --> AUD

    classDef coreClass fill:#e1f5fe,stroke:#0277bd,stroke-width:2px
    classDef mgrClass fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    classDef decClass fill:#fff3e0,stroke:#e65100,stroke-width:2px
    classDef useClass fill:#e8f5e9,stroke:#2e7d32,stroke-width:1px

    class CV,CF coreClass
    class DSM,UCM,CM mgrClass
    class WDB,WUC,WFC decClass
    class MW,SVC,AUD useClass
```

## 依赖关系说明

### 对其他模块的依赖

**直接依赖**:
- `component.database_session_provider.DatabaseSessionProvider` - 数据库会话提供者
- `specs/ac_mod/core.di.ac.mod.md` - DI容器（@component装饰器、get_bean_by_type）
- `core.observation.logger` - 日志记录

**标准库依赖**:
- `contextvars` - Python上下文变量支持
- `sqlmodel.ext.asyncio.session.AsyncSession` - 异步数据库会话

### 被依赖关系

**中间件层**:
- `src/core/middleware/database_session_middleware.py` - 导入 set/get/clear_current_session
- `src/core/middleware/user_context_middleware.py` - 导入用户上下文函数
- `src/core/middleware/app_context_middleware.py` - 导入应用上下文函数
- `src/core/middleware/hmac_signature_middleware.py` - 使用上下文

**业务层**:
- `src/core/oxm/pg/audit_base.py` - 导入 get_current_user_info 用于审计字段
- `src/core/authorize/decorators.py` - 导入 get_current_user_info 用于权限验证
- `src/core/asynctasks/task_manager.py` - 导入 ContextManager 用于异步任务
- `src/manage.py` - 导入 ContextManager 用于应用管理

**使用场景**:
1. **HTTP请求处理**: Middleware设置会话和用户上下文，业务代码直接获取
2. **审计跟踪**: AuditBase自动从上下文获取user_id填充created_by/updated_by
3. **权限控制**: authorize装饰器从上下文获取用户信息进行权限验证
4. **异步任务**: 任务执行时携带上下文信息

## 可以验证模块可运行的测试命令

```bash
# 检查模块导入
python -c "from core.context.context import get_current_session, get_current_user_info; print('✅ context.py')"

python -c "from core.context.context_manager import ContextManager, with_database_session; print('✅ context_manager.py')"

# 交互式测试上下文变量
python -c "
from core.context.context import set_current_user_info, get_current_user_info
token = set_current_user_info({'user_id': 123})
info = get_current_user_info()
assert info['user_id'] == 123
print('✅ ContextVar 设置和获取正常')
"

# 如果有pytest测试
pytest src/core/context/tests -v
```

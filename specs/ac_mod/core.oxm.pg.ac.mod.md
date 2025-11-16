# core.oxm.pg

PostgreSQL ORM 模块，基于 SQLModel 提供审计字段自动填充和软删除功能

## 模块位置

**源码路径**: `src/core/oxm/pg/`
**文档路径**: `specs/ac_mod/core.oxm.pg.ac.mod.md`
**模块类型**: 包模块

## 目录结构

```
src/core/oxm/pg/
├── __init__.py               # 包初始化
├── audit_base.py            # 审计基类（时间戳/用户追踪）
└── base_repository.py       # 仓储基类（软删除接口）
```

## 快速开始

### 基本使用

```python
from sqlmodel import SQLModel, Field
from core.oxm.pg.audit_base import get_auditable_model
from core.oxm.pg.base_repository import BaseSoftDeleteRepository

# 1. 定义审计模型
AuditableModel = get_auditable_model()

class User(AuditableModel, table=True):
    __tablename__ = "users"

    id: int = Field(primary_key=True)
    name: str
    email: str
    # created_at/updated_at/created_by/updated_by 自动继承

# 2. 定义仓储接口
class UserRepository(BaseSoftDeleteRepository[User]):
    async def add(self, entity: User) -> User:
        # 实现具体逻辑
        pass

    async def get(self, entity_id: int, include_deleted: bool = False) -> User:
        pass

# 3. 使用（审计字段自动填充）
user = User(id=1, name="Alice", email="alice@example.com")
# 插入时自动设置：
# - created_at = 当前时区时间
# - updated_at = 当前时区时间
# - created_by = 当前用户 ID（从上下文获取）
# - updated_by = 当前用户 ID

# 更新时自动设置：
# - updated_at = 当前时区时间
# - updated_by = 当前用户 ID

# 软删除
user.soft_delete(deleted_by="admin")
# 设置 deleted_at = 当前时区时间
# 设置 deleted_by = "admin"
```

### 事件监听器机制

```python
# 审计字段由 SQLAlchemy 事件监听器自动填充
# before_insert: 设置 created_at, created_by, updated_at, updated_by
# before_update: 设置 updated_at, updated_by, deleted_at, deleted_by

from sqlmodel import Session

with Session(engine) as session:
    user = User(name="Bob", email="bob@example.com")
    session.add(user)
    session.commit()
    # ✅ user.created_at 已自动填充
    # ✅ user.created_by 已自动填充（来自 core.context.context）

    user.name = "Bobby"
    session.add(user)
    session.commit()
    # ✅ user.updated_at 已自动更新
    # ✅ user.updated_by 已自动更新
```

## 核心组件详解

### 1. audit_base.py - 审计模型工厂

**核心函数**: `get_auditable_model() -> SQLModel`

**功能**:
- 工厂函数，返回带审计字段的 SQLModel 基类
- 注册 SQLAlchemy 事件监听器（before_insert/before_update）
- 自动填充时间戳（使用 `common_utils.datetime_utils.get_now_with_timezone()`）
- 自动填充操作用户（从 `core.context.context.get_current_user_info()` 获取）

**审计字段**:
| 字段 | 类型 | 说明 | 填充时机 |
|------|------|------|---------|
| created_at | datetime | 创建时间 | INSERT 时自动填充 |
| updated_at | datetime | 更新时间 | INSERT/UPDATE 时自动填充 |
| deleted_at | datetime | 删除时间 | 软删除时填充 |
| created_by | str | 创建者 | INSERT 时自动填充 |
| updated_by | str | 更新者 | INSERT/UPDATE 时自动填充 |
| deleted_by | str | 删除者 | 软删除时填充 |

**方法**:
- `soft_delete(deleted_by: str)`: 软删除记录
- `restore(restored_by: str)`: 恢复软删除记录
- `is_deleted` 属性: 检查是否已软删除

**事件监听器**:
```python
@event.listens_for(AuditableModel, 'before_insert', propagate=True)
def before_insert_listener(mapper, connection, target):
    target.created_at = get_now_with_timezone()
    target.created_by = get_current_user_id() or "system"
    target.updated_at = get_now_with_timezone()
    target.updated_by = get_current_user_id() or "system"

@event.listens_for(AuditableModel, 'before_update', propagate=True)
def before_update_listener(mapper, connection, target):
    target.updated_at = get_now_with_timezone()
    if target.updated_by is None:
        target.updated_by = get_current_user_id() or "system"
    # 特殊处理软删除场景
    if target.deleted_at is not None and target.deleted_by is None:
        target.deleted_by = get_current_user_id() or "system"
```

### 2. base_repository.py - 软删除仓储接口

**核心类**: `BaseSoftDeleteRepository[T]`

**特性**:
- 泛型仓储接口（`T` 必须继承 AuditableModel）
- 纯业务接口，不包含技术实现细节
- 强制子类实现具体的数据库操作

**接口方法**:
| 方法 | 参数 | 返回值 | 说明 |
|------|------|--------|------|
| add | entity: T | T | 添加新实体 |
| get | entity_id: int, include_deleted: bool | Optional[T] | 获取实体（默认排除已删除） |
| get_all | include_deleted: bool | List[T] | 获取所有实体 |
| update | entity: T | T | 更新实体 |
| delete | entity_id: int, deleted_by: str | bool | 软删除实体 |
| restore | entity_id: int, restored_by: str | bool | 恢复软删除实体 |
| hard_delete | entity_id: int | bool | 硬删除实体（慎用） |
| count | include_deleted: bool | int | 统计实体数量 |

**使用示例**:
```python
from typing import List, Optional
from sqlmodel import Session, select
from core.di.decorators import repository

@repository
class UserRepositoryImpl(BaseSoftDeleteRepository[User]):
    def __init__(self, session: Session):
        self.session = session

    async def add(self, entity: User) -> User:
        self.session.add(entity)
        self.session.commit()
        self.session.refresh(entity)
        return entity

    async def get(self, entity_id: int, include_deleted: bool = False) -> Optional[User]:
        stmt = select(User).where(User.id == entity_id)
        if not include_deleted:
            stmt = stmt.where(User.deleted_at.is_(None))
        return self.session.exec(stmt).first()

    async def delete(self, entity_id: int, deleted_by: str = "system") -> bool:
        user = await self.get(entity_id)
        if user:
            user.soft_delete(deleted_by)
            self.session.add(user)
            self.session.commit()
            return True
        return False
```

## Mermaid 依赖图

```mermaid
graph TB
    subgraph pg["core.oxm.pg"]
        AUDIT[audit_base.py<br/>get_auditable_model工厂]
        REPO[base_repository.py<br/>BaseSoftDeleteRepository接口]
    end

    subgraph deps["依赖模块"]
        SQLMODEL[sqlmodel<br/>SQLModel基类]
        SQLALCHEMY[sqlalchemy<br/>事件监听器]
        CTX[core.context.context<br/>用户上下文]
        DT[common_utils.datetime_utils<br/>时区处理]
        DI[core.di.decorators<br/>@repository]
    end

    AUDIT --> SQLMODEL
    AUDIT --> SQLALCHEMY
    AUDIT --> CTX
    AUDIT --> DT
    REPO --> AUDIT
    REPO --> DI

    classDef coreClass fill:#e1f5fe,stroke:#0277bd,stroke-width:2px
    classDef depClass fill:#fff3e0,stroke:#e65100,stroke-width:1px

    class AUDIT,REPO coreClass
    class SQLMODEL,SQLALCHEMY,CTX,DT,DI depClass
```

## 依赖关系说明

### 对其他模块的依赖

**core 模块**:
- `core.context.context.get_current_user_info()` - 获取当前用户信息（audit_base.py:138）
- `core.observation.logger.get_logger()` - 日志记录（audit_base.py:8）
- `core.di.decorators.repository` - 仓储装饰器（base_repository.py:4）

**common 模块**:
- `common_utils.datetime_utils.get_now_with_timezone()` - 获取带时区的当前时间（audit_base.py:61）

**外部库**:
- `sqlmodel` - ORM 基础（Field, SQLModel）
- `sqlalchemy` - 事件监听器（Column, TIMESTAMP, event）

### 被依赖关系

通过 Grep 验证，未发现直接使用 `core.oxm.pg` 的代码（项目主要使用 MongoDB）

**潜在使用场景**:
- PostgreSQL 关系型数据存储
- 需要强审计功能的业务模块
- 需要软删除的场景

## 验证测试命令

```bash
# 验证模块导入
python -c "
from core.oxm.pg.audit_base import get_auditable_model
from core.oxm.pg.base_repository import BaseSoftDeleteRepository

# 创建审计模型
AuditModel = get_auditable_model()
print('✅ AuditModel 创建成功')

# 检查字段
import inspect
fields = [f for f in dir(AuditModel) if not f.startswith('_')]
audit_fields = ['created_at', 'updated_at', 'deleted_at', 'created_by', 'updated_by', 'deleted_by']
assert all(f in fields for f in audit_fields), '❌ 审计字段缺失'
print('✅ 审计字段验证通过')

# 检查方法
methods = ['soft_delete', 'restore']
assert all(hasattr(AuditModel, m) for m in methods), '❌ 方法缺失'
print('✅ 方法验证通过')
"

# 验证依赖
cd /home/user/EverMemOS
grep -n "get_current_user_info" src/core/oxm/pg/audit_base.py
grep -n "get_now_with_timezone" src/core/oxm/pg/audit_base.py

# 搜索使用场景
grep -r "from core.oxm.pg" src --include="*.py"
grep -r "get_auditable_model" src --include="*.py"
```

## 最佳实践

### 1. 模型定义
```python
# ✅ 推荐：使用工厂函数
AuditableModel = get_auditable_model()

class MyModel(AuditableModel, table=True):
    __tablename__ = "my_table"
    id: int = Field(primary_key=True)
    # 其他字段

# ❌ 避免：不要手动定义审计字段
class BadModel(SQLModel, table=True):
    created_at: datetime  # 不会自动填充
```

### 2. 软删除
```python
# ✅ 推荐：使用 soft_delete 方法
user.soft_delete(deleted_by="admin")

# ❌ 避免：手动设置 deleted_at
user.deleted_at = datetime.now()  # 时区可能不正确
```

### 3. 查询已删除记录
```python
# ✅ 推荐：使用仓储接口的 include_deleted 参数
users = await repo.get_all(include_deleted=True)

# ✅ 或显式过滤
stmt = select(User).where(User.deleted_at.is_(None))
```

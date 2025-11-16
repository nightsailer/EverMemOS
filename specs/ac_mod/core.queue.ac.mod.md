# core.queue

Core 队列模块根包，提供消息队列管理功能。

## 模块位置

**源码路径**: `src/core/queue/`
**文档路径**: `specs/ac_mod/core.queue.ac.mod.md`
**模块类型**: 包模块

## 目录结构

```
src/core/queue/
├── __init__.py                              # 包初始化文件
├── msg_group_queue/                         # 消息分组队列子包（内存实现）
│   ├── __init__.py                          # 子包初始化
│   ├── msg_group_queue_manager.py           # 消息分组队列管理器
│   └── msg_group_queue_manager_factory.py   # 管理器工厂
└── redis_group_queue/                       # Redis分组队列子包
    ├── __init__.py                          # 子包初始化
    ├── redis_group_queue_item.py            # 队列项接口定义
    ├── kafka_consumer_record_item.py        # Kafka消费记录队列项
    ├── redis_group_queue_lua_scripts.py     # Lua脚本集合
    ├── redis_msg_group_queue_manager.py     # Redis消息分组队列管理器
    └── redis_msg_group_queue_manager_factory.py  # Redis管理器工厂
```

**注意**: 本文档保存在 `specs/ac_mod/` 目录下，不在包源码目录中。

## 快速开始

### 基本使用方式

```python
# === 使用内存消息分组队列 ===
from core.queue.msg_group_queue.msg_group_queue_manager_factory import MsgGroupQueueManagerFactory

# 创建工厂
factory = MsgGroupQueueManagerFactory()

# 获取默认管理器
manager = await factory.get_default_manager(auto_start=True)

# 投递消息
await manager.deliver_message("user_123", {"action": "login"})

# 获取消息
message = await manager.get_by_queue(queue_id=5, wait=True, timeout=1.0)
if message:
    group_key, data = message
    print(f"Group: {group_key}, Data: {data}")

# 获取统计信息
stats = await manager.get_manager_stats()
print(f"总消息: {stats['total_current_messages']}")

# === 使用 Redis 分组队列 ===
from core.queue.redis_group_queue.redis_msg_group_queue_manager_factory import RedisGroupQueueManagerFactory
from core.queue.redis_group_queue.redis_group_queue_item import SimpleQueueItem
from component.redis_provider import RedisProvider

# 创建工厂
redis_provider = RedisProvider()
redis_factory = RedisGroupQueueManagerFactory(redis_provider)

# 获取管理器
redis_manager = await redis_factory.get_manager_with_config(
    key_prefix="my_queue",
    max_total_messages=20000,
    auto_start=True
)

# 投递消息
item = SimpleQueueItem(data={"action": "process"}, item_type="task")
await redis_manager.deliver_message("task_group_1", item)

# 获取消息
messages = await redis_manager.get_messages(score_threshold=1000)
for msg in messages:
    print(f"数据: {msg.data}")

# 获取统计
stats = await redis_manager.get_stats(include_consumer_info=True)
print(f"总消息: {stats['total_current_messages']}")
print(f"活跃消费者: {stats['active_consumers_count']}")
```

### 子模块说明

- **msg_group_queue**: 基于内存的消息分组队列，使用 asyncio.Queue 实现，支持固定队列数量、哈希路由、统计监控
- **redis_group_queue**: 基于 Redis 的消息分组队列，使用 Redis Sorted Set 实现，支持固定分区、动态消费者管理、Lua 脚本原子操作

## 核心组件详解

### 1. msg_group_queue 子包 - 内存队列

**核心功能：**
- 固定数量队列（默认10个）
- 基于 group_key 哈希路由
- 最大消息数量限制
- 空队列优先投递策略
- wait/no-wait 模式消息获取
- 详细的统计和日志

**主要组件：**
- `MsgGroupQueueManager`: 消息分组队列管理器
- `MsgGroupQueueManagerFactory`: 管理器工厂，支持配置管理和实例缓存

**适用场景：**
- 进程内消息队列
- 轻量级任务分发
- 临时消息缓冲

详细文档参考: `specs/ac_mod/core.queue.msg_group_queue.ac.mod.md`

### 2. redis_group_queue 子包 - Redis 队列

**核心功能：**
- 固定 50 个分区（001-050）
- 基于 group_key 哈希路由到固定分区
- 多消费者并发消费，动态 owner 管理
- Redis ZSET 存储，支持按分数排序和时间过滤
- Lua 脚本保证原子性
- 支持 JSON 和 BSON 序列化

**主要组件：**
- `RedisGroupQueueItem`: 队列项接口定义
- `SimpleQueueItem`: 简单队列项实现
- `KafkaConsumerRecordItem`: Kafka 消费记录队列项
- `RedisGroupQueueManager`: Redis 消息分组队列管理器
- `RedisGroupQueueManagerFactory`: 管理器工厂

**适用场景：**
- 分布式消息队列
- Kafka 消费缓冲
- 持久化消息存储
- 多消费者协同处理

详细文档参考: `specs/ac_mod/core.queue.redis_group_queue.ac.mod.md`

## Mermaid 依赖图

```mermaid
graph TB
    Queue[core.queue<br/>队列根包]
    MsgGroupQueue[msg_group_queue<br/>内存消息队列]
    RedisGroupQueue[redis_group_queue<br/>Redis消息队列]

    subgraph "内存队列组件"
        MsgManager[MsgGroupQueueManager<br/>内存队列管理器]
        MsgFactory[MsgGroupQueueManagerFactory<br/>内存队列工厂]
    end

    subgraph "Redis队列组件"
        RedisManager[RedisGroupQueueManager<br/>Redis队列管理器]
        RedisFactory[RedisGroupQueueManagerFactory<br/>Redis队列工厂]
        QueueItem[RedisGroupQueueItem<br/>队列项接口]
        SimpleItem[SimpleQueueItem<br/>简单队列项]
        KafkaItem[KafkaConsumerRecordItem<br/>Kafka队列项]
        LuaScripts[Lua脚本集合<br/>原子操作]
    end

    Queue --> MsgGroupQueue
    Queue --> RedisGroupQueue

    MsgGroupQueue --> MsgManager
    MsgGroupQueue --> MsgFactory
    MsgFactory -->|创建| MsgManager

    RedisGroupQueue --> RedisManager
    RedisGroupQueue --> RedisFactory
    RedisGroupQueue --> QueueItem
    RedisFactory -->|创建| RedisManager
    RedisManager --> QueueItem
    RedisManager --> LuaScripts
    QueueItem <|-- SimpleItem
    QueueItem <|-- KafkaItem

    classDef coreClass fill:#e1f5fe,stroke:#0277bd,stroke-width:2px
    classDef subClass fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    classDef managerClass fill:#fff3e0,stroke:#f57c00,stroke-width:2px
    classDef factoryClass fill:#e8f5e9,stroke:#388e3c,stroke-width:2px
    classDef itemClass fill:#fce4ec,stroke:#c2185b,stroke-width:1px

    class Queue coreClass
    class MsgGroupQueue,RedisGroupQueue subClass
    class MsgManager,RedisManager managerClass
    class MsgFactory,RedisFactory factoryClass
    class QueueItem,SimpleItem,KafkaItem,LuaScripts itemClass
```

## 依赖关系说明

### 对其他模块的依赖

通过 Grep 验证:
```bash
grep -r "from component.redis_provider" src/core/queue/
# src/core/queue/redis_group_queue/redis_msg_group_queue_manager_factory.py

grep -r "from core.observation.logger" src/core/queue/
# src/core/queue/msg_group_queue/msg_group_queue_manager.py
# src/core/queue/msg_group_queue/msg_group_queue_manager_factory.py
# src/core/queue/redis_group_queue/redis_group_queue_item.py
# src/core/queue/redis_group_queue/kafka_consumer_record_item.py
# src/core/queue/redis_group_queue/redis_msg_group_queue_manager.py
# src/core/queue/redis_group_queue/redis_msg_group_queue_manager_factory.py
```

**msg_group_queue 依赖：**
- `core.observation.logger.get_logger`: 日志记录器
- `common_utils.datetime_utils`: 时间工具（get_now_with_timezone, to_iso_format）

**redis_group_queue 依赖：**
- `component.redis_provider.RedisProvider`: Redis 连接提供者
- `core.observation.logger.get_logger`: 日志记录器
- `common_utils.datetime_utils`: 时间工具
- `core.rate_limit.rate_limiter.rate_limit`: 限流装饰器

### 被依赖关系

通过 Grep 验证:
```bash
grep -r "from core.queue" src/ --include="*.py" | grep -v "src/core/queue/"
# （查找使用队列模块的其他模块）
```

目前无其他模块直接依赖（独立使用）。

## 对比：内存队列 vs Redis 队列

| 特性 | msg_group_queue | redis_group_queue |
|------|----------------|-------------------|
| 存储方式 | 内存 (asyncio.Queue) | Redis (ZSET) |
| 持久化 | 否 | 是 |
| 队列数量 | 可配置（默认10个） | 固定50个分区 |
| 最大消息数 | 可配置（默认100） | 可配置（默认20000） |
| 路由方式 | MD5 哈希取模 | MD5 哈希取模 |
| 消费模式 | 单进程多队列 | 多消费者动态分配 |
| 排序 | FIFO | 按 score 排序 |
| 统计监控 | 时间窗口统计 | 分区级统计 |
| 序列化 | 无需序列化 | JSON/BSON |
| 性能 | 极高（内存） | 高（网络） |
| 适用场景 | 进程内 | 分布式 |

## 可以验证模块可运行的测试命令

```bash
# 1. 验证内存队列导入
python -c "
from core.queue.msg_group_queue.msg_group_queue_manager import MsgGroupQueueManager
from core.queue.msg_group_queue.msg_group_queue_manager_factory import MsgGroupQueueManagerFactory
print('内存队列模块导入成功')
print(f'管理器: {MsgGroupQueueManager}')
print(f'工厂: {MsgGroupQueueManagerFactory}')
"

# 2. 验证 Redis 队列导入
python -c "
from core.queue.redis_group_queue import RedisGroupQueueItem, RedisGroupQueueManager
from core.queue.redis_group_queue.redis_group_queue_item import SimpleQueueItem
from core.queue.redis_group_queue.kafka_consumer_record_item import KafkaConsumerRecordItem
print('Redis队列模块导入成功')
print(f'队列项接口: {RedisGroupQueueItem}')
print(f'简单队列项: {SimpleQueueItem}')
print(f'Kafka队列项: {KafkaConsumerRecordItem}')
"

# 3. 验证 Lua 脚本
python -c "
from core.queue.redis_group_queue.redis_group_queue_lua_scripts import (
    ENQUEUE_SCRIPT,
    GET_MESSAGES_SCRIPT,
    REBALANCE_PARTITIONS_SCRIPT
)
print(f'入队脚本行数: {len(ENQUEUE_SCRIPT.splitlines())}')
print(f'获取消息脚本行数: {len(GET_MESSAGES_SCRIPT.splitlines())}')
print(f'重新分区脚本行数: {len(REBALANCE_PARTITIONS_SCRIPT.splitlines())}')
"

# 4. 测试内存队列基本功能
python -c "
import asyncio
from core.queue.msg_group_queue.msg_group_queue_manager import MsgGroupQueueManager

async def test():
    manager = MsgGroupQueueManager(name='test', num_queues=5, max_total_messages=50)

    # 投递消息
    success = await manager.deliver_message('group_1', {'data': 'test'})
    print(f'投递成功: {success}')

    # 获取统计
    stats = await manager.get_manager_stats()
    print(f'总消息: {stats[\"total_current_messages\"]}')
    print(f'总投递: {stats[\"total_delivered_messages\"]}')

asyncio.run(test())
"

# 5. 测试队列项序列化
python -c "
from core.queue.redis_group_queue.redis_group_queue_item import SimpleQueueItem
import json

# 创建队列项
item = SimpleQueueItem(data={'test': 'value'}, item_type='test')

# JSON 序列化
json_str = item.to_json_str()
print(f'JSON: {json_str}')

# 反序列化
restored = SimpleQueueItem.from_json_str(json_str)
print(f'反序列化: {restored.data}')

# BSON 序列化
bson_bytes = item.to_bson_bytes()
print(f'BSON 长度: {len(bson_bytes)}')

# BSON 反序列化
restored_bson = SimpleQueueItem.from_bson_bytes(bson_bytes)
print(f'BSON 反序列化: {restored_bson.data}')
"

# 6. 运行测试套件（如果存在）
pytest src/core/queue/ -v

# 7. 测试哈希路由
python -c "
import hashlib

def hash_route(group_key, num_queues):
    hash_obj = hashlib.md5(group_key.encode('utf-8'))
    hash_int = int(hash_obj.hexdigest(), 16)
    return hash_int % num_queues

# 测试路由分布
groups = [f'group_{i}' for i in range(100)]
distribution = {}
for group in groups:
    queue_id = hash_route(group, 10)
    distribution[queue_id] = distribution.get(queue_id, 0) + 1

print('路由分布:', distribution)
"
```

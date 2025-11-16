# core.queue.redis_group_queue

基于 Redis 实现的分布式消息分组队列，支持固定分区、动态消费者管理、Kafka 消费记录缓冲。

## 模块位置

**源码路径**: `src/core/queue/redis_group_queue/`
**文档路径**: `specs/ac_mod/core.queue.redis_group_queue.ac.mod.md`
**模块类型**: 包模块

## 目录结构

```
src/core/queue/redis_group_queue/
├── __init__.py                                  # 包导出
├── redis_group_queue_item.py                    # 队列项接口定义
├── kafka_consumer_record_item.py                # Kafka消费记录队列项
├── redis_group_queue_lua_scripts.py             # Lua脚本集合
├── redis_msg_group_queue_manager.py             # Redis消息分组队列管理器
└── redis_msg_group_queue_manager_factory.py     # 管理器工厂
```

## 快速开始

### 基本使用方式

```python
from core.queue.redis_group_queue.redis_msg_group_queue_manager_factory import RedisGroupQueueManagerFactory
from core.queue.redis_group_queue.redis_group_queue_item import SimpleQueueItem, SerializationMode
from component.redis_provider import RedisProvider

# === 1. 创建工厂 ===
redis_provider = RedisProvider()
factory = RedisGroupQueueManagerFactory(redis_provider)

# === 2. 获取管理器 ===
# 使用默认配置
manager = await factory.get_manager_with_config(
    key_prefix="my_queue",
    serialization_mode=SerializationMode.JSON,
    max_total_messages=20000,
    auto_start=True
)

# === 3. 投递消息 ===
# 创建队列项
item = SimpleQueueItem(
    data={"action": "process", "user_id": 123},
    item_type="task"
)

# 投递消息（基于 group_key 哈希路由到固定分区）
success = await manager.deliver_message("user_123", item)
print(f"投递成功: {success}")

# === 4. 消费消息 ===
# 获取消息（自动加入消费者，分配分区）
messages = await manager.get_messages(
    score_threshold=1000,  # score差值阈值（毫秒）
    current_score=None     # 当前score，默认使用当前时间
)

for msg in messages:
    print(f"消息类型: {msg.item_type}, 数据: {msg.data}")

# === 5. 消费者管理 ===
# 手动加入消费者（自动触发rebalance）
owner_count, assigned_partitions = await manager.join_consumer()
print(f"当前消费者数: {owner_count}")
print(f"分配的分区: {assigned_partitions}")

# 保活（建议每30秒调用一次）
success = await manager.keepalive_consumer()

# 退出消费者（自动触发rebalance）
await manager.exit_consumer()

# === 6. 获取统计信息 ===
# 获取管理器统计
stats = await manager.get_stats(
    include_partition_details=True,
    include_consumer_info=True
)
print(f"总消息: {stats['total_current_messages']}")
print(f"活跃消费者: {stats['active_consumers_count']}")
print(f"分区分配: {stats['partition_assignments']}")

# 获取特定队列统计
queue_stats = await manager.get_queue_stats("user_123")
print(f"队列大小: {queue_stats['current_size']}")

# === 7. 管理操作 ===
# 手动触发rebalance
owner_count, assigned = await manager.rebalance_partitions()

# 清理不活跃消费者（默认5分钟不活跃）
cleaned, remaining, assigned = await manager.cleanup_inactive_owners()
print(f"清理了{cleaned}个不活跃消费者")

# 强制清理和重置
await manager.force_cleanup_and_reset(purge_all=False)  # 仅清理消费者
await manager.force_cleanup_and_reset(purge_all=True)   # 清空所有队列（危险）

# === 8. 关闭管理器 ===
await manager.shutdown()
```

### 使用 Kafka 消费记录队列项

```python
from core.queue.redis_group_queue.kafka_consumer_record_item import (
    KafkaConsumerRecordItem,
    serialize_consumer_record_to_bson,
    deserialize_bson_to_consumer_record
)
from aiokafka import ConsumerRecord

# === 1. 序列化 Kafka 消费记录 ===
# 创建 Kafka 消费记录
kafka_record = ConsumerRecord(
    topic="test_topic",
    partition=0,
    offset=12345,
    timestamp=1700000000000,
    timestamp_type=0,
    key=b"user_123",
    value={"action": "login"},
    checksum=None,
    serialized_key_size=8,
    serialized_value_size=20,
    headers=[("trace_id", b"abc123")]
)

# 转换为队列项
queue_item = KafkaConsumerRecordItem(kafka_record)

# BSON 序列化
bson_bytes = queue_item.to_bson_bytes()
print(f"BSON 长度: {len(bson_bytes)}")

# === 2. 投递到 Redis 队列 ===
# 使用 BSON 序列化模式的管理器
manager = await factory.get_manager_with_config(
    key_prefix="kafka_buffer",
    serialization_mode=SerializationMode.BSON,
    item_class=KafkaConsumerRecordItem,
    auto_start=True
)

# 投递消息
await manager.deliver_message(
    group_key=f"{kafka_record.topic}_{kafka_record.partition}",
    item=queue_item
)

# === 3. 消费并恢复 Kafka 记录 ===
messages = await manager.get_messages(score_threshold=1000)
for kafka_item in messages:
    # 转换回 ConsumerRecord
    restored_record = kafka_item.to_consumer_record()
    print(f"Topic: {restored_record.topic}, Offset: {restored_record.offset}")
```

### 自定义队列项

```python
from core.queue.redis_group_queue.redis_group_queue_item import RedisGroupQueueItem
from typing import Dict, Any
import json

class CustomQueueItem(RedisGroupQueueItem):
    """自定义队列项"""

    def __init__(self, user_id: int, action: str, metadata: Dict):
        self.user_id = user_id
        self.action = action
        self.metadata = metadata

    def to_dict(self) -> Dict[str, Any]:
        return {
            "user_id": self.user_id,
            "action": self.action,
            "metadata": self.metadata
        }

    def to_json_str(self) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False)

    @classmethod
    def from_json_str(cls, json_str: str) -> 'CustomQueueItem':
        data = json.loads(json_str)
        return cls(
            user_id=data["user_id"],
            action=data["action"],
            metadata=data["metadata"]
        )

# 使用自定义队列项
manager = await factory.get_manager_with_config(
    key_prefix="custom_queue",
    item_class=CustomQueueItem,
    auto_start=True
)

item = CustomQueueItem(
    user_id=123,
    action="purchase",
    metadata={"amount": 100}
)
await manager.deliver_message("user_123", item)
```

## 核心组件详解

### 1. RedisGroupQueueItem - 队列项接口

**源码**: `redis_group_queue_item.py`

**接口定义：**
```python
class RedisGroupQueueItem(ABC):
    @abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        """将对象转换为字典"""

    @abstractmethod
    def from_json_str(cls, json_str: str) -> 'RedisGroupQueueItem':
        """从JSON字符串创建对象"""

    @abstractmethod
    def from_bson_bytes(cls, bson_bytes: bytes) -> 'RedisGroupQueueItem':
        """从BSON字节数据反序列化对象"""

    def to_json_str(self) -> str:
        """将对象转换为JSON字符串（默认实现）"""

    def to_bson_bytes(self) -> bytes:
        """将对象序列化为BSON字节数据（默认实现）"""
```

**SerializationMode - 序列化模式：**
```python
class SerializationMode(Enum):
    JSON = "json"  # JSON字符串序列化
    BSON = "bson"  # BSON字节序列化
```

**SimpleQueueItem - 简单队列项：**
```python
class SimpleQueueItem(RedisGroupQueueItem):
    def __init__(self, data: Any, item_type: str = "simple"):
        self.data = data
        self.item_type = item_type
```

### 2. KafkaConsumerRecordItem - Kafka 消费记录队列项

**源码**: `kafka_consumer_record_item.py`

**核心功能：**
- 实现 RedisGroupQueueItem 接口
- 提供 ConsumerRecord 的序列化/反序列化
- 使用 BSON 格式处理二进制数据
- 使用 Base64 编码处理 bytes 字段

**字段：**
```python
@dataclass
class KafkaConsumerRecordItem(RedisGroupQueueItem):
    topic: str
    partition: int
    offset: int
    timestamp: int
    timestamp_type: int
    key: Optional[str]          # Base64 编码
    value: Optional[Any]
    checksum: Optional[int]
    serialized_key_size: int
    serialized_value_size: int
    headers: Sequence[Tuple[str, bytes]]  # Base64 编码
```

**主要方法：**
```python
# 序列化
def to_bson_bytes(self) -> bytes

# 反序列化
@classmethod
def from_bson_bytes(cls, bson_bytes: bytes) -> 'KafkaConsumerRecordItem'

# 转换为 ConsumerRecord
def to_consumer_record(self) -> ConsumerRecord

# 便捷函数
serialize_consumer_record_to_bson(consumer_record: ConsumerRecord) -> bytes
deserialize_bson_to_consumer_record(bson_bytes: bytes) -> ConsumerRecord
```

### 3. RedisGroupQueueManager - Redis 消息分组队列管理器

**源码**: `redis_msg_group_queue_manager.py`

**核心特性：**
1. **固定 50 个分区**（001-050）⚠️ 不可修改
2. 基于 group_key 哈希路由到固定分区
3. 多消费者并发消费，基于 owner 机制防冲突
4. 使用 Redis Sorted Set (ZSET) 存储消息
5. 支持按分数排序和时间过滤
6. Lua 脚本保证原子性操作

**初始化参数：**
```python
RedisGroupQueueManager(
    redis_client,                           # Redis客户端
    key_prefix="default",                   # Redis键前缀
    serialization_mode=SerializationMode.JSON,  # 序列化模式
    item_class=None,                        # 队列项类型（默认SimpleQueueItem）
    sort_key_func=None,                     # 排序键生成函数
    max_total_messages=20000,               # 最大总消息数
    queue_expire_seconds=24*3600,           # 队列过期时间
    activity_expire_seconds=24*3600,        # 活动记录过期时间
    enable_metrics=True,                    # 是否启用统计
    log_interval_seconds=600,               # 日志间隔
    owner_expire_seconds=3600,              # owner过期时间
    inactive_threshold_seconds=300,         # 不活跃阈值
    cleanup_interval_seconds=300            # 清理间隔
)
```

**Redis 键设计：**
```python
# 分区队列键（50个）
{key_prefix}:queue:001
{key_prefix}:queue:002
...
{key_prefix}:queue:050

# Owner 活跃时间 ZSET
{key_prefix}:owner_activate_time_zset

# Owner 的队列列表
{key_prefix}:queue_list:{owner_id}

# 消息总数计数器
{key_prefix}:counter
```

**主要方法：**

**投递消息：**
```python
@rate_limit(max_rate=200, time_period=1)
async def deliver_message(
    group_key: str,
    item: RedisGroupQueueItem,
    return_mode: str = "normal",
    max_total_messages: int = None
) -> bool
```
- 基于 group_key 哈希路由到固定分区
- 使用 Lua 脚本原子性添加消息
- 检查总数限制
- 更新统计信息

**获取消息：**
```python
@rate_limit(max_rate=4, time_period=1, key_func=lambda owner_id: f"get_messages_{owner_id}")
async def get_messages(
    score_threshold: int,
    current_score: Optional[int] = None,
    owner_id: Optional[str] = None,
    _retry_depth: int = 2
) -> List[RedisGroupQueueItem]
```
- 遍历所有分配给该 owner 的分区
- 每个分区尝试获取 1 个消息
- 检查 score 差值阈值
- 按需 keepalive 机制（超过30秒触发）
- 自动加入消费者（JOIN_REQUIRED）

**消费者管理：**
```python
# 加入消费者（触发rebalance）
@rate_limit(max_rate=1, time_period=1)
async def join_consumer(owner_id: Optional[str] = None) -> Tuple[int, Dict[str, List[str]]]

# 退出消费者（触发rebalance）
@rate_limit(max_rate=1, time_period=1)
async def exit_consumer(owner_id: Optional[str] = None) -> Tuple[int, Dict[str, List[str]]]

# 保活（建议每30秒调用）
@rate_limit(max_rate=1, time_period=2)
async def keepalive_consumer(owner_id: Optional[str] = None) -> bool

# Rebalance重新分区
@rate_limit(max_rate=1, time_period=1)
async def rebalance_partitions() -> Tuple[int, Dict[str, List[str]]]

# 清理不活跃消费者（默认5分钟）
@rate_limit(max_rate=1, time_period=5)
async def cleanup_inactive_owners() -> Tuple[int, int, Dict[str, List[str]]]

# 强制清理和重置
@rate_limit(max_rate=1, time_period=5)
async def force_cleanup_and_reset(purge_all: bool = False) -> int
```

**统计信息：**
```python
@rate_limit(max_rate=1, time_period=5)
async def get_stats(
    group_key: Optional[str] = None,
    include_all_partitions: bool = False,
    include_partition_details: bool = False,
    include_consumer_info: bool = False
) -> Dict[str, Any]
```

### 4. Lua 脚本集合

**源码**: `redis_group_queue_lua_scripts.py`

**核心脚本：**

**ENQUEUE_SCRIPT** - 入队脚本：
- 检查总数限制
- 原子性添加消息到 ZSET
- 更新计数器和过期时间

**GET_MESSAGES_SCRIPT** - 获取消息脚本：
- 检查 owner 是否存在
- 获取 owner 的队列列表
- 遍历分区获取消息
- 检查 score 差值阈值
- 使用 ZPOPMIN 删除消息
- 更新计数器

**REBALANCE_PARTITIONS_SCRIPT** - 重新分区脚本：
- 获取所有活跃 owner
- 清理所有 owner 的 queue_list
- 平均分配分区给 owner
- 设置过期时间

**JOIN_CONSUMER_SCRIPT** - 加入消费者脚本：
- 加入 owner_activate_time_zset
- 调用 rebalance 函数

**EXIT_CONSUMER_SCRIPT** - 退出消费者脚本：
- 从 owner_activate_time_zset 删除
- 删除对应的 queue_list
- 如果还有剩余 owner，调用 rebalance

**KEEPALIVE_CONSUMER_SCRIPT** - 保活脚本：
- 更新 owner_activate_time_zset 的时间
- 续期 queue_list

**CLEANUP_INACTIVE_OWNERS_SCRIPT** - 清理不活跃 owner 脚本：
- 查找不活跃的 owner（5分钟前）
- 删除 owner 和 queue_list
- 重算 counter 确保数据一致性
- 如果有清理，调用 rebalance

**FORCE_CLEANUP_SCRIPT** - 强制清理脚本：
- 删除所有 owner 的 queue_list
- 删除 owner_activate_time_zset
- purge_all=True: 清空所有分区队列
- purge_all=False: 仅重算计数器

**GET_QUEUE_STATS_SCRIPT** - 获取队列统计脚本：
- 获取队列大小
- 获取总数
- 获取分数范围

**GET_ALL_PARTITIONS_STATS_SCRIPT** - 获取所有分区统计脚本：
- 遍历所有分区
- 获取每个分区的大小和分数范围
- 返回全局统计信息

### 5. RedisGroupQueueManagerFactory - 管理器工厂

**源码**: `redis_msg_group_queue_manager_factory.py`

**核心功能：**
- 配置管理：支持环境变量和代码配置
- 实例缓存：相同配置复用同一实例
- 根据序列化模式选择 Redis 客户端
  - JSON 模式：使用 default 客户端（decode_responses=True）
  - BSON 模式：使用 binary_cache 客户端（decode_responses=False）

**配置类：**
```python
class RedisGroupQueueConfig:
    key_prefix: str
    serialization_mode: SerializationMode
    sort_key_func: Optional[Callable]
    max_total_messages: int
    queue_expire_seconds: int
    activity_expire_seconds: int
    enable_metrics: bool
    log_interval_seconds: int
    cleanup_interval_seconds: int

    @classmethod
    def from_env(cls, prefix: str = "") -> 'RedisGroupQueueConfig'
```

**主要方法：**
```python
# 获取管理器
async def get_manager(
    config: Optional[RedisGroupQueueConfig] = None,
    item_class: Optional[Type[RedisGroupQueueItem]] = None,
    auto_start: bool = True,
    redis_client_name: str = "default"
) -> RedisGroupQueueManager

# 使用参数创建管理器
async def get_manager_with_config(...) -> RedisGroupQueueManager

# 停止管理器
async def stop_manager(...)
async def stop_all_managers()
```

### 6. 核心算法

**哈希路由算法：**
```python
def _hash_group_key_to_partition(self, group_key: str) -> str:
    """将 group_key 通过 hash 路由到固定分区"""
    hash_value = hashlib.md5(group_key.encode('utf-8')).hexdigest()
    partition_index = int(hash_value[:8], 16) % self.FIXED_PARTITION_COUNT
    return self.partition_names[partition_index]  # "001" - "050"
```

**Rebalance 平均分配算法：**
```lua
-- 平均分配分区
local partitions_per_owner = math.floor(total_partitions / owner_count)
local extra_partitions = total_partitions % owner_count

-- 前 extra_partitions 个 owner 多分配一个分区
for i, owner_id in ipairs(active_owners) do
    local partitions_for_this_owner = partitions_per_owner
    if i <= extra_partitions then
        partitions_for_this_owner = partitions_for_this_owner + 1
    end
    -- 分配分区...
end
```

**Score 差值阈值检查：**
```lua
-- 检查最早消息 score 与当前 score 的差值
if (current_score - earliest_message_score) >= score_threshold then
    -- 获取消息
    local popped = redis.call('ZPOPMIN', queue_key)
end
```

## Mermaid 架构图

```mermaid
graph TB
    subgraph "工厂层"
        Factory[RedisGroupQueueManagerFactory<br/>工厂]
        Config[RedisGroupQueueConfig<br/>配置]
    end

    subgraph "管理器层"
        Manager[RedisGroupQueueManager<br/>队列管理器]
        HashRouter[哈希路由器<br/>MD5 % 50]
        OwnerManager[Owner管理器<br/>动态分配]
    end

    subgraph "Lua脚本层"
        EnqueueScript[ENQUEUE_SCRIPT<br/>入队]
        GetScript[GET_MESSAGES_SCRIPT<br/>获取消息]
        RebalanceScript[REBALANCE_SCRIPT<br/>重新分区]
        JoinScript[JOIN_CONSUMER_SCRIPT<br/>加入消费者]
        ExitScript[EXIT_CONSUMER_SCRIPT<br/>退出消费者]
        CleanupScript[CLEANUP_SCRIPT<br/>清理不活跃]
    end

    subgraph "Redis存储层"
        Queue001[(queue:001<br/>分区队列)]
        Queue050[(queue:050<br/>分区队列)]
        OwnerZset[(owner_activate_time_zset<br/>Owner活跃时间)]
        QueueList[(queue_list:owner_id<br/>Owner队列列表)]
        Counter[(counter<br/>消息总数)]
    end

    subgraph "队列项层"
        ItemInterface[RedisGroupQueueItem<br/>接口]
        SimpleItem[SimpleQueueItem<br/>简单队列项]
        KafkaItem[KafkaConsumerRecordItem<br/>Kafka队列项]
    end

    Factory -->|创建| Manager
    Factory --> Config
    Config -->|配置| Manager

    Manager --> HashRouter
    Manager --> OwnerManager
    Manager --> ItemInterface

    HashRouter -->|路由| Queue001
    HashRouter -->|路由| Queue050

    Manager --> EnqueueScript
    Manager --> GetScript
    Manager --> RebalanceScript
    Manager --> JoinScript
    Manager --> ExitScript
    Manager --> CleanupScript

    EnqueueScript --> Queue001
    EnqueueScript --> Counter
    GetScript --> Queue001
    GetScript --> QueueList
    RebalanceScript --> OwnerZset
    RebalanceScript --> QueueList

    ItemInterface <|-- SimpleItem
    ItemInterface <|-- KafkaItem

    classDef factoryClass fill:#e1f5fe,stroke:#0277bd,stroke-width:2px
    classDef managerClass fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    classDef scriptClass fill:#fff3e0,stroke:#f57c00,stroke-width:1px
    classDef storageClass fill:#e8f5e9,stroke:#388e3c,stroke-width:2px
    classDef itemClass fill:#fce4ec,stroke:#c2185b,stroke-width:1px

    class Factory,Config factoryClass
    class Manager,HashRouter,OwnerManager managerClass
    class EnqueueScript,GetScript,RebalanceScript,JoinScript,ExitScript,CleanupScript scriptClass
    class Queue001,Queue050,OwnerZset,QueueList,Counter storageClass
    class ItemInterface,SimpleItem,KafkaItem itemClass
```

## 依赖关系说明

### 对其他模块的依赖

通过 Grep 验证:
```bash
grep -r "^from\|^import" src/core/queue/redis_group_queue/*.py | grep -v "^#"
```

**redis_group_queue_item.py**:
- `json`: JSON 序列化
- `abc`: 抽象基类
- `typing`: 类型注解
- `enum`: 枚举类
- `bson`: BSON 序列化

**kafka_consumer_record_item.py**:
- `json`: JSON 处理
- `base64`: Base64 编码
- `typing`: 类型注解
- `dataclasses`: 数据类
- `bson`: BSON 序列化
- `aiokafka.ConsumerRecord`: Kafka 消费记录
- `core.observation.logger.get_logger`: 日志记录器

**redis_msg_group_queue_manager.py**:
- `asyncio`: 异步锁
- `time`: 时间戳
- `random`: 随机数
- `hashlib`: MD5 哈希
- `typing`: 类型注解
- `dataclasses`: 数据类
- `enum`: 枚举类
- `redis.asyncio`: Redis 异步客户端
- `core.observation.logger.get_logger`: 日志记录器
- `common_utils.datetime_utils`: 时间工具
- `core.rate_limit.rate_limiter.rate_limit`: 限流装饰器

**redis_msg_group_queue_manager_factory.py**:
- `os`: 环境变量
- `asyncio`: 异步锁
- `typing`: 类型注解
- `core.di.decorators.component`: DI 装饰器
- `core.observation.logger.get_logger`: 日志记录器
- `component.redis_provider.RedisProvider`: Redis 连接提供者

### 被依赖关系

通过 Grep 验证:
```bash
grep -r "from core.queue.redis_group_queue\|import.*RedisGroupQueue" src/ --include="*.py" | grep -v "src/core/queue/redis_group_queue/"
```

目前无其他模块直接依赖（独立使用）。

## 使用场景

### 1. Kafka 消费缓冲队列

```python
from aiokafka import AIOKafkaConsumer
from core.queue.redis_group_queue.kafka_consumer_record_item import KafkaConsumerRecordItem

# 创建 Redis 队列管理器（BSON 模式）
manager = await factory.get_manager_with_config(
    key_prefix="kafka_buffer",
    serialization_mode=SerializationMode.BSON,
    item_class=KafkaConsumerRecordItem,
    max_total_messages=50000,
    auto_start=True
)

# Kafka 消费者：投递到 Redis 队列
async def kafka_consumer_worker():
    consumer = AIOKafkaConsumer(
        'my_topic',
        bootstrap_servers='localhost:9092'
    )
    await consumer.start()

    async for msg in consumer:
        # 转换为队列项
        queue_item = KafkaConsumerRecordItem(msg)

        # 投递到 Redis（基于 topic_partition 路由）
        group_key = f"{msg.topic}_{msg.partition}"
        await manager.deliver_message(group_key, queue_item)

# 处理器：从 Redis 队列消费
async def message_processor():
    while True:
        # 获取消息（score_threshold = 1秒）
        messages = await manager.get_messages(score_threshold=1000)

        for kafka_item in messages:
            # 转换回 ConsumerRecord
            record = kafka_item.to_consumer_record()

            # 处理消息
            await process_kafka_message(record)
```

### 2. 分布式任务队列

```python
# 创建任务队列管理器（JSON 模式）
manager = await factory.get_manager_with_config(
    key_prefix="task_queue",
    serialization_mode=SerializationMode.JSON,
    item_class=SimpleQueueItem,
    max_total_messages=20000,
    auto_start=True
)

# 任务生产者
async def task_producer():
    for i in range(1000):
        task = SimpleQueueItem(
            data={
                "task_id": i,
                "action": "process",
                "params": {"value": i * 2}
            },
            item_type="task"
        )
        await manager.deliver_message(f"task_{i % 10}", task)

# 任务消费者（多个实例）
async def task_consumer():
    # 自动加入消费者并分配分区
    while True:
        messages = await manager.get_messages(score_threshold=5000)

        for task_item in messages:
            task_data = task_item.data
            await execute_task(task_data)
```

### 3. 多消费者协同处理

```python
# 启动多个消费者实例
async def consumer_instance(instance_id: str):
    # 使用命名 owner_id
    manager.owner_id = f"consumer_{instance_id}"

    # 加入消费者（触发 rebalance）
    owner_count, assigned_partitions = await manager.join_consumer()
    print(f"实例{instance_id} 分配的分区: {assigned_partitions}")

    try:
        while True:
            # 获取消息
            messages = await manager.get_messages(score_threshold=1000)

            for msg in messages:
                await process_message(msg)

            # 每隔 30 秒保活一次
            await asyncio.sleep(30)
            await manager.keepalive_consumer()

    finally:
        # 退出消费者（触发 rebalance）
        await manager.exit_consumer()

# 启动多个实例
await asyncio.gather(
    consumer_instance("1"),
    consumer_instance("2"),
    consumer_instance("3")
)
```

## 可以验证模块可运行的测试命令

```bash
# 1. 验证模块导入
python -c "
from core.queue.redis_group_queue import (
    RedisGroupQueueItem,
    RedisGroupQueueManager,
    RedisGroupQueueManagerFactory
)
from core.queue.redis_group_queue.redis_group_queue_item import SimpleQueueItem, SerializationMode
from core.queue.redis_group_queue.kafka_consumer_record_item import KafkaConsumerRecordItem
print('模块导入成功')
print(f'队列项接口: {RedisGroupQueueItem}')
print(f'简单队列项: {SimpleQueueItem}')
print(f'Kafka队列项: {KafkaConsumerRecordItem}')
print(f'管理器: {RedisGroupQueueManager}')
print(f'工厂: {RedisGroupQueueManagerFactory}')
"

# 2. 验证 Lua 脚本
python -c "
from core.queue.redis_group_queue.redis_group_queue_lua_scripts import (
    ENQUEUE_SCRIPT,
    GET_MESSAGES_SCRIPT,
    REBALANCE_PARTITIONS_SCRIPT,
    JOIN_CONSUMER_SCRIPT,
    EXIT_CONSUMER_SCRIPT,
    KEEPALIVE_CONSUMER_SCRIPT,
    CLEANUP_INACTIVE_OWNERS_SCRIPT,
    FORCE_CLEANUP_SCRIPT,
    GET_QUEUE_STATS_SCRIPT,
    GET_ALL_PARTITIONS_STATS_SCRIPT
)
print('Lua 脚本验证:')
print(f'入队脚本行数: {len(ENQUEUE_SCRIPT.splitlines())}')
print(f'获取消息脚本行数: {len(GET_MESSAGES_SCRIPT.splitlines())}')
print(f'重新分区脚本行数: {len(REBALANCE_PARTITIONS_SCRIPT.splitlines())}')
print(f'加入消费者脚本行数: {len(JOIN_CONSUMER_SCRIPT.splitlines())}')
print(f'退出消费者脚本行数: {len(EXIT_CONSUMER_SCRIPT.splitlines())}')
print(f'保活脚本行数: {len(KEEPALIVE_CONSUMER_SCRIPT.splitlines())}')
print(f'清理不活跃脚本行数: {len(CLEANUP_INACTIVE_OWNERS_SCRIPT.splitlines())}')
print(f'强制清理脚本行数: {len(FORCE_CLEANUP_SCRIPT.splitlines())}')
print(f'获取统计脚本行数: {len(GET_QUEUE_STATS_SCRIPT.splitlines())}')
print(f'获取所有分区统计脚本行数: {len(GET_ALL_PARTITIONS_STATS_SCRIPT.splitlines())}')
"

# 3. 测试队列项序列化
python -c "
from core.queue.redis_group_queue.redis_group_queue_item import SimpleQueueItem

# JSON 序列化
item = SimpleQueueItem(data={'test': 'value', 'number': 123}, item_type='test')
json_str = item.to_json_str()
print(f'JSON 序列化: {json_str}')

restored = SimpleQueueItem.from_json_str(json_str)
print(f'JSON 反序列化: {restored.data}')

# BSON 序列化
bson_bytes = item.to_bson_bytes()
print(f'BSON 序列化长度: {len(bson_bytes)}')

restored_bson = SimpleQueueItem.from_bson_bytes(bson_bytes)
print(f'BSON 反序列化: {restored_bson.data}')
"

# 4. 测试 Kafka 队列项
python -c "
from core.queue.redis_group_queue.kafka_consumer_record_item import KafkaConsumerRecordItem
from aiokafka import ConsumerRecord

# 创建 Kafka 消费记录
record = ConsumerRecord(
    topic='test',
    partition=0,
    offset=123,
    timestamp=1700000000000,
    timestamp_type=0,
    key=b'key123',
    value={'data': 'test'},
    checksum=None,
    serialized_key_size=6,
    serialized_value_size=15,
    headers=[('trace_id', b'abc')]
)

# 转换为队列项
item = KafkaConsumerRecordItem(record)
print(f'Kafka 队列项: topic={item.topic}, offset={item.offset}')

# BSON 序列化
bson_bytes = item.to_bson_bytes()
print(f'BSON 长度: {len(bson_bytes)}')

# 反序列化
restored = KafkaConsumerRecordItem.from_bson_bytes(bson_bytes)
print(f'反序列化: topic={restored.topic}, offset={restored.offset}')

# 转换回 ConsumerRecord
restored_record = restored.to_consumer_record()
print(f'恢复的 ConsumerRecord: topic={restored_record.topic}, offset={restored_record.offset}')
"

# 5. 测试哈希路由
python -c "
import hashlib

def hash_to_partition(group_key, num_partitions=50):
    hash_value = hashlib.md5(group_key.encode('utf-8')).hexdigest()
    partition_index = int(hash_value[:8], 16) % num_partitions
    return f'{partition_index + 1:03d}'

# 测试路由一致性
for i in range(5):
    partition = hash_to_partition('user_123')
    print(f'第{i+1}次路由: partition_{partition}')

# 测试路由分布
distribution = {}
for i in range(10000):
    partition = hash_to_partition(f'user_{i}')
    distribution[partition] = distribution.get(partition, 0) + 1

print(f'路由分布（前10个）: {dict(list(distribution.items())[:10])}')
print(f'总分区数: {len(distribution)}')
print(f'平均每分区: {sum(distribution.values()) / len(distribution):.1f}')
"

# 6. 测试完整功能（需要 Redis）
python -c "
import asyncio
from core.queue.redis_group_queue.redis_msg_group_queue_manager_factory import RedisGroupQueueManagerFactory
from core.queue.redis_group_queue.redis_group_queue_item import SimpleQueueItem, SerializationMode
from component.redis_provider import RedisProvider

async def test():
    # 创建工厂
    redis_provider = RedisProvider()
    factory = RedisGroupQueueManagerFactory(redis_provider)

    # 获取管理器
    manager = await factory.get_manager_with_config(
        key_prefix='test_queue',
        serialization_mode=SerializationMode.JSON,
        max_total_messages=100,
        auto_start=True
    )

    # 投递消息
    for i in range(10):
        item = SimpleQueueItem(data={'id': i}, item_type='test')
        success = await manager.deliver_message(f'group_{i}', item)
        print(f'投递消息{i}: {success}')

    # 获取统计
    stats = await manager.get_stats(include_consumer_info=True)
    print(f'总消息: {stats[\"total_current_messages\"]}')
    print(f'总投递: {stats[\"total_delivered_messages\"]}')

    # 获取消息
    messages = await manager.get_messages(score_threshold=1000)
    print(f'获取消息数: {len(messages)}')

    # 关闭
    await manager.shutdown()
    await factory.stop_all_managers()

asyncio.run(test())
"

# 7. 运行测试套件（如果存在）
pytest src/core/queue/redis_group_queue/ -v
```

# infra_layer.adapters.input.mq

消息队列（Message Queue）输入适配器，异步消息消费者

## 模块位置

**源码路径**: `src/infra_layer/adapters/input/mq/`
**文档路径**: `specs/ac_mod/infra_layer.adapters.input.mq.ac.mod.md`
**模块类型**: 包模块

## 目录结构

```
src/infra_layer/adapters/input/mq/
├── __init__.py                # 空包（待实现）
└── mapper/                    # MQ 消息映射器
    └── __init__.py
```

## 快速开始

### 消息队列消费者

```python
# 使用 RabbitMQ/Kafka 消费消息
from agentic_layer.memory_manager import MemoryManager
from infra_layer.adapters.input.format_transfer import convert_single_message_to_raw_data

# 预期实现
class MessageConsumer:
    def __init__(self):
        self.memory_manager = MemoryManager()

    async def consume_chat_message(self, message: dict):
        """消费聊天消息"""
        # 1. 转换为 RawData
        raw_data = await convert_single_message_to_raw_data(
            input_data=message,
            group_name=message.get("groupName")
        )

        # 2. 调用记忆存储
        await self.memory_manager.memorize([raw_data])
```

### RabbitMQ 集成

```python
import aio_pika
from infra_layer.adapters.input.mq.consumer import MessageConsumer

async def consume_from_rabbitmq():
    connection = await aio_pika.connect_robust("amqp://guest:guest@localhost/")
    channel = await connection.channel()
    queue = await channel.declare_queue("chat_messages", durable=True)

    consumer = MessageConsumer()

    async with queue.iterator() as queue_iter:
        async for message in queue_iter:
            async with message.process():
                data = json.loads(message.body)
                await consumer.consume_chat_message(data)
```

### Kafka 集成

```python
from aiokafka import AIOKafkaConsumer
from infra_layer.adapters.input.mq.consumer import MessageConsumer

async def consume_from_kafka():
    consumer = AIOKafkaConsumer(
        'chat_messages',
        bootstrap_servers='localhost:9092',
        group_id='evermem_consumer'
    )

    mq_consumer = MessageConsumer()

    await consumer.start()
    try:
        async for msg in consumer:
            data = json.loads(msg.value)
            await mq_consumer.consume_chat_message(data)
    finally:
        await consumer.stop()
```

## 核心组件详解

### 1. MQ 适配器模式

**作用**: 将异步消息转换为记忆存储调用

**特点**:
- 异步非阻塞处理
- 支持批量消费
- 错误重试机制
- 消息确认（ACK）

### 2. 预期消息类型

**聊天消息**:
```json
{
  "message_id": "msg_123",
  "group_id": "group_456",
  "group_name": "项目组",
  "sender_id": "user_001",
  "sender_name": "张三",
  "content": "讨论新功能",
  "timestamp": "2024-01-15T10:00:00Z",
  "message_type": "text"
}
```

**系统事件**:
```json
{
  "event_type": "user_joined",
  "group_id": "group_456",
  "user_id": "user_002",
  "timestamp": "2024-01-15T10:05:00Z"
}
```

### 3. Mapper 映射器

**预期功能**:
- MQ 消息格式 → 内部格式
- 字段验证和转换
- 错误消息处理

```python
# mq/mapper/message_mapper.py (待实现)
from infra_layer.adapters.input.mq.mapper import map_mq_message_to_raw_data

raw_data = await map_mq_message_to_raw_data(mq_message)
```

### 4. 消息消费流程

```
MQ (RabbitMQ/Kafka)
        ↓
   Consumer 接收
        ↓
   Mapper 转换
        ↓
format_transfer (RawData)
        ↓
  MemoryManager
        ↓
   Memory Layer
```

## Mermaid 依赖图

```mermaid
graph TB
    MQ[adapters.input.mq<br/>消息队列适配器]

    Consumer[Message Consumer<br/>消息消费者]
    Mapper[mq/mapper<br/>消息映射器]

    RabbitMQ[RabbitMQ<br/>消息队列]
    Kafka[Kafka<br/>消息队列]

    FormatTransfer[format_transfer<br/>格式转换]
    MemoryManager[agentic_layer<br/>MemoryManager]

    MQ -.待实现.-> Consumer
    MQ --> Mapper

    RabbitMQ -.消息.-> Consumer
    Kafka -.消息.-> Consumer

    Consumer --> Mapper
    Mapper --> FormatTransfer
    FormatTransfer --> MemoryManager

    classDef emptyClass fill:#f5f5f5,stroke:#9e9e9e,stroke-width:1px,stroke-dasharray: 5 5
    classDef consumerClass fill:#fff3e0,stroke:#e65100,stroke-width:2px
    classDef mapperClass fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    classDef mqClass fill:#e3f2fd,stroke:#1976d2,stroke-width:2px
    classDef businessClass fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px

    class MQ emptyClass
    class Consumer consumerClass
    class Mapper mapperClass
    class RabbitMQ,Kafka mqClass
    class FormatTransfer,MemoryManager businessClass
```

## 依赖关系说明

### 对其他模块的依赖

预期依赖（待实现）:
- MQ 客户端（`aio_pika` / `aiokafka`）
- `specs/ac_mod/infra_layer.adapters.input.ac.mod.md` - format_transfer
- `agentic_layer.memory_manager` - 业务逻辑
- `specs/ac_mod/infra_layer.adapters.input.mq.mapper.ac.mod.md` - 消息映射

### 被依赖关系

- 消息生产者（外部系统）
- `specs/ac_mod/infra_layer.adapters.input.ac.mod.md` - 父模块

## 可以验证模块可运行的测试命令

```bash
# 检查 mq 包
python -c "import infra_layer.adapters.input.mq; print('Empty package')"

# 检查 MQ 客户端（如果已安装）
python -c "
try:
    import aio_pika
    print('aio_pika installed')
except ImportError:
    print('aio_pika not installed')

try:
    import aiokafka
    print('aiokafka installed')
except ImportError:
    print('aiokafka not installed')
"

# 示例：手动测试消息转换
python -c "
from infra_layer.adapters.input.format_transfer import convert_single_message_to_raw_data
import asyncio

async def test():
    msg = {
        '_id': 'msg_1',
        'content': 'test',
        'createTime': '2024-01-15T10:00:00Z',
        'createBy': 'user_1'
    }
    raw_data = await convert_single_message_to_raw_data(msg)
    print('Conversion OK:', raw_data.data_id)

asyncio.run(test())
"

# 查看 MQ 文件
find src/infra_layer/adapters/input/mq -name "*.py" -type f | grep -v __pycache__
```

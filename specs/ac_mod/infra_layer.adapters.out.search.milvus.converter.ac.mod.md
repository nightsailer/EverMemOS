# infra_layer.adapters.out.search.milvus.converter

Milvus 转换器包，负责将 MongoDB 记忆文档转换为 Milvus Collection 实体，处理向量数据、时间戳转换和 JSON 序列化。

## 模块位置

**源码路径**: `src/infra_layer/adapters/out/search/milvus/converter/`
**文档路径**: `specs/ac_mod/infra_layer.adapters.out.search.milvus.converter.ac.mod.md`
**模块类型**: 包模块

## 目录结构

```
src/infra_layer/adapters/out/search/milvus/converter/
├── __init__.py                                  # 导出3个转换器
├── episodic_memory_milvus_converter.py          # 情景记忆转换器
├── semantic_memory_milvus_converter.py          # 语义记忆转换器
└── event_log_milvus_converter.py                # 事件日志转换器
```

## 快速开始

### 基本转换

```python
from infra_layer.adapters.out.search.milvus.converter import (
    EpisodicMemoryMilvusConverter,
    SemanticMemoryMilvusConverter,
    EventLogMilvusConverter
)

# MongoDB → Milvus 转换
mongo_doc = await MongoEpisodicMemory.objects.get(id="xxx")
milvus_entity = EpisodicMemoryMilvusConverter.from_mongo(mongo_doc)

# milvus_entity 是 Dict[str, Any]，可直接插入 Milvus
await collection.insert([milvus_entity])
```

### 批量转换

```python
# 批量转换
mongo_docs = await MongoEpisodicMemory.objects.filter(user_id="user123").to_list()
milvus_entities = [
    EpisodicMemoryMilvusConverter.from_mongo(doc) for doc in mongo_docs
]

# 批量插入
await collection.insert(milvus_entities)
```

## 核心组件详解

### 1. EpisodicMemoryMilvusConverter

**功能**: MongoDB EpisodicMemory → Milvus EpisodicMemoryCollection

**from_mongo() 返回字典**:
```python
{
    "id": str,                    # event_id
    "vector": List[float],        # 1024维向量
    "user_id": str,
    "group_id": str,
    "participants": List[str],
    "event_type": str,
    "timestamp": int,             # Unix时间戳
    "episode": str,
    "search_content": str,        # JSON字符串
    "detail": str,                # JSON字符串（元数据）
    "created_at": int,
    "updated_at": int
}
```

**字段处理**:
- `timestamp`: datetime → int(timestamp())
- `search_content`: List[str] → JSON.dumps([subject, summary, episode[:500]])
- `detail`: Dict → JSON.dumps({user_name, title, summary, ...})
- `vector`: 直接使用 source_doc.vector

### 2. SemanticMemoryMilvusConverter

**功能**: MongoDB PersonalSemanticMemory → Milvus SemanticMemoryCollection

**特殊字段**:
```python
{
    "id": str,                    # memory_id
    "user_id": str,
    "group_id": str,
    "parent_episode_id": str,
    "start_time": int,            # Unix时间戳
    "end_time": int,              # Unix时间戳
    "duration_days": int,
    "content": str,               # 语义记忆内容
    "evidence": str,              # 证据
    "search_content": str,        # JSON: [content, evidence]
    "metadata": str,              # JSON元数据
    "vector": List[float]
}
```

**时间字段处理**:
```python
# 支持 datetime 和 ISO 字符串
if isinstance(source_doc.start_time, str):
    start_dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
    start_time = int(start_dt.timestamp())
elif isinstance(source_doc.start_time, datetime):
    start_time = int(source_doc.start_time.timestamp())
```

### 3. EventLogMilvusConverter

**功能**: MongoDB EventLog → Milvus EventLogCollection

**特殊字段**:
```python
{
    "id": str,                    # log_id
    "parent_episode_id": str,
    "event_type": str,
    "timestamp": int,
    "atomic_fact": str,           # 原子事实
    "search_content": str,        # JSON: [atomic_fact]
    "metadata": str,              # JSON元数据
    "vector": List[float]
}
```

### 4. 通用转换逻辑

**search_content 构建**:
```python
@staticmethod
def _build_search_content(source_doc) -> str:
    """构建搜索内容（JSON列表格式）"""
    text_content = []

    if hasattr(source_doc, 'subject') and source_doc.subject:
        text_content.append(source_doc.subject)

    if hasattr(source_doc, 'summary') and source_doc.summary:
        text_content.append(source_doc.summary)

    if hasattr(source_doc, 'episode') and source_doc.episode:
        text_content.append(source_doc.episode[:500])  # 限制长度

    return json.dumps(text_content, ensure_ascii=False)
```

**metadata 构建**:
```python
@classmethod
def _build_detail(cls, source_doc) -> Dict[str, Any]:
    """构建详细信息字典（非检索字段）"""
    detail = {
        "user_name": getattr(source_doc, 'user_name', None),
        "title": getattr(source_doc, 'subject', None),
        "summary": getattr(source_doc, 'summary', None),
        "keywords": getattr(source_doc, 'keywords', None),
        "extend": getattr(source_doc, 'extend', None),
    }

    # 过滤 None 值
    return {k: v for k, v in detail.items() if v is not None}
```

## Mermaid 依赖图

```mermaid
graph TB
    Conv[converter<br/>转换器包]

    EpisConv[EpisodicMemoryMilvusConverter]
    SemConv[SemanticMemoryMilvusConverter]
    EventConv[EventLogMilvusConverter]

    MongoEpis[MongoEpisodicMemory]
    MongoSem[MongoPersonalSemanticMemory]
    MongoEvent[MongoEventLog]

    EpisColl[EpisodicMemoryCollection]
    SemColl[SemanticMemoryCollection]
    EventColl[EventLogCollection]

    JSON[json.dumps<br/>JSON序列化]
    Timestamp[timestamp()<br/>时间转换]

    Conv --> EpisConv
    Conv --> SemConv
    Conv --> EventConv

    EpisConv --> MongoEpis
    SemConv --> MongoSem
    EventConv --> MongoEvent

    EpisConv -.返回Dict.-> EpisColl
    SemConv -.返回Dict.-> SemColl
    EventConv -.返回Dict.-> EventColl

    EpisConv --> JSON
    EpisConv --> Timestamp
    SemConv --> JSON
    SemConv --> Timestamp
    EventConv --> JSON
    EventConv --> Timestamp

    classDef coreClass fill:#e1f5fe,stroke:#0277bd,stroke-width:2px
    classDef convClass fill:#fff3e0,stroke:#e65100,stroke-width:1px
    classDef docClass fill:#f3e5f5,stroke:#7b1fa2,stroke-width:1px
    classDef utilClass fill:#e8f5e9,stroke:#2e7d32,stroke-width:1px

    class Conv coreClass
    class EpisConv,SemConv,EventConv convClass
    class MongoEpis,MongoSem,MongoEvent,EpisColl,SemColl,EventColl docClass
    class JSON,Timestamp utilClass
```

## 依赖关系说明

### 对其他模块的依赖
- `specs/ac_mod/core.oxm.milvus.base_converter.ac.mod.md` - BaseMilvusConverter
- `specs/ac_mod/infra_layer.adapters.out.search.milvus.memory.ac.mod.md` - Collection 定义
- `specs/ac_mod/infra_layer.adapters.out.persistence.document.memory.ac.mod.md` - MongoDB 文档
- `specs/ac_mod/core.observation.logger.ac.mod.md` - 日志工具

### 被依赖关系
- `specs/ac_mod/biz_layer.personal_memory_sync.ac.mod.md` - 个人记忆同步
- `specs/ac_mod/biz_layer.memcell_milvus_sync.ac.mod.md` - 记忆单元 Milvus 同步

## Grep 验证

```bash
# 验证转换器类定义
grep "class.*MilvusConverter" src/infra_layer/adapters/out/search/milvus/converter/*.py

# 验证 from_mongo 方法
grep -A 5 "def from_mongo" src/infra_layer/adapters/out/search/milvus/converter/*.py

# 验证 JSON 序列化
grep "json.dumps" src/infra_layer/adapters/out/search/milvus/converter/*.py

# 验证时间戳转换
grep "timestamp()" src/infra_layer/adapters/out/search/milvus/converter/*.py

# 验证导出
grep "__all__" src/infra_layer/adapters/out/search/milvus/converter/__init__.py
```

## 可运行示例

### 情景记忆转换

```python
from datetime import datetime
from infra_layer.adapters.out.search.milvus.converter import EpisodicMemoryMilvusConverter

# 模拟 MongoDB 文档
class MockMongoDoc:
    def __init__(self):
        self.event_id = "evt001"
        self.user_id = "user123"
        self.timestamp = datetime(2024, 1, 1, 12, 0, 0)
        self.episode = "参加了技术分享会，学习了Milvus向量数据库"
        self.subject = "技术分享会"
        self.summary = "学习了向量数据库"
        self.type = "conversation"
        self.vector = [0.1] * 1024
        self.created_at = datetime.now()
        self.updated_at = datetime.now()

mongo_doc = MockMongoDoc()

# 转换
milvus_entity = EpisodicMemoryMilvusConverter.from_mongo(mongo_doc)

print(f"ID: {milvus_entity['id']}")
print(f"Timestamp: {milvus_entity['timestamp']}")  # Unix时间戳
print(f"Vector length: {len(milvus_entity['vector'])}")
print(f"Search content: {milvus_entity['search_content']}")  # JSON字符串

# 输出:
# ID: evt001
# Timestamp: 1704106800
# Vector length: 1024
# Search content: ["技术分享会", "学习了向量数据库", "参加了技术分享会，学习了Milvus向量数据库"[:500]]
```

### 语义记忆转换

```python
from infra_layer.adapters.out.search.milvus.converter import SemanticMemoryMilvusConverter

# 模拟 MongoDB 语义记忆
class MockSemanticMemory:
    def __init__(self):
        self.id = "sem001"
        self.user_id = "user123"
        self.parent_episode_id = "evt001"
        self.content = "Milvus 是开源向量数据库"
        self.evidence = "官方文档说明"
        self.start_time = datetime(2024, 1, 1)
        self.end_time = datetime(2024, 12, 31)
        self.duration_days = 365
        self.vector = [0.2] * 1024
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        self.participants = []
        self.group_id = ""

mongo_sem = MockSemanticMemory()
milvus_entity = SemanticMemoryMilvusConverter.from_mongo(mongo_sem)

print(f"ID: {milvus_entity['id']}")
print(f"Content: {milvus_entity['content']}")
print(f"Evidence: {milvus_entity['evidence']}")
print(f"Start time: {milvus_entity['start_time']}")  # Unix时间戳
print(f"Duration days: {milvus_entity['duration_days']}")
```

### 事件日志转换

```python
from infra_layer.adapters.out.search.milvus.converter import EventLogMilvusConverter

# 模拟 MongoDB 事件日志
class MockEventLog:
    def __init__(self):
        self.id = "log001"
        self.user_id = "user123"
        self.parent_episode_id = "evt001"
        self.timestamp = datetime.now()
        self.atomic_fact = "用户参加技术分享会"
        self.event_type = "attendance"
        self.vector = [0.3] * 1024
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        self.participants = []
        self.group_id = ""

mongo_log = MockEventLog()
milvus_entity = EventLogMilvusConverter.from_mongo(mongo_log)

print(f"ID: {milvus_entity['id']}")
print(f"Atomic fact: {milvus_entity['atomic_fact']}")
print(f"Event type: {milvus_entity['event_type']}")
print(f"Search content: {milvus_entity['search_content']}")  # JSON: ["用户参加技术分享会"]
```

## 测试命令

```bash
# 测试所有转换器
pytest src/infra_layer/adapters/out/search/milvus/converter/test_*.py -v

# 验证导入
python -c "from infra_layer.adapters.out.search.milvus.converter import EpisodicMemoryMilvusConverter, SemanticMemoryMilvusConverter, EventLogMilvusConverter; print('OK')"

# 测试 JSON 序列化
python -c "
import json
from infra_layer.adapters.out.search.milvus.converter import EpisodicMemoryMilvusConverter

text_content = ['标题', '摘要', '内容']
search_content = json.dumps(text_content, ensure_ascii=False)
print(search_content)
"
```

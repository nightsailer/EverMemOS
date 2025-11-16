# memory_layer.cluster_manager

MemCell 自动聚类管理器，基于向量相似度和时间接近性实现增量聚类，支持事件回调和持久化存储

## 模块位置

**源码路径**: `src/memory_layer/cluster_manager/`
**文档路径**: `specs/ac_mod/memory_layer.cluster_manager.ac.mod.md`
**模块类型**: 包模块

## 目录结构

```
src/memory_layer/cluster_manager/
├── __init__.py                 # 导出 ClusterManager, Config, Storage
├── manager.py                  # ClusterManager 核心实现
├── config.py                   # ClusterManagerConfig 配置
├── storage.py                  # ClusterStorage 抽象和 InMemoryClusterStorage 实现
└── mongo_cluster_storage.py    # MongoClusterStorage 实现
```

## 快速开始

### 基本使用

```python
from memory_layer.cluster_manager import (
    ClusterManager,
    ClusterManagerConfig,
    InMemoryClusterStorage
)

# 1. 配置聚类参数
config = ClusterManagerConfig(
    similarity_threshold=0.65,      # 余弦相似度阈值（0.0-1.0）
    max_time_gap_days=7.0,          # 最大时间间隔（天）
    enable_persistence=True,        # 启用持久化
    persist_dir="./cluster_data",   # 持久化目录
    clustering_algorithm="centroid" # 聚类算法（centroid/nearest）
)

# 2. 初始化存储（可选，默认使用 InMemoryClusterStorage）
storage = InMemoryClusterStorage(
    enable_persistence=True,
    persist_dir="./cluster_data"
)

# 3. 创建 ClusterManager
cluster_mgr = ClusterManager(config=config, storage=storage)

# 4. 注册聚类事件回调
async def on_cluster_callback(group_id, memcell, cluster_id, recent_memcells):
    print(f"MemCell {memcell['event_id']} → Cluster {cluster_id}")

cluster_mgr.on_cluster_assigned(on_cluster_callback)

# 5. 手动分配聚类
await cluster_mgr.assign_cluster(
    group_id="group1",
    memcell={
        "event_id": "evt001",
        "summary": "讨论项目进度",
        "timestamp": 1699999999.0
    },
    embedding=[0.1, 0.2, 0.3, ...]  # 向量（可选，会自动提取）
)

# 6. 查询聚类结果
assignments = await storage.get_cluster_assignments("group1")
print(assignments)  # {"evt001": "cluster_000", ...}
```

### 与 MemCellExtractor 集成

```python
from memory_layer.memcell_extractor.conv_memcell_extractor import ConvMemCellExtractor
from memory_layer.llm import create_provider_from_env

# 1. 创建 LLM Provider 和 MemCellExtractor
llm_provider = create_provider_from_env("openai")
memcell_extractor = ConvMemCellExtractor(llm_provider)

# 2. 创建 ClusterManager 并附加到 Extractor
cluster_mgr = ClusterManager(config)
cluster_mgr.attach_to_extractor(memcell_extractor)

# 3. 提取 MemCell 时自动触发聚类
memcell, status = await memcell_extractor.extract_memcell(request)
# → ClusterManager 自动分配聚类 ID 并触发回调
```

## 核心组件详解

### 1. ClusterManager 类

**功能**：
- **增量聚类**：基于余弦相似度（centroid/nearest 算法）和时间间隔
- **事件通知**：聚类分配时触发回调（group_id, memcell, cluster_id, recent_memcells）
- **向量提取**：自动调用 `agentic_layer.vectorize_service` 生成 embedding
- **持久化**：支持 JSON 文件或 MongoDB 存储

**主要方法**：

| 方法 | 功能 | 参数 | 返回值 |
|------|------|------|--------|
| `assign_cluster()` | 为 MemCell 分配聚类 | group_id, memcell, embedding(可选) | cluster_id |
| `on_cluster_assigned()` | 注册聚类回调 | callback(async func) | - |
| `attach_to_extractor()` | 附加到 MemCellExtractor | extractor | - |
| `get_cluster_info()` | 获取聚类统计信息 | group_id, cluster_id(可选) | Dict |

### 2. ClusterManagerConfig 配置

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `similarity_threshold` | float | 0.65 | 余弦相似度阈值（0.0-1.0） |
| `max_time_gap_days` | float | 7.0 | 最大时间间隔（天） |
| `enable_persistence` | bool | False | 是否启用持久化 |
| `persist_dir` | str | None | 持久化目录（启用时必填） |
| `clustering_algorithm` | str | "centroid" | 聚类算法（centroid/nearest） |

**验证规则**：
- `similarity_threshold` ∈ [0.0, 1.0]
- `max_time_gap_days` ≥ 0
- `enable_persistence=True` 时 `persist_dir` 必填

### 3. ClusterStorage 抽象

**接口定义**：
```python
class ClusterStorage(ABC):
    async def save_cluster_state(group_id: str, state: Dict) -> bool
    async def load_cluster_state(group_id: str) -> Optional[Dict]
    async def get_cluster_assignments(group_id: str) -> Dict[str, str]
    async def clear(group_id: Optional[str]) -> bool
```

**实现类**：
- **InMemoryClusterStorage**: 内存 + JSON 文件（可选）
- **MongoClusterStorage**: MongoDB 持久化

### 4. ClusterState 内部状态

**字段**：
```python
class ClusterState:
    event_ids: List[str]                    # 事件 ID 列表
    timestamps: List[float]                 # 时间戳列表
    vectors: List[np.ndarray]               # 向量列表
    cluster_ids: List[str]                  # 聚类 ID 列表
    eventid_to_cluster: Dict[str, str]      # 事件→聚类映射
    cluster_centroids: Dict[str, np.ndarray]# 聚类质心
    cluster_counts: Dict[str, int]          # 聚类计数
    cluster_last_ts: Dict[str, float]       # 聚类最后时间戳
```

**序列化**：
- `to_dict()`: 转为 JSON 可序列化字典（numpy 数组→列表）
- `from_dict()`: 从字典恢复状态

## 聚类算法详解

### Centroid 算法（默认）

```python
# 伪代码
for existing_cluster in clusters:
    similarity = cosine(new_vector, cluster_centroid)
    time_gap = abs(new_timestamp - cluster_last_ts)

    if similarity >= threshold and time_gap <= max_gap:
        # 加入现有聚类，更新质心
        centroid_new = (centroid * count + new_vector) / (count + 1)
        return cluster_id

# 创建新聚类
return new_cluster_id
```

**优点**：
- 质心平滑，抗噪声
- 计算复杂度 O(K)，K 为聚类数

### Nearest 算法

```python
# 对每个聚类，计算 new_vector 与所有成员的最大相似度
max_similarity = max(cosine(new_vector, member_vector) for member in cluster)
```

**优点**：
- 更严格的相似性要求
- 适用于高维稀疏向量

## Mermaid 依赖图

```mermaid
graph TB
    CM[ClusterManager<br/>聚类管理器]
    Config[config.py<br/>配置类]
    Storage[storage.py<br/>存储抽象]
    InMemStorage[InMemoryClusterStorage<br/>内存存储]
    MongoStorage[MongoClusterStorage<br/>MongoDB存储]
    VectorService[agentic_layer<br/>vectorize_service]
    MemCellExt[memcell_extractor<br/>MemCell提取器]

    CM --> Config
    CM --> Storage
    Storage <|-- InMemStorage
    Storage <|-- MongoStorage
    CM -.->|可选| VectorService
    MemCellExt -->|attach| CM

    classDef coreClass fill:#e1f5fe,stroke:#0277bd,stroke-width:2px
    classDef subClass fill:#f3e5f5,stroke:#7b1fa2,stroke-width:1px
    classDef extClass fill:#fff3e0,stroke:#f57c00,stroke-width:1px

    class CM coreClass
    class Config,Storage subClass
    class InMemStorage,MongoStorage,VectorService,MemCellExt extClass
```

## 依赖关系说明

### 对其他模块的依赖

通过 Grep 验证：
```bash
grep -rn "^from " src/memory_layer/cluster_manager/*.py | grep -v "^from memory_layer.cluster_manager"
```

**结果**：
- `core.observation.logger`: 日志记录
- `agentic_layer.vectorize_service`: 向量化服务（**可选**，聚类时自动提取 embedding）

**内部依赖**：
- `memory_layer.cluster_manager.config`: ClusterManagerConfig
- `memory_layer.cluster_manager.storage`: ClusterStorage, InMemoryClusterStorage

### 被依赖关系

通过 Grep 验证：
```bash
grep -rn "from memory_layer.cluster_manager\|import.*ClusterManager" src/
```

**结果**：
- 目前无外部直接依赖（设计为可选组件）
- 通常通过 `ProfileManager` 间接使用

**文档引用**：
- `specs/ac_mod/memory_layer.profile_manager.ac.mod.md`（ProfileManager 依赖 ClusterManager）

## 可运行的测试命令

```bash
# 1. 验证导入
python -c "from memory_layer.cluster_manager import ClusterManager, ClusterManagerConfig; print('✅ Import OK')"

# 2. 验证配置创建
python -c "
from memory_layer.cluster_manager import ClusterManagerConfig
config = ClusterManagerConfig(similarity_threshold=0.7, max_time_gap_days=3)
print(f'✅ Config: threshold={config.similarity_threshold}, max_gap={config.max_time_gap_days}')
"

# 3. 验证 ClusterManager 实例化
python -c "
from memory_layer.cluster_manager import ClusterManager, ClusterManagerConfig
config = ClusterManagerConfig()
cm = ClusterManager(config)
print('✅ ClusterManager OK')
"

# 4. 验证存储接口
python -c "
from memory_layer.cluster_manager import InMemoryClusterStorage
import asyncio

async def test():
    storage = InMemoryClusterStorage()
    await storage.save_cluster_state('test_group', {'eventid_to_cluster': {'evt1': 'c1'}})
    state = await storage.load_cluster_state('test_group')
    print(f'✅ Storage OK: {state}')

asyncio.run(test())
"

# 5. 运行完整测试（如果存在）
pytest src/memory_layer/cluster_manager/tests/ -v

# 6. 验证配置验证逻辑
python -c "
from memory_layer.cluster_manager import ClusterManagerConfig
try:
    ClusterManagerConfig(similarity_threshold=1.5)  # 应该失败
except ValueError as e:
    print(f'✅ Validation works: {e}')
"
```

## 示例场景

### 场景 1: 对话聚类

```python
from memory_layer.cluster_manager import ClusterManager, ClusterManagerConfig
from memory_layer.memcell_extractor.conv_memcell_extractor import ConvMemCellExtractor
from memory_layer.llm import create_provider_from_env

# 1. 初始化
config = ClusterManagerConfig(
    similarity_threshold=0.7,   # 相似度阈值
    max_time_gap_days=3,        # 3 天内的对话可聚类
    clustering_algorithm="centroid"
)
cluster_mgr = ClusterManager(config)

# 2. 注册回调（例如触发画像提取）
async def trigger_profile_extraction(group_id, memcell, cluster_id, recent_memcells):
    if len(recent_memcells) >= 3:  # 聚类达到 3 个 MemCell
        print(f"触发画像提取: {cluster_id}")
        # await profile_manager.extract_profile(recent_memcells)

cluster_mgr.on_cluster_assigned(trigger_profile_extraction)

# 3. 附加到 MemCellExtractor
llm = create_provider_from_env("openai")
extractor = ConvMemCellExtractor(llm)
cluster_mgr.attach_to_extractor(extractor)

# 4. 提取 MemCell（自动聚类）
memcell, status = await extractor.extract_memcell(request)
# → 自动分配聚类 ID，触发回调
```

### 场景 2: 手动聚类分配

```python
import numpy as np

# 1. 创建 ClusterManager
cluster_mgr = ClusterManager()

# 2. 手动分配聚类（提供 embedding）
cluster_id = await cluster_mgr.assign_cluster(
    group_id="team_chat",
    memcell={
        "event_id": "evt123",
        "summary": "讨论 Q4 OKR",
        "timestamp": 1699999999.0
    },
    embedding=np.random.rand(768)  # 768 维向量
)

print(f"分配到聚类: {cluster_id}")

# 3. 查询聚类信息
info = await cluster_mgr.get_cluster_info("team_chat", cluster_id)
print(f"聚类包含 {info['count']} 个 MemCell")
```

### 场景 3: 持久化聚类状态

```python
from pathlib import Path

# 1. 启用持久化
config = ClusterManagerConfig(
    enable_persistence=True,
    persist_dir="./data/clusters"
)
cluster_mgr = ClusterManager(config)

# 2. 分配聚类（自动保存到磁盘）
await cluster_mgr.assign_cluster(
    group_id="project_alpha",
    memcell={...}
)

# 3. 重启后自动加载
# ClusterManager 初始化时会从 persist_dir 加载历史状态
cluster_mgr_new = ClusterManager(config)
# 历史聚类状态已恢复

# 4. 查看持久化文件
# ls ./data/clusters/
# cluster_state_project_alpha.json
# cluster_map_project_alpha.json
```

## 性能优化

**向量缓存**：
- ClusterManager 内部缓存向量，避免重复提取

**算法选择**：
- 小规模数据（< 1000 MemCells）：使用 `centroid`
- 大规模数据（> 1000 MemCells）：考虑外部向量数据库（Milvus/Pinecone）

**时间复杂度**：
- Centroid 算法：O(K)，K 为聚类数
- Nearest 算法：O(N)，N 为总 MemCell 数

## 扩展阅读

- **ProfileManager 集成**：`specs/ac_mod/memory_layer.profile_manager.ac.mod.md`
- **向量化服务**：`specs/ac_mod/agentic_layer.vectorize_service.ac.mod.md`（待创建）
- **MemCellExtractor**：`specs/ac_mod/memory_layer.memcell_extractor.ac.mod.md`（待创建）

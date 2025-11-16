# memory_layer.profile_manager

用户画像自动提取与管理器，基于聚类MemCell自动生成、更新、过滤高质量用户画像

## 模块位置

**源码路径**: `src/memory_layer/profile_manager/`
**文档路径**: `specs/ac_mod/memory_layer.profile_manager.ac.mod.md`
**模块类型**: 包模块

## 目录结构

```
src/memory_layer/profile_manager/
├── __init__.py                 # 导出 ProfileManager, Config, Discriminator, Storage
├── manager.py                  # ProfileManager 核心实现
├── config.py                   # ProfileManagerConfig, ScenarioType
├── discriminator.py            # ValueDiscriminator（LLM 判断画像价值）
├── storage.py                  # ProfileStorage 抽象和 InMemoryProfileStorage 实现
├── mongo_profile_storage.py    # MongoProfileStorage 实现
└── README.md                   # 模块说明
```

## 快速开始

### 基本使用

```python
from memory_layer.profile_manager import (
    ProfileManager,
    ProfileManagerConfig,
    ScenarioType,
    InMemoryProfileStorage
)
from memory_layer.llm import create_provider_from_env

# 1. 配置 ProfileManager
config = ProfileManagerConfig(
    scenario=ScenarioType.GROUP_CHAT,  # 或 ScenarioType.ASSISTANT
    min_confidence=0.6,                # 最小置信度阈值
    enable_versioning=True,            # 启用版本历史
    auto_extract=True,                 # 自动提取
    batch_size=50                      # 批处理大小
)

# 2. 创建 LLM Provider
llm_provider = create_provider_from_env("openai")

# 3. 初始化存储（可选）
storage = InMemoryProfileStorage(
    enable_persistence=True,
    persist_dir="./profile_data",
    enable_versioning=True
)

# 4. 创建 ProfileManager
profile_mgr = ProfileManager(
    llm_provider=llm_provider,
    config=config,
    storage=storage,
    group_id="team_alpha",
    group_name="Alpha Team"
)

# 5. 手动触发画像提取
await profile_mgr.on_memcell_clustered(
    memcell={"event_id": "evt1", "summary": "讨论项目", ...},
    cluster_id="cluster_001",
    recent_memcells=[...]  # 该聚类中的最近 MemCells
)

# 6. 查询画像
user_profile = await profile_mgr.get_profile("user123")
all_profiles = await profile_mgr.get_all_profiles()
```

### 与 MemCellExtractor 集成

```python
from memory_layer.memcell_extractor.conv_memcell_extractor import ConvMemCellExtractor

# 1. 创建 MemCellExtractor
memcell_extractor = ConvMemCellExtractor(llm_provider)

# 2. 附加 ProfileManager（自动监听 MemCell 提取事件）
profile_mgr.attach_to_extractor(memcell_extractor)

# 3. 提取 MemCell 时自动触发画像更新
memcell, status = await memcell_extractor.extract_memcell(request)
# → ProfileManager 自动判断价值、提取画像、合并更新
```

### 与 ClusterManager 联动

```python
from memory_layer.cluster_manager import ClusterManager, ClusterManagerConfig

# 1. 创建 ClusterManager
cluster_config = ClusterManagerConfig(similarity_threshold=0.7)
cluster_mgr = ClusterManager(cluster_config)

# 2. ProfileManager 监听聚类事件
cluster_mgr.on_cluster_assigned(profile_mgr.on_memcell_clustered)

# 3. 当 MemCell 被分配到聚类时，自动触发画像提取
await cluster_mgr.assign_cluster(group_id, memcell, embedding)
# → ProfileManager.on_memcell_clustered() 被调用
```

## 核心组件详解

### 1. ProfileManager 类

**功能**：
- **价值判别**：通过 ValueDiscriminator 判断 MemCell 是否包含画像信息
- **自动提取**：达到阈值（默认 ≥1 个 MemCell）时触发画像提取
- **增量合并**：将新提取的画像与历史画像合并
- **版本管理**：保留画像历史版本（可选）

**主要方法**：

| 方法 | 功能 | 参数 | 返回值 |
|------|------|------|--------|
| `attach_to_extractor()` | 附加到 MemCellExtractor | extractor | - |
| `on_memcell_clustered()` | 聚类事件回调 | memcell, cluster_id, recent_memcells | - |
| `get_profile()` | 获取用户画像 | user_id | ProfileMemory |
| `get_all_profiles()` | 获取所有画像 | - | Dict[user_id, ProfileMemory] |
| `get_profile_history()` | 获取画像历史 | user_id, limit(可选) | List[Dict] |

**工作流程**：
```
MemCell 聚类
    ↓
ValueDiscriminator 判断价值
    ↓ (高价值)
ProfileMemoryExtractor 提取画像
    ↓
ProfileMemoryMerger 合并历史画像
    ↓
ProfileStorage 持久化
    ↓
版本历史记录（可选）
```

### 2. ProfileManagerConfig 配置

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `scenario` | ScenarioType | GROUP_CHAT | 场景类型（GROUP_CHAT/ASSISTANT） |
| `min_confidence` | float | 0.6 | 最小置信度阈值（0.0-1.0） |
| `enable_versioning` | bool | True | 启用版本历史 |
| `auto_extract` | bool | True | 自动提取画像 |
| `batch_size` | int | 50 | 批处理大小 |
| `max_retries` | int | 3 | 最大重试次数 |

**ScenarioType 枚举**：
- **GROUP_CHAT**: 工作/群聊场景（关注角色、技能、项目）
- **ASSISTANT**: 助手/陪伴场景（关注稳定特质、偏好、性格）

### 3. ValueDiscriminator 价值判别器

**功能**：
- 使用 LLM 判断 MemCell 是否包含高价值画像信息
- 支持上下文窗口（previous memcells）
- 返回置信度和理由

**判别维度**（GROUP_CHAT）：
- 角色/职责声明
- 技能展示/提及
- 项目参与
- 工作习惯和偏好
- 性格指标
- 决策模式

**判别维度**（ASSISTANT）：
- 稳定个人特质
- 持久偏好
- 性格维度
- 决策风格
- 习惯和惯例

**方法**：
```python
is_high, confidence, reason = await discriminator.is_high_value(
    latest_memcell=memcell,
    recent_memcells=[prev1, prev2]
)
# 返回: (True, 0.85, "包含明确的技能声明")
```

### 4. ProfileStorage 抽象

**接口定义**：
```python
class ProfileStorage(ABC):
    async def save_profile(user_id: str, profile: Any, metadata: Optional[Dict]) -> bool
    async def get_profile(user_id: str) -> Optional[Any]
    async def get_all_profiles() -> Dict[str, Any]
    async def get_profile_history(user_id: str, limit: Optional[int]) -> List[Dict]
    async def clear() -> bool
```

**实现类**：
- **InMemoryProfileStorage**: 内存 + JSON 文件（可选）
- **MongoProfileStorage**: MongoDB 持久化

**元数据字段**：
```python
metadata = {
    "cluster_id": "cluster_001",
    "confidence": 0.85,
    "timestamp": "2024-11-16T12:00:00Z",
    "memcell_count": 5,
    "version": 3
}
```

### 5. ProfileMemoryExtractor 集成

ProfileManager 内部使用 `ProfileMemoryExtractor` 提取画像：

```python
# ProfileManager 内部调用
extractor = ProfileMemoryExtractor(llm_provider)
request = ProfileMemoryExtractRequest(
    memcell_list=recent_memcells,
    user_id_list=user_ids,
    group_id=group_id,
    old_memory_list=old_profiles
)
new_profiles = await extractor.extract_memory(request)
```

详见：`specs/ac_mod/memory_layer.memory_extractor.profile_memory.ac.mod.md`

## Mermaid 依赖图

```mermaid
graph TB
    PM[ProfileManager<br/>画像管理器]
    Config[config.py<br/>配置类]
    Disc[discriminator.py<br/>价值判别器]
    Storage[storage.py<br/>存储抽象]
    InMemStorage[InMemoryProfileStorage<br/>内存存储]
    MongoStorage[MongoProfileStorage<br/>MongoDB存储]
    Extractor[ProfileMemoryExtractor<br/>画像提取器]
    Merger[ProfileMemoryMerger<br/>画像合并器]
    LLM[llm.LLMProvider<br/>LLM接口]
    MemCellExt[memcell_extractor<br/>MemCell提取器]
    ClusterMgr[cluster_manager<br/>聚类管理器]

    PM --> Config
    PM --> Disc
    PM --> Storage
    PM --> Extractor
    PM --> Merger
    Storage <|-- InMemStorage
    Storage <|-- MongoStorage
    Disc --> LLM
    Extractor --> LLM
    MemCellExt -->|attach| PM
    ClusterMgr -.->|callback| PM

    classDef coreClass fill:#e1f5fe,stroke:#0277bd,stroke-width:2px
    classDef subClass fill:#f3e5f5,stroke:#7b1fa2,stroke-width:1px
    classDef extClass fill:#fff3e0,stroke:#f57c00,stroke-width:1px

    class PM coreClass
    class Config,Disc,Storage subClass
    class InMemStorage,MongoStorage,Extractor,Merger,LLM extClass
    class MemCellExt,ClusterMgr extClass
```

## 依赖关系说明

### 对其他模块的依赖

通过 Grep 验证：
```bash
grep -rn "^from " src/memory_layer/profile_manager/*.py | grep -v "^from memory_layer.profile_manager"
```

**结果**：
- `memory_layer.llm.llm_provider`: LLMProvider
- `memory_layer.memory_extractor.profile_memory_extractor`: ProfileMemoryExtractor, ProfileMemoryExtractRequest
- `core.observation.logger`: 日志记录
- `common_utils.datetime_utils`: 时间格式化

**文档引用**：
- `specs/ac_mod/memory_layer.llm.ac.mod.md`
- `specs/ac_mod/memory_layer.memory_extractor.profile_memory.ac.mod.md`

### 被依赖关系

通过 Grep 验证：
```bash
grep -rn "from memory_layer.profile_manager\|import.*ProfileManager" src/
```

**结果**：
- 目前无外部直接依赖（设计为可选组件）
- 通常与 ClusterManager 联动使用

## 可运行的测试命令

```bash
# 1. 验证导入
python -c "from memory_layer.profile_manager import ProfileManager, ProfileManagerConfig, ScenarioType; print('✅ Import OK')"

# 2. 验证配置创建
python -c "
from memory_layer.profile_manager import ProfileManagerConfig, ScenarioType
config = ProfileManagerConfig(scenario=ScenarioType.ASSISTANT, min_confidence=0.7)
print(f'✅ Config: scenario={config.scenario.value}, min_confidence={config.min_confidence}')
"

# 3. 验证 ProfileManager 实例化
python -c "
from memory_layer.profile_manager import ProfileManager, ProfileManagerConfig
from memory_layer.llm import create_provider
import asyncio

async def test():
    llm = create_provider('openai', api_key='test', base_url='http://localhost')
    config = ProfileManagerConfig()
    pm = ProfileManager(llm, config)
    print('✅ ProfileManager OK')

asyncio.run(test())
"

# 4. 验证 ValueDiscriminator
python -c "
from memory_layer.profile_manager import ValueDiscriminator, DiscriminatorConfig
from memory_layer.llm import create_provider

llm = create_provider('openai', api_key='test', base_url='http://localhost')
config = DiscriminatorConfig(min_confidence=0.7)
disc = ValueDiscriminator(llm, config, scenario='group_chat')
print('✅ ValueDiscriminator OK')
"

# 5. 验证存储接口
python -c "
from memory_layer.profile_manager import InMemoryProfileStorage
import asyncio

async def test():
    storage = InMemoryProfileStorage()
    await storage.save_profile('user1', {'name': 'Alice'}, {'confidence': 0.9})
    profile = await storage.get_profile('user1')
    print(f'✅ Storage OK: {profile}')

asyncio.run(test())
"

# 6. 运行完整测试（如果存在）
pytest src/memory_layer/profile_manager/tests/ -v
```

## 示例场景

### 场景 1: 群聊画像自动提取

```python
from memory_layer.profile_manager import ProfileManager, ProfileManagerConfig, ScenarioType
from memory_layer.cluster_manager import ClusterManager, ClusterManagerConfig
from memory_layer.memcell_extractor.conv_memcell_extractor import ConvMemCellExtractor
from memory_layer.llm import create_provider_from_env

# 1. 初始化组件
llm = create_provider_from_env("openai")
memcell_extractor = ConvMemCellExtractor(llm)
cluster_mgr = ClusterManager(ClusterManagerConfig(similarity_threshold=0.7))

# 2. 创建 ProfileManager（群聊场景）
profile_config = ProfileManagerConfig(
    scenario=ScenarioType.GROUP_CHAT,
    min_confidence=0.6,
    enable_versioning=True
)
profile_mgr = ProfileManager(
    llm_provider=llm,
    config=profile_config,
    group_id="team_dev",
    group_name="开发团队"
)

# 3. 集成三者
profile_mgr.attach_to_extractor(memcell_extractor)
cluster_mgr.attach_to_extractor(memcell_extractor)
cluster_mgr.on_cluster_assigned(profile_mgr.on_memcell_clustered)

# 4. 提取 MemCell（自动聚类 + 画像提取）
request = ConversationMemCellExtractRequest(
    history_raw_data_list=[],
    new_raw_data_list=[...],
    user_id_list=["alice", "bob"],
    group_id="team_dev"
)
memcell, status = await memcell_extractor.extract_memcell(request)

# → 自动聚类、判断价值、提取画像

# 5. 查询画像
alice_profile = await profile_mgr.get_profile("alice")
print(alice_profile.to_dict())
```

### 场景 2: 助手场景画像

```python
# 1. 助手场景配置
profile_config = ProfileManagerConfig(
    scenario=ScenarioType.ASSISTANT,  # 关注稳定特质、偏好
    min_confidence=0.7,
    auto_extract=True
)

profile_mgr = ProfileManager(
    llm_provider=llm,
    config=profile_config,
    group_id="user_alice"
)

# 2. 手动触发画像提取
await profile_mgr.on_memcell_clustered(
    memcell={"event_id": "evt1", "summary": "用户分享了旅行偏好", ...},
    cluster_id="cluster_prefs",
    recent_memcells=[...]
)

# 3. 查看画像历史
history = await profile_mgr.get_profile_history("alice", limit=5)
for version in history:
    print(f"Version {version['version']}: {version['timestamp']}")
```

### 场景 3: 价值判别调试

```python
from memory_layer.profile_manager import ValueDiscriminator, DiscriminatorConfig

# 1. 创建 Discriminator
config = DiscriminatorConfig(
    min_confidence=0.6,
    use_context=True,
    context_window=2
)
discriminator = ValueDiscriminator(llm, config, scenario="group_chat")

# 2. 判断 MemCell 价值
latest_memcell = {
    "event_id": "evt1",
    "summary": "Alice 提到她负责后端开发",
    "episode": "Alice: 我主要负责后端 API 开发，用 Python 写的"
}

is_high, confidence, reason = await discriminator.is_high_value(
    latest_memcell=latest_memcell,
    recent_memcells=[]
)

print(f"高价值: {is_high}, 置信度: {confidence}, 原因: {reason}")
# 输出: 高价值: True, 置信度: 0.9, 原因: 包含明确的角色和技能声明
```

### 场景 4: 持久化画像管理

```python
from pathlib import Path

# 1. 启用持久化
storage = InMemoryProfileStorage(
    enable_persistence=True,
    persist_dir="./data/profiles",
    enable_versioning=True
)

profile_mgr = ProfileManager(
    llm_provider=llm,
    config=profile_config,
    storage=storage,
    group_id="team_dev"
)

# 2. 保存画像（自动持久化到磁盘）
await profile_mgr.on_memcell_clustered(...)

# 3. 重启后自动加载
# ProfileManager 初始化时会从 persist_dir 加载历史画像

# 4. 查看持久化文件
# ls ./data/profiles/
# profile_alice.json
# profile_bob.json
```

## 性能优化

**批处理**：
- `batch_size` 控制单次处理的 MemCell 数量
- 避免单次提取过多画像导致 LLM 超时

**缓存**：
- ProfileStorage 内部缓存最新画像，避免重复读取

**阈值调优**：
- `min_confidence` 越高，画像越精准但更新频率越低
- 推荐值：GROUP_CHAT=0.6, ASSISTANT=0.7

**版本历史限制**：
- `enable_versioning=True` 时，定期清理旧版本
- 建议保留最近 10 个版本

## 扩展阅读

- **ProfileMemoryExtractor**：`specs/ac_mod/memory_layer.memory_extractor.profile_memory.ac.mod.md`
- **ClusterManager**：`specs/ac_mod/memory_layer.cluster_manager.ac.mod.md`
- **LLM Provider**：`specs/ac_mod/memory_layer.llm.ac.mod.md`

# EverMemOS ac_mod 文档编写最终计划

## 调整说明

**排除项**:
- ❌ migrations 相关包 (3个)
- ❌ devops_scripts 相关包 (2个)
- ❌ core/oxm/*/migration 相关包 (2个)
- ❌ infra_layer/scripts/migrations (1个)
- ❌ 测试和示例代码

**调整后总计**: 74 个包需要编写文档

---

## 文档编写清单

### 📦 第1批: core 核心层 - 基础设施 (20个)

| 序号 | 模块路径 | 文档路径 |
|------|---------|---------|
| 1 | `core/di` | `specs/ac_mod/core.di.ac.mod.md` |
| 2 | `core/context` | `specs/ac_mod/core.context.ac.mod.md` |
| 3 | `core/config` | `specs/ac_mod/core.config.ac.mod.md` |
| 4 | `core/constants` | `specs/ac_mod/core.constants.ac.mod.md` |
| 5 | `core/class_annotations` | `specs/ac_mod/core.class_annotations.ac.mod.md` |
| 6 | `core/authorize` | `specs/ac_mod/core.authorize.ac.mod.md` |
| 7 | `core/middleware` | `specs/ac_mod/core.middleware.ac.mod.md` |
| 8 | `core/interface` | `specs/ac_mod/core.interface.ac.mod.md` |
| 9 | `core/interface/controller` | `specs/ac_mod/core.interface.controller.ac.mod.md` |
| 10 | `core/interface/controller/debug` | `specs/ac_mod/core.interface.controller.debug.ac.mod.md` |
| 11 | `core/lifespan` | `specs/ac_mod/core.lifespan.ac.mod.md` |
| 12 | `core/asynctasks` | `specs/ac_mod/core.asynctasks.ac.mod.md` |
| 13 | `core/longjob` | `specs/ac_mod/core.longjob.ac.mod.md` |
| 14 | `core/lock` | `specs/ac_mod/core.lock.ac.mod.md` |
| 15 | `core/rate_limit` | `specs/ac_mod/core.rate_limit.ac.mod.md` |
| 16 | `core/nlp` | `specs/ac_mod/core.nlp.ac.mod.md` |
| 17 | `core/observation/tracing` | `specs/ac_mod/core.observation.tracing.ac.mod.md` |
| 18 | `core/capability` | `specs/ac_mod/core.capability.ac.mod.md` |
| 19 | `core/capability/configuration` | `specs/ac_mod/core.capability.configuration.ac.mod.md` |
| 20 | `core/capability/logging` | `specs/ac_mod/core.capability.logging.ac.mod.md` |

### 📦 第2批: core 核心层 - ORM (6个)

| 序号 | 模块路径 | 文档路径 |
|------|---------|---------|
| 21 | `core/oxm` | `specs/ac_mod/core.oxm.ac.mod.md` |
| 22 | `core/oxm/pg` | `specs/ac_mod/core.oxm.pg.ac.mod.md` |
| 23 | `core/oxm/mongo` | `specs/ac_mod/core.oxm.mongo.ac.mod.md` |
| 24 | `core/oxm/es` | `specs/ac_mod/core.oxm.es.ac.mod.md` |
| 25 | `core/oxm/milvus` | `specs/ac_mod/core.oxm.milvus.ac.mod.md` |

### 📦 第3批: core 核心层 - 队列和缓存 (5个)

| 序号 | 模块路径 | 文档路径 |
|------|---------|---------|
| 26 | `core/cache` | `specs/ac_mod/core.cache.ac.mod.md` |
| 27 | `core/cache/redis_cache_queue` | `specs/ac_mod/core.cache.redis_cache_queue.ac.mod.md` |
| 28 | `core/queue` | `specs/ac_mod/core.queue.ac.mod.md` |
| 29 | `core/queue/msg_group_queue` | `specs/ac_mod/core.queue.msg_group_queue.ac.mod.md` |
| 30 | `core/queue/redis_group_queue` | `specs/ac_mod/core.queue.redis_group_queue.ac.mod.md` |

**core 层小计**: 31个包

---

### 📦 第4批: component 组件层 (4个)

| 序号 | 模块路径 | 文档路径 |
|------|---------|---------|
| 31 | `component` | `specs/ac_mod/component.ac.mod.md` |
| 32 | `component/llm_adapter` | `specs/ac_mod/component.llm_adapter.ac.mod.md` |
| 33 | `component/llm_adapter/llm` | `specs/ac_mod/component.llm_adapter.llm.ac.mod.md` |
| 34 | `common_utils` | `specs/ac_mod/common_utils.ac.mod.md` |

---

### 📦 第5批: infra_layer - 输入适配器 (10个)

| 序号 | 模块路径 | 文档路径 |
|------|---------|---------|
| 35 | `infra_layer` | `specs/ac_mod/infra_layer.ac.mod.md` |
| 36 | `infra_layer/adapters` | `specs/ac_mod/infra_layer.adapters.ac.mod.md` |
| 37 | `infra_layer/adapters/input` | `specs/ac_mod/infra_layer.adapters.input.ac.mod.md` |
| 38 | `infra_layer/adapters/input/api` | `specs/ac_mod/infra_layer.adapters.input.api.ac.mod.md` |
| 39 | `infra_layer/adapters/input/api/dto` | `specs/ac_mod/infra_layer.adapters.input.api.dto.ac.mod.md` |
| 40 | `infra_layer/adapters/input/api/mapper` | `specs/ac_mod/infra_layer.adapters.input.api.mapper.ac.mod.md` |
| 41 | `infra_layer/adapters/input/api/v2` | `specs/ac_mod/infra_layer.adapters.input.api.v2.ac.mod.md` |
| 42 | `infra_layer/adapters/input/jobs` | `specs/ac_mod/infra_layer.adapters.input.jobs.ac.mod.md` |
| 43 | `infra_layer/adapters/input/mcp` | `specs/ac_mod/infra_layer.adapters.input.mcp.ac.mod.md` |
| 44 | `infra_layer/adapters/input/mq` | `specs/ac_mod/infra_layer.adapters.input.mq.ac.mod.md` |
| 45 | `infra_layer/adapters/input/mq/mapper` | `specs/ac_mod/infra_layer.adapters.input.mq.mapper.ac.mod.md` |

### 📦 第6批: infra_layer - 持久化 (4个)

| 序号 | 模块路径 | 文档路径 |
|------|---------|---------|
| 46 | `infra_layer/adapters/out/persistence/document` | `specs/ac_mod/infra_layer.adapters.out.persistence.document.ac.mod.md` |
| 47 | `infra_layer/adapters/out/persistence/document/memory` | `specs/ac_mod/infra_layer.adapters.out.persistence.document.memory.ac.mod.md` |
| 48 | `infra_layer/adapters/out/persistence/mapper` | `specs/ac_mod/infra_layer.adapters.out.persistence.mapper.ac.mod.md` |
| 49 | `infra_layer/adapters/out/persistence/repository` | `specs/ac_mod/infra_layer.adapters.out.persistence.repository.ac.mod.md` |

### 📦 第7批: infra_layer - 搜索 (9个)

| 序号 | 模块路径 | 文档路径 |
|------|---------|---------|
| 50 | `infra_layer/adapters/out/search` | `specs/ac_mod/infra_layer.adapters.out.search.ac.mod.md` |
| 51 | `infra_layer/adapters/out/search/elasticsearch` | `specs/ac_mod/infra_layer.adapters.out.search.elasticsearch.ac.mod.md` |
| 52 | `infra_layer/adapters/out/search/elasticsearch/converter` | `specs/ac_mod/infra_layer.adapters.out.search.elasticsearch.converter.ac.mod.md` |
| 53 | `infra_layer/adapters/out/search/elasticsearch/memory` | `specs/ac_mod/infra_layer.adapters.out.search.elasticsearch.memory.ac.mod.md` |
| 54 | `infra_layer/adapters/out/search/milvus` | `specs/ac_mod/infra_layer.adapters.out.search.milvus.ac.mod.md` |
| 55 | `infra_layer/adapters/out/search/milvus/converter` | `specs/ac_mod/infra_layer.adapters.out.search.milvus.converter.ac.mod.md` |
| 56 | `infra_layer/adapters/out/search/milvus/memory` | `specs/ac_mod/infra_layer.adapters.out.search.milvus.memory.ac.mod.md` |
| 57 | `infra_layer/adapters/out/search/mapper` | `specs/ac_mod/infra_layer.adapters.out.search.mapper.ac.mod.md` |
| 58 | `infra_layer/adapters/out/search/repository` | `specs/ac_mod/infra_layer.adapters.out.search.repository.ac.mod.md` |

### 📦 第8批: infra_layer - 其他 (2个)

| 序号 | 模块路径 | 文档路径 |
|------|---------|---------|
| 59 | `infra_layer/log` | `specs/ac_mod/infra_layer.log.ac.mod.md` |
| 60 | `infra_layer/scripts` | `specs/ac_mod/infra_layer.scripts.ac.mod.md` |

**infra_layer 层小计**: 25个包

---

### 📦 第9批: memory_layer - 核心 (4个)

| 序号 | 模块路径 | 文档路径 |
|------|---------|---------|
| 61 | `memory_layer` | `specs/ac_mod/memory_layer.ac.mod.md` |
| 62 | `memory_layer/cluster_manager` | `specs/ac_mod/memory_layer.cluster_manager.ac.mod.md` |
| 63 | `memory_layer/profile_manager` | `specs/ac_mod/memory_layer.profile_manager.ac.mod.md` |
| 64 | `memory_layer/llm` | `specs/ac_mod/memory_layer.llm.ac.mod.md` |

### 📦 第10批: memory_layer - 提取器 (2个)

| 序号 | 模块路径 | 文档路径 |
|------|---------|---------|
| 65 | `memory_layer/memory_extractor/group_profile` | `specs/ac_mod/memory_layer.memory_extractor.group_profile.ac.mod.md` |
| 66 | `memory_layer/memory_extractor/profile_memory` | `specs/ac_mod/memory_layer.memory_extractor.profile_memory.ac.mod.md` |

### 📦 第11批: memory_layer - 提示词 (4个)

| 序号 | 模块路径 | 文档路径 |
|------|---------|---------|
| 67 | `memory_layer/prompts` | `specs/ac_mod/memory_layer.prompts.ac.mod.md` |
| 68 | `memory_layer/prompts/en` | `specs/ac_mod/memory_layer.prompts.en.ac.mod.md` |
| 69 | `memory_layer/prompts/zh` | `specs/ac_mod/memory_layer.prompts.zh.ac.mod.md` |
| 70 | `memory_layer/prompts/eval` | `specs/ac_mod/memory_layer.prompts.eval.ac.mod.md` |

**memory_layer 层小计**: 10个包

---

### 📦 第12批: agentic_layer (2个)

| 序号 | 模块路径 | 文档路径 |
|------|---------|---------|
| 71 | `agentic_layer` | `specs/ac_mod/agentic_layer.ac.mod.md` |
| 72 | `agentic_layer/dtos` | `specs/ac_mod/agentic_layer.dtos.ac.mod.md` |

---

### 📦 第13批: 配置层 (1个)

| 序号 | 模块路径 | 文档路径 |
|------|---------|---------|
| 73 | `config` | `specs/ac_mod/config.ac.mod.md` |

---

### 📦 第14批: 根目录 (1个)

| 序号 | 模块路径 | 文档路径 |
|------|---------|---------|
| 74 | `src` | `specs/ac_mod/src.ac.mod.md` |

---

## 最终统计

| 分层 | 包数量 |
|------|-------|
| core 核心层 | 31 |
| infra_layer 基础设施层 | 25 |
| memory_layer 记忆层 | 10 |
| component 组件层 | 4 |
| agentic_layer 智能体层 | 2 |
| 配置层 | 1 |
| 根目录 | 1 |
| **总计** | **74** |

---

## 执行策略

**分批执行原则**:
1. 自下而上：基础模块 → 上层模块
2. 每批完成后提交一次
3. 严格遵循 `specs/doc_rules.md` 和 `specs/ac_mod.md`
4. 所有文档保存在 `specs/ac_mod/` 目录

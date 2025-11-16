# EverMemOS ac_mod 文档编写清单

## 项目概览

**源码路径**: `src/`
**文档存放**: `specs/ac_mod/`
**总计包数**: 82 个
**Python 文件**: 332 个

---

## 文档编写清单

### 📦 第1批: 根目录模块 (1个)

| 序号 | 模块路径 | 文档路径 | 模块类型 | 包含文件数 |
|------|---------|---------|---------|-----------|
| 1 | `src` | `specs/ac_mod/src.ac.mod.md` | 根包 | 10个py文件 |

**主要文件**: manage.py, project_meta.py, longjob_runner.py, base_app.py, app.py 等

---

### 📦 第2批: core 核心层 - 基础设施 (18个)

| 序号 | 模块路径 | 文档路径 | 功能说明 |
|------|---------|---------|---------|
| 2 | `core/di` | `specs/ac_mod/core.di.ac.mod.md` | 依赖注入容器 |
| 3 | `core/context` | `specs/ac_mod/core.context.ac.mod.md` | 上下文管理 |
| 4 | `core/config` | `specs/ac_mod/core.config.ac.mod.md` | 配置管理 |
| 5 | `core/constants` | `specs/ac_mod/core.constants.ac.mod.md` | 常量和错误定义 |
| 6 | `core/class_annotations` | `specs/ac_mod/core.class_annotations.ac.mod.md` | 类注解装饰器 |
| 7 | `core/authorize` | `specs/ac_mod/core.authorize.ac.mod.md` | 授权策略 |
| 8 | `core/middleware` | `specs/ac_mod/core.middleware.ac.mod.md` | 中间件 |
| 9 | `core/interface` | `specs/ac_mod/core.interface.ac.mod.md` | 接口层 |
| 10 | `core/interface/controller` | `specs/ac_mod/core.interface.controller.ac.mod.md` | 控制器基类 |
| 11 | `core/interface/controller/debug` | `specs/ac_mod/core.interface.controller.debug.ac.mod.md` | 调试控制器 |
| 12 | `core/lifespan` | `specs/ac_mod/core.lifespan.ac.mod.md` | 生命周期管理 |
| 13 | `core/asynctasks` | `specs/ac_mod/core.asynctasks.ac.mod.md` | 异步任务管理 |
| 14 | `core/longjob` | `specs/ac_mod/core.longjob.ac.mod.md` | 长任务管理 |
| 15 | `core/lock` | `specs/ac_mod/core.lock.ac.mod.md` | 分布式锁 |
| 16 | `core/rate_limit` | `specs/ac_mod/core.rate_limit.ac.mod.md` | 限流器 |
| 17 | `core/nlp` | `specs/ac_mod/core.nlp.ac.mod.md` | NLP工具 |
| 18 | `core/observation/tracing` | `specs/ac_mod/core.observation.tracing.ac.mod.md` | 链路追踪 |
| 19 | `core/capability` | `specs/ac_mod/core.capability.ac.mod.md` | 应用能力 |
| 20 | `core/capability/configuration` | `specs/ac_mod/core.capability.configuration.ac.mod.md` | 能力配置 |
| 21 | `core/capability/logging` | `specs/ac_mod/core.capability.logging.ac.mod.md` | 日志能力 |

---

### 📦 第3批: core 核心层 - ORM 对象关系映射 (8个)

| 序号 | 模块路径 | 文档路径 | 功能说明 |
|------|---------|---------|---------|
| 22 | `core/oxm` | `specs/ac_mod/core.oxm.ac.mod.md` | ORM顶层包 |
| 23 | `core/oxm/pg` | `specs/ac_mod/core.oxm.pg.ac.mod.md` | PostgreSQL ORM |
| 24 | `core/oxm/mongo` | `specs/ac_mod/core.oxm.mongo.ac.mod.md` | MongoDB ORM |
| 25 | `core/oxm/mongo/migration` | `specs/ac_mod/core.oxm.mongo.migration.ac.mod.md` | MongoDB迁移 |
| 26 | `core/oxm/es` | `specs/ac_mod/core.oxm.es.ac.mod.md` | Elasticsearch ORM |
| 27 | `core/oxm/es/migration` | `specs/ac_mod/core.oxm.es.migration.ac.mod.md` | ES迁移工具 |
| 28 | `core/oxm/milvus` | `specs/ac_mod/core.oxm.milvus.ac.mod.md` | Milvus向量库ORM |
| 29 | `core/oxm/milvus/migration` | `specs/ac_mod/core.oxm.milvus.migration.ac.mod.md` | Milvus迁移 |

---

### 📦 第4批: core 核心层 - 队列和缓存 (6个)

| 序号 | 模块路径 | 文档路径 | 功能说明 |
|------|---------|---------|---------|
| 30 | `core/cache` | `specs/ac_mod/core.cache.ac.mod.md` | 缓存管理 |
| 31 | `core/cache/redis_cache_queue` | `specs/ac_mod/core.cache.redis_cache_queue.ac.mod.md` | Redis缓存队列 |
| 32 | `core/queue` | `specs/ac_mod/core.queue.ac.mod.md` | 队列管理 |
| 33 | `core/queue/msg_group_queue` | `specs/ac_mod/core.queue.msg_group_queue.ac.mod.md` | 消息分组队列 |
| 34 | `core/queue/redis_group_queue` | `specs/ac_mod/core.queue.redis_group_queue.ac.mod.md` | Redis分组队列 |

**core 层小计**: 32个包

---

### 📦 第5批: component 组件层 (4个)

| 序号 | 模块路径 | 文档路径 | 功能说明 |
|------|---------|---------|---------|
| 35 | `component` | `specs/ac_mod/component.ac.mod.md` | 组件顶层包 |
| 36 | `component/llm_adapter` | `specs/ac_mod/component.llm_adapter.ac.mod.md` | LLM适配器 |
| 37 | `component/llm_adapter/llm` | `specs/ac_mod/component.llm_adapter.llm.ac.mod.md` | LLM实现 |
| 38 | `common_utils` | `specs/ac_mod/common_utils.ac.mod.md` | 通用工具 |

---

### 📦 第6批: infra_layer 基础设施层 - 输入适配器 (10个)

| 序号 | 模块路径 | 文档路径 | 功能说明 |
|------|---------|---------|---------|
| 39 | `infra_layer` | `specs/ac_mod/infra_layer.ac.mod.md` | 基础设施层顶层 |
| 40 | `infra_layer/adapters` | `specs/ac_mod/infra_layer.adapters.ac.mod.md` | 适配器顶层 |
| 41 | `infra_layer/adapters/input` | `specs/ac_mod/infra_layer.adapters.input.ac.mod.md` | 输入适配器 |
| 42 | `infra_layer/adapters/input/api` | `specs/ac_mod/infra_layer.adapters.input.api.ac.mod.md` | API接口 |
| 43 | `infra_layer/adapters/input/api/dto` | `specs/ac_mod/infra_layer.adapters.input.api.dto.ac.mod.md` | API数据传输对象 |
| 44 | `infra_layer/adapters/input/api/mapper` | `specs/ac_mod/infra_layer.adapters.input.api.mapper.ac.mod.md` | API映射器 |
| 45 | `infra_layer/adapters/input/api/v2` | `specs/ac_mod/infra_layer.adapters.input.api.v2.ac.mod.md` | API v2版本 |
| 46 | `infra_layer/adapters/input/jobs` | `specs/ac_mod/infra_layer.adapters.input.jobs.ac.mod.md` | 任务输入 |
| 47 | `infra_layer/adapters/input/mcp` | `specs/ac_mod/infra_layer.adapters.input.mcp.ac.mod.md` | MCP协议适配 |
| 48 | `infra_layer/adapters/input/mq` | `specs/ac_mod/infra_layer.adapters.input.mq.ac.mod.md` | 消息队列输入 |
| 49 | `infra_layer/adapters/input/mq/mapper` | `specs/ac_mod/infra_layer.adapters.input.mq.mapper.ac.mod.md` | MQ映射器 |

---

### 📦 第7批: infra_layer 基础设施层 - 持久化适配器 (3个)

| 序号 | 模块路径 | 文档路径 | 功能说明 |
|------|---------|---------|---------|
| 50 | `infra_layer/adapters/out/persistence/document` | `specs/ac_mod/infra_layer.adapters.out.persistence.document.ac.mod.md` | 文档模型 |
| 51 | `infra_layer/adapters/out/persistence/document/memory` | `specs/ac_mod/infra_layer.adapters.out.persistence.document.memory.ac.mod.md` | 内存文档模型 |
| 52 | `infra_layer/adapters/out/persistence/mapper` | `specs/ac_mod/infra_layer.adapters.out.persistence.mapper.ac.mod.md` | 持久化映射器 |
| 53 | `infra_layer/adapters/out/persistence/repository` | `specs/ac_mod/infra_layer.adapters.out.persistence.repository.ac.mod.md` | 持久化仓储 |

---

### 📦 第8批: infra_layer 基础设施层 - 搜索适配器 (10个)

| 序号 | 模块路径 | 文档路径 | 功能说明 |
|------|---------|---------|---------|
| 54 | `infra_layer/adapters/out/search` | `specs/ac_mod/infra_layer.adapters.out.search.ac.mod.md` | 搜索适配器 |
| 55 | `infra_layer/adapters/out/search/elasticsearch` | `specs/ac_mod/infra_layer.adapters.out.search.elasticsearch.ac.mod.md` | ES搜索 |
| 56 | `infra_layer/adapters/out/search/elasticsearch/converter` | `specs/ac_mod/infra_layer.adapters.out.search.elasticsearch.converter.ac.mod.md` | ES转换器 |
| 57 | `infra_layer/adapters/out/search/elasticsearch/memory` | `specs/ac_mod/infra_layer.adapters.out.search.elasticsearch.memory.ac.mod.md` | ES内存模型 |
| 58 | `infra_layer/adapters/out/search/milvus` | `specs/ac_mod/infra_layer.adapters.out.search.milvus.ac.mod.md` | Milvus搜索 |
| 59 | `infra_layer/adapters/out/search/milvus/converter` | `specs/ac_mod/infra_layer.adapters.out.search.milvus.converter.ac.mod.md` | Milvus转换器 |
| 60 | `infra_layer/adapters/out/search/milvus/memory` | `specs/ac_mod/infra_layer.adapters.out.search.milvus.memory.ac.mod.md` | Milvus内存模型 |
| 61 | `infra_layer/adapters/out/search/mapper` | `specs/ac_mod/infra_layer.adapters.out.search.mapper.ac.mod.md` | 搜索映射器 |
| 62 | `infra_layer/adapters/out/search/repository` | `specs/ac_mod/infra_layer.adapters.out.search.repository.ac.mod.md` | 搜索仓储 |

---

### 📦 第9批: infra_layer 基础设施层 - 其他 (4个)

| 序号 | 模块路径 | 文档路径 | 功能说明 |
|------|---------|---------|---------|
| 63 | `infra_layer/log` | `specs/ac_mod/infra_layer.log.ac.mod.md` | 日志服务 |
| 64 | `infra_layer/scripts` | `specs/ac_mod/infra_layer.scripts.ac.mod.md` | 脚本工具 |
| 65 | `infra_layer/scripts/migrations` | `specs/ac_mod/infra_layer.scripts.migrations.ac.mod.md` | 迁移脚本 |

**infra_layer 层小计**: 27个包

---

### 📦 第10批: memory_layer 记忆层 - 核心模块 (5个)

| 序号 | 模块路径 | 文档路径 | 功能说明 |
|------|---------|---------|---------|
| 66 | `memory_layer` | `specs/ac_mod/memory_layer.ac.mod.md` | 记忆层顶层 |
| 67 | `memory_layer/cluster_manager` | `specs/ac_mod/memory_layer.cluster_manager.ac.mod.md` | 聚类管理器 |
| 68 | `memory_layer/profile_manager` | `specs/ac_mod/memory_layer.profile_manager.ac.mod.md` | 画像管理器 |
| 69 | `memory_layer/llm` | `specs/ac_mod/memory_layer.llm.ac.mod.md` | LLM集成 |

---

### 📦 第11批: memory_layer 记忆层 - 提取器 (2个)

| 序号 | 模块路径 | 文档路径 | 功能说明 |
|------|---------|---------|---------|
| 70 | `memory_layer/memory_extractor/group_profile` | `specs/ac_mod/memory_layer.memory_extractor.group_profile.ac.mod.md` | 群组画像提取 |
| 71 | `memory_layer/memory_extractor/profile_memory` | `specs/ac_mod/memory_layer.memory_extractor.profile_memory.ac.mod.md` | 个人记忆提取 |

---

### 📦 第12批: memory_layer 记忆层 - 提示词模板 (4个)

| 序号 | 模块路径 | 文档路径 | 功能说明 |
|------|---------|---------|---------|
| 72 | `memory_layer/prompts` | `specs/ac_mod/memory_layer.prompts.ac.mod.md` | 提示词顶层 |
| 73 | `memory_layer/prompts/en` | `specs/ac_mod/memory_layer.prompts.en.ac.mod.md` | 英文提示词 |
| 74 | `memory_layer/prompts/zh` | `specs/ac_mod/memory_layer.prompts.zh.ac.mod.md` | 中文提示词 |
| 75 | `memory_layer/prompts/eval` | `specs/ac_mod/memory_layer.prompts.eval.ac.mod.md` | 评估提示词 |

**memory_layer 层小计**: 10个包

---

### 📦 第13批: agentic_layer 智能体层 (2个)

| 序号 | 模块路径 | 文档路径 | 功能说明 |
|------|---------|---------|---------|
| 76 | `agentic_layer` | `specs/ac_mod/agentic_layer.ac.mod.md` | 智能体层顶层 |
| 77 | `agentic_layer/dtos` | `specs/ac_mod/agentic_layer.dtos.ac.mod.md` | 智能体DTO |

---

### 📦 第14批: 辅助模块 (5个)

| 序号 | 模块路径 | 文档路径 | 功能说明 |
|------|---------|---------|---------|
| 78 | `config` | `specs/ac_mod/config.ac.mod.md` | 配置包 |
| 79 | `migrations` | `specs/ac_mod/migrations.ac.mod.md` | 数据迁移 |
| 80 | `migrations/mongodb` | `specs/ac_mod/migrations.mongodb.ac.mod.md` | MongoDB迁移 |
| 81 | `migrations/postgresql` | `specs/ac_mod/migrations.postgresql.ac.mod.md` | PostgreSQL迁移 |
| 82 | `devops_scripts` | `specs/ac_mod/devops_scripts.ac.mod.md` | 运维脚本 |
| 83 | `devops_scripts/data_fix` | `specs/ac_mod/devops_scripts.data_fix.ac.mod.md` | 数据修复脚本 |

---

## 统计汇总

| 模块分组 | 包数量 |
|---------|-------|
| 根目录 | 1 |
| core 核心层 | 32 |
| component 组件层 | 4 |
| infra_layer 基础设施层 | 27 |
| memory_layer 记忆层 | 10 |
| agentic_layer 智能体层 | 2 |
| 辅助模块 | 6 |
| **总计** | **82** |

---

## 执行策略

### 顺序原则
1. **自下而上**: 先编写基础模块，后编写依赖它们的上层模块
2. **按层级**: 优先完成同一层级的所有模块
3. **关联性**: 相关模块集中编写，便于理解依赖关系

### 批次划分
- 第1-4批: core 核心层 (32个包) - 基础设施
- 第5批: component 组件层 (4个包) - 通用组件
- 第6-9批: infra_layer 基础设施层 (27个包) - 适配器
- 第10-12批: memory_layer 记忆层 (10个包) - 业务核心
- 第13批: agentic_layer 智能体层 (2个包) - 上层应用
- 第14批: 辅助模块 (6个包) - 配置和运维
- 第15批: 根目录 (1个包) - 应用入口

---

## 注意事项

1. ✅ **遵循规范**: 严格按照 `specs/doc_rules.md` 和 `specs/ac_mod.md` 编写
2. ✅ **路径一致**: 文档保存在 `specs/ac_mod/` 目录
3. ✅ **命名规则**: 使用点号分隔的路径作为文件名，如 `core.di.ac.mod.md`
4. ✅ **完整覆盖**: 每个包都需要完整的文档
5. ✅ **依赖准确**: 依赖关系必须基于实际代码分析
6. ✅ **可执行性**: 所有代码示例必须可运行

---

## 待审核项

请审核以下内容：

1. 模块清单是否完整？是否有遗漏的包？
2. 模块分组是否合理？
3. 执行顺序是否需要调整？
4. 是否有特殊的模块需要优先处理？
5. 是否有不需要编写文档的模块（如测试、示例等）？

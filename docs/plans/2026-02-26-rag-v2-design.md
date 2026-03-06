# RAG 知识库 v2 版本需求与演进计划

> 版本：v2.0 | 状态：规划中

---

## 一、项目背景与 V2 目标

在 V1 版本（MVP）中，我们已经成功搭建了单进程的、基于基础语义检索（Top-K）和简单切分的 RAG 核心链路，并提供了 CLI 及基础 Streamlit UI 收口。
V2 版本的核心目标是将当前的“玩具级（Toy）” RAG 升级为**“准工业级（Production-Ready）”** 的高级检索增强生成系统。重点解决 V1 在**复杂文档解析、长尾/复杂问题检索准确率、多轮对话支持**以及**服务化对外暴露**等方面的痛点。

---

## 二、新特性与功能需求 (PRD)

### 2.1 核心模块升级需求

#### 模块一：复杂文档解析与高级分块 (Data Ingestion)
| 编号 | 功能名称 | 描述说明 | 优先级 |
|------|----------|----------|--------|
| F-01 | 多格式文档支持 | 新增对 PDF（重点解决分栏、简单表格或图文混合）、Docx、HTML 及 Web URL 的解析支持。 | P0 |
| F-02 | 语义与结构化分块 (Chunking) | 摒弃单纯的字符截断，支持基于 Markdown 语法的标题层级分块（Header-based分块），或是基于语义边界的分块（Semantic Chunking）。 | P1 |
| F-03 | 数据增量更新与元数据管理 | 支持文档的更新和软删除、去重机制升级，能针对特定来源（Source）附加更丰富的局部和全局元数据。| P1 |

#### 模块二：高级检索与重排 (Advanced Retrieval)
| 编号 | 功能名称 | 描述说明 | 优先级 |
|------|----------|----------|--------|
| F-04 | 混合检索 (Hybrid Search) | 结合基于关键词的明确检索（BM25 倒排索引）与现有的稠密向量（Dense Vector）检索，做多路召回。 | P0 |
| F-05 | 结果重排 (Reranking) | 引入专属的 Reranker 模型（如 BGE-Reranker、Cohere 接口等），对多路召回后的合并候选项进行上下文语义的二次打分和精确截断。 | P0 |
| F-06 | 假设性提问/查询重写 (HyDE/Query Rewrite) | 用 LLM 将用户的模糊提问（Query）扩展或重写为更利于向量匹配的标准形态或假想答案。 | P2 |

#### 模块三：对话管理与生成质量 (Generation & Chain)
| 编号 | 功能名称 | 描述说明 | 优先级 |
|------|----------|----------|--------|
| F-07 | 多轮对话与长期记忆 (Memory) | 提供 Session 维度的会话历史管理。用户的后续追问能够精准引用过往聊天的上下文意图。 | P0 |
| F-08 | 引用高亮与精准溯源 (Citation) | 回答生成时强制要求模型标注具体的引用块（chunk 级别），在前端不仅显示来源文件，还能高亮出处的文本句子。 | P1 |

#### 模块四：系统架构与服务化 (Engineering & Architecture)
| 编号 | 功能名称 | 描述说明 | 优先级 |
|------|----------|----------|--------|
| F-09 | FastAPI 服务化 | 剥离现有的单体脚本形态，基于 FastAPI 给出标准的 RESTful/SSE 接口结构，支持流式内容输出 (Streaming)。 | P0 |
| F-10 | 异步任务隔离 | 将耗时的【文档向量化】等 Ingestion 动作切分到后台异步任务，不在同步 API 接口阻塞。 | P2 |
| F-11 | 测评对比闭环 (Evaluation) | 引入 Ragas（或类似方案），以数据集形式运行评价指标（如 回答忠实度、检索精确率），为持续的 Prompt 调优给出客观数字。| P1 |

---

## 三、架构演进方案设计 (Tech Spec)

### 3.1 核心链路架构变迁
```text
[ V1 基础单体链路 ]
Query -> Text Embedding -> Vector DB (Chroma) -> Context -> LLM Generation

[ V2 高级双路混合架构 ]
                   ┌──> [Query Rewrite 检索词重写] ──┐
                   │                                │
Query -> Router ───┼──> BM25 Keyword Search ────────┼──> 合并与去重 -> Reranker 模型交叉打分 -> Top-K 
                   │                                │                           │
                   └──> Text Embedding Search ──────┘                           v
                                                                          带有 Session 的上下文组装
                                                                                │
                                                            LLM Generation (带精准溯源的流式应答)
```

### 3.2 关键组件技术选型变更
* **API 框架：** 引入 **FastAPI** 负责接口规范化。
* **关键词检索支持：** Elasticsearch/Meilisearch 太重，可采用 **SQLite 的 FTS5** 或者 Python 原生库 **Rank-BM25** 与 ChromaDB 并跑。
* **Reranker：** 选用开源 **BAAI/bge-reranker-base**，支持快速本地部署。
* **评估框架：** 引入 **Ragas** 与 Pytest 的集成，用 LLM 评价 LLM。

---

## 四、开发分期排期 (Roadmap)

考虑到 V2 的实施复杂度，建议分为以下三个 Sprint（周期）：

* **Sprint 1: 基础设施及召回升级** 
  * 引入 FastAPI 构建对外流式查询及文档建库接口。
  * 引入混合检索（实现 BM25 与现存 ChromaDB 的双路并行）。
  * 接入 Reranking 组件。
* **Sprint 2: 数据底座与文档解析升级**
  * 升级文档解析器，加入对 PDF (PyMuPDF / pdfplumber) 及 Docx 格式支持。
  * 落实 Markdown Header 结构的精准分块，优化段落丢失问题。
* **Sprint 3: 对话记忆与前端交互闭环**
  * 完成带 Session 机制的连续对话。
  * 升级 Streamlit UI，接入 FastAPI 的 SSE 流式接口，增加引用标记交互体验。
  * 构建一份黄金评测集并运行初步的 Ragas 自动化评分。

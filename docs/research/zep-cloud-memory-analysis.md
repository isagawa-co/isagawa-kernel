# Zep Cloud Memory Architecture Analysis

**Date:** 2026-04-05
**Backlog:** 001 — Research Zep Cloud Memory for JSONL Execution Log
**Status:** Complete

## Executive Summary

Zep Cloud is a memory layer service for AI agents built on Graphiti, a temporally-aware knowledge graph engine. It uses a three-tier subgraph architecture (episodes, semantic entities, communities) with bi-temporal metadata tracking. Its hybrid retrieval combines semantic embeddings, BM25 keyword search, and graph traversal without LLM calls during retrieval. Zep achieves 94.8% on the DMR benchmark (vs MemGPT's 93.4%) and up to 18.5% accuracy improvements on LongMemEval with 90% latency reduction.

Key insight for the kernel: Zep's temporal invalidation of old facts and non-lossy episodic storage directly map to our JSONL execution log use case.

## Zep Architecture

### Three-Tier Knowledge Graph

1. **Episode Subgraph** — Raw input data (messages, text, JSON). Non-lossy data store from which entities and relations are extracted. Analogous to our proposed JSONL execution log.

2. **Semantic Entity Subgraph** — Extracted entities resolved against existing graph entities. Represents "what we know" at any point in time.

3. **Community Subgraph** — Clusters of strongly connected entities with high-level summarizations. Provides overview-level context without reading all raw data.

### Temporal Model

Zep implements bi-temporal tracking:
- **Chronological timeline** — When events actually happened
- **Transactional timeline** — When data was ingested into the system

Every edge carries explicit temporal metadata: `valid_from`, `valid_to`, `invalid_at`. This enables answering questions like "What was true before X changed?" — a capability our kernel currently lacks.

### Retrieval Strategy: Hybrid (Graph + Vector + BM25)

Three complementary search methods:
- **Full-text search (BM25)** — Word-level similarity
- **Cosine similarity (vector embeddings)** — Semantic similarity
- **Breadth-first graph traversal** — Contextual similarity (proximity in conversation graph)

Reranking uses Reciprocal Rank Fusion (RRF), Maximal Marginal Relevance (MMR), and custom graph-based rerankers. No LLM calls during retrieval — near-constant time access regardless of graph size.

### Memory Consolidation

Graphiti dynamically updates the knowledge graph in a non-lossy manner. When new information contradicts existing facts, old facts are invalidated (not deleted) with temporal markers. Community subgraph provides automatic summarization of entity clusters.

## Kernel Comparison

| Aspect | Zep Cloud | Kernel (Current) |
|--------|-----------|-------------------|
| **Raw storage** | Episode subgraph (non-lossy) | `session_state.json` context key |
| **Structured knowledge** | Entity subgraph (auto-extracted) | `lessons/` modules (manually triggered) |
| **Summarization** | Community subgraph (auto-generated) | None |
| **Temporal tracking** | Bi-temporal with valid_from/valid_to | Single timestamp (last_lesson_timestamp) |
| **Cross-session** | Built-in, graph-persisted | `session_state.json` resume fields |
| **Retrieval** | Hybrid: vector + BM25 + graph traversal | None (lessons are read sequentially) |
| **Enforcement** | None (pure data layer) | Hook-based enforcement (unique to kernel) |
| **Invalidation** | Temporal invalidation of old facts | None (lessons accumulate forever) |

## Gap Analysis

1. **No append-only log** — The kernel has no durable, append-only record of all agent actions. `session_state.json` is mutable and loses history.

2. **No temporal invalidation** — Lessons accumulate without expiration markers. Tiered memory decay (backlog 006) partially addresses this but doesn't track validity windows.

3. **No retrieval strategy** — As lessons grow, there's no way to search or rank them. The agent reads all of them or none.

4. **No entity extraction** — The kernel doesn't automatically extract structured entities from lessons. Pattern keys (backlog 008) are a step in this direction but only capture fingerprints, not relationships.

5. **No summarization layer** — No automatic summarization of lesson clusters for overview context.

## Recommendations

### 1. JSONL Execution Log (High Priority, Medium Effort)

**What:** Implement an append-only JSONL file (`.claude/state/execution_log.jsonl`) that records every significant agent action with timestamps.

**Format:**
```json
{"timestamp": "...", "action": "write", "target": "path", "session_id": "...", "domain": "..."}
{"timestamp": "...", "action": "learn", "pattern_key": "abc123", "issue": "...", "session_id": "..."}
{"timestamp": "...", "action": "anchor", "actions_count": 10, "session_id": "..."}
```

**Rationale from Zep:** Zep's episode subgraph proves that a non-lossy raw data store is the foundation everything else builds on. Without it, you can't do temporal queries, can't replay sessions, can't audit.

**Integration:** Hook the universal-gate-enforcer.py to append to the log on every tracked action.

### 2. Temporal Validity Markers on Lessons (Medium Priority, Low Effort)

**What:** Add `valid_from` and `valid_to` fields to lesson records. When a lesson is superseded (same pattern key, different fix), mark the old one as `valid_to = now`.

**Rationale from Zep:** Zep's key insight is temporal invalidation — facts have lifespans. This directly maps to our lesson problem: a lesson learned 3 months ago may have been superseded by a better understanding.

**Integration:** Extend `LessonRecord` in `lessons/schema.py` with validity fields. Update recurrence tracker to invalidate old entries.

### 3. Lesson Retrieval Index (Low Priority, Medium Effort)

**What:** Build a simple search index over lessons using TF-IDF or BM25 (no external dependencies needed). Enable searching lessons by keyword, pattern key, or tag.

**Rationale from Zep:** Zep's hybrid retrieval demonstrates that as memory grows, retrieval becomes critical. Our current approach (read all lessons) won't scale past 50-100 lessons.

**Integration:** New module `lessons/search.py` with `search_lessons(query: str) -> list` function. Use Python stdlib's difflib or a simple TF-IDF implementation.

### 4. Session-Level Summarization (Low Priority, High Effort)

**What:** At session end, auto-generate a summary of what was accomplished, analogous to Zep's community subgraph.

**Rationale from Zep:** Community subgraph provides overview without reading raw data. Useful for cross-session context that's currently manually written in `context.notes`.

**Integration:** Extend `/kernel/complete` to append a session summary to a summary log.

## Next Steps

1. Implement recommendation 1 (JSONL execution log) as the highest-value, most foundational change
2. Add temporal validity to lessons (recommendation 2) — low effort, compounds with existing recurrence detection
3. Defer recommendations 3 and 4 until lesson count exceeds 50

## Sources

- [Zep: A Temporal Knowledge Graph Architecture for Agent Memory (arXiv)](https://arxiv.org/abs/2501.13956)
- [Zep Cloud Platform](https://www.getzep.com/)
- [Best AI Agent Memory Frameworks 2026 (Atlan)](https://atlan.com/know/best-ai-agent-memory-frameworks-2026/)
- [Graphiti: Knowledge Graph Memory (Neo4j)](https://neo4j.com/blog/developer/graphiti-knowledge-graph-memory/)
- [Mem0 vs Zep Comparison (Vectorize)](https://vectorize.io/articles/mem0-vs-zep)
- [Zep Paper PDF](https://blog.getzep.com/content/files/2025/01/ZEP__USING_KNOWLEDGE_GRAPHS_TO_POWER_LLM_AGENT_MEMORY_2025011700.pdf)

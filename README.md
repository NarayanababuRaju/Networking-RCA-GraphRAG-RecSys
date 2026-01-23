# Networking-RCA-GraphRAG-RecSys

## 🚀 Overview

**Networking-RCA-GraphRAG-RecSys** is an enterprise-grade **Root Cause Analysis (RCA) recommendation system** for large-scale networking infrastructure (ISPs, data centers, cloud backbones).

The system applies **GraphRAG** principles—combining **Knowledge Graph reasoning** with **Vector-based semantic retrieval**—to convert dense, fragmented technical knowledge (IETF RFCs, vendor datasheets, internal runbooks, and SME guidelines) into **actionable, explainable diagnostics**.

It is optimized for **low-latency, high-throughput environments**, using a **C++ core** for event processing and inference orchestration, and **Python-based ML pipelines** for semantic understanding and knowledge construction.

---

## 🎯 Problem Statement

Traditional RCA systems struggle with:

* Fragmented knowledge across RFCs, vendor docs, and tribal expertise
* Keyword-based search that ignores protocol context
* Black-box ML models with poor explainability
* High latency when correlating multi-layer network failures

This project addresses these gaps by:

* Structuring networking knowledge as a **graph of entities and relationships**
* Using **semantic embeddings** for contextual retrieval
* Preserving **causal chains** across protocols, hardware, and configurations
* Producing **human-readable RCA narratives**, not just alerts

---

## 🏗️ High-Level Architecture

The core strategy is "Accuracy, Accuracy, Accuracy." By combining the structured reasoning of a Knowledge Graph with the semantic retrieval of Vector Embeddings, the system can provide context-aware recommendations for complex protocol and hardware failures.


The guiding principle of the system is:

> **Accuracy → Explainability → Performance**

By fusing symbolic reasoning (graphs) with semantic similarity (vectors), the system provides deterministic yet flexible RCA recommendations.

**Core flow:**

1. Technical documents are cleaned and semantically chunked
2. Entities and relationships are extracted and stored in a Knowledge Graph
3. Chunks are embedded and indexed for fast semantic retrieval
4. Incoming alarms/events seed graph traversal and vector search
5. Results are merged into an explainable RCA report


---

## 📂 Project Structure

```text
Networking-RCA-GraphRAG-RecSys/
├── src/
│   ├── indexing/
│   │   ├── data-preprocessing/               # Phase 1: Cleaning & Semantic Chunking
│   │   │   ├── DataCleaner                     # Removing boilerplate (headers, footers, page markers)
│   │   │   ├── Deduplicator                    # Locality Sensitive Hashing (LSH)
│   │   │   ├── DomainNormalizer                # Alias Resolver
│   │   │   └── VersionResolver                 # RegEx based version extraction
│   │   │   ├── ConditionalExtractor            # Python based NLP
│   │   │   ├── NegationTagger                  # Adding Negative-weight
│   │   │   ├── MetadataEnricher                # Adding metadata (Source Type, Authority Score)
│   │   │   ├── TemporalAnnotator               # Enrichment v2.0 (Draft vs Proposed vs Internet Standard)
│   │   │   ├── SemanticChunker                 # Semantic chunking using LLM
│   │   ├── extraction/                       # Phase 2: Entity & Relationship Extraction
│   │   |   ├── DeterministicExtractor          # Regex-based (IPs, ASNs, Interfaces)
│   │   |   ├── SemanticExtractor               # BERT-NER (Behaviors, Causal Triples)
│   │   |   └── Disambiguator                   # Context-aware sense resolution
|   |   |-- graph-engine/                     # Phase 2.5: Graph Engineering
|   |   |   ├── GraphBuilder                    # Graph construction from entities & relationships
│   |   |   └── GraphValidator                  # Graph quality checks (TODO)
│   |   |── semantic-indexing/                # Phase 3: Vector Indexing
│   │   |   ├── Embedder.py                     # Sentence-Transformers (MiniLM)
│   │   |   └── VectorStore                     # Faiss indexing logic (Planned)
│   |   ├── clustering/                       # Phase 4: Graph Communities & Partitioning
│   │   |   ├── Projector.py                    # Spectral Weighting (View Builder)
│   │   |   ├── LeidenEngine.py                 # Standard 2-Level Clustering
│   │   |   ├── LeidenEngineHierarchical.py     # Advanced N-Level Dendrogram Engine
│   │   |   ├── BridgeIdentifier.py             # Inter-Community Bottleneck Detection
│   │   |   ├── DriftDetector.py                # Temporal Stability Analysis
│   │   |   └── Fingerprinter.py                # Deterministic Community Signatures
│   |   |── summarization/                    # Phase 5: Community-level LLM summaries
│   │   |   ├── TopologyFilter.py               # Intra-community PageRank
│   │   |   ├── ContextBuilder.py               # Technical Biography Generation
│   │   |   ├── KnowledgeSynthesizer.py         # LLM Abstractive Synthesis
│   │   |   └── SummaryIndexer.py               # Thematic Vectorization
│   ├── querying/                             # Phase 6: Querying & Inference
│   │   ├── query-processor/                    # Alarm parsing & intent extraction
│   │   ├── search-engine/                      # Faiss-based vector retrieval
│   │   ├── organizer/                          # Graph traversal & reasoning
│   │   └── generator/                          # RCA explanation synthesis
│   └── validator/                            # Phase 7: Accuracy evaluation & SME feedback loop
├── data/
│   ├── raw/                                  # RFCs, datasheets, logs
│   └── processed/                            # Cleaned text, chunks, embeddings
├── docs/
│   └── architecture/
└── README.md
```

---

## 🛠️ Tech Stack

### Core Languages

* **C++17/20** – High-performance ingestion, graph traversal, inference orchestration
* **Python 3.9+** – NLP, ML pipelines, offline indexing

### Storage & Retrieval

* **Graph Database**: FalkorDB

  * C-based implementation
  * GraphBLAS-backed matrix operations for fast traversal
* **Vector Search**: Faiss (Meta)

  * Approximate nearest neighbor search
  * Optimized for sub-millisecond semantic retrieval

### NLP & ML

* **Embeddings**: BERT / Sentence-Transformers
* **Inference**: ONNX Runtime (C++ integration)
* **Clustering**: Community detection over embedding + graph structure

### Parsing & Ingestion

* **PugiXML (C++)** – Structured RFC and XML parsing
* **Docling (Python)** – PDF and datasheet extraction

---

## 🧹 Core Components

### 1. C++ Technical Data Cleaner

* Removes RFC boilerplate (headers, footers, page markers)
* Preserves section hierarchy and numbering
* Normalizes protocol acronyms and aliases
* Ensures deterministic, repeatable preprocessing

**Goal:** produce machine-consumable yet semantically faithful text.

---

### 2. Python Semantic Chunker

* Uses contextual embeddings to detect topic boundaries
* Avoids naive fixed-size chunking
* Keeps protocol workflows (e.g., BGP FSM transitions) intact

**Outcome:** graph nodes represent *concepts*, not arbitrary text slices.

---

### 3. Entity & Relationship Extraction

* Protocols, states, timers, error codes, hardware components
* Relationships such as:

  * *causes*
  * *depends_on*
  * *violates*
  * *mitigated_by*

Extraction is designed to be **schema-light**, allowing evolution as new protocols and vendors are introduced.

* **DeterministicExtractor (C++)**: High-speed identification of structured assets (IPs, ASNs, Interfaces) using optimized Regex.
* **SemanticExtractor (Python)**: BERT-based understanding of abstract behaviors and multi-hop causal relationships.
* **Entity Disambiguator (C++)**: Context-aware resolution of technical polysemy (e.g., distinguishing "Session" in BGP vs. TCP).

**Status:** Fully implemented and integrated into the C++ Graph Engine.

---

### 4. Semantic Embedding Generation

* Uses **all-MiniLM-L6-v2** Sentence-Transformers for local, high-precision vectorization.
* Encodes both **Node Properties** and **Relationship Triples** into a 384-dimensional space.
* Optimized for **Apple Silicon (MPS)** and batch-processing for sub-millisecond per-chunk inference.

**Goal:** Enable sub-millisecond semantic similarity search for "Fuzzy" RCA matching.

---

### 5. Knowledge Graph Reasoning (C++ Graph Engine)

* Graph walking seeded by alarms and symptoms
* Combines:

  * Topological proximity
  * Semantic similarity scores
  * Confidence weighting from document sources

This allows the system to infer **multi-hop causal chains**.

* High-performance adjacency-list storage with **Record Linkage** logic.
* Multi-hop **BFS Traversal API** for discovering causal chains across diverse protocols.
* Fuses symbolic graph logic with vector-based retrieval intent.

---

### 6. Community Detection & Topology Intelligence (Phase 4)

This layer converts the raw Knowledge Graph into high-level "Fault Domains" using advanced unsupervised learning.

*   **Leiden Clustering (Python)**: Discovers dense communities at multiple resolutions (Macro/Micro). Supports both a standard 2-level engine and an N-level **Hierarchical Dendrogram** engine.
*   **Bridge Identification**: Pinpoints "Bottleneck" nodes that act as critical connectors between disparate protocol communities (e.g., OSPF <---> BGP).
*   **Temporal Drift Detector**: Analyzes how community memberships shift between indexing runs, detecting evolving technical faults.
*   **Community Fingerprinting**: Generates deterministic SHA-256 signatures for each domain. Acts as a **Lazy Trigger** to skip re-summarizing unchanged communities, saving 90% in LLM API costs.

**Goal:** Provide the "Intelligence Layer" that allows the system to reason about systemic failures, not just isolated events.

### 7. Community Summarization (Phase 5: The Intelligence Layer)
This phase transforms mathematical clusters into actionable RCA briefs using Generative AI.
- **Topology Filter**: Uses PageRank to focus LLM attention on "Information Hubs."
- **Context Builder**: Aggregates 1-hop relationships to build technical biographies.
- **LLM Synthesis**: Produces structured "Knowledge Briefs" (Title, Summary, Symptoms, Causes).
- **Thematic Indexing**: Makes the summaries searchable via the Unified Vector Registry.
---

### 8. RCA Explanation Generator

* Merges graph paths and retrieved text
* Produces:

  * Probable root causes
  * Supporting evidence
  * Recommended verification steps

Designed for **software-developers/network-engineers**, not just ML practitioners.

---

## 📊 Evaluation & Validation

Accuracy is treated as a first-class concern:

* Synthetic fault-injection scenarios
* Historical incident replay
* SME-in-the-loop validation
* Precision@K and causal-chain correctness metrics

---

## 🛤️ Project Roadmap

* [x] Phase 1: Ingestion & Semantic Chunking
* [x] Phase 2: Entity & Relationship Extraction (Deterministic + Semantic)
* [x] Phase 2b: Knowledge Graph Population (C++ Graph Engine Core)
* [x] Phase 3: Semantic Indexing & Vectorization
* [x] Phase 4: Community Detection (Leiden + Topology Intelligence)
* [x] Phase 5: Community Summarization (LLM Knowledge Briefs)
* [ ] Phase 6: Query Pipeline & RCA Synthesis (Next Step)
* [ ] Phase 7: Benchmarking, SME Review & Hardening

---

## 🛠️ Setup & Local Testing

### Prerequisites

* GCC 9+ or Clang 12+
* Python 3.9+
* CMake (recommended)

### Verify Ingestion Pipeline

```bash
# C++ Cleaner
g++ -std=c++17 src/indexing/data-preprocessing/DataCleaner.cpp -o cleaner
./cleaner

# Python Semantic Chunker
python3 src/indexing/data-preprocessing/SemanticChunker.py
```

---

## ⚠️ Current Limitations

* Entity extraction is under active development
* No real-time streaming integration yet (batch-oriented)
* Limited vendor-specific hardware modeling

---

## 📌 Intended Audience

* Network Reliability Engineers (NREs)
* SREs working on networking layers
* Networking researchers
* Platform teams building RCA or observability systems

---

## 📄 License

TBD (Internal / Research-focused at present)


---
---
name: rag-evaluation
description: Run and interpret the project's RAG regression and evaluation workflows.
---

# RAG evaluation

Use this Skill when changing retrieval, chunking, query rewriting, or answer generation.

1. Read `docs/RAG_EVALUATION.md` and the evaluation notes in `docs/PROJECT_DETAILS.md`.
2. Run focused tests for the changed service, then `uv run pytest -q tests/test_rag.py tests/test_search.py tests/test_evaluation.py`.
3. For an end-to-end evaluation, ensure PostgreSQL, indexed source PDFs, and Ollama are available.
4. Compare a candidate report with a reviewed baseline; do not overwrite the baseline as part of routine evaluation.
5. Report retrieval and answer-quality changes separately, including any regression and its affected cases.

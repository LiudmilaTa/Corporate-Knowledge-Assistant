# RAG Evaluation: Methodology, Results, and Improvement Plan

This document describes the evaluation set and the measured state of the RAG pipeline. It is an engineering benchmark for comparing changes.

## Why Evaluate RAG?

A model's answer can sound convincing even when retrieval found the wrong passages. Looking only at the answer text does not reveal where a failure occurred: retrieval, context assembly, or generation. The evaluation therefore checks these stages separately:

1. **Retrieval:** Did the expected PDF pages appear near the top of the results?
2. **Context and generation:** Was the retrieved context useful, and was the answer grounded, relevant, correct, and complete?

The same labeled dataset can be run after changing chunking, embeddings, ranking, prompts, or models. Comparing runs helps identify regressions and check whether a change improves the intended part of the pipeline.

## Source Documents

The local PDFs used to build the evaluation corpus correspond to the following Czech laws. Page numbers in the dataset refer to pages in the downloaded PDFs, not to statutory section numbers.

| Local PDF | Public text | Main evaluation topics |
| --- | --- | --- |
| `Zákon 326_1999 Sb. (12.6.2026).pdf` | [Act No. 326/1999 Sb. — residence of foreign nationals](https://www.zakonyprolidi.cz/cs/1999-326) | Scope, family reunification, decision periods for study visas and employee cards, job loss, and supplementary documents |
| `Zákon 435_2004 Sb. (1.7.2026).pdf` | [Act No. 435/2004 Sb. — Employment](https://www.zakonyprolidi.cz/cs/2004-435) | The aim of employment policy and participants in employment-law relations |
| `Zákon 500_2004 Sb. (1.7.2025).pdf` | [Act No. 500/2004 Sb. — Administrative Procedure Code](https://www.zakonyprolidi.cz/cs/2004-500) | Duties of administrative authorities, processing without undue delay, and requests to supplement documents |

Questions, reference answers, expected pages, and answerability labels are in [`evals/dataset.json`](../evals/dataset.json). The dataset contains 32 cases in Czech, Russian, and English, including informal practical questions and three questions that cannot be answered from the indexed documents. The dataset is not evenly distributed across languages and laws.

## What Is Measured?

Each question goes through the application's retrieval and answer-generation pipeline. Search returns up to `k` chunks; metrics compare the unique `(filename, PDF page)` pairs represented by those chunks with `expected_sources`. Multiple chunks from the same page count as one source, but the current system does not fetch additional results after deduplication. Therefore, the number of unique pages may be lower than `k`, even though precision is divided by `k`. Cases without expected sources have no numeric retrieval metrics, but the LLM judge evaluates whether the system abstains appropriately.

| Metric | What it measures |
| --- | --- |
| `precision_at_k` | The fraction of the first `k` result positions that are expected relevant pages. |
| `recall_at_k` | The fraction of expected pages found among the sources represented in the top-`k` chunks. |
| `f1_at_k` | The harmonic mean of precision and recall. |
| `mrr` | How highly the first expected page is ranked. |
| `ndcg_at_k` | Ranking quality, with more credit for relevant pages near the top. |
| `hit_rate_at_k` | The proportion of answerable cases with at least one expected page in the first `k` results. |
| `context_precision` / `context_recall` | LLM-judge estimates of how relevant the context is and how well it covers facts in the reference answer. |
| `faithfulness` | The LLM judge's estimate of whether factual claims in the answer are supported by the supplied context. |
| `answer_relevance` | The LLM judge's estimate of how directly the answer addresses the question. |
| `correctness` / `completeness` | LLM-judge estimates of agreement with the reference answer and coverage of its key facts. |

Retrieval metrics are deterministic when the indexed database and configuration are unchanged. Context and answer scores are approximate estimates from Mistral; Mistral is also used to generate the answers in these runs. An LLM judge is not ground truth: using the same model for generation and evaluation can introduce shared biases. Review individual cases and manually inspect a sample before drawing conclusions about quality.

## Latest Measured Results

The local report is saved as `evals/results/trial-fixed.json`.

Configuration: `k=5`, maximum relevant cosine distance `0.6`, multilingual embedding model `paraphrase-multilingual-MiniLM-L12-v2`, `mistral` for generation and judging, chunk size 1,000 characters, and overlap 200. All 32 cases in the current dataset were included.

| Metric | Before exact-section fix (`trial.json`) | After fix (`trial-fixed.json`) | Change |
| --- | ---: | ---: | ---: |
| Precision@5 | 0.083 | 0.097 | +0.014 |
| Recall@5 | 0.362 | 0.431 | +0.069 |
| F1@5 | 0.130 | 0.153 | +0.023 |
| MRR | 0.374 | 0.443 | +0.069 |
| NDCG@5 | 0.342 | 0.411 | +0.069 |
| Hit rate@5 | 0.414 | 0.483 | +0.069 |
| Context precision | 0.184 | 0.231 | +0.047 |
| Context recall | 0.200 | 0.270 | +0.070 |
| Faithfulness | 0.369 | 0.447 | +0.078 |
| Answer relevance | 0.516 | 0.541 | +0.025 |
| Correctness | 0.425 | 0.456 | +0.031 |
| Completeness | 0.238 | 0.288 | +0.050 |

Both reports contain the same 32 case IDs and the same recorded configuration. The code fix changed exact statutory-section matching so that `§ 1` is no longer treated as an exact match for `§ 10`, `§ 175`, or `§ 1a`. The metric increases are consistent with this fix, particularly for ranking, but they are evidence supporting the change—not proof that the remaining retrieval issues have been solved.

The latest run printed `Evaluation gates passed` because it was run **without `--min` thresholds or a baseline comparison**. This only means that evaluation completed; it does not mean the system reached a quality target such as 0.80.

### Results Analysis

- **Retrieval is the main bottleneck.** `Recall@5 = 0.431`; the expected page was absent from the top five in 15 of 29 answerable cases. `Hit rate@5 = 0.483`. Many answers therefore start with incomplete or irrelevant evidence.
- **Retrieved context is weak.** `Context precision = 0.231` and `context recall = 0.270`. This is consistent with low `faithfulness = 0.447` and `completeness = 0.288`: the model often lacks relevant, verifiable passages.
- **Results may contain multiple chunks from one page.** These are deduplicated for metrics, but repeated chunks consume the result/context limit without covering additional pages.
- **Failures occur across languages.** For the English question about the scope of Act No. 326, the expected PDF page is 1, but the top-five results included pages 175/185. Several practical questions about decision periods also missed expected pages 151 or 59. This suggests document-wide ranking and query-term matching issues, not only cross-language retrieval problems.
- **A fluent answer is not necessarily grounded.** High answer relevance alone does not establish factual support. Retrieval, context quality, and generation must be analyzed separately.
- **The dataset is small and uneven.** It is useful for regression testing, but it is not a representative production benchmark. Three unanswerable questions have no expected source page, so retrieval metrics are undefined for them; abstention behavior is assessed primarily by the LLM judge.

## Improvement Plan and Expected Impact

Work from retrieval toward generation so prompt changes do not mask missing evidence.

| Priority | Planned change | Expected impact | How to verify |
| --- | --- | --- | --- |
| 1 | Audit dataset labels, page numbers, and indexed chunks against the exact PDFs; inspect failed cases and the text actually retrieved. Correct any inaccurate labels or page attribution before changing ranking. | More trustworthy recall/precision measurements and correct page citations. | Manually check every case where an expected page was not found; confirm the gold page and corresponding indexed chunk. |
| 2 | Replace the simple lexical score with a well-defined hybrid ranker, such as PostgreSQL full-text/BM25-style lexical retrieval combined with vector retrieval. Treat exact section references as a separate signal. Deduplicate or aggregate candidates by page before assembling context. | Improve Recall@5, HitRate@5, MRR/NDCG; reduce repeated pages; likely improve context precision/recall. | Compare the same dataset and `k`; inspect per-case ranks, not just aggregate metrics. |
| 3 | Evaluate multilingual retrieval separately from query rewriting. Test the embedding model on Czech, Russian, and English variants; if needed, compare a stronger multilingual model or a separately configurable translation/query-expansion stage. | Improve cross-language recall and reduce costly or unreliable Ollama translation calls. | Record model and translation settings; compare metrics by language and measure end-to-end latency. |
| 4 | Add a reranker, such as a multilingual cross-encoder, to reorder a broader candidate set before selecting context. | Primarily improve Precision@5, MRR, NDCG, and context precision. | Compare ranking and latency; first confirm that the broader initial retrieval can find the required source. |
| 5 | Tune chunk boundaries, `k`, the distance threshold, deduplication, and context size using the evaluation set. Re-index after changing chunking or embeddings. | Improve context precision/recall and reduce unsupported answers, while balancing coverage, noise, and latency. | Change one parameter group at a time and compare against an unchanged baseline. |
| 6 | After retrieval improves, refine the answer prompt to require context-grounded claims, cautious abstention when evidence is missing, and clear source references. | Improve faithfulness, correctness, and answer relevance; a prompt cannot compensate for missing retrieved evidence. | Manually review legal answers and abstentions, including conditions and exceptions. |
| 7 | Calibrate the LLM judge against human labels and, if practical, use an independent judge model. Expand and balance the golden set. | Increase confidence in generation-quality measurements and broaden regression coverage; this does not directly improve application answers. | Track judge-human agreement and keep some cases as a stable holdout set. |

Do not set a `0.80` threshold just because it appeared in an example command. Choose thresholds after reviewing the labels and defining a target quality level. A new baseline should be created after the page/label audit and the first retrieval-improvement iteration.

## Re-running the Evaluation

Start PostgreSQL, ensure the exact versions of all three PDFs are indexed, and verify that Ollama is available. Save each new report under a different name rather than overwriting earlier runs:

```powershell
$env:OLLAMA_TIMEOUT = "600"
uv run python -m app.evaluate `
  --dataset evals/dataset.json `
  --output evals/results/candidate.json `
  --k 5
```

The CLI prints progress for each case and pipeline stage. `evals/results/` is excluded from Git because reports contain questions, model-generated answers, and retrieved document text. The aggregate results above are recorded here for reference.

Unit tests for the evaluator that do not require PostgreSQL or Ollama:

```powershell
uv run pytest -q tests/test_evaluation.py tests/test_rag.py
```

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

Retrieval metrics are deterministic when the indexed database, configuration, and any rewritten query are unchanged. Context and answer scores are approximate estimates from Mistral; Mistral is also used to generate the answers in these runs. An LLM judge is not ground truth: using the same model for generation and evaluation can introduce shared biases. Review individual cases and manually inspect a sample before drawing conclusions about quality.

## Latest Measured Results

The reports are [`trial.json`](../evals/results/trial.json), [`trial-fixed.json`](../evals/results/trial-fixed.json), [`page-dedup.json`](../evals/results/page-dedup.json), [`hybrid-page-ranking.json`](../evals/results/hybrid-page-ranking.json), and [`query-rewrite-off-full.json`](../evals/results/query-rewrite-off-full.json). Each contains the same 32 evaluation cases and uses `k=5`, maximum relevant cosine distance `0.6`, `paraphrase-multilingual-MiniLM-L12-v2`, Mistral for generation and judging, and 1,000-character chunks with 200-character overlap.

| Metric | Baseline<br>`trial.json` | Section fix<br>`trial-fixed.json` | Page dedup<br>`page-dedup.json` | Hybrid + page bonus<br>`hybrid-page-ranking.json` | Query rewriting off<br>`query-rewrite-off-full.json` |
| --- | ---: | ---: | ---: | ---: | ---: |
| Precision@5 | 0.083 | 0.097 | 0.110 | 0.117 | 0.110 |
| Recall@5 | 0.362 | 0.431 | 0.500 | 0.509 | 0.500 |
| F1@5 | 0.130 | 0.153 | 0.176 | 0.184 | 0.176 |
| MRR | 0.374 | 0.443 | 0.460 | 0.506 | 0.494 |
| NDCG@5 | 0.342 | 0.411 | 0.440 | 0.474 | 0.467 |
| Hit rate@5 | 0.414 | 0.483 | 0.552 | 0.586 | 0.552 |
| Context precision | 0.184 | 0.231 | 0.188 | 0.197 | 0.197 |
| Context recall | 0.200 | 0.270 | 0.219 | 0.223 | 0.250 |
| Faithfulness | 0.369 | 0.447 | 0.341 | 0.328 | 0.453 |
| Answer relevance | 0.516 | 0.541 | 0.416 | 0.409 | 0.550 |
| Correctness | 0.425 | 0.456 | 0.350 | 0.359 | 0.472 |
| Completeness | 0.238 | 0.288 | 0.228 | 0.231 | 0.284 |
| Full evaluation time (min) | 30 | 30 | 32 | 37.6 | 29.8 |

*The `page-dedup` duration is an approximate wall-clock estimate. Earlier reports did not record duration; new reports save total runtime as `config.elapsed_seconds`.

### Changes evaluated

- **Exact-section matching fix:** prevents `§ 1` from matching `§ 10`, `§ 175`, or `§ 1a`. It is included in the current application and improved all measured metrics over `trial.json`.
- **Gold-page audit:** on 2026-11-18, checked the expected labels against the three matching PDFs in the local database. All 10 distinct expected filename/page pairs had non-empty indexed text, and spot-checks matched the labeled topics. No labels were changed.
- **Page-deduplication experiment:** returned only the highest-ranked chunk per page. It improved retrieval metrics over `trial-fixed.json` (Recall@5 +0.069; Hit rate@5 +0.069) but reduced all context and answer-quality metrics. The experiment is recorded in `page-dedup.json`; the hard filter was not retained in the application.
- **Hybrid-ranking experiment:** combined normalized vector similarity and lexical coverage, prioritized exact section references, and added a small bonus for a previously unseen page. Retrieval improved over `trial-fixed.json` (Recall@5 +0.078; Hit rate@5 +0.103), but the regression gate failed for faithfulness, answer relevance, correctness, and completeness. The run took 2,257 seconds (37.6 minutes); this ranking change was not retained.
- **Multilingual/query-rewriting ablation:** compared the current multilingual embedding model with query rewriting enabled and disabled in [`query-rewrite-on-retrieval.json`](../evals/results/query-rewrite-on-retrieval.json), [`query-rewrite-off-retrieval.json`](../evals/results/query-rewrite-off-retrieval.json), and [`query-rewrite-off-full.json`](../evals/results/query-rewrite-off-full.json). In retrieval-only runs, disabling rewriting improved Recall@5 from 0.431 to 0.500, Hit rate@5 from 0.483 to 0.552, and MRR from 0.443 to 0.494; there were two additional hit cases and no hit losses. Recall improved for Czech (0.500 → 0.600) and English (0.225 → 0.325), and was unchanged for Russian (0.583). Retrieval-only elapsed time fell from 309.6 to 7.6 seconds. The full run without rewriting improved retrieval and aggregate faithfulness, relevance, and correctness versus `trial-fixed.json`, but context precision/recall fell (0.231 → 0.197 and 0.270 → 0.250), completeness was slightly lower (0.288 → 0.284), and the per-case regression gate failed. Manual review confirmed a judge false negative for `435-purpose-cs`: the retrieved § 1 passage contains the answer verbatim despite the judge's rationale. Query rewriting remains enabled by default; the ablation controls are for evaluation only.
- **E5 embedding candidate:** evaluated `intfloat/multilingual-e5-small` offline against the same 2,265 chunks; its 384 dimensions match the existing schema, but it requires `query: ` and `passage: ` prefixes. The full run without query rewriting is in [`multilingual-e5-small-full.json`](../evals/results/multilingual-e5-small-full.json), with retrieval-only metrics in [`multilingual-e5-small-retrieval.json`](../evals/results/multilingual-e5-small-retrieval.json). Compared with MiniLM without rewriting, E5 improved Recall@5 (0.500 → 0.681), Hit rate@5 (0.552 → 0.759), MRR (0.494 → 0.615), context precision/recall (0.197/0.250 → 0.378/0.438), faithfulness (0.453 → 0.566), answer relevance (0.550 → 0.781), correctness (0.472 → 0.600), and completeness (0.284 → 0.428). The full run took 30.6 minutes. However, the per-case regression gate failed: `326-family-reunification-cs` lost the chunk listing applicants under § 42a(1), `326-family-reunification-en` ranked § 42b/§ 42c above the needed § 42a context, and `student-visa-time-cs` returned an unrelated § 180e period instead of the expected decision period. These are substantive evidence/answer regressions despite the aggregate gains.
- **E5 plus query rewriting:** the retrieval-only comparison in [`multilingual-e5-small-rewrite-on-retrieval.json`](../evals/results/multilingual-e5-small-rewrite-on-retrieval.json) was worse than E5 without rewriting: Recall@5 fell from 0.681 to 0.543, Hit rate@5 from 0.759 to 0.621, and MRR from 0.615 to 0.529. It lost four hit cases and gained none; English hit rate fell from 0.800 to 0.500, while Czech was unchanged and Russian fell from 0.778 to 0.667. Query evaluation took 300 seconds rather than 3.8 seconds. No full generation/judge run was warranted for this weaker combination.

### Conclusions

- **Retrieval remains the main bottleneck:** with the current exact-section fix, Recall@5 is 0.431 and the expected page is absent from the top five in 15 of 29 answerable cases.
- **Higher page coverage alone is not enough:** `page-dedup.json` raises Recall@5 to 0.500, but faithfulness falls from 0.447 to 0.341 and correctness from 0.456 to 0.350. For example, `435-purpose-cs` retrieves page 1 but misses the chunk containing the answer in § 1; `326-family-reunification-cs` loses supporting details from other chunks on page 18.
- **The hybrid candidate also needs more work:** it found the expected page in three additional cases and lost none, but answer-quality scores fell versus `trial-fixed.json` (faithfulness 0.447 → 0.328; correctness 0.456 → 0.359). Per-case inspection found a judge false negative for `435-purpose-cs` even though the answer and retrieved § 1 chunk contained the expected fact; `326-family-reunification-en` did lose supporting evidence. Review retrieved chunk IDs and text alongside judge scores before another tuning pass.
- **The current application keeps MiniLM, the exact-section fix, and the existing query-rewriting default.** Neither page deduplication nor the tested hybrid score is retained. Disabling rewriting is not adopted as the default because context metrics and several per-case scores regressed despite better aggregate retrieval. E5 is also not promoted yet: its aggregate gains do not outweigh the reviewed answer-support regressions, and adding rewriting makes its retrieval worse. The E5 experiment used in-memory vectors only; production embeddings and the database were not changed. Continue with the page-aware reranking experiment, paying particular attention to retaining all chunks needed for exact-section questions.
- **Failures span languages and topics.** E5 without rewriting improved aggregate cross-language metrics, but family-reunification and visa-period evidence still regressed. Several questions about visa and employee-card decision periods miss their expected pages; investigate these cases in the page-aware reranking experiment.
- **Scores need cautious interpretation:** Mistral both generates and judges answers, and the 32-case dataset is small and uneven. Three unanswerable cases have no expected source page, so their retrieval metrics are undefined. Review per-case results and manually inspect legal answers before treating judge scores as ground truth.

## Improvement Plan and Expected Impact

Work from retrieval toward generation so prompt changes do not mask missing evidence.

| Priority | Planned change | Expected impact | How to verify |
| --- | --- | --- | --- |
| 1 | Audit dataset labels, page numbers, and indexed chunks against the exact PDFs; inspect failed cases and the text actually retrieved. Correct any inaccurate labels or page attribution before changing ranking. **Completed for the currently indexed PDF versions; see Changes evaluated.** | More trustworthy recall/precision measurements and correct page citations. | Recheck when source PDF versions or dataset labels change. |
| 2 | Diagnose the failed page-deduplication and hybrid-ranking cases, then test a page-aware ranker that does not displace answer-supporting chunks. Keep exact section references separate and review chunk text where the LLM judge reports a regression. | Improve retrieval coverage while maintaining or improving context precision/recall and answer faithfulness. | Compare all retrieval and judge metrics with the same dataset and `k`; manually review cases where retrieval gains and answer-quality losses diverge. |
| 3 | Evaluate multilingual retrieval separately from query rewriting. **Completed on 2026-11-26:** E5 without rewriting substantially improved aggregate metrics, but manual review found answer-support regressions; E5 with rewriting reduced retrieval quality and added latency. Keep MiniLM in production until the regressions are resolved. | Improve cross-language recall and reduce costly or unreliable Ollama translation calls without losing answer-supporting evidence. | Record model and translation settings; compare metrics by language, inspect per-case chunk evidence, and measure end-to-end latency. |
| 4 | Add a reranker, such as a multilingual cross-encoder, to reorder a broader candidate set before selecting context. | Primarily improve Precision@5, MRR, NDCG, and context precision. | Compare ranking and latency; first confirm that the broader initial retrieval can find the required source. |
| 5 | Tune chunk boundaries, `k`, the distance threshold, page diversity, and context size using the evaluation set. Re-index after changing chunking or embeddings. | Improve context precision/recall and reduce unsupported answers, while balancing coverage, noise, and latency. | Change one parameter group at a time and compare against an unchanged baseline. |
| 6 | After retrieval improves, refine the answer prompt to require context-grounded claims, cautious abstention when evidence is missing, and clear source references. | Improve faithfulness, correctness, and answer relevance; a prompt cannot compensate for missing retrieved evidence. | Manually review legal answers and abstentions, including conditions and exceptions. |
| 7 | Calibrate the LLM judge against human labels and, if practical, use an independent judge model. Expand and balance the golden set. | Increase confidence in generation-quality measurements and broaden regression coverage; this does not directly improve application answers. | Track judge-human agreement and keep some cases as a stable holdout set. |

## Re-running the Evaluation

Start PostgreSQL, ensure the exact versions of all three PDFs are indexed, and verify that Ollama is available. Save each new report under a different name rather than overwriting earlier runs:

Compare retrieval with query rewriting enabled and disabled before spending time on answer generation and judging:

```powershell
uv run python -m app.evaluate `
  --dataset evals/dataset.json `
  --output evals/results/query-rewrite-on-retrieval.json `
  --retrieval-only `
  --k 5

uv run python -m app.evaluate `
  --dataset evals/dataset.json `
  --output evals/results/query-rewrite-off-retrieval.json `
  --retrieval-only `
  --disable-query-rewriting `
  --k 5
```

Retrieval-only reports leave answer-quality metrics as `null`. The evaluator records whether query rewriting was enabled, whether the run was retrieval-only, and total elapsed seconds in each report's `config`. Use the full evaluation below to assess answer-quality effects before changing the application's default behavior.

```powershell
$env:OLLAMA_TIMEOUT = "600"
uv run python -m app.evaluate `
  --dataset evals/dataset.json `
  --output evals/results/candidate.json `
  --k 5
```

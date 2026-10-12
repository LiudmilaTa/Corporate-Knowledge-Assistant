import json
import math

import pytest

from app.services.evaluation import (
    ALL_METRIC_FIELDS,
    EvaluationCase,
    JudgeScores,
    compare_baseline,
    evaluate_thresholds,
    judge_answer,
    load_evaluation_dataset,
    parse_thresholds,
    retrieval_metrics,
    run_evaluation,
)


def test_retrieval_metrics_calculate_ranking_quality():
    metrics = retrieval_metrics(
        [("a.pdf", 1), ("b.pdf", 2), ("c.pdf", 3)],
        {("b.pdf", 2), ("c.pdf", 3)},
        k=3,
    )

    assert metrics == {
        "precision_at_k": pytest.approx(2 / 3),
        "recall_at_k": 1.0,
        "f1_at_k": pytest.approx(0.8),
        "mrr": 0.5,
        "ndcg_at_k": pytest.approx(
            (1 / math.log2(3) + 1 / math.log2(4))
            / (1 + 1 / math.log2(3))
        ),
        "hit_rate_at_k": 1.0,
    }


def test_retrieval_metrics_deduplicate_sources_and_handle_no_relevant_sources():
    metrics = retrieval_metrics(
        [("a.pdf", 1), ("a.pdf", 1)],
        {("b.pdf", 2)},
        k=2,
    )
    no_gold_metrics = retrieval_metrics([("a.pdf", 1)], set(), k=2)

    assert metrics["precision_at_k"] == 0
    assert metrics["recall_at_k"] == 0
    assert metrics["mrr"] == 0
    assert no_gold_metrics == dict.fromkeys(ALL_METRIC_FIELDS[:6])


def test_retrieval_metrics_reject_nonpositive_k():
    with pytest.raises(ValueError, match="at least 1"):
        retrieval_metrics([], set(), k=0)


def test_load_evaluation_dataset_validates_nonempty_unique_cases(tmp_path):
    dataset = tmp_path / "dataset.json"
    dataset.write_text(
        json.dumps(
            [
                {
                    "id": "case-1",
                    "question": "What is the policy?",
                    "expected_sources": [{"filename": "policy.pdf", "page": 1}],
                    "reference_answer": "The policy says ...",
                }
            ]
        ),
        encoding="utf-8",
    )

    cases = load_evaluation_dataset(dataset)

    assert cases[0].id == "case-1"
    assert cases[0].answerable is True


def test_load_evaluation_dataset_rejects_empty_dataset_and_duplicate_ids(tmp_path):
    dataset = tmp_path / "dataset.json"
    dataset.write_text("[]", encoding="utf-8")
    with pytest.raises(ValueError, match="non-empty"):
        load_evaluation_dataset(dataset)

    duplicate = {
        "id": "same",
        "question": "Question?",
        "expected_sources": [],
        "reference_answer": "Answer.",
    }
    dataset.write_text(json.dumps([duplicate, duplicate]), encoding="utf-8")
    with pytest.raises(ValueError, match="unique"):
        load_evaluation_dataset(dataset)


def test_parse_thresholds_validates_metric_names_and_ranges():
    assert parse_thresholds(["recall_at_k=0.8", "faithfulness=0.9"]) == {
        "recall_at_k": 0.8,
        "faithfulness": 0.9,
    }
    with pytest.raises(ValueError, match="Unknown evaluation metric"):
        parse_thresholds(["unknown=0.5"])
    with pytest.raises(ValueError, match="between 0 and 1"):
        parse_thresholds(["mrr=1.1"])


def test_evaluate_thresholds_reports_failed_gates():
    summary = {metric: 0.9 for metric in ALL_METRIC_FIELDS}
    summary["recall_at_k"] = 0.6

    failures = evaluate_thresholds(summary, {"recall_at_k": 0.8})

    assert failures == ["recall_at_k=0.6 is below the required minimum 0.800"]


def test_compare_baseline_detects_regression_and_checks_compatibility():
    baseline = {
        "config": {"k": 5},
        "summary": {metric: 1.0 for metric in ALL_METRIC_FIELDS},
        "cases": [{"id": "case-1"}],
    }
    current = {
        "config": {"k": 5},
        "summary": {metric: 1.0 for metric in ALL_METRIC_FIELDS},
        "cases": [{"id": "case-1"}],
    }
    current["summary"]["faithfulness"] = 0.8

    regressions = compare_baseline(current, baseline, max_regression=0.1)

    assert [regression["metric"] for regression in regressions] == ["faithfulness"]
    current["config"]["k"] = 3
    with pytest.raises(ValueError, match="same k"):
        compare_baseline(current, baseline, max_regression=0.1)


def test_compare_baseline_detects_per_case_regressions_hidden_by_average():
    baseline = {
        "config": {"k": 5},
        "summary": {metric: 0.6 for metric in ALL_METRIC_FIELDS},
        "cases": [
            {"id": "worse", "metrics": {"faithfulness": 0.6}},
            {"id": "better", "metrics": {"faithfulness": 0.6}},
        ],
    }
    current = {
        "config": {"k": 5},
        "summary": {metric: 0.6 for metric in ALL_METRIC_FIELDS},
        "cases": [
            {"id": "worse", "metrics": {"faithfulness": 0.4}},
            {"id": "better", "metrics": {"faithfulness": 0.8}},
        ],
    }

    regressions = compare_baseline(current, baseline, max_regression=0.1)

    assert regressions == [
        {
            "metric": "faithfulness",
            "baseline": 0.6,
            "current": 0.4,
            "drop": pytest.approx(0.2),
            "case_id": "worse",
        }
    ]


def test_judge_answer_parses_ollama_json_response(monkeypatch):
    expected_scores = {
        "context_precision": 0.9,
        "context_recall": 1.0,
        "faithfulness": 0.8,
        "answer_relevance": 0.9,
        "correctness": 0.8,
        "completeness": 0.7,
        "rationale": "The response is supported by the context.",
    }

    class FakeResponse:
        def raise_for_status(self):
            pass

        def json(self):
            return {"response": json.dumps(expected_scores)}

    def fake_post(url, json, timeout):
        assert json["format"] == "json"
        assert json["options"]["temperature"] == 0.0
        return FakeResponse()

    monkeypatch.setattr("app.services.evaluation.requests.post", fake_post)

    result = judge_answer(
        question="What is stated?",
        chunks=["The policy states a fact."],
        answer="A fact is stated.",
        reference_answer="The policy states a fact.",
    )

    assert isinstance(result, JudgeScores)
    assert result.faithfulness == 0.8
    assert result.rationale == expected_scores["rationale"]


def test_judge_answer_rejects_out_of_range_scores(monkeypatch):
    class FakeResponse:
        def raise_for_status(self):
            pass

        def json(self):
            return {
                "response": json.dumps(
                    {
                        "context_precision": 1.2,
                        "context_recall": 1,
                        "faithfulness": 1,
                        "answer_relevance": 1,
                        "correctness": 1,
                        "completeness": 1,
                        "rationale": "Invalid score.",
                    }
                )
            }

    monkeypatch.setattr(
        "app.services.evaluation.requests.post",
        lambda *args, **kwargs: FakeResponse(),
    )

    with pytest.raises(ValueError, match="invalid evaluation response"):
        judge_answer("Question", [], "Answer", "Reference")


def test_run_evaluation_uses_search_candidates_and_judges_final_context(monkeypatch):
    from app.services import rag

    trace = {
        "answer": "The policy allows it.",
        "search_candidates": [
            {
                "filename": "policy.pdf",
                "page": 1,
                "chunk_id": 0,
                "content": "Relevant policy text.",
                "distance": 0.2,
            },
            {
                "filename": "policy.pdf",
                "page": 2,
                "chunk_id": 1,
                "content": "Additional details.",
                "distance": 0.3,
            },
        ],
        "retrieved_chunks": [
            {
                "filename": "policy.pdf",
                "page": 1,
                "chunk_id": 0,
                "content": "Relevant policy text.",
                "distance": 0.2,
            }
        ],
    }
    def fake_ask_question_with_trace(*args, **kwargs):
        kwargs["progress_callback"]("generating answer with Ollama")
        return trace

    monkeypatch.setattr(rag, "ask_question_with_trace", fake_ask_question_with_trace)
    monkeypatch.setattr(
        "app.services.evaluation.judge_answer",
        lambda **kwargs: JudgeScores(
            context_precision=1,
            context_recall=1,
            faithfulness=1,
            answer_relevance=1,
            correctness=1,
            completeness=1,
            rationale="All criteria pass.",
        ),
    )
    case = EvaluationCase(
        id="case-1",
        question="What does the policy allow?",
        expected_sources=[{"filename": "policy.pdf", "page": 1}],
        reference_answer="It allows it.",
    )

    progress = []
    report = run_evaluation([case], k=2, progress_callback=progress.append)

    assert progress == [
        "[1/1] case-1: starting RAG pipeline",
        "[1/1] case-1: generating answer with Ollama",
        "[1/1] case-1: evaluating answer with judge",
        "[1/1] case-1: complete",
    ]
    assert report["summary"]["recall_at_k"] == 1
    assert report["summary"]["precision_at_k"] == 0.5
    assert report["cases"][0]["search_candidates"] == [
        {"filename": "policy.pdf", "page": 1},
        {"filename": "policy.pdf", "page": 2},
    ]
    assert report["cases"][0]["retrieved_sources"] == [
        {"filename": "policy.pdf", "page": 1}
    ]

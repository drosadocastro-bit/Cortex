from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_adr_035_documents_predictive_memory_boundary() -> None:
    text = read("docs/ADR-035-predictive-memory-and-expectation-layer.md")

    for phrase in [
        "Predictive Memory And Expectation Layer",
        "PredictiveMemoryEngine",
        "ExpectationTrace",
        "PredictionCandidate",
        "PredictionError",
        "SurpriseSignal",
        "Predictive memory must not:",
        "treat expectation as truth",
    ]:
        assert phrase in text


def test_memory_model_mentions_predictive_memory_layer() -> None:
    text = read("docs/MEMORY_MODEL.md")

    assert "Phase 33 adds `PredictiveMemoryEngine`" in text
    assert "Predictive memory does not predict truth" in text
    assert "surprise is not disproof" in text


def test_ai_debt_tracks_predictive_memory_risk() -> None:
    text = read("docs/AI_DEBT.md")

    assert "Predictive Memory Debt" in text
    assert "Predictive review attention could be mistaken for truth prediction" in text
    assert "expectation is not truth" in text
    assert "Do not treat expected patterns, surprise signals, or predicted review needs" in text


def test_readme_lists_predictive_memory_artifacts() -> None:
    text = read("README.md")

    assert "Predictive memory organizes prior memory structure" in text
    assert "ADR-035-predictive-memory-and-expectation-layer.md" in text
    assert "predictive_memory.py" in text
    assert "test_phase33_predictive_memory.py" in text


def test_current_state_tracks_predictive_memory_phase() -> None:
    text = read("docs/CURRENT_STATE.md")

    assert "predictive memory / expectation traces" in text
    assert "Predictive memory must remain review attention only" in text
    assert "Phase 34: Hard-Adversarial Remediation Or Predictive-Memory Boundary Evaluation" in text

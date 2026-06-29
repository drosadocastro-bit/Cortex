from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_dream_replay_adr_defines_offline_boundary() -> None:
    text = read("docs/ADR-033-offline-memory-consolidation-and-dream-replay.md")

    for phrase in [
        "Offline Memory Consolidation And Dream Replay",
        "Dream replay is read-only.",
        "Dream artifacts are internal cognitive artifacts.",
        "create evidence",
        "merge memories automatically",
        "resolve contradictions",
    ]:
        assert phrase in text


def test_memory_model_separates_dream_replay_from_decay_and_merge() -> None:
    text = read("docs/MEMORY_MODEL.md")

    for phrase in [
        "Phase 31 adds `DreamReplayEngine`",
        "decay still decides how memory strength changes over time",
        "merge still decides whether duplicate memories are actually collapsed",
        "dream replay only recommends what may deserve later review",
        "Dream artifacts are internal cognitive artifacts, not evidence.",
    ]:
        assert phrase in text


def test_readme_mentions_dream_replay_without_truth_language() -> None:
    text = read("README.md")

    assert "offline dream replay" in text
    assert "without becoming truth signals" in text
    assert "ADR-033-offline-memory-consolidation-and-dream-replay.md" in text
    assert "dream_replay.py" in text
    assert "test_phase31_dream_replay.py" in text


def test_ai_debt_tracks_dream_replay_risk() -> None:
    text = read("docs/AI_DEBT.md")

    for phrase in [
        "Dream Replay Debt",
        "Future offline consolidation could be mistaken for insight, evidence",
        "`DreamReplayEngine` is deterministic and read-only",
        "Do not treat dream replay, repeated replay, or consolidation recommendations as",
    ]:
        assert phrase in text


def test_current_state_tracks_phase31_and_next_boundary() -> None:
    text = read("docs/CURRENT_STATE.md")

    assert "offline memory consolidation / dream replay" in text
    assert "Dream replay must remain recommendation-only" in text
    assert "Phase 34: Hard-Adversarial Remediation Or Predictive-Memory Boundary Evaluation" in text

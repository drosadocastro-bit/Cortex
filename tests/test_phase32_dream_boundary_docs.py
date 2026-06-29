from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_adr_034_documents_dream_boundary() -> None:
    text = read("docs/ADR-034-dream-replay-boundary-integration.md")

    for phrase in [
        "Dream Replay Boundary Integration",
        "DreamInfluencePolicy",
        "DreamReviewAdapter",
        "DreamBoundaryGuardrails",
        "Dream replay must not:",
        "create evidence",
        "increase memory strength",
        "treat duplicate replay as corroboration",
    ]:
        assert phrase in text


def test_memory_model_mentions_phase32_boundary() -> None:
    text = read("docs/MEMORY_MODEL.md")

    assert "Phase 32 adds the dream-to-review boundary" in text
    assert "review visibility, context inclusion, and discourse annotations only" in text
    assert "not\nevidence, confirmation, mutation" in text


def test_ai_debt_tracks_phase32_dream_boundary_components() -> None:
    text = read("docs/AI_DEBT.md")

    assert "Dream Replay Debt" in text
    assert "`DreamInfluencePolicy`, `DreamReviewAdapter`, and `DreamBoundaryGuardrails`" in text
    assert "influence review visibility only through explicit warnings" in text


def test_readme_lists_phase32_artifacts() -> None:
    text = read("README.md")

    assert "dream boundary integration lets replay affect" in text
    assert "ADR-034-dream-replay-boundary-integration.md" in text
    assert "dream_influence.py" in text
    assert "test_phase32_dream_boundary_integration.py" in text


def test_current_state_moves_past_phase32() -> None:
    text = read("docs/CURRENT_STATE.md")

    assert "dream replay boundary integration" in text
    assert "Phase 34: Hard-Adversarial Remediation Or Predictive-Memory Boundary Evaluation" in text
    assert "Dream replay must remain recommendation-only" in text


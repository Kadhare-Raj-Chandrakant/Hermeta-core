import pytest

from brain.domain.understanding import Understanding


def create_understanding(
    summary: str = "System uses event sourcing",
    rationale: str = "Needed for audit trail",
    current_state: str = "Implemented in core module",
    alternatives: tuple[str, ...] = ("CRUD", "CQRS"),
    trade_offs: tuple[str, ...] = ("Higher complexity", "Better auditability"),
    open_questions: tuple[str, ...] = ("Retention policy?",),
) -> Understanding:
    return Understanding(
        summary=summary,
        rationale=rationale,
        current_state=current_state,
        alternatives=alternatives,
        trade_offs=trade_offs,
        open_questions=open_questions,
    )


class TestUnderstandingImmutability:
    def test_summary_is_frozen(self):
        u = create_understanding()
        with pytest.raises(AttributeError):
            u.summary = "new"

    def test_rationale_is_frozen(self):
        u = create_understanding()
        with pytest.raises(AttributeError):
            u.rationale = "new"

    def test_current_state_is_frozen(self):
        u = create_understanding()
        with pytest.raises(AttributeError):
            u.current_state = "new"

    def test_alternatives_is_frozen(self):
        u = create_understanding()
        with pytest.raises(AttributeError):
            u.alternatives = ()

    def test_trade_offs_is_frozen(self):
        u = create_understanding()
        with pytest.raises(AttributeError):
            u.trade_offs = ()

    def test_open_questions_is_frozen(self):
        u = create_understanding()
        with pytest.raises(AttributeError):
            u.open_questions = ()


class TestUnderstandingValidation:
    def test_empty_summary_raises(self):
        with pytest.raises(ValueError, match="summary"):
            create_understanding(summary="")

    def test_whitespace_summary_raises(self):
        with pytest.raises(ValueError, match="summary"):
            create_understanding(summary="   ")

    def test_empty_rationale_raises(self):
        with pytest.raises(ValueError, match="rationale"):
            create_understanding(rationale="")

    def test_empty_current_state_raises(self):
        with pytest.raises(ValueError, match="current_state"):
            create_understanding(current_state="")


class TestUnderstandingEquality:
    def test_equal_instances(self):
        u1 = Understanding(
            summary="s",
            rationale="r",
            current_state="c",
            alternatives=("a",),
            trade_offs=("t",),
            open_questions=("q",),
        )
        u2 = Understanding(
            summary="s",
            rationale="r",
            current_state="c",
            alternatives=("a",),
            trade_offs=("t",),
            open_questions=("q",),
        )
        assert u1 == u2

    def test_unequal_instances(self):
        u1 = create_understanding(summary="one")
        u2 = create_understanding(summary="two")
        assert u1 != u2


class TestUnderstandingTuples:
    def test_empty_tuples_allowed(self):
        u = create_understanding(
            alternatives=(),
            trade_offs=(),
            open_questions=(),
        )
        assert u.alternatives == ()
        assert u.trade_offs == ()
        assert u.open_questions == ()

    def test_multiple_items(self):
        u = create_understanding(
            alternatives=("a", "b", "c"),
            trade_offs=("x", "y"),
            open_questions=("1", "2", "3"),
        )
        assert len(u.alternatives) == 3
        assert len(u.trade_offs) == 2
        assert len(u.open_questions) == 3

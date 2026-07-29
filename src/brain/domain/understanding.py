from dataclasses import dataclass


@dataclass(frozen=True)
class Understanding:
    summary: str
    rationale: str
    current_state: str
    alternatives: tuple[str, ...]
    trade_offs: tuple[str, ...]
    open_questions: tuple[str, ...]

    def __post_init__(self) -> None:
        if not self.summary.strip():
            raise ValueError("summary must not be empty")
        if not self.rationale.strip():
            raise ValueError("rationale must not be empty")
        if not self.current_state.strip():
            raise ValueError("current_state must not be empty")

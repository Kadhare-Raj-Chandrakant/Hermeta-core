from dataclasses import dataclass


@dataclass(frozen=True)
class ExecutionPolicy:
    allow_parallel: bool = False
    stop_on_failure: bool = True
    require_confirmation: bool = False

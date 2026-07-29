from dataclasses import dataclass

from brain.runtime.runtime import BrainRuntime


@dataclass(frozen=True)
class BrainHealthReport:
    healthy: bool
    components: tuple[str, ...]
    failures: tuple[str, ...]


def check_health(runtime: BrainRuntime) -> BrainHealthReport:
    components: list[str] = []
    failures: list[str] = []

    checks = [
        ("repository", runtime.repository),
        ("service", runtime.service),
        ("session", runtime.session),
        ("adapter", runtime.adapter),
        ("validation", runtime.validation),
        ("retrieval", runtime.retrieval),
        ("reflection", runtime.reflection),
        ("evolution", runtime.evolution),
        ("detection", runtime.detection),
        ("learning", runtime.learning),
        ("publisher", runtime.publisher),
        ("workflow", runtime.workflow),
    ]

    for name, component in checks:
        if component is not None:
            components.append(name)
        else:
            failures.append(name)

    return BrainHealthReport(
        healthy=len(failures) == 0,
        components=tuple(components),
        failures=tuple(failures),
    )

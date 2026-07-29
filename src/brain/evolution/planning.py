from brain.evolution.evolution_context import EvolutionContext
from brain.evolution.evolution_operation import EvolutionOperation
from brain.evolution.evolution_plan import EvolutionPlan
from brain.evolution.transition_type import TransitionType


class EvolutionPlanner:
    """Pure planning component with zero infrastructure dependencies.

    Planning boundary:
    ┌─────────────────────────────────────────────┐
    │  Request + Context → Planning → Plan        │
    │                                             │
    │  Does NOT:                                  │
    │  • mutate                                   │
    │  • inspect runtime                          │
    │  • schedule maintenance                     │
    │  • persist state                            │
    │  • validate optimistic concurrency          │
    │  • persist state                            │
    │  • interact with repositories/runtime       │
    └─────────────────────────────────────────────┘

    Determinism guarantee:
    Identical (targets, category, context) always
    produce identical operation ordering, identical
    metadata, identical target ordering, identical plan.
    """

    def plan(
        self,
        targets: tuple,
        category: str,
        context: EvolutionContext,
    ) -> EvolutionPlan:
        quarantined = tuple(sorted(context.quarantined_targets))
        available = tuple(t for t in targets if t not in quarantined)

        ordered = tuple(sorted(available))

        operations: list[EvolutionOperation] = []

        if category == "duplicate":
            for i in range(0, len(ordered) - 1, 2):
                if i + 1 < len(ordered):
                    a, b = ordered[i], ordered[i + 1]
                    operations.append(EvolutionOperation(
                        target_id=a,
                        expected_version_id=a,
                        transition_type=TransitionType.SUPERSEDES,
                        reason=f"Planned supersede: duplicate {a} -> {b}",
                    ))
        elif category == "conflict":
            for i in range(0, len(ordered) - 1, 2):
                if i + 1 < len(ordered):
                    a, b = ordered[i], ordered[i + 1]
                    operations.append(EvolutionOperation(
                        target_id=a,
                        expected_version_id=a,
                        transition_type=TransitionType.REFINEMENT,
                        reason=f"Planned refinement: conflict between {a} and {b}",
                    ))
        elif category == "obsolete":
            for target in ordered:
                operations.append(EvolutionOperation(
                    target_id=target,
                    expected_version_id=target,
                    transition_type=TransitionType.UPDATE,
                    reason=f"Planned archival: obsolete target {target}",
                ))

        operations.sort(key=lambda op: (op.target_id, op.transition_type.value, op.reason))

        affected = tuple(sorted(set(op.target_id for op in operations)))
        quarantined_count = len(targets) - len(available)

        return EvolutionPlan(
            operations=tuple(operations),
            affected_targets=affected,
            metadata=(
                ("category", category),
                ("quarantined_skipped", str(quarantined_count)),
            ),
        )

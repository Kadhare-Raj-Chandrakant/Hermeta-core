import uuid
from collections import defaultdict, deque

from brain.planning.action import Action
from brain.planning.dependency import Dependency
from brain.planning.strategies.strategy import PlanningStrategy


class DependencyStrategy(PlanningStrategy):
    def organize(
        self,
        actions: tuple[Action, ...],
        dependencies: tuple[Dependency, ...],
    ) -> tuple[Action, ...]:
        action_map: dict[uuid.UUID, Action] = {a.id: a for a in actions}
        in_degree: dict[uuid.UUID, int] = {a.id: 0 for a in actions}
        graph: dict[uuid.UUID, list[uuid.UUID]] = defaultdict(list)

        for dep in dependencies:
            if dep.to_action_id in action_map and dep.from_action_id in action_map:
                graph[dep.from_action_id].append(dep.to_action_id)
                in_degree[dep.to_action_id] += 1

        queue: deque[uuid.UUID] = deque()
        for action_id, degree in in_degree.items():
            if degree == 0:
                queue.append(action_id)

        result_ids: list[uuid.UUID] = []
        while queue:
            current = queue.popleft()
            result_ids.append(current)
            for neighbor in graph[current]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)

        if len(result_ids) != len(actions):
            missing = [a.id for a in actions if a.id not in result_ids]
            raise ValueError(
                f"Circular dependency detected involving {len(missing)} action(s)"
            )

        return tuple(action_map[aid] for aid in result_ids)

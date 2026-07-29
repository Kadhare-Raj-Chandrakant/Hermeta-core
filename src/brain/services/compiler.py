import uuid
from dataclasses import dataclass

from brain.domain.enums import KnowledgeType
from brain.domain.task import Task
from brain.domain.version import KnowledgeVersion
from brain.services.selection import SelectedKnowledgePackage


@dataclass(frozen=True)
class ContextSection:
    section_type: str
    title: str
    content: tuple[KnowledgeVersion, ...]


@dataclass(frozen=True)
class ContextPackage:
    task: Task
    sections: tuple[ContextSection, ...]


SECTION_ORDER: list[tuple[str, str, set[KnowledgeType]]] = [
    ("project", "Project Context", {KnowledgeType.ARCHITECTURE, KnowledgeType.COMPONENT}),
    ("objective", "Objective", {KnowledgeType.GOAL, KnowledgeType.TASK}),
    ("architecture", "Architecture", {KnowledgeType.ARCHITECTURE}),
    ("decisions", "Decisions", {KnowledgeType.DECISION}),
    ("patterns", "Patterns", {KnowledgeType.PATTERN}),
    ("rules", "Rules", {KnowledgeType.RULE}),
    ("bugs", "Known Issues", {KnowledgeType.BUG}),
    ("assumptions", "Assumptions", {KnowledgeType.ASSUMPTION}),
    ("questions", "Open Questions", {KnowledgeType.QUESTION}),
    ("discoveries", "Discoveries", {KnowledgeType.DISCOVERY}),
]


class ContextCompiler:
    def compile(
        self, task: Task, selected: SelectedKnowledgePackage
    ) -> ContextPackage:
        seen_ids: set[uuid.UUID] = set()
        unique: list[KnowledgeVersion] = []
        for v in selected.selected:
            if v.identity_id not in seen_ids:
                seen_ids.add(v.identity_id)
                unique.append(v)

        sections: list[ContextSection] = []
        assigned: set[uuid.UUID] = set()

        for section_type, title, types in SECTION_ORDER:
            matching = [
                v
                for v in unique
                if v.identity_id not in assigned and v.knowledge_type in types
            ]
            if matching:
                for v in matching:
                    assigned.add(v.identity_id)
                sections.append(
                    ContextSection(
                        section_type=section_type,
                        title=title,
                        content=tuple(matching),
                    )
                )

        return ContextPackage(task=task, sections=tuple(sections))

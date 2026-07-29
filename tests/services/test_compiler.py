import uuid
from datetime import datetime, timezone

from brain.domain.enums import KnowledgeType, LifecycleState
from brain.domain.references import Evidence, Relationship
from brain.domain.task import Priority, Task, TaskType
from brain.domain.version import KnowledgeVersion
from brain.services.compiler import ContextCompiler, ContextPackage, ContextSection
from brain.services.selection import SelectedKnowledgePackage


def make_version(
    knowledge_type: KnowledgeType = KnowledgeType.DECISION,
    title: str = "Test",
) -> KnowledgeVersion:
    return KnowledgeVersion(
        identity_id=uuid.uuid4(),
        version_number=1,
        knowledge_type=knowledge_type,
        title=title,
        understanding="Understanding",
        confidence=0.8,
        lifecycle_state=LifecycleState.ACTIVE,
        evidence=(),
        relationships=(),
        created_at=datetime.now(timezone.utc),
    )


def make_task() -> Task:
    return Task(
        task_type=TaskType.IMPLEMENT,
        project="hermes-brain",
        component="domain",
        objective="Add feature",
        constraints=(),
        priority=Priority.MEDIUM,
    )


def make_selected(*versions: KnowledgeVersion) -> SelectedKnowledgePackage:
    return SelectedKnowledgePackage(
        selected=versions,
        budget_used=len(versions),
        budget_remaining=0,
    )


class TestDeterministicOrdering:
    def test_same_input_same_output(self):
        arch = make_version(KnowledgeType.ARCHITECTURE, "Arch")
        dec = make_version(KnowledgeType.DECISION, "Dec")
        selected = make_selected(arch, dec)

        compiler = ContextCompiler()
        r1 = compiler.compile(make_task(), selected)
        r2 = compiler.compile(make_task(), selected)

        assert [s.section_type for s in r1.sections] == [s.section_type for s in r2.sections]

    def test_order_follows_section_order(self):
        dec = make_version(KnowledgeType.DECISION, "Dec")
        goal = make_version(KnowledgeType.GOAL, "Goal")
        selected = make_selected(dec, goal)

        compiler = ContextCompiler()
        result = compiler.compile(make_task(), selected)

        section_types = [s.section_type for s in result.sections]
        assert section_types.index("objective") < section_types.index("decisions")


class TestEmptySectionRemoval:
    def test_empty_sections_not_included(self):
        dec = make_version(KnowledgeType.DECISION, "Dec")
        selected = make_selected(dec)

        compiler = ContextCompiler()
        result = compiler.compile(make_task(), selected)

        section_types = [s.section_type for s in result.sections]
        assert "architecture" not in section_types
        assert "patterns" not in section_types
        assert "bugs" not in section_types

    def test_all_empty_returns_no_sections(self):
        selected = make_selected()

        compiler = ContextCompiler()
        result = compiler.compile(make_task(), selected)

        assert result.sections == ()


class TestMultipleKnowledgeTypes:
    def test_different_types_in_correct_sections(self):
        goal = make_version(KnowledgeType.GOAL, "Goal")
        dec = make_version(KnowledgeType.DECISION, "Dec")
        bug = make_version(KnowledgeType.BUG, "Bug")
        selected = make_selected(goal, dec, bug)

        compiler = ContextCompiler()
        result = compiler.compile(make_task(), selected)

        section_map = {s.section_type: s for s in result.sections}
        assert "objective" in section_map
        assert "decisions" in section_map
        assert "bugs" in section_map

    def test_multiple_same_type_in_one_section(self):
        dec1 = make_version(KnowledgeType.DECISION, "Dec1")
        dec2 = make_version(KnowledgeType.DECISION, "Dec2")
        selected = make_selected(dec1, dec2)

        compiler = ContextCompiler()
        result = compiler.compile(make_task(), selected)

        assert len(result.sections) == 1
        assert result.sections[0].section_type == "decisions"
        assert len(result.sections[0].content) == 2


class TestDuplicateAvoidance:
    def test_no_duplicate_versions(self):
        arch = make_version(KnowledgeType.ARCHITECTURE, "Arch")
        selected = make_selected(arch, arch)

        compiler = ContextCompiler()
        result = compiler.compile(make_task(), selected)

        all_versions = [v for s in result.sections for v in s.content]
        assert len(all_versions) == 1


class TestImmutableContextPackage:
    def test_context_package_is_frozen(self):
        selected = make_selected()

        compiler = ContextCompiler()
        result = compiler.compile(make_task(), selected)

        with pytest.raises(AttributeError):
            result.task = make_task()

    def test_sections_is_frozen(self):
        selected = make_selected()

        compiler = ContextCompiler()
        result = compiler.compile(make_task(), selected)

        with pytest.raises(AttributeError):
            result.sections = ()

    def test_section_content_is_frozen(self):
        arch = make_version(KnowledgeType.ARCHITECTURE, "Arch")
        selected = make_selected(arch)

        compiler = ContextCompiler()
        result = compiler.compile(make_task(), selected)

        with pytest.raises(AttributeError):
            result.sections[0].content = ()


class TestCompilerDeterminism:
    def test_order_independent_input(self):
        arch = make_version(KnowledgeType.ARCHITECTURE, "Arch")
        dec = make_version(KnowledgeType.DECISION, "Dec")
        selected_a = make_selected(arch, dec)
        selected_b = make_selected(dec, arch)

        compiler = ContextCompiler()
        r1 = compiler.compile(make_task(), selected_a)
        r2 = compiler.compile(make_task(), selected_b)

        assert [s.section_type for s in r1.sections] == [s.section_type for s in r2.sections]


class TestPreservesUnderstanding:
    def test_all_versions_included(self):
        arch = make_version(KnowledgeType.ARCHITECTURE, "Arch")
        dec = make_version(KnowledgeType.DECISION, "Dec")
        pattern = make_version(KnowledgeType.PATTERN, "Pattern")
        selected = make_selected(arch, dec, pattern)

        compiler = ContextCompiler()
        result = compiler.compile(make_task(), selected)

        total = sum(len(s.content) for s in result.sections)
        assert total == 3


import pytest

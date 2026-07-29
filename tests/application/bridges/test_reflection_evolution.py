import uuid

import pytest

from brain.application.bridges.reflection_evolution import ReflectionEvolutionBridge
from brain.application.usecases.models import (
    EvolutionRequest,
    FindingType,
    ReflectionFindingDTO,
)


def _make_finding(
    finding_type: FindingType = FindingType.DUPLICATE,
    affected_versions: tuple[uuid.UUID, ...] = (),
    explanation: str = "test explanation",
    confidence: float = 0.8,
) -> ReflectionFindingDTO:
    return ReflectionFindingDTO(
        finding_type=finding_type,
        affected_versions=affected_versions,
        explanation=explanation,
        confidence=confidence,
    )


class TestConstruction:
    def test_bridge_creation(self):
        bridge = ReflectionEvolutionBridge()
        assert isinstance(bridge, ReflectionEvolutionBridge)

    def test_no_dependencies(self):
        bridge = ReflectionEvolutionBridge()
        assert not hasattr(bridge, "_engine")
        assert not hasattr(bridge, "_repository")

    def test_frozen(self):
        bridge = ReflectionEvolutionBridge()
        with pytest.raises(AttributeError):
            bridge._engine = None


class TestTranslation:
    def test_returns_evolution_request(self):
        bridge = ReflectionEvolutionBridge()
        finding = _make_finding()
        result = bridge.translate(finding)
        assert isinstance(result, EvolutionRequest)

    def test_duplicate_finding_targets(self):
        a, b = uuid.uuid4(), uuid.uuid4()
        bridge = ReflectionEvolutionBridge()
        finding = _make_finding(
            finding_type=FindingType.DUPLICATE,
            affected_versions=(a, b),
        )
        result = bridge.translate(finding)
        assert result.targets == (a, b)

    def test_duplicate_finding_category(self):
        bridge = ReflectionEvolutionBridge()
        finding = _make_finding(finding_type=FindingType.DUPLICATE)
        result = bridge.translate(finding)
        assert result.context == "duplicate"

    def test_conflict_finding_targets(self):
        a, b = uuid.uuid4(), uuid.uuid4()
        bridge = ReflectionEvolutionBridge()
        finding = _make_finding(
            finding_type=FindingType.CONFLICT,
            affected_versions=(a, b),
        )
        result = bridge.translate(finding)
        assert result.targets == (a, b)

    def test_conflict_finding_category(self):
        bridge = ReflectionEvolutionBridge()
        finding = _make_finding(finding_type=FindingType.CONFLICT)
        result = bridge.translate(finding)
        assert result.context == "conflict"

    def test_obsolete_finding_single_target(self):
        v = uuid.uuid4()
        bridge = ReflectionEvolutionBridge()
        finding = _make_finding(
            finding_type=FindingType.OBSOLETE,
            affected_versions=(v,),
        )
        result = bridge.translate(finding)
        assert result.targets == (v,)

    def test_obsolete_finding_category(self):
        bridge = ReflectionEvolutionBridge()
        finding = _make_finding(finding_type=FindingType.OBSOLETE)
        result = bridge.translate(finding)
        assert result.context == "obsolete"

    def test_gap_finding_no_targets(self):
        bridge = ReflectionEvolutionBridge()
        finding = _make_finding(
            finding_type=FindingType.GAP,
            affected_versions=(),
        )
        result = bridge.translate(finding)
        assert result.targets == ()

    def test_gap_finding_category(self):
        bridge = ReflectionEvolutionBridge()
        finding = _make_finding(finding_type=FindingType.GAP)
        result = bridge.translate(finding)
        assert result.context == "gap"

    def test_metadata_source_is_reflection(self):
        bridge = ReflectionEvolutionBridge()
        finding = _make_finding()
        result = bridge.translate(finding)
        assert ("source", "reflection") in result.metadata

    def test_metadata_confidence_preserved(self):
        bridge = ReflectionEvolutionBridge()
        finding = _make_finding(confidence=0.65)
        result = bridge.translate(finding)
        assert ("confidence", "0.65") in result.metadata

    def test_metadata_tuple_of_tuples(self):
        bridge = ReflectionEvolutionBridge()
        finding = _make_finding()
        result = bridge.translate(finding)
        assert isinstance(result.metadata, tuple)
        assert all(isinstance(pair, tuple) for pair in result.metadata)
        assert all(len(pair) == 2 for pair in result.metadata)


class TestNoDecisionLeakage:
    def test_no_action_field(self):
        bridge = ReflectionEvolutionBridge()
        finding = _make_finding()
        result = bridge.translate(finding)
        assert not hasattr(result, "action")
        assert not hasattr(result, "strategy")
        assert not hasattr(result, "resolution")

    def test_no_merge_in_output(self):
        bridge = ReflectionEvolutionBridge()
        finding = _make_finding()
        result = bridge.translate(finding)
        for key, value in result.metadata:
            assert "merge" not in key.lower()
            assert "merge" not in value.lower()

    def test_no_replace_in_output(self):
        bridge = ReflectionEvolutionBridge()
        finding = _make_finding()
        result = bridge.translate(finding)
        for key, value in result.metadata:
            assert "replace" not in key.lower()
            assert "replace" not in value.lower()

    def test_no_delete_in_output(self):
        bridge = ReflectionEvolutionBridge()
        finding = _make_finding()
        result = bridge.translate(finding)
        for key, value in result.metadata:
            assert "delete" not in key.lower()
            assert "delete" not in value.lower()

    def test_no_resolve_in_output(self):
        bridge = ReflectionEvolutionBridge()
        finding = _make_finding()
        result = bridge.translate(finding)
        for key, value in result.metadata:
            assert "resolve" not in key.lower()
            assert "resolve" not in value.lower()

    def test_no_keep_in_output(self):
        bridge = ReflectionEvolutionBridge()
        finding = _make_finding()
        result = bridge.translate(finding)
        for key, value in result.metadata:
            assert "keep" not in key.lower()
            assert "keep" not in value.lower()

    def test_no_discard_in_output(self):
        bridge = ReflectionEvolutionBridge()
        finding = _make_finding()
        result = bridge.translate(finding)
        for key, value in result.metadata:
            assert "discard" not in key.lower()
            assert "discard" not in value.lower()


class TestDeterminism:
    def test_same_input_same_output(self):
        a, b = uuid.uuid4(), uuid.uuid4()
        bridge = ReflectionEvolutionBridge()
        finding = _make_finding(
            finding_type=FindingType.CONFLICT,
            affected_versions=(a, b),
            explanation="same scope different conclusions",
            confidence=0.7,
        )
        r1 = bridge.translate(finding)
        r2 = bridge.translate(finding)
        assert r1 == r2

    def test_repeated_calls_equivalent(self):
        a = uuid.uuid4()
        bridge = ReflectionEvolutionBridge()
        finding = _make_finding(
            finding_type=FindingType.OBSOLETE,
            affected_versions=(a,),
        )
        results = [bridge.translate(finding) for _ in range(10)]
        assert all(r == results[0] for r in results)


class TestBoundaryIsolation:
    def test_no_evolution_engine_import(self):
        import inspect
        source = inspect.getsource(ReflectionEvolutionBridge)
        assert "EvolutionEngine" not in source
        assert "from brain.evolution" not in source

    def test_no_repository_import(self):
        import inspect
        source = inspect.getsource(ReflectionEvolutionBridge)
        assert "Repository" not in source
        assert "from brain.repositories" not in source

    def test_no_runtime_import(self):
        import inspect
        source = inspect.getsource(ReflectionEvolutionBridge)
        assert "BrainRuntime" not in source
        assert "from brain.runtime" not in source

    def test_no_workflow_import(self):
        import inspect
        source = inspect.getsource(ReflectionEvolutionBridge)
        assert "Workflow" not in source
        assert "from brain.application.workflow" not in source

    def test_no_maintenance_import(self):
        import inspect
        source = inspect.getsource(ReflectionEvolutionBridge)
        assert "Maintenance" not in source
        assert "from brain.application.maintenance" not in source

    def test_no_reflection_domain_import(self):
        import inspect
        source = inspect.getsource(ReflectionEvolutionBridge)
        assert "from brain.reflection" not in source
        assert "ReflectionEngine" not in source
        assert "ReflectionDetector" not in source

    def test_no_learning_import(self):
        import inspect
        source = inspect.getsource(ReflectionEvolutionBridge)
        assert "from brain.learning" not in source

    def test_only_uses_application_dto(self):
        import inspect
        source = inspect.getsource(ReflectionEvolutionBridge)
        assert "EvolutionRequest" in source
        assert "ReflectionFindingDTO" in source

    def test_imports_from_application_models(self):
        import brain.application.bridges.reflection_evolution as mod
        import brain.application.usecases.models as models
        assert hasattr(models, "FindingType")
        assert hasattr(models, "ReflectionFindingDTO")
        assert hasattr(models, "EvolutionRequest")

import uuid

import pytest

from brain.runtime import create_memory_runtime, create_sqlite_runtime, BrainRuntime
from brain.application.bridges.execution_learning import ExecutionLearningMapper
from brain.application.maintenance.service import ReflectionMaintenanceService
from brain.application.workflow.workflow import BrainWorkflow
from brain.application.usecases.planning import PlanningUseCase
from brain.application.usecases.execution import ExecutionUseCase
from brain.application.usecases.learning import LearningUseCase
from brain.application.usecases.reflection import ReflectionUseCase


class TestMemoryRuntimeCreation:
    def test_creates_successfully(self):
        r = create_memory_runtime()
        assert isinstance(r, BrainRuntime)

    def test_has_all_components(self):
        r = create_memory_runtime()
        assert r.adapter is not None
        assert r.session is not None
        assert r.service is not None
        assert r.repository is not None
        assert r.validation is not None
        assert r.retrieval is not None
        assert r.reflection is not None
        assert r.evolution is not None
        assert r.detection is not None
        assert r.learning is not None
        assert r.publisher is not None
        assert r.workflow is not None
        assert r.maintenance is not None


class TestSQLiteRuntimeCreation:
    def test_creates_successfully(self):
        r = create_sqlite_runtime(":memory:")
        assert isinstance(r, BrainRuntime)

    def test_has_all_components(self):
        r = create_sqlite_runtime(":memory:")
        assert r.adapter is not None
        assert r.session is not None
        assert r.service is not None
        assert r.repository is not None
        assert r.workflow is not None
        assert r.maintenance is not None


class TestRuntimeImmutability:
    def test_frozen(self):
        r = create_memory_runtime()
        with pytest.raises(AttributeError):
            r.adapter = None

    def test_workflow_frozen(self):
        r = create_memory_runtime()
        with pytest.raises(AttributeError):
            r.workflow = None

    def test_maintenance_frozen(self):
        r = create_memory_runtime()
        with pytest.raises(AttributeError):
            r.maintenance = None


class TestRuntimeDependencyWiring:
    def test_adapter_uses_correct_session(self):
        r = create_memory_runtime()
        assert r.adapter._session is r.session

    def test_session_uses_correct_service(self):
        r = create_memory_runtime()
        assert r.session._brain is r.service

    def test_service_uses_correct_repository(self):
        r = create_memory_runtime()
        assert r.service._repository is r.repository

    def test_service_uses_correct_validation(self):
        r = create_memory_runtime()
        assert r.service._validator is r.validation

    def test_evolution_uses_correct_repository(self):
        r = create_memory_runtime()
        assert r.evolution._knowledge is r.repository
        assert r.evolution._evolution is r.repository

    def test_workflow_uses_correct_session(self):
        r = create_memory_runtime()
        assert r.workflow._session is r.session

    def test_workflow_uses_correct_planning(self):
        r = create_memory_runtime()
        assert r.workflow._planning is not None
        assert isinstance(r.workflow._planning, PlanningUseCase)

    def test_workflow_uses_correct_execution(self):
        r = create_memory_runtime()
        assert r.workflow._execution is not None
        assert isinstance(r.workflow._execution, ExecutionUseCase)

    def test_workflow_uses_correct_learning(self):
        r = create_memory_runtime()
        assert r.workflow._learning is not None
        assert isinstance(r.workflow._learning, LearningUseCase)

    def test_workflow_uses_correct_mapper(self):
        r = create_memory_runtime()
        assert r.workflow._mapper is not None
        assert isinstance(r.workflow._mapper, ExecutionLearningMapper)

    def test_planning_uses_correct_engine(self):
        r = create_memory_runtime()
        assert r.workflow._planning.engine is not None

    def test_execution_uses_correct_engine(self):
        r = create_memory_runtime()
        assert r.workflow._execution.engine is not None

    def test_execution_uses_same_planning(self):
        r = create_memory_runtime()
        assert r.workflow._execution.planning is r.workflow._planning

    def test_learning_uses_correct_coordinator(self):
        r = create_memory_runtime()
        assert r.workflow._learning.coordinator is not None

    def test_maintenance_is_reflection_maintenance_service(self):
        r = create_memory_runtime()
        assert isinstance(r.maintenance, ReflectionMaintenanceService)

    def test_maintenance_uses_correct_reflection_use_case(self):
        r = create_memory_runtime()
        assert r.maintenance.reflection is not None
        assert isinstance(r.maintenance.reflection, ReflectionUseCase)

    def test_reflection_use_case_uses_correct_engine(self):
        r = create_memory_runtime()
        assert r.maintenance.reflection.engine is r.reflection

    def test_reflection_use_case_uses_correct_repository(self):
        r = create_memory_runtime()
        assert r.maintenance.reflection.repository is r.repository

    def test_workflow_is_brain_workflow(self):
        r = create_memory_runtime()
        assert isinstance(r.workflow, BrainWorkflow)

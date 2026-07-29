# Graph Report - .  (2026-07-26)

## Corpus Check
- Corpus is ~30,807 words - fits in a single context window. You may not need a graph.

## Summary
- 1755 nodes · 6842 edges · 98 communities (92 shown, 6 thin omitted)
- Extraction: 66% EXTRACTED · 34% INFERRED · 0% AMBIGUOUS · INFERRED: 2355 edges (avg confidence: 0.5)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- Application Layer
- Domain Tasks & Retrieval
- Scoring Factors
- Identity & Evolution
- Domain Enums & SQLite
- Memory Repository
- Identity Repository
- Detection Pipeline
- Integration Coordinator
- Domain Enums & Pipeline
- Evolution Engine
- Service & Detection
- Knowledge Version
- Runtime Composition
- Validation & Service
- Integration Events
- Reflection Detectors
- Validation Engine
- BrainService Tests
- Adapter Lifecycle
- Planning Goals & Plans
- Adapter Core
- Understanding Model
- Integration Learning
- Integration State
- Integration Tests
- Planning Actions
- Adapter Tests
- Domain References
- Integration Models
- Planning Blockers
- Strategy Tests
- Task Mapper
- Pipeline Evidence
- Planning Goal Model
- Evolution Transition
- Evolution Conflict Tests
- Reflection Finding Tests
- Pipeline Events
- Planning Engine
- Reflection Engine
- Coordinator Tests
- Adapter Learning
- Planning Action Model
- SQLite Connection
- Pipeline Validator Tests
- Detection Report
- Adapter Models
- Service Init
- Event Recorder
- Gap Detector
- Reflection Type
- Evidence Rule
- Confidence Rule
- Type Rules
- Dependency Tests
- Integration Facade
- Transition Type
- Duplicate Detector Tests
- Obsolete Detector Tests
- Completeness Rule
- Conflict Detector Tests
- BrainAdapter
- Planning Context
- Duplicate Detector
- Dependency Boundary
- Service History

## God Nodes (most connected - your core abstractions)
1. `KnowledgeVersion` - 265 edges
2. `KnowledgeType` - 247 edges
3. `Task` - 134 edges
4. `LifecycleState` - 133 edges
5. `KnowledgeCandidate` - 129 edges
6. `Evidence` - 119 edges
7. `TaskType` - 101 edges
8. `InMemoryKnowledgeRepository` - 100 edges
9. `Evidence` - 97 edges
10. `SQLiteKnowledgeRepository` - 95 edges

## Surprising Connections (you probably didn't know these)
- `TestCompleteWithLifecycle` --uses--> `BrainAdapter`  [INFERRED]
  tests/adapter/test_adapter.py → src/brain/adapter/adapter.py
- `TestErrorBoundary` --uses--> `BrainAdapter`  [INFERRED]
  tests/adapter/test_adapter.py → src/brain/adapter/adapter.py
- `TestLearnWithLifecycle` --uses--> `BrainAdapter`  [INFERRED]
  tests/adapter/test_adapter.py → src/brain/adapter/adapter.py
- `TestStartTaskWithMapper` --uses--> `BrainAdapter`  [INFERRED]
  tests/adapter/test_adapter.py → src/brain/adapter/adapter.py
- `TestCompleteTaskOrchestration` --uses--> `BrainAdapter`  [INFERRED]
  tests/integration/test_coordinator.py → src/brain/adapter/adapter.py

## Import Cycles
- None detected.

## Communities (98 total, 6 thin omitted)

### Community 0 - "Application Layer"
Cohesion: 0.05
Nodes (62): BrainSession, SessionStatus, KnowledgeType, Priority, Enum, Task, TaskType, ContextCompiler (+54 more)

### Community 1 - "Domain Tasks & Retrieval"
Cohesion: 0.05
Nodes (23): ABC, TriggerCondition, ComponentCondition, KeywordCondition, KnowledgeTypeCondition, ProjectCondition, TaskTypeCondition, RetrievalTriggerEngine (+15 more)

### Community 2 - "Scoring Factors"
Cohesion: 0.08
Nodes (25): IntentMatch, KnowledgePriority, LifecycleStateFactor, RecencyFactor, RelationshipDistance, RelevanceEngine, ScoredVersion, ABC (+17 more)

### Community 3 - "Identity & Evolution"
Cohesion: 0.07
Nodes (23): Conflict, ConflictStatus, Enum, KnowledgeTransition, Enum, TransitionType, KnowledgeRepository, ABC (+15 more)

### Community 4 - "Domain Enums & SQLite"
Cohesion: 0.13
Nodes (23): LifecycleState, Evidence, Relationship, SQLiteKnowledgeRepository, DuplicateVersionError, Exception, VersionNotFoundError, make_version() (+15 more)

### Community 5 - "Memory Repository"
Cohesion: 0.09
Nodes (14): InMemoryKnowledgeRepository, make_conflict(), make_transition(), TestInMemoryConflictStorage, TestInMemoryTransitionStorage, make_version(), UUID, TestDuplicateRejection (+6 more)

### Community 6 - "Identity Repository"
Cohesion: 0.10
Nodes (11): KnowledgeIdentity, Create and store a new KnowledgeIdentity., TestKnowledgeIdentityCreation, TestKnowledgeIdentityImmutability, create_version(), UUID, TestKnowledgeVersionId, TestKnowledgeVersionIdentityStability (+3 more)

### Community 7 - "Detection Pipeline"
Cohesion: 0.11
Nodes (12): ABC, Observation, MultiCandidateDetector, RuleBasedDetector, TestDetectorInterfaceCompliance, TestDeterministicExecution, TestMultipleCandidateScenarios, TestZeroCandidateScenarios (+4 more)

### Community 8 - "Integration Coordinator"
Cohesion: 0.12
Nodes (12): IntegrationStatus, IntegrationEvent, UUID, SessionCoordinator, IntegrationError, Exception, IntegrationLayer, IntegrationEvent (+4 more)

### Community 9 - "Domain Enums & Pipeline"
Cohesion: 0.16
Nodes (8): Enum, UUID, ValidationReport, ValidationResult, ABC, ValidationRule, TestValidationResult, TestValidationRuleInterface

### Community 10 - "Evolution Engine"
Cohesion: 0.12
Nodes (14): EvolutionEngine, make_engine(), make_version(), UUID, TestEvolveDeterministic, TestEvolveDifferentIdentity, TestEvolveExplicitTypes, TestEvolveNoPreviousVersion (+6 more)

### Community 11 - "Service & Detection"
Cohesion: 0.25
Nodes (19): BrainService, KnowledgeDetector, DetectionPipeline, CandidateValidator, ValidationResult, EmptyDetector, FailValidator, make_observation() (+11 more)

### Community 12 - "Knowledge Version"
Cohesion: 0.10
Nodes (11): KnowledgeVersion, UUID, UUID, Store a KnowledgeVersion. Rejects duplicate version numbers for the same identit, Retrieve a KnowledgeIdentity by ID. Raises KeyError if not found., Retrieve the latest version for an identity. Raises KeyError if none found., Retrieve a specific version. Raises KeyError if not found., Return all versions for an identity, ordered by version number. (+3 more)

### Community 13 - "Runtime Composition"
Cohesion: 0.14
Nodes (11): create_memory_runtime(), create_sqlite_runtime(), BrainHealthReport, check_health(), BrainRuntime, TestCheckHealthFunction, TestHealthReport, TestMemoryRuntimeCreation (+3 more)

### Community 14 - "Validation & Service"
Cohesion: 0.09
Nodes (14): KnowledgeCandidate, ValidationResult, ValidationResult, ValidationResult, ValidationResult, ValidationResult, make_candidate(), ValidationResult (+6 more)

### Community 15 - "Integration Events"
Cohesion: 0.17
Nodes (11): ContextPrepared, ContextUnavailable, KnowledgeLearned, LearningFailed, TaskCompleted, TestContextPrepared, TestContextUnavailable, TestKnowledgeLearned (+3 more)

### Community 16 - "Reflection Detectors"
Cohesion: 0.15
Nodes (12): ConflictDetector, DuplicateDetector, ObsoleteDetector, ReflectionEngine, ReflectionFinding, _create_common_components(), make_duplicate_versions(), make_version() (+4 more)

### Community 17 - "Validation Engine"
Cohesion: 0.23
Nodes (7): ValidationEngine, FailingRule, make_candidate(), PassingRule, ValidationResult, TestDefaultRules, TestValidationEngine

### Community 18 - "BrainService Tests"
Cohesion: 0.15
Nodes (13): add_version_to_repo(), make_candidate(), make_service(), make_task(), make_version(), UUID, TestHistory, TestLatest (+5 more)

### Community 19 - "Adapter Lifecycle"
Cohesion: 0.16
Nodes (7): AdapterNotReadyError, AdapterLifecycle, AdapterLifecycleState, AdapterState, Enum, UUID, TestAdapterLifecycle

### Community 20 - "Planning Goals & Plans"
Cohesion: 0.15
Nodes (11): Goal, Plan, PlanStatus, Enum, make_goal(), make_plan(), TestPlanCreation, TestPlanImmutability (+3 more)

### Community 21 - "Adapter Core"
Cohesion: 0.14
Nodes (8): UUID, HermesBrainAdapter, ABC, UUID, AdapterContext, TestHermesBrainAdapter, _make_context_package(), TestAdapterContext

### Community 22 - "Understanding Model"
Cohesion: 0.16
Nodes (6): Understanding, create_understanding(), TestUnderstandingEquality, TestUnderstandingImmutability, TestUnderstandingTuples, TestUnderstandingValidation

### Community 23 - "Integration Learning"
Cohesion: 0.16
Nodes (7): IntegrationLearning, _make_coordinator(), _make_integration_task(), _make_layer(), _make_version(), TestCoordinatorMetrics, TestIntegrationLearning

### Community 24 - "Integration State"
Cohesion: 0.14
Nodes (3): IntegrationStateMachine, TestIntegrationState, TestIntegrationStateMachine

### Community 25 - "Integration Tests"
Cohesion: 0.21
Nodes (9): _make_context_package(), _make_integration_task(), _make_layer(), _make_version(), TestDeterministicBehavior, TestIntegrationLayerComplete, TestIntegrationLayerErrorBoundary, TestIntegrationLayerLearn (+1 more)

### Community 26 - "Planning Actions"
Cohesion: 0.35
Nodes (5): Action, Dependency, DependencyStrategy, PlanningStrategy, ABC

### Community 27 - "Adapter Tests"
Cohesion: 0.22
Nodes (9): _make_adapter(), _make_adapter_task(), _make_context_package(), _make_learning(), _make_version(), TestCompleteWithLifecycle, TestErrorBoundary, TestLearnWithLifecycle (+1 more)

### Community 29 - "Integration Models"
Cohesion: 0.20
Nodes (4): IntegrationTask, _make_full_stack(), TestEndToEndFlow, TestIntegrationTask

### Community 30 - "Planning Blockers"
Cohesion: 0.18
Nodes (8): Blocker, BlockerSeverity, Enum, make_blocker(), TestBlockerCreation, TestBlockerImmutability, TestBlockerSeverity, TestBlockerValidation

### Community 31 - "Strategy Tests"
Cohesion: 0.19
Nodes (5): make_action(), make_dependency(), UUID, TestDependencyStrategy, TestSequentialStrategy

### Community 32 - "Task Mapper"
Cohesion: 0.27
Nodes (4): InvalidAdapterTaskError, TaskMapper, _make_adapter_task(), TestTaskMapper

### Community 33 - "Pipeline Evidence"
Cohesion: 0.19
Nodes (6): Evidence, TestEvidenceCreation, TestEvidenceEquality, TestEvidenceImmutability, TestEvidenceValidation, TestVersionCreatorDeterminism

### Community 34 - "Planning Goal Model"
Cohesion: 0.18
Nodes (7): GoalStatus, Enum, make_goal(), TestGoalCreation, TestGoalImmutability, TestGoalStatus, TestGoalValidation

### Community 35 - "Evolution Transition"
Cohesion: 0.18
Nodes (4): make_transition(), TestTransitionCreation, TestTransitionImmutability, TestTransitionValidation

### Community 36 - "Evolution Conflict Tests"
Cohesion: 0.17
Nodes (5): make_conflict(), TestConflictCreation, TestConflictImmutability, TestConflictStatus, TestConflictValidation

### Community 37 - "Reflection Finding Tests"
Cohesion: 0.19
Nodes (4): make_finding(), TestReflectionFindingCreation, TestReflectionFindingImmutability, TestReflectionFindingValidation

### Community 38 - "Pipeline Events"
Cohesion: 0.18
Nodes (8): KnowledgeEvent, make_event(), make_evidence(), Evidence, TestKnowledgeEventCreation, TestKnowledgeEventEquality, TestKnowledgeEventImmutability, TestKnowledgeEventValidation

### Community 39 - "Planning Engine"
Cohesion: 0.35
Nodes (6): PlanningEngine, SequentialStrategy, make_action(), make_goal(), UUID, TestPlanningEngineBehavior

### Community 40 - "Reflection Engine"
Cohesion: 0.19
Nodes (6): ReflectionReport, make_finding(), make_report(), TestReflectionReportCreation, TestReflectionReportImmutability, TestReflectionReportValidation

### Community 41 - "Coordinator Tests"
Cohesion: 0.25
Nodes (7): _make_context_package(), _make_coordinator(), _make_integration_task(), _make_version(), TestCompleteTaskOrchestration, TestErrorWrapping, TestStartTaskOrchestration

### Community 42 - "Adapter Learning"
Cohesion: 0.24
Nodes (5): AdapterLearning, TestAdapterLearning, _make_task(), TestMemoryRuntimeLifecycle, TestSQLiteRuntimePersistence

### Community 43 - "Planning Action Model"
Cohesion: 0.22
Nodes (6): ActionStatus, Enum, make_action(), TestActionCreation, TestActionImmutability, TestActionValidation

### Community 44 - "SQLite Connection"
Cohesion: 0.19
Nodes (5): Connection, Cursor, Path, SQLiteConnection, initialize_schema()

### Community 45 - "Pipeline Validator Tests"
Cohesion: 0.22
Nodes (6): make_candidate(), make_evidence(), Evidence, TestValidatorFailure, TestValidatorImmutability, TestValidatorSuccess

### Community 46 - "Detection Report"
Cohesion: 0.25
Nodes (5): DetectionReport, make_candidate(), make_version(), TestDetectionReportCreation, TestDetectionReportImmutability

### Community 47 - "Adapter Models"
Cohesion: 0.27
Nodes (3): AdapterTask, _make_adapter_task(), TestAdapterTask

### Community 48 - "Service Init"
Cohesion: 0.33
Nodes (4): VersionCreator, make_candidate(), TestVersionCreatorImmutability, TestVersionCreatorSuccess

### Community 49 - "Event Recorder"
Cohesion: 0.27
Nodes (4): TaskStarted, EventRecorder, IntegrationEvent, TestEventRecorder

### Community 50 - "Gap Detector"
Cohesion: 0.19
Nodes (3): GapDetector, make_version(), TestGapDetector

### Community 51 - "Reflection Type"
Cohesion: 0.18
Nodes (4): Enum, ReflectionType, TestReflectionTypeImmutability, TestReflectionTypeValues

### Community 52 - "Evidence Rule"
Cohesion: 0.33
Nodes (4): EvidenceRule, make_candidate(), make_candidate_with_mock_source(), TestEvidenceRule

### Community 53 - "Confidence Rule"
Cohesion: 0.35
Nodes (4): ConfidenceRule, TestDependencyInjection, make_candidate(), TestConfidenceRule

### Community 54 - "Type Rules"
Cohesion: 0.42
Nodes (3): TypeRules, make_candidate(), TestTypeRules

### Community 55 - "Dependency Tests"
Cohesion: 0.27
Nodes (4): make_dependency(), TestDependencyCreation, TestDependencyImmutability, TestDependencyValidation

### Community 56 - "Integration Facade"
Cohesion: 0.25
Nodes (4): IntegrationContext, IntegrationSection, TestIntegrationContext, TestIntegrationSection

### Community 59 - "Obsolete Detector Tests"
Cohesion: 0.31
Nodes (3): make_version(), UUID, TestObsoleteDetector

### Community 60 - "Completeness Rule"
Cohesion: 0.49
Nodes (3): CompletenessRule, make_candidate(), TestCompletenessRule

### Community 61 - "Conflict Detector Tests"
Cohesion: 0.33
Nodes (3): make_version(), Evidence, TestConflictDetector

### Community 62 - "BrainAdapter"
Cohesion: 0.39
Nodes (5): BrainAdapter, AdapterError, Exception, TestDependencyInjection, TestDeterministicBehavior

### Community 63 - "Planning Context"
Cohesion: 0.39
Nodes (3): PlanningContext, TestPlanningContextCreation, TestPlanningContextImmutability

## Knowledge Gaps
- **6 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `KnowledgeType` connect `Application Layer` to `Domain Tasks & Retrieval`, `Scoring Factors`, `Identity & Evolution`, `Domain Enums & SQLite`, `Memory Repository`, `Identity Repository`, `Detection Pipeline`, `Integration Coordinator`, `Domain Enums & Pipeline`, `Evolution Engine`, `Service & Detection`, `Knowledge Version`, `Validation & Service`, `Reflection Detectors`, `Validation Engine`, `BrainService Tests`, `Planning Goals & Plans`, `Adapter Core`, `Integration Learning`, `Integration Tests`, `Planning Actions`, `Adapter Tests`, `Domain References`, `Integration Models`, `Strategy Tests`, `Pipeline Evidence`, `Pipeline Events`, `Planning Engine`, `Coordinator Tests`, `Planning Action Model`, `Pipeline Validator Tests`, `Detection Report`, `Service Init`, `Event Recorder`, `Gap Detector`, `Evidence Rule`, `Confidence Rule`, `Type Rules`, `Duplicate Detector Tests`, `Obsolete Detector Tests`, `Completeness Rule`, `Conflict Detector Tests`, `BrainAdapter`, `Planning Context`, `Duplicate Detector`?**
  _High betweenness centrality (0.295) - this node is a cross-community bridge._
- **Why does `KnowledgeVersion` connect `Knowledge Version` to `Application Layer`, `Scoring Factors`, `Identity & Evolution`, `Domain Enums & SQLite`, `Memory Repository`, `Identity Repository`, `Integration Coordinator`, `Domain Enums & Pipeline`, `Evolution Engine`, `Service & Detection`, `Validation & Service`, `Reflection Detectors`, `BrainService Tests`, `Adapter Core`, `Integration Learning`, `Integration Tests`, `Adapter Tests`, `Domain References`, `Integration Models`, `Reflection Engine`, `Coordinator Tests`, `Adapter Learning`, `Detection Report`, `Adapter Models`, `Service Init`, `Event Recorder`, `Gap Detector`, `Confidence Rule`, `Duplicate Detector Tests`, `Obsolete Detector Tests`, `Conflict Detector Tests`, `BrainAdapter`, `Duplicate Detector`, `Service History`?**
  _High betweenness centrality (0.220) - this node is a cross-community bridge._
- **Why does `Priority` connect `Application Layer` to `Task Mapper`, `Domain Tasks & Retrieval`, `Planning Goal Model`, `Planning Engine`, `Integration Coordinator`, `Coordinator Tests`, `Adapter Learning`, `Adapter Models`, `Event Recorder`, `BrainService Tests`, `Planning Goals & Plans`, `Adapter Core`, `Confidence Rule`, `Integration Learning`, `Integration Tests`, `Adapter Tests`, `BrainAdapter`?**
  _High betweenness centrality (0.066) - this node is a cross-community bridge._
- **Are the 171 inferred relationships involving `KnowledgeVersion` (e.g. with `BrainAdapter` and `HermesBrainAdapter`) actually correct?**
  _`KnowledgeVersion` has 171 INFERRED edges - model-reasoned connections that need verification._
- **Are the 202 inferred relationships involving `KnowledgeType` (e.g. with `BrainAdapter` and `KnowledgeVersion`) actually correct?**
  _`KnowledgeType` has 202 INFERRED edges - model-reasoned connections that need verification._
- **Are the 91 inferred relationships involving `Task` (e.g. with `TaskMapper` and `BrainService`) actually correct?**
  _`Task` has 91 INFERRED edges - model-reasoned connections that need verification._
- **Are the 121 inferred relationships involving `LifecycleState` (e.g. with `KnowledgeVersion` and `SQLiteKnowledgeRepository`) actually correct?**
  _`LifecycleState` has 121 INFERRED edges - model-reasoned connections that need verification._
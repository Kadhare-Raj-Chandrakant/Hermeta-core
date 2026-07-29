# Hermes Brain Runtime Architecture

## Why Runtime Exists

Hermes Brain contains many independent modules: domain models, repositories, services, validation, detection, evolution, reflection, retrieval, and adapter layers. Each module is independently testable and follows strict dependency rules. However, manually constructing and wiring these components is error-prone and creates coupling between consumers and internal implementation details.

BrainRuntime solves this by providing a single composition root where all components are assembled. Consumers receive a fully configured runtime and never manually wire internal brain components again.

## Why Factories Own Dependency Creation

The factory (`create_memory_runtime`, `create_sqlite_runtime`) is the only place where concrete implementations are chosen. This separation means:

- Consumers depend on abstractions (interfaces), not concrete classes
- Swapping storage backends (memory vs SQLite vs future cloud) requires only calling a different factory
- Test fixtures can create isolated runtimes without knowing internal wiring
- Configuration changes are centralized in one location

## Why Business Logic Does Not Belong Here

BrainRuntime is purely structural. It holds references to configured components but adds no behavior:

- It does not decide which knowledge to store
- It does not evaluate relevance or selection
- It does not validate or transform data
- It does not manage lifecycle or state transitions

All intelligence lives in the components it references. Runtime is the skeleton, not the brain.

## Dependency Direction

```
Hermes Application
        |
        v
   BrainRuntime
        |
        +---> BrainAdapter
        |         |
        |         v
        |    BrainSession
        |         |
        |         v
        |    BrainService
        |         |
        |    +---------+
        |    |         |
        |  Validation  Repository
        |  Engine      (Memory | SQLite)
        |
        +---> RetrievalTriggerEngine
        |
        +---> ReflectionEngine
        |
        +---> EvolutionEngine
        |         |
        |         v
        |    KnowledgeRepository + EvolutionRepository
        |
        +---> DetectionPipeline
```

**Runtime depends on everything. Nothing depends on runtime.**

Allowed imports into runtime:
- adapter
- application (BrainService, BrainSession)
- services
- detection
- validation
- evolution
- reflection
- retrieval
- repositories
- infrastructure (for SQLite factory)

Forbidden: no inner module imports runtime.

## How Hermes Application Integrates with Runtime

```python
from brain.runtime import create_memory_runtime

# Create the runtime
runtime = create_memory_runtime()

# Or with SQLite persistence
runtime = create_sqlite_runtime("brain.db")

# Use the adapter to interact with the brain
from brain.adapter.models import AdapterTask, AdapterLearning
from brain.domain.task import TaskType

task = AdapterTask(
    task_id=uuid.uuid4(),
    task_type=TaskType.IMPLEMENT,
    objective="Build authentication system",
    project="myapp",
    component="auth",
    metadata={},
)

context = runtime.adapter.start_task(task)
runtime.adapter.learn(AdapterLearning(
    task_id=task.task_id,
    knowledge_type="ARCHITECTURE",
    title="Auth Architecture",
    understanding="Uses JWT tokens with refresh rotation...",
    confidence=0.9,
))
runtime.adapter.complete_task(task.task_id)

# Check system health
from brain.runtime import check_health
health = check_health(runtime)
assert health.healthy

# Perform reflection
versions = runtime.repository.list_all_versions()
report = runtime.reflection.reflect(versions)
```

## Available Runtimes

| Factory | Storage | Persistence | Use Case |
|---------|---------|-------------|----------|
| `create_memory_runtime()` | In-memory dict | No | Testing, development |
| `create_sqlite_runtime(path)` | SQLite file | Yes | Production, persistence |

## Health Checking

`check_health(runtime)` verifies all components are available and returns a `BrainHealthReport`:

```python
@dataclass(frozen=True)
class BrainHealthReport:
    healthy: bool
    components: tuple[str, ...]  # names of available components
    failures: tuple[str, ...]    # names of missing components
```

## Future Extension Points

Prepared for:

1. **Configuration files** - Factory parameters for tuning
2. **Environment-based factories** - Select runtime via environment variables
3. **Multiple project runtimes** - Isolated brain instances per project
4. **Remote repository runtime** - Network-backed storage
5. **Observability hooks** - Metrics and tracing integration
6. **Background reflection workers** - Async reflection processing
7. **Automatic retrieval loops** - Continuous knowledge gathering

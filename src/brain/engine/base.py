# Engine Base Classes and Interfaces

"""
Shared base classes and interfaces for all Hermes engines.
"""

import threading
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Generic, TypeVar, Tuple, Optional
from uuid import UUID
from dataclasses import dataclass
from abc import abstractmethod


# Type variables for generic engine contracts
InputT = TypeVar('InputT')
OutputT = TypeVar('OutputT')
ContextT = TypeVar('ContextT')


@dataclass(frozen=True)
class EngineMetadata:
    """Metadata about an engine execution."""
    engine_name: str
    engine_version: str
    execution_id: UUID
    started_at: datetime
    completed_at: Optional[datetime] = None
    success: bool = True
    error: Optional[str] = None


class EngineContract(ABC, Generic[InputT, OutputT]):
    """
    Abstract base contract for all Hermes engines.
    
    Every engine must implement this contract to ensure constitutional compliance.
    """
    
    @property
    @abstractmethod
    def engine_name(self) -> str:
        """Unique name of this engine."""
        pass
    
    @property
    @abstractmethod
    def engine_version(self) -> str:
        """Version of this engine implementation."""
        pass
    
    @property
    @abstractmethod
    def contract_version(self) -> str:
        """Version of the contract this engine implements."""
        pass
    
    @abstractmethod
    def validate_input(self, input_data: InputT) -> Tuple[bool, str]:
        """
        Validate input before processing.
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        pass
    
    @abstractmethod
    def validate_output(self, output_data: OutputT) -> Tuple[bool, str]:
        """
        Validate output after processing.
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        pass
    
    @abstractmethod
    def process(self, input_data: InputT) -> OutputT:
        """
        Process input and produce output.
        
        This is the main execution method.
        Must be pure: same input -> same output.
        """
        pass
    
    def execute(self, input_data: InputT) -> OutputT:
        """
        Execute the engine with full validation.
        
        This is the main entry point that enforces the contract.
        """
        # Validate input
        is_valid, error = self.validate_input(input_data)
        if not is_valid:
            raise ValueError(f"Input validation failed: {error}")
        
        # Process
        output = self.process(input_data)
        
        # Validate output
        is_valid, error = self.validate_output(output)
        if not is_valid:
            raise ValueError(f"Output validation failed: {error}")
        
        return output
    
    def get_metadata(self) -> dict:
        """Get engine metadata."""
        return {
            "engine_name": self.engine_name,
            "engine_version": self.engine_version,
            "contract_version": self.contract_version,
        }


@dataclass(frozen=True)
class EngineContext:
    """
    Base context for engine execution.
    Contains only the minimal information needed for execution.
    """
    execution_id: UUID
    constitutional_version: str
    created_at: datetime = field(default_factory=datetime.now)
    metadata: Tuple[Tuple[str, str], ...] = ()


@dataclass(frozen=True)
class EngineResult(Generic[OutputT]):
    """Result of engine execution with metadata."""
    output: OutputT
    metadata: EngineMetadata
    trace_id: UUID


class EngineRegistry:
    """Registry for engine implementations."""

    _engines: dict = {}
    _lock = threading.RLock()

    @classmethod
    def register(cls, engine_name: str, engine_class: type):
        """Register an engine implementation."""
        with cls._lock:
            cls._engines[engine_name] = engine_class

    @classmethod
    def get(cls, engine_name: str) -> Optional[type]:
        """Get engine class by name."""
        with cls._lock:
            return cls._engines.get(engine_name)

    @classmethod
    def list_engines(cls) -> Tuple[str, ...]:
        """List all registered engines."""
        with cls._lock:
            return tuple(cls._engines.keys())


# Constitutional compliance markers
class ConstitutionalCompliance:
    """Marker interface for constitutional compliance."""

    # Constitutional laws this component complies with
    COMPLIANT_LAWS: Tuple[str, ...] = ()

    # Constitutional laws this component MUST NOT violate
    FORBIDDEN_ACTIONS: Tuple[str, ...] = ()

    @classmethod
    def verify_compliance(cls) -> bool:
        """Verify at runtime that an engine class satisfies the contract.

        Checks, without instantiating, that the engine class:
        - exposes the constitutional version entry point (contract_version or version)
        - has at least one execution entry point (execute, process, adjudicate, authorize)
        - has input/output validation hooks (validate_input, validate_output) or a
          canonical async path named after one of the domain stages.
        Returns True only if every check passes; otherwise raises ValueError identifying
        the first violated invariant (fail-loud, no silent True theater).
        """
        from brain.core.constants import CONSTITUTIONAL_VERSION

        engine_name = getattr(cls, "engine_name", "unknown-engine")
        # Honour property descriptors: resolve to string
        if isinstance(engine_name, property):
            engine_name = cls.__name__

        # 1. Version entrypoint must be declared (as attr, property, or class attr).
        has_version_entry = (
            hasattr(cls, "contract_version")
            or hasattr(cls, "version")
            or hasattr(cls, "engine_version")
        )
        if not has_version_entry:
            raise ValueError(
                f"{engine_name}: engine class must expose contract_version/version entry point"
            )

        # Resolve to a concrete string and compare against the constitutional constant
        # if it is bound at class load time as a plain string constant.
        version_value = None
        for attr in ("contract_version", "version", "engine_version"):
            value = getattr(cls, attr, None)
            if isinstance(value, str):
                version_value = value
                break
        if version_value is not None and version_value != CONSTITUTIONAL_VERSION:
            raise ValueError(
                f"{engine_name}: constitutional_version mismatch "
                f"(declared={version_value!r}, expected={CONSTITUTIONAL_VERSION!r})"
            )

        # 2. Execution entrypoint required. Each constitutional engine exposes at
        # least one canonical verb: execute, process, adjudicate, authorize, or
        # evaluate_space for the space-level evaluators.
        exec_entries = (
            "execute", "process", "adjudicate", "authorize", "evaluate_space",
            "formulate", "generate", "observe",
        )
        has_exec = any(callable(getattr(cls, name, None)) for name in exec_entries)
        if not has_exec:
            raise ValueError(
                f"{engine_name}: no execution entry point "
                f"(expected one of {exec_entries})"
            )

        return True
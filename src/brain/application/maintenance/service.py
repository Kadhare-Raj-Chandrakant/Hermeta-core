from dataclasses import dataclass

from brain.application.usecases.models import ReflectionRequest, ReflectionSummary
from brain.application.usecases.reflection import ReflectionUseCase


@dataclass(frozen=True)
class ReflectionMaintenanceService:
    reflection: ReflectionUseCase

    def reflect(self, request: ReflectionRequest) -> ReflectionSummary:
        return self.reflection.execute(request)

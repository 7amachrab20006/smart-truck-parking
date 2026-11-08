"""Abstract base adapter for jurisdiction-specific traffic and parking regulations."""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Optional

from app.domain.regulatory_engine.models import (
    RegulationRecord,
    RequestedActivity,
    RuleEvaluationResult,
    VehicleProfile,
)


class JurisdictionRuleAdapter(ABC):
    """Abstract interface for local legal definitions and traffic rules.
    
    Each city or municipality has distinct legal definitions for terms like
    'No Parking', 'No Standing', 'Commercial Vehicle', and truck routing bylaws.
    """

    @property
    @abstractmethod
    def jurisdiction_code(self) -> str:
        """Standard jurisdiction identifier (e.g. 'US-NYC')."""
        pass

    @property
    @abstractmethod
    def jurisdiction_name(self) -> str:
        """Human-readable jurisdiction name."""
        pass

    @abstractmethod
    def evaluate(
        self,
        vehicle: VehicleProfile,
        regulations: List[RegulationRecord],
        activity: RequestedActivity,
        eval_time: datetime,
        is_truck_route: Optional[bool] = None,
    ) -> RuleEvaluationResult:
        """Evaluate whether the given vehicle can perform the activity at eval_time
        under the supplied regulations.
        """
        pass

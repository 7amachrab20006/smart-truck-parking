"""Core Regulatory Intelligence Engine.

Answers the master business question:
'Can this specific vehicle perform this specific activity at this geographical location at this exact date and time?'
"""

from datetime import datetime
from typing import Dict, List, Optional

from app.domain.regulatory_engine.adapters.base import JurisdictionRuleAdapter
from app.domain.regulatory_engine.adapters.nyc import NYCRuleAdapter
from app.domain.regulatory_engine.models import (
    AlternativeLocation,
    EvaluationDecision,
    RegulationRecord,
    RegulatoryEvaluationResponse,
    RequestedActivity,
    StreetSide,
    VehicleProfile,
)


class RegulatoryEngine:
    """Enterprise Regulatory Evaluation Engine."""

    def __init__(self):
        self._adapters: Dict[str, JurisdictionRuleAdapter] = {}
        # Register default NYC adapter
        self.register_adapter(NYCRuleAdapter())

    def register_adapter(self, adapter: JurisdictionRuleAdapter) -> None:
        """Registers a jurisdiction rule adapter."""
        self._adapters[adapter.jurisdiction_code] = adapter

    def get_adapter(self, jurisdiction_code: str) -> JurisdictionRuleAdapter:
        """Retrieves adapter for jurisdiction, defaulting to NYC."""
        return self._adapters.get(jurisdiction_code, self._adapters["US-NYC"])

    def evaluate(
        self,
        vehicle: VehicleProfile,
        regulations: List[RegulationRecord],
        activity: RequestedActivity,
        eval_time: Optional[datetime] = None,
        street_side: Optional[StreetSide] = None,
        is_truck_route: Optional[bool] = None,
        jurisdiction_code: str = "US-NYC",
        alternatives: Optional[List[AlternativeLocation]] = None,
    ) -> RegulatoryEvaluationResponse:
        """Evaluates whether the vehicle can legally perform activity at the location."""
        if eval_time is None:
            eval_time = datetime.now()

        adapter = self.get_adapter(jurisdiction_code)
        warnings: List[str] = []

        # 1. Street side filtering
        # Curb regulations apply strictly to the specific side of the street (Rule #5)
        filtered_regs = regulations
        if street_side and street_side != StreetSide.UNKNOWN:
            filtered_regs = [
                r for r in regulations
                if r.street_side in (street_side, StreetSide.BOTH, StreetSide.UNKNOWN)
            ]
            if not filtered_regs and regulations:
                warnings.append(
                    f"Street has different regulations on each side. Evaluating specifically for {street_side.value} curb."
                )

        # 2. Check for conflicting regulations (Rule #8: If information conflicts, return UNKNOWN or CONDITIONAL)
        classifications = {r.classification for r in filtered_regs}
        has_conflict = False
        if (
            "NO_STOPPING" in [c.value for c in classifications]
            and any(c.value in ("COMMERCIAL_LOADING", "TRUCK_LOADING_ONLY") for c in classifications)
        ):
            has_conflict = True
            warnings.append(
                "CONFLICT DETECTED: Conflicting posted signs detected at this segment. Manual inspection advised."
            )

        # 3. Invoke jurisdiction adapter
        result = adapter.evaluate(
            vehicle=vehicle,
            regulations=filtered_regs,
            activity=activity,
            eval_time=eval_time,
            is_truck_route=is_truck_route,
        )

        decision = result.decision
        confidence = result.confidence_score
        explanation = result.explanation

        if has_conflict:
            decision = EvaluationDecision.CONDITIONAL
            confidence = min(confidence, 0.60)
            explanation = f"Conflicting regulations found. {explanation}"

        # 4. Find matched regulation record
        applicable_reg = None
        if result.applicable_regulation_id:
            applicable_reg = next(
                (r for r in regulations if r.id == result.applicable_regulation_id),
                None
            )

        all_warnings = warnings + result.warnings

        return RegulatoryEvaluationResponse(
            decision=decision,
            explanation=explanation,
            applicable_regulation=applicable_reg,
            source_reference=result.source_reference or adapter.jurisdiction_name,
            validity_period=eval_time.strftime("%A %Y-%m-%d %H:%M:%S"),
            confidence=confidence,
            relevant_restrictions=[r.classification.value for r in filtered_regs],
            nearest_alternatives=alternatives or [],
            warnings=all_warnings,
        )

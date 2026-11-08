"""New York City Regulatory Adapter.

Implements the official NYC Department of Transportation Traffic Rules:
- 34 RCNY § 4-08: Parking, Stopping, Standing
- 34 RCNY § 4-13: Truck Routing Rules
"""

from datetime import datetime, time
from typing import List, Optional

from app.domain.regulatory_engine.adapters.base import JurisdictionRuleAdapter
from app.domain.regulatory_engine.models import (
    EvaluationDecision,
    RegulationClassification,
    RegulationRecord,
    RequestedActivity,
    RuleEvaluationResult,
    VehicleProfile,
)


class NYCRuleAdapter(JurisdictionRuleAdapter):
    """Adapter enforcing NYC DOT Traffic Rules (34 RCNY § 4-08 and § 4-13)."""

    @property
    def jurisdiction_code(self) -> str:
        return "US-NYC"

    @property
    def jurisdiction_name(self) -> str:
        return "City of New York, Department of Transportation"

    def _is_rule_active_at_time(self, reg: RegulationRecord, eval_time: datetime) -> bool:
        """Determines if the regulation's temporal constraints apply at eval_time."""
        # 1. Effective date check
        if reg.effective_start and eval_time < reg.effective_start:
            return False
        if reg.effective_end and eval_time > reg.effective_end:
            return False

        # If no time rules, the restriction is active 24/7 (Anytime)
        if not reg.time_rules:
            return True

        current_day = eval_time.weekday()  # Monday is 0, Sunday is 6
        current_time = eval_time.time()

        for rule in reg.time_rules:
            # Check day of week
            if rule.days_of_week and current_day not in rule.days_of_week:
                continue

            # Check time of day window
            if rule.start_time and rule.end_time:
                if rule.is_overnight or rule.start_time > rule.end_time:
                    # Spans midnight: e.g. 20:00 to 06:00
                    if current_time >= rule.start_time or current_time <= rule.end_time:
                        return True
                else:
                    if rule.start_time <= current_time <= rule.end_time:
                        return True
            else:
                # All day on specified days
                return True

        return False

    def _is_truck(self, vehicle: VehicleProfile) -> bool:
        """Determines if a vehicle meets the NYC DOT legal definition of a truck:
        Two axles with six tires, or three or more axles (34 RCNY § 4-13(a)).
        """
        truck_types = {"BOX_TRUCK", "STRAIGHT_TRUCK", "HEAVY_DUTY_TRUCK", "SEMI_TRUCK"}
        if vehicle.vehicle_type in truck_types:
            return True
        if vehicle.axle_count and vehicle.axle_count >= 3:
            return True
        if vehicle.has_trailer:
            return True
        return False

    def evaluate(
        self,
        vehicle: VehicleProfile,
        regulations: List[RegulationRecord],
        activity: RequestedActivity,
        eval_time: datetime,
        is_truck_route: Optional[bool] = None,
    ) -> RuleEvaluationResult:
        """Evaluates vehicle activity according to 34 RCNY § 4-08 & § 4-13."""

        # -------------------------------------------------------------
        # 1. TRUCK ROUTE ENFORCEMENT (34 RCNY § 4-13)
        # -------------------------------------------------------------
        if activity == RequestedActivity.PASS_THROUGH and self._is_truck(vehicle):
            if is_truck_route is False:
                # Truck driving on a non-designated street
                return RuleEvaluationResult(
                    decision=EvaluationDecision.CONDITIONAL,
                    explanation=(
                        "Non-designated truck route. Under 34 RCNY § 4-13, trucks must travel "
                        "on designated truck routes and may only deviate via the closest "
                        "intersection to reach their delivery destination."
                    ),
                    conditions=[
                        "Vehicle must be travelling via the most direct street to an immediate local delivery/pickup",
                        "Truck must return to the designated truck route network at the nearest intersection"
                    ],
                    warnings=["Parkways are strictly prohibited to all commercial vehicles and trucks."],
                    source_reference="34 RCNY § 4-13 (NYC Truck Routing Network)",
                    confidence_score=0.95,
                )

        # -------------------------------------------------------------
        # 2. PHYSICAL CLEARANCE & WEIGHT RESTRICTIONS
        # -------------------------------------------------------------
        for reg in regulations:
            if not self._is_rule_active_at_time(reg, eval_time):
                continue

            # Height restriction (Low bridge / tunnel)
            if reg.classification == RegulationClassification.HEIGHT_RESTRICTION:
                if reg.max_height_m is not None:
                    if vehicle.height_m is None:
                        return RuleEvaluationResult(
                            decision=EvaluationDecision.UNKNOWN,
                            explanation=(
                                f"Low clearance ahead ({reg.max_height_m:.2f} m / "
                                f"{reg.max_height_m * 3.28084:.1f} ft). Vehicle height is not configured."
                            ),
                            applicable_regulation_id=reg.id,
                            warnings=["Verify physical bridge clearance before proceeding!"],
                            source_reference="NYC DOT Bridge Clearances",
                            confidence_score=0.90,
                        )
                    if vehicle.height_m >= reg.max_height_m:
                        return RuleEvaluationResult(
                            decision=EvaluationDecision.PROHIBITED,
                            explanation=(
                                f"LOW CLEARANCE VIOLATION: Bridge/structure clearance is {reg.max_height_m:.2f} m "
                                f"({reg.max_height_m * 3.28084:.1f} ft). Vehicle height is {vehicle.height_m:.2f} m "
                                f"({vehicle.height_m * 3.28084:.1f} ft)."
                            ),
                            applicable_regulation_id=reg.id,
                            applicable_regulation_type=reg.classification.value,
                            source_reference="NYC DOT Bridge Clearances (34 RCNY § 4-08)",
                            confidence_score=1.0,
                        )

            # Weight restriction
            if reg.classification == RegulationClassification.WEIGHT_RESTRICTION:
                if reg.max_weight_kg is not None:
                    weight_to_test = vehicle.operating_weight_kg or vehicle.gvwr_kg
                    if weight_to_test is None:
                        return RuleEvaluationResult(
                            decision=EvaluationDecision.UNKNOWN,
                            explanation=(
                                f"Weight-posted roadway/bridge ({reg.max_weight_kg:.0f} kg). "
                                "Vehicle weight is not configured."
                            ),
                            applicable_regulation_id=reg.id,
                            warnings=["Verify posted load rating before proceeding."],
                            source_reference="NYSDOT Posted Bridges",
                            confidence_score=0.90,
                        )
                    if weight_to_test > reg.max_weight_kg:
                        return RuleEvaluationResult(
                            decision=EvaluationDecision.PROHIBITED,
                            explanation=(
                                f"OVERWEIGHT VIOLATION: Structure limit is {reg.max_weight_kg:.0f} kg "
                                f"({reg.max_weight_kg * 2.20462:.0f} lbs). Vehicle weight is "
                                f"{weight_to_test:.0f} kg ({weight_to_test * 2.20462:.0f} lbs)."
                            ),
                            applicable_regulation_id=reg.id,
                            applicable_regulation_type=reg.classification.value,
                            source_reference="NYSDOT Load Posted Bridges",
                            confidence_score=1.0,
                        )

            # Temporary road closure
            if reg.classification == RegulationClassification.TEMPORARY_RESTRICTION:
                if activity in (RequestedActivity.PASS_THROUGH, RequestedActivity.STOP, RequestedActivity.PARK):
                    return RuleEvaluationResult(
                        decision=EvaluationDecision.PROHIBITED,
                        explanation=f"Temporary road closure in effect: {reg.sign_text or 'Construction/Emergency closure'}",
                        applicable_regulation_id=reg.id,
                        applicable_regulation_type=reg.classification.value,
                        source_reference="NYC DOT Construction Street Closures",
                        confidence_score=0.95,
                    )

        # If user just requested PASS_THROUGH and no clearance/closures were violated
        if activity == RequestedActivity.PASS_THROUGH:
            return RuleEvaluationResult(
                decision=EvaluationDecision.ALLOWED,
                explanation="Roadway segment is clear and legally compliant for pass-through travel.",
                confidence_score=1.0,
            )

        # -------------------------------------------------------------
        # 3. CURB REGULATIONS (34 RCNY § 4-08)
        # -------------------------------------------------------------
        # Find active parking/standing/loading regulations
        active_regs = [r for r in regulations if self._is_rule_active_at_time(r, eval_time)]

        if not active_regs:
            # If regulations list was provided but none are currently active (e.g. alternate side cleaning finished)
            if regulations:
                return RuleEvaluationResult(
                    decision=EvaluationDecision.ALLOWED,
                    explanation="No active parking or standing restrictions at this location for the specified date and time.",
                    confidence_score=0.95,
                    source_reference="NYC DOT SIMS",
                )
            # No data at all for this curb
            return RuleEvaluationResult(
                decision=EvaluationDecision.UNKNOWN,
                explanation="No verified municipal regulation data available for this curb segment.",
                warnings=["Always verify physical street signage before parking or leaving vehicle unattended."],
                confidence_score=0.0,
            )

        # Regulations hierarchy in NYC DOT:
        # NO_STOPPING > NO_STANDING > NO_PARKING > COMMERCIAL_LOADING / METERED
        for reg in active_regs:
            # A. NO STOPPING (34 RCNY § 4-08(c)(1))
            if reg.classification == RegulationClassification.NO_STOPPING:
                return RuleEvaluationResult(
                    decision=EvaluationDecision.PROHIBITED,
                    explanation=(
                        f"NO STOPPING ZONE: Under 34 RCNY § 4-08(c)(1), no vehicle may stop, stand, "
                        f"or park here at this time. Sign: '{reg.sign_text or 'NO STOPPING'}'."
                    ),
                    applicable_regulation_id=reg.id,
                    applicable_regulation_type=reg.classification.value,
                    source_reference="34 RCNY § 4-08(c)(1)",
                    confidence_score=reg.confidence_score,
                )

            # B. NO STANDING (34 RCNY § 4-08(c)(2))
            if reg.classification == RegulationClassification.NO_STANDING:
                if activity in (RequestedActivity.LOAD, RequestedActivity.UNLOAD, RequestedActivity.PARK):
                    return RuleEvaluationResult(
                        decision=EvaluationDecision.PROHIBITED,
                        explanation=(
                            f"NO STANDING ZONE: Under 34 RCNY § 4-08(c)(2), loading/unloading of merchandise "
                            f"and parking are strictly prohibited. Sign: '{reg.sign_text or 'NO STANDING'}'."
                        ),
                        applicable_regulation_id=reg.id,
                        applicable_regulation_type=reg.classification.value,
                        source_reference="34 RCNY § 4-08(c)(2)",
                        confidence_score=reg.confidence_score,
                    )
                elif activity == RequestedActivity.STOP:
                    return RuleEvaluationResult(
                        decision=EvaluationDecision.CONDITIONAL,
                        explanation=(
                            "NO STANDING ZONE: Temporary stop permitted solely for expediting "
                            "passenger pickup or dropoff. Driver must remain in vehicle."
                        ),
                        applicable_regulation_id=reg.id,
                        conditions=["Expeditious passenger pickup/dropoff only", "No merchandise transfer permitted"],
                        source_reference="34 RCNY § 4-08(c)(2)",
                        confidence_score=reg.confidence_score,
                    )

            # C. NO PARKING (34 RCNY § 4-08(c)(3))
            if reg.classification == RegulationClassification.NO_PARKING:
                if activity == RequestedActivity.PARK:
                    return RuleEvaluationResult(
                        decision=EvaluationDecision.PROHIBITED,
                        explanation=(
                            f"NO PARKING ZONE: Under 34 RCNY § 4-08(c)(3), parking unattended is prohibited. "
                            f"Sign: '{reg.sign_text or 'NO PARKING'}'."
                        ),
                        applicable_regulation_id=reg.id,
                        applicable_regulation_type=reg.classification.value,
                        source_reference="34 RCNY § 4-08(c)(3)",
                        confidence_score=reg.confidence_score,
                    )
                elif activity in (RequestedActivity.LOAD, RequestedActivity.UNLOAD, RequestedActivity.STOP):
                    return RuleEvaluationResult(
                        decision=EvaluationDecision.ALLOWED,
                        explanation=(
                            "Under 34 RCNY § 4-08(c)(3), commercial vehicles may temporarily stop and actively "
                            "load or unload merchandise or freight in No Parking zones."
                        ),
                        applicable_regulation_id=reg.id,
                        conditions=[
                            "Vehicle must be actively and expeditiously engaged in loading or unloading",
                            "Driver must be present with vehicle or engaged in immediate receipt/delivery"
                        ],
                        max_permitted_duration_minutes=30,
                        source_reference="34 RCNY § 4-08(c)(3)",
                        confidence_score=reg.confidence_score,
                    )

            # D. TRUCK LOADING ONLY / COMMERCIAL LOADING (34 RCNY § 4-08(k))
            if reg.classification in (
                RegulationClassification.TRUCK_LOADING_ONLY,
                RegulationClassification.COMMERCIAL_LOADING,
                RegulationClassification.LOADING_ONLY,
            ):
                if not vehicle.is_commercial and not self._is_truck(vehicle):
                    return RuleEvaluationResult(
                        decision=EvaluationDecision.PROHIBITED,
                        explanation=(
                            "COMMERCIAL LOADING ONLY: Under 34 RCNY § 4-08(k), non-commercial vehicles "
                            "may not stand or park in dedicated truck loading zones."
                        ),
                        applicable_regulation_id=reg.id,
                        source_reference="34 RCNY § 4-08(k)",
                        confidence_score=reg.confidence_score,
                    )

                if activity in (RequestedActivity.LOAD, RequestedActivity.UNLOAD, RequestedActivity.STOP):
                    max_duration = 180  # Default 3 hours in NYC Midtown
                    if reg.time_rules and reg.time_rules[0].max_duration_minutes:
                        max_duration = reg.time_rules[0].max_duration_minutes

                    return RuleEvaluationResult(
                        decision=EvaluationDecision.ALLOWED,
                        explanation=(
                            f"Permitted commercial loading zone. Commercial vehicle may load/unload for up to "
                            f"{max_duration} minutes."
                        ),
                        applicable_regulation_id=reg.id,
                        max_permitted_duration_minutes=max_duration,
                        conditions=[
                            "Vehicle must display commercial license plates",
                            "Active loading/unloading required; vehicle cannot be stored"
                        ],
                        source_reference="34 RCNY § 4-08(k)",
                        confidence_score=reg.confidence_score,
                    )
                elif activity == RequestedActivity.PARK:
                    return RuleEvaluationResult(
                        decision=EvaluationDecision.PROHIBITED,
                        explanation=(
                            "Parking without active commercial loading or beyond allowable dwell time "
                            "is prohibited in loading zones."
                        ),
                        applicable_regulation_id=reg.id,
                        source_reference="34 RCNY § 4-08(k)",
                        confidence_score=reg.confidence_score,
                    )

            # E. METERED COMMERCIAL PARKING (34 RCNY § 4-08(h))
            if reg.classification == RegulationClassification.METERED_PARKING:
                max_duration = 180
                if reg.time_rules and reg.time_rules[0].max_duration_minutes:
                    max_duration = reg.time_rules[0].max_duration_minutes

                return RuleEvaluationResult(
                    decision=EvaluationDecision.CONDITIONAL,
                    explanation=(
                        f"Metered parking zone. Payment required at ParkNYC meter or mobile app. "
                        f"Maximum stay: {max_duration} minutes."
                    ),
                    applicable_regulation_id=reg.id,
                    max_permitted_duration_minutes=max_duration,
                    conditions=["Pay required meter rate", f"Observe maximum {max_duration} min stay limit"],
                    source_reference="34 RCNY § 4-08(h)",
                    confidence_score=reg.confidence_score,
                )

        return RuleEvaluationResult(
            decision=EvaluationDecision.ALLOWED,
            explanation="Activity is permitted under current posted municipal regulations.",
            confidence_score=0.9,
        )

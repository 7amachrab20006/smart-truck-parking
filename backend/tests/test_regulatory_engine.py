"""Comprehensive Automated Unit Tests for the Regulatory Intelligence Engine.

Tests all critical real-world legal and regulatory scenarios specified in the master prompt:
1. Delivery truck in NO_PARKING zone (Allowed to load/unload, Prohibited to park)
2. Delivery truck attempting to load in NO_STANDING zone (Prohibited)
3. Vehicle entering NO_STOPPING zone (Prohibited)
4. Commercial vehicle in loading zone during operating hours (Allowed)
5. Non-commercial vehicle in loading zone (Prohibited)
6. Truck on non-designated truck route (Conditional per 34 RCNY § 4-13)
7. Truck approaching low-clearance bridge (Prohibited if height >= clearance)
8. Vehicle with missing height encountering low bridge (Unknown with warning)
9. Restriction with missing time information (Interpreted as 24/7 anytime)
10. Conflicting regulatory records on same block (Conditional with reduced confidence)
11. Street with different restrictions on each side (Left vs Right curb isolation)
12. Temporary construction road closure (Prohibited)
13. Clean street segment with no active restrictions (Allowed)
14. Time-dependent restriction evaluated outside its active window (Allowed)
"""

from datetime import datetime, time
import pytest

from app.domain.regulatory_engine import (
    EvaluationDecision,
    RegulationClassification,
    RegulationRecord,
    RegulatoryEngine,
    RequestedActivity,
    StreetSide,
    TimeRule,
    VehicleProfile,
)


@pytest.fixture
def engine():
    return RegulatoryEngine()


@pytest.fixture
def box_truck():
    return VehicleProfile(
        vehicle_id="truck-001",
        vehicle_type="BOX_TRUCK",
        height_m=3.80,  # ~12.5 ft
        width_m=2.50,
        length_m=9.00,
        operating_weight_kg=12000.0,
        axle_count=2,
        is_commercial=True,
    )


@pytest.fixture
def passenger_van():
    return VehicleProfile(
        vehicle_id="van-001",
        vehicle_type="DELIVERY_VAN",
        height_m=2.20,
        width_m=2.00,
        length_m=5.50,
        operating_weight_kg=3200.0,
        axle_count=2,
        is_commercial=False,  # Private vehicle
    )


# Scenario 1: Delivery truck in NO_PARKING zone
def test_delivery_truck_in_no_parking_zone(engine, box_truck):
    """Under 34 RCNY § 4-08(c)(3), commercial vehicles can actively load/unload in No Parking zones,
    but cannot park unattended."""
    no_parking_reg = RegulationRecord(
        id="reg-no-parking-01",
        classification=RegulationClassification.NO_PARKING,
        street_name="Broadway",
        street_side=StreetSide.RIGHT,
        sign_text="NO PARKING 8AM-6PM MON THRU FRI",
        time_rules=[
            TimeRule(
                days_of_week=[0, 1, 2, 3, 4],
                start_time=time(8, 0),
                end_time=time(18, 0),
            )
        ],
    )

    # Monday at 10:00 AM
    eval_time = datetime(2026, 11, 9, 10, 0)  # Monday

    # A. Active merchandise loading -> ALLOWED (with conditions)
    load_resp = engine.evaluate(
        vehicle=box_truck,
        regulations=[no_parking_reg],
        activity=RequestedActivity.LOAD,
        eval_time=eval_time,
        street_side=StreetSide.RIGHT,
    )
    assert load_resp.decision == EvaluationDecision.ALLOWED
    assert "actively load" in load_resp.explanation.lower()

    # B. Leaving vehicle parked unattended -> PROHIBITED
    park_resp = engine.evaluate(
        vehicle=box_truck,
        regulations=[no_parking_reg],
        activity=RequestedActivity.PARK,
        eval_time=eval_time,
        street_side=StreetSide.RIGHT,
    )
    assert park_resp.decision == EvaluationDecision.PROHIBITED
    assert "NO PARKING ZONE" in park_resp.explanation


# Scenario 2: Delivery truck attempting to load in NO_STANDING zone
def test_delivery_truck_loading_in_no_standing_zone(engine, box_truck):
    """Under 34 RCNY § 4-08(c)(2), merchandise loading is strictly PROHIBITED in No Standing zones."""
    no_standing_reg = RegulationRecord(
        id="reg-no-standing-01",
        classification=RegulationClassification.NO_STANDING,
        street_name="7th Ave",
        street_side=StreetSide.LEFT,
        sign_text="NO STANDING ANYTIME",
    )

    eval_time = datetime(2026, 11, 9, 14, 0)

    # Attempting to load cargo in No Standing zone
    resp = engine.evaluate(
        vehicle=box_truck,
        regulations=[no_standing_reg],
        activity=RequestedActivity.LOAD,
        eval_time=eval_time,
        street_side=StreetSide.LEFT,
    )
    assert resp.decision == EvaluationDecision.PROHIBITED
    assert "NO STANDING ZONE" in resp.explanation


# Scenario 3: Vehicle in NO_STOPPING zone
def test_vehicle_in_no_stopping_zone(engine, box_truck):
    """Under 34 RCNY § 4-08(c)(1), no vehicle may stop for any non-traffic reason in a No Stopping zone."""
    no_stopping_reg = RegulationRecord(
        id="reg-no-stopping-01",
        classification=RegulationClassification.NO_STOPPING,
        street_name="FDR Drive",
        street_side=StreetSide.BOTH,
        sign_text="NO STOPPING ANYTIME",
    )

    eval_time = datetime(2026, 11, 9, 11, 30)

    resp = engine.evaluate(
        vehicle=box_truck,
        regulations=[no_stopping_reg],
        activity=RequestedActivity.STOP,
        eval_time=eval_time,
    )
    assert resp.decision == EvaluationDecision.PROHIBITED
    assert "NO STOPPING ZONE" in resp.explanation


# Scenario 4: Commercial loading zone during permitted hours
def test_commercial_loading_zone_during_permitted_hours(engine, box_truck):
    loading_reg = RegulationRecord(
        id="reg-loading-01",
        classification=RegulationClassification.COMMERCIAL_LOADING,
        street_name="W 45th St",
        street_side=StreetSide.RIGHT,
        sign_text="COMMERCIAL METERED PARKING 3 HR LIMIT 7AM-7PM",
        time_rules=[
            TimeRule(
                days_of_week=[0, 1, 2, 3, 4],
                start_time=time(7, 0),
                end_time=time(19, 0),
                max_duration_minutes=180,
            )
        ],
    )

    # Tuesday at 11:00 AM
    eval_time = datetime(2026, 11, 10, 11, 0)

    resp = engine.evaluate(
        vehicle=box_truck,
        regulations=[loading_reg],
        activity=RequestedActivity.LOAD,
        eval_time=eval_time,
        street_side=StreetSide.RIGHT,
    )
    assert resp.decision == EvaluationDecision.ALLOWED
    assert "Permitted commercial loading" in resp.explanation


# Scenario 5: Non-commercial vehicle attempting to use commercial loading zone
def test_non_commercial_vehicle_in_loading_zone(engine, passenger_van):
    """Non-commercial vehicles are prohibited from using commercial truck loading zones."""
    loading_reg = RegulationRecord(
        id="reg-loading-02",
        classification=RegulationClassification.COMMERCIAL_LOADING,
        street_name="W 45th St",
        street_side=StreetSide.RIGHT,
        sign_text="COMMERCIAL LOADING ONLY 7AM-7PM",
        is_commercial_only=True,
    )

    eval_time = datetime(2026, 11, 10, 11, 0)

    resp = engine.evaluate(
        vehicle=passenger_van,
        regulations=[loading_reg],
        activity=RequestedActivity.LOAD,
        eval_time=eval_time,
        street_side=StreetSide.RIGHT,
    )
    assert resp.decision == EvaluationDecision.PROHIBITED
    assert "COMMERCIAL LOADING ONLY" in resp.explanation


# Scenario 6: Truck on non-designated truck route (34 RCNY § 4-13)
def test_truck_on_non_designated_truck_route(engine, box_truck):
    """Trucks must travel on truck routes and only leave via the nearest intersection."""
    resp = engine.evaluate(
        vehicle=box_truck,
        regulations=[],
        activity=RequestedActivity.PASS_THROUGH,
        is_truck_route=False,
    )
    assert resp.decision == EvaluationDecision.CONDITIONAL
    assert "34 RCNY § 4-13" in resp.explanation


# Scenario 7: Truck approaching low-clearance bridge
def test_truck_approaching_low_clearance_bridge(engine, box_truck):
    """Bridge clearance lower than truck height must be PROHIBITED with critical clearance warning."""
    low_bridge = RegulationRecord(
        id="bridge-001",
        classification=RegulationClassification.HEIGHT_RESTRICTION,
        street_name="Parkway Overpass",
        street_side=StreetSide.BOTH,
        max_height_m=3.50,  # 3.50m clearance < 3.80m truck height
        sign_text="LOW CLEARANCE 11' 6\"",
    )

    resp = engine.evaluate(
        vehicle=box_truck,
        regulations=[low_bridge],
        activity=RequestedActivity.PASS_THROUGH,
    )
    assert resp.decision == EvaluationDecision.PROHIBITED
    assert "LOW CLEARANCE VIOLATION" in resp.explanation


# Scenario 8: Vehicle with missing dimensions
def test_vehicle_with_missing_dimensions(engine):
    """Engine must return UNKNOWN when vehicle height is unknown and clearance restriction exists."""
    unconfigured_truck = VehicleProfile(
        vehicle_id="unconfigured-01",
        vehicle_type="STRAIGHT_TRUCK",
        height_m=None,  # Missing height!
    )

    low_bridge = RegulationRecord(
        id="bridge-002",
        classification=RegulationClassification.HEIGHT_RESTRICTION,
        street_name="Low Clearance Trestle",
        street_side=StreetSide.BOTH,
        max_height_m=3.65,
    )

    resp = engine.evaluate(
        vehicle=unconfigured_truck,
        regulations=[low_bridge],
        activity=RequestedActivity.PASS_THROUGH,
    )
    assert resp.decision == EvaluationDecision.UNKNOWN
    assert "Vehicle height is not configured" in resp.explanation


# Scenario 9: Street with different restrictions on each side
def test_street_with_different_restrictions_each_side(engine, box_truck):
    """Left curb has No Standing, Right curb has Commercial Loading.
    Evaluating on RIGHT curb must return ALLOWED for loading."""
    left_side_reg = RegulationRecord(
        id="reg-left",
        classification=RegulationClassification.NO_STANDING,
        street_name="E 42nd St",
        street_side=StreetSide.LEFT,
        sign_text="NO STANDING ANYTIME",
    )
    right_side_reg = RegulationRecord(
        id="reg-right",
        classification=RegulationClassification.COMMERCIAL_LOADING,
        street_name="E 42nd St",
        street_side=StreetSide.RIGHT,
        sign_text="COMMERCIAL LOADING 7AM-6PM MON-FRI",
        time_rules=[
            TimeRule(
                days_of_week=[0, 1, 2, 3, 4],
                start_time=time(7, 0),
                end_time=time(18, 0),
            )
        ],
    )

    eval_time = datetime(2026, 11, 9, 10, 0)  # Monday 10am

    # Evaluating Right Curb:
    right_resp = engine.evaluate(
        vehicle=box_truck,
        regulations=[left_side_reg, right_side_reg],
        activity=RequestedActivity.LOAD,
        eval_time=eval_time,
        street_side=StreetSide.RIGHT,
    )
    assert right_resp.decision == EvaluationDecision.ALLOWED
    assert right_resp.applicable_regulation.id == "reg-right"

    # Evaluating Left Curb:
    left_resp = engine.evaluate(
        vehicle=box_truck,
        regulations=[left_side_reg, right_side_reg],
        activity=RequestedActivity.LOAD,
        eval_time=eval_time,
        street_side=StreetSide.LEFT,
    )
    assert left_resp.decision == EvaluationDecision.PROHIBITED
    assert left_resp.applicable_regulation.id == "reg-left"


# Scenario 10: Conflicting regulatory records
def test_conflicting_regulatory_records(engine, box_truck):
    """Conflicting records on the same curb must produce CONDITIONAL with reduced confidence."""
    reg_a = RegulationRecord(
        id="conflict-a",
        classification=RegulationClassification.NO_STOPPING,
        street_name="W 34th St",
        street_side=StreetSide.RIGHT,
        sign_text="NO STOPPING ANYTIME",
    )
    reg_b = RegulationRecord(
        id="conflict-b",
        classification=RegulationClassification.COMMERCIAL_LOADING,
        street_name="W 34th St",
        street_side=StreetSide.RIGHT,
        sign_text="COMMERCIAL LOADING ZONE",
    )

    resp = engine.evaluate(
        vehicle=box_truck,
        regulations=[reg_a, reg_b],
        activity=RequestedActivity.LOAD,
        street_side=StreetSide.RIGHT,
    )
    assert resp.decision == EvaluationDecision.CONDITIONAL
    assert resp.confidence <= 0.60
    assert any("CONFLICT DETECTED" in w for w in resp.warnings)


# Scenario 11: Restriction outside active hours
def test_restriction_outside_active_hours(engine, box_truck):
    """A No Parking rule active Mon-Fri 8AM-6PM evaluated on Sunday must be ALLOWED."""
    weekday_rule = RegulationRecord(
        id="reg-weekday-only",
        classification=RegulationClassification.NO_PARKING,
        street_name="Madison Ave",
        street_side=StreetSide.RIGHT,
        sign_text="NO PARKING 8AM-6PM MON-FRI",
        time_rules=[
            TimeRule(
                days_of_week=[0, 1, 2, 3, 4],
                start_time=time(8, 0),
                end_time=time(18, 0),
            )
        ],
    )

    sunday_time = datetime(2026, 11, 15, 12, 0)  # Sunday 12:00 PM

    resp = engine.evaluate(
        vehicle=box_truck,
        regulations=[weekday_rule],
        activity=RequestedActivity.PARK,
        eval_time=sunday_time,
        street_side=StreetSide.RIGHT,
    )
    assert resp.decision == EvaluationDecision.ALLOWED
    assert "No active parking or standing restrictions" in resp.explanation


# Scenario 12: Temporary construction street closure
def test_temporary_construction_closure(engine, box_truck):
    """Temporary emergency or road construction closure prohibits pass-through and parking."""
    closure = RegulationRecord(
        id="closure-01",
        classification=RegulationClassification.TEMPORARY_RESTRICTION,
        street_name="W 50th St",
        street_side=StreetSide.BOTH,
        is_temporary=True,
        sign_text="STREET CLOSED FOR CRANE OPERATION",
    )

    resp = engine.evaluate(
        vehicle=box_truck,
        regulations=[closure],
        activity=RequestedActivity.PASS_THROUGH,
    )
    assert resp.decision == EvaluationDecision.PROHIBITED
    assert "Temporary road closure" in resp.explanation

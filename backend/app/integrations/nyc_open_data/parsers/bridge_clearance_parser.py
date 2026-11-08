"""Parser for NYC Citywide Low Bridges (Dataset rn6h-i66u)."""

from typing import Any, Dict, Optional

from app.domain.regulatory_engine.models import (
    RegulationClassification,
    RegulationRecord,
    StreetSide,
)


class NYCLowBridgeParser:
    """Parses NYC Low Bridge records into vertical clearance restrictions."""

    @classmethod
    def parse_clearance_meters(cls, feet_val: Any, inches_val: Any) -> Optional[float]:
        """Converts feet and inches into meters."""
        try:
            feet = float(feet_val) if feet_val else 0.0
            inches = float(inches_val) if inches_val else 0.0
            total_inches = (feet * 12.0) + inches
            return total_inches * 0.0254  # 1 inch = 0.0254 meters
        except (ValueError, TypeError):
            return None

    @classmethod
    def parse_record(cls, raw: Dict[str, Any]) -> RegulationRecord:
        """Parses a raw low bridge JSON object into a RegulationRecord."""
        feet = raw.get("clearance_feet", raw.get("min_feet", 0))
        inches = raw.get("clearance_inches", raw.get("min_inches", 0))
        clearance_m = cls.parse_clearance_meters(feet, inches)

        structure = raw.get("cross_street", raw.get("structure_name", "Low Bridge Overpass"))
        highway = raw.get("highway", raw.get("feature_crossed", "Roadway"))

        return RegulationRecord(
            id=str(raw.get("bin", raw.get("id", "nyc-bridge"))),
            jurisdiction_code="US-NYC",
            classification=RegulationClassification.HEIGHT_RESTRICTION,
            street_name=highway,
            street_side=StreetSide.BOTH,
            sign_text=f"LOW CLEARANCE {feet}' {inches}\" AT {structure}",
            max_height_m=clearance_m,
            data_source="NYC Open Data (rn6h-i66u)",
            confidence_score=1.0,
            verification_status="VERIFIED",
        )

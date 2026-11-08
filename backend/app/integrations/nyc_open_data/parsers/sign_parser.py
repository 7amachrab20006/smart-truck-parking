"""Parser for NYC DOT SIMS Parking Signs (Dataset xswq-wnv9).

Normalizes raw sign text like:
- "NO PARKING 8AM-6PM MON THRU FRI"
- "NO STANDING EXCEPT TRUCKS LOADING & UNLOADING 7AM-7PM EXCEPT SUNDAY"
- "COMMERCIAL METERED PARKING 3 HR LIMIT 7AM-6PM"
into structured RegulationRecord and TimeRule domain objects.
"""

import re
from datetime import time
from typing import Any, Dict, List, Optional, Tuple

from app.domain.regulatory_engine.models import (
    RegulationClassification,
    RegulationRecord,
    StreetSide,
    TimeRule,
)


class NYCSignParser:
    """Parser transforming raw NYC SIMS sign records into verified RegulationRecords."""

    DAY_MAP = {
        "MON": 0, "MONDAY": 0,
        "TUE": 1, "TUES": 1, "TUESDAY": 1,
        "WED": 2, "WEDNESDAY": 2,
        "THU": 3, "THUR": 3, "THURS": 3, "THURSDAY": 3,
        "FRI": 4, "FRIDAY": 4,
        "SAT": 5, "SATURDAY": 5,
        "SUN": 6, "SUNDAY": 6,
    }

    SIDE_MAP = {
        "N": StreetSide.RIGHT,  # Mapped according to street azimuth or standardized side
        "S": StreetSide.LEFT,
        "E": StreetSide.RIGHT,
        "W": StreetSide.LEFT,
        "B": StreetSide.BOTH,
    }

    @classmethod
    def parse_classification(cls, text: str) -> RegulationClassification:
        """Determines legal regulation classification from sign description text."""
        upper = text.upper()

        if "NO STOPPING" in upper:
            return RegulationClassification.NO_STOPPING

        if "NO STANDING EXCEPT TRUCKS" in upper or "TRUCK LOADING" in upper:
            return RegulationClassification.TRUCK_LOADING_ONLY

        if "COMMERCIAL LOADING" in upper or "COMMERCIAL VEHICLES ONLY" in upper or "NLZ LOADING" in upper:
            return RegulationClassification.COMMERCIAL_LOADING

        if "NO STANDING" in upper:
            return RegulationClassification.NO_STANDING

        if "COMMERCIAL METERED" in upper or "COMMERCIAL METER" in upper:
            return RegulationClassification.COMMERCIAL_LOADING

        if "METER" in upper or "PARKNYC" in upper:
            return RegulationClassification.METERED_PARKING

        if "NO PARKING" in upper:
            return RegulationClassification.NO_PARKING

        if "LOADING ONLY" in upper:
            return RegulationClassification.LOADING_ONLY

        return RegulationClassification.NO_PARKING

    @classmethod
    def parse_time_window(cls, text: str) -> Tuple[Optional[time], Optional[time], bool]:
        """Extracts start and end times from strings like '8AM-6PM', '7:30AM-8:30AM', 'MIDNIGHT-6AM'."""
        pattern = r"(\d{1,2}(?::\d{2})?\s*(?:AM|PM)|NOON|MIDNIGHT)\s*(?:-|TO|THRU)\s*(\d{1,2}(?::\d{2})?\s*(?:AM|PM)|NOON|MIDNIGHT)"
        match = re.search(pattern, text, re.IGNORECASE)

        if not match:
            return None, None, False

        def _to_time(val: str) -> time:
            v = val.upper().strip()
            if v == "NOON":
                return time(12, 0)
            if v == "MIDNIGHT":
                return time(0, 0)

            is_pm = "PM" in v
            v_clean = v.replace("AM", "").replace("PM", "").strip()
            if ":" in v_clean:
                h_str, m_str = v_clean.split(":")
                h, m = int(h_str), int(m_str)
            else:
                h, m = int(v_clean), 0

            if is_pm and h < 12:
                h += 12
            elif not is_pm and h == 12:
                h = 0
            return time(h, m)

        start = _to_time(match.group(1))
        end = _to_time(match.group(2))
        is_overnight = start > end
        return start, end, is_overnight

    @classmethod
    def parse_days_of_week(cls, text: str) -> List[int]:
        """Extracts active days from phrases like 'MON THRU FRI', 'EXCEPT SUNDAY', 'TUE & FRI'."""
        upper = text.upper()

        if "MON THRU FRI" in upper or "MON-FRI" in upper:
            return [0, 1, 2, 3, 4]
        if "MON THRU SAT" in upper or "MON-SAT" in upper:
            return [0, 1, 2, 3, 4, 5]
        if "EXCEPT SUNDAY" in upper or "EXC SUN" in upper:
            return [0, 1, 2, 3, 4, 5]
        if "EXCEPT SAT & SUN" in upper or "EXC SAT SUN" in upper:
            return [0, 1, 2, 3, 4]
        if "ALL DAYS" in upper or "ANYTIME" in upper or "DAILY" in upper:
            return [0, 1, 2, 3, 4, 5, 6]

        # Specific day lists (e.g. "TUE FRI", "MON WED FRI")
        found = []
        for word in re.findall(r"\b[A-Z]{3,}\b", upper):
            if word in cls.DAY_MAP and cls.DAY_MAP[word] not in found:
                found.append(cls.DAY_MAP[word])

        return found if found else [0, 1, 2, 3, 4, 5, 6]

    @classmethod
    def parse_record(cls, raw: Dict[str, Any]) -> RegulationRecord:
        """Parses a raw NYC Open Data SIMS sign JSON record into a normalized RegulationRecord."""
        desc = raw.get("sign_description", "").strip()
        classification = cls.parse_classification(desc)

        start_time, end_time, is_overnight = cls.parse_time_window(desc)
        days = cls.parse_days_of_week(desc)

        # Max duration parsing (e.g. "3 HR LIMIT")
        duration = None
        limit_match = re.search(r"(\d+)\s*(?:HR|HOUR)", desc, re.IGNORECASE)
        if limit_match:
            duration = int(limit_match.group(1)) * 60

        time_rule = TimeRule(
            days_of_week=days,
            start_time=start_time,
            end_time=end_time,
            max_duration_minutes=duration,
            is_overnight=is_overnight,
        )

        side_raw = raw.get("side_of_street", raw.get("sos", "B")).upper()
        street_side = cls.SIDE_MAP.get(side_raw, StreetSide.UNKNOWN)

        return RegulationRecord(
            id=str(raw.get("order_number", raw.get("sg_order_name", "nyc-sign"))),
            jurisdiction_code="US-NYC",
            classification=classification,
            street_name=raw.get("main_street", raw.get("main_st", "UNKNOWN STREET")),
            street_side=street_side,
            sign_text=desc,
            time_rules=[time_rule] if (start_time or days != [0, 1, 2, 3, 4, 5, 6]) else [],
            is_commercial_only="COMMERCIAL" in desc.upper() or "TRUCK" in desc.upper(),
            data_source="NYC Open Data (xswq-wnv9)",
            confidence_score=0.98 if raw.get("record_type") == "Current" else 0.85,
            verification_status="VERIFIED",
        )

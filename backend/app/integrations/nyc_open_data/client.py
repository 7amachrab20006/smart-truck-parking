"""NYC Open Data Socrata (SODA) API client.

Handles querying official municipal datasets:
- Parking signs: xswq-wnv9
- NYC Truck Routes: spax-mybh
- Neighborhood Loading Zones: 6pjf-tf5u
- Citywide Low Bridges: rn6h-i66u
- Block Closures: i6b5-j7bu
"""

import logging
from typing import Any, Dict, List, Optional
import httpx

from app.config import settings

logger = logging.getLogger(__name__)


class NYCOpenDataClient:
    """Async client for NYC Open Data SODA API."""

    def __init__(self, base_url: Optional[str] = None, app_token: Optional[str] = None):
        self.base_url = (base_url or settings.nyc_open_data_base_url).rstrip("/")
        self.app_token = app_token or settings.nyc_open_data_app_token
        self.headers = {"Accept": "application/json"}
        if self.app_token:
            self.headers["X-App-Token"] = self.app_token

    async def fetch_dataset(
        self,
        dataset_id: str,
        where_clause: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
        order: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Queries a SODA dataset endpoint by 4x4 identifier."""
        url = f"{self.base_url}/resource/{dataset_id}.json"
        params: Dict[str, Any] = {
            "$limit": limit,
            "$offset": offset,
        }
        if where_clause:
            params["$where"] = where_clause
        if order:
            params["$order"] = order

        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.get(url, params=params, headers=self.headers)
                response.raise_for_status()
                return response.json()
        except httpx.HTTPError as exc:
            logger.error(f"SODA API request failed for {dataset_id}: {exc}")
            raise RuntimeError(f"NYC Open Data API error: {exc}") from exc

    async def get_parking_signs(
        self,
        street_name: Optional[str] = None,
        borough: Optional[str] = None,
        limit: int = 50,
    ) -> List[Dict[str, Any]]:
        """Queries NYC Parking Regulation Locations & Signs (xswq-wnv9)."""
        clauses = ["record_type = 'Current'"]
        if street_name:
            clean_street = street_name.upper().replace("'", "''")
            clauses.append(f"main_street = '{clean_street}'")
        if borough:
            clauses.append(f"borough = '{borough.upper()}'")

        where = " AND ".join(clauses)
        return await self.fetch_dataset("xswq-wnv9", where_clause=where, limit=limit)

    async def get_truck_routes(self, borough: Optional[str] = None, limit: int = 50) -> List[Dict[str, Any]]:
        """Queries NYC Truck Routes (spax-mybh)."""
        where = f"borough = '{borough.upper()}'" if borough else None
        return await self.fetch_dataset("spax-mybh", where_clause=where, limit=limit)

    async def get_loading_zones(self, borough: Optional[str] = None, limit: int = 50) -> List[Dict[str, Any]]:
        """Queries Neighborhood Loading Zones (6pjf-tf5u)."""
        where = f"borough = '{borough.upper()}'" if borough else None
        return await self.fetch_dataset("6pjf-tf5u", where_clause=where, limit=limit)

    async def get_low_bridges(self, borough: Optional[str] = None, limit: int = 50) -> List[Dict[str, Any]]:
        """Queries Citywide Low Bridges (rn6h-i66u)."""
        where = f"borough = '{borough.upper()}'" if borough else None
        return await self.fetch_dataset("rn6h-i66u", where_clause=where, limit=limit)

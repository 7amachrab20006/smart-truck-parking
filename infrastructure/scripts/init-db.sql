-- Smart Truck & Parking Assistant — Database Initialization
-- This script runs automatically on first container creation.

-- Enable PostGIS extension
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS postgis_topology;
CREATE EXTENSION IF NOT EXISTS pg_trgm;  -- For fuzzy text search on street names
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";  -- For UUID generation

-- Verify PostGIS is working
SELECT PostGIS_Full_Version();

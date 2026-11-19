-- RetailPulse: Unity Catalog structure
-- Run in the Databricks SQL Editor (serverless warehouse).

CREATE CATALOG IF NOT EXISTS retailpulse
  COMMENT 'RetailPulse retail data lakehouse';

CREATE SCHEMA IF NOT EXISTS retailpulse.bronze
  COMMENT 'Raw data as received from sources, plus ingestion metadata';
CREATE SCHEMA IF NOT EXISTS retailpulse.silver
  COMMENT 'Cleaned, deduplicated, CDC-applied data';
CREATE SCHEMA IF NOT EXISTS retailpulse.gold
  COMMENT 'Business-ready star schema (dbt models)';
CREATE SCHEMA IF NOT EXISTS retailpulse.audit
  COMMENT 'Pipeline runs, file registry and data quality results';

CREATE VOLUME IF NOT EXISTS retailpulse.bronze.landing
  COMMENT 'Landing zone for files uploaded by the Python ingestion framework';

  
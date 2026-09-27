-- GA.LAW.HELP internal Georgia legal corpus
-- Stores source-grounded public legal material locally for retrieval by the app AI.

CREATE TABLE IF NOT EXISTS legal_sources (
  id BIGSERIAL PRIMARY KEY,
  source_type TEXT NOT NULL,
  issuing_body TEXT NOT NULL,
  title TEXT NOT NULL,
  canonical_url TEXT,
  retrieved_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  effective_date DATE,
  superseded_date DATE,
  version_label TEXT,
  sha256 TEXT,
  is_official BOOLEAN NOT NULL DEFAULT FALSE
);

CREATE TABLE IF NOT EXISTS statutes (
  id BIGSERIAL PRIMARY KEY,
  code TEXT NOT NULL DEFAULT 'O.C.G.A.',
  title_number TEXT NOT NULL,
  chapter_number TEXT,
  article_number TEXT,
  section_number TEXT NOT NULL,
  heading TEXT,
  text_body TEXT NOT NULL,
  effective_from DATE,
  effective_to DATE,
  source_id BIGINT REFERENCES legal_sources(id),
  UNIQUE(section_number, effective_from)
);
CREATE INDEX IF NOT EXISTS statutes_search_idx ON statutes USING GIN (to_tsvector('english', coalesce(heading,'') || ' ' || text_body));

CREATE TABLE IF NOT EXISTS opinions (
  id BIGSERIAL PRIMARY KEY,
  court TEXT NOT NULL,
  docket_number TEXT,
  citation TEXT,
  case_name TEXT NOT NULL,
  decision_date DATE,
  status TEXT NOT NULL DEFAULT 'published',
  full_text TEXT NOT NULL,
  holding TEXT,
  procedural_posture TEXT,
  disposition TEXT,
  source_id BIGINT REFERENCES legal_sources(id),
  UNIQUE(court, docket_number, decision_date)
);
CREATE INDEX IF NOT EXISTS opinions_search_idx ON opinions USING GIN (to_tsvector('english', case_name || ' ' || coalesce(citation,'') || ' ' || full_text));

CREATE TABLE IF NOT EXISTS opinion_statutes (
  opinion_id BIGINT NOT NULL REFERENCES opinions(id) ON DELETE CASCADE,
  statute_id BIGINT NOT NULL REFERENCES statutes(id) ON DELETE CASCADE,
  treatment TEXT,
  PRIMARY KEY(opinion_id, statute_id)
);

CREATE TABLE IF NOT EXISTS charges (
  id BIGSERIAL PRIMARY KEY,
  name TEXT NOT NULL,
  normalized_name TEXT NOT NULL,
  statute_section TEXT,
  description TEXT,
  elements_json JSONB,
  UNIQUE(normalized_name, statute_section)
);
CREATE INDEX IF NOT EXISTS charges_name_idx ON charges(normalized_name);

CREATE TABLE IF NOT EXISTS opinion_charges (
  opinion_id BIGINT NOT NULL REFERENCES opinions(id) ON DELETE CASCADE,
  charge_id BIGINT NOT NULL REFERENCES charges(id) ON DELETE CASCADE,
  relationship TEXT,
  PRIMARY KEY(opinion_id, charge_id)
);

CREATE TABLE IF NOT EXISTS motions (
  id BIGSERIAL PRIMARY KEY,
  name TEXT NOT NULL,
  category TEXT NOT NULL,
  description TEXT NOT NULL,
  legal_basis TEXT,
  prerequisites TEXT,
  timing_rules TEXT,
  requested_relief TEXT,
  opposing_arguments TEXT,
  evidence_needed TEXT,
  source_id BIGINT REFERENCES legal_sources(id)
);
CREATE INDEX IF NOT EXISTS motions_search_idx ON motions USING GIN (to_tsvector('english', name || ' ' || description || ' ' || coalesce(legal_basis,'')));

CREATE TABLE IF NOT EXISTS procedure_rules (
  id BIGSERIAL PRIMARY KEY,
  topic TEXT NOT NULL,
  encounter_type TEXT,
  rule_title TEXT NOT NULL,
  classification TEXT NOT NULL CHECK (classification IN ('generally_permitted','generally_prohibited','fact_dependent','unsettled','policy_specific')),
  rule_text TEXT NOT NULL,
  citizen_rights TEXT,
  officer_authority TEXT,
  limitations TEXT,
  safest_response TEXT,
  evidence_to_preserve TEXT,
  source_id BIGINT REFERENCES legal_sources(id),
  effective_from DATE,
  effective_to DATE
);
CREATE INDEX IF NOT EXISTS procedure_search_idx ON procedure_rules USING GIN (to_tsvector('english', topic || ' ' || rule_title || ' ' || rule_text));

CREATE TABLE IF NOT EXISTS court_rules (
  id BIGSERIAL PRIMARY KEY,
  court TEXT NOT NULL,
  rule_number TEXT,
  title TEXT,
  text_body TEXT NOT NULL,
  effective_from DATE,
  effective_to DATE,
  source_id BIGINT REFERENCES legal_sources(id)
);

CREATE TABLE IF NOT EXISTS corpus_updates (
  id BIGSERIAL PRIMARY KEY,
  source_name TEXT NOT NULL,
  started_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  completed_at TIMESTAMPTZ,
  records_added INTEGER NOT NULL DEFAULT 0,
  records_updated INTEGER NOT NULL DEFAULT 0,
  status TEXT NOT NULL DEFAULT 'running',
  error_text TEXT
);

-- AI retrieval must return source IDs and distinguish source text from generated explanation.
-- Never synthesize a nonexistent case, statute, motion, citation, or procedural rule.

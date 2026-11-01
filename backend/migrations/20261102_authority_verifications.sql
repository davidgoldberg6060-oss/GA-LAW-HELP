-- Official-source verification as a small side table (no rewrite of legal_authorities, so no
-- dead tuples / WAL from touching its large text and search_vector columns, and the
-- search_vector trigger never fires). Rows are inserted by .github/scripts/verify-authorities.sh
-- (db-maintenance action "verify-authorities"). Idempotent and additive.
CREATE TABLE IF NOT EXISTS verification_sources (
  id smallint PRIMARY KEY,
  source_key varchar(120) NOT NULL UNIQUE,
  source_name varchar(300) NOT NULL,
  source_url varchar(1000) NOT NULL,
  edition varchar(200),
  as_of_date date,
  as_of_label varchar(200),
  method varchar(80) NOT NULL DEFAULT 'official_source_provenance',
  created_at timestamp NOT NULL DEFAULT (now() AT TIME ZONE 'utc')
);

CREATE TABLE IF NOT EXISTS authority_verifications (
  authority_id integer PRIMARY KEY REFERENCES legal_authorities(id) ON DELETE CASCADE,
  source_id smallint NOT NULL REFERENCES verification_sources(id),
  verified_at timestamp NOT NULL DEFAULT (now() AT TIME ZONE 'utc')
);

INSERT INTO verification_sources (id, source_key, source_name, source_url, edition, as_of_date, as_of_label, method) VALUES
 (1, 'pro_ocga_release86.2022.11', 'Official Code of Georgia Annotated, State release published by Public.Resource.Org (Internet Archive item gov.ga.ocga.2018)',
     'https://archive.org/details/gov.ga.ocga.2018', 'release86.2022.11 (2022 edition)', DATE '2022-11-01', 'text as of 2022 edition', 'official_source_provenance'),
 (2, 'ga_sos_rules', 'Rules and Regulations of the State of Georgia, Georgia Secretary of State (rules.sos.ga.gov)',
     'https://rules.sos.ga.gov/', 'as retrieved', NULL, 'text as retrieved from rules.sos.ga.gov', 'official_source_provenance'),
 (3, 'courtlistener_opinions', 'Georgia appellate opinions, Free Law Project / CourtListener',
     'https://www.courtlistener.com/', 'opinion as published', NULL, 'opinion text as published', 'official_source_provenance'),
 (4, 'ga_court_rules', 'Georgia court rules from official court websites',
     'https://www.gasupreme.us/', 'as retrieved', NULL, 'rule text as retrieved', 'official_source_provenance')
ON CONFLICT (id) DO NOTHING;

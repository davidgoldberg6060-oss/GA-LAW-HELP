\pset footer off
SELECT version();
SELECT pg_size_pretty(pg_database_size(current_database())) AS database_size, pg_database_size(current_database()) AS database_bytes;
SELECT relname AS table, n_live_tup AS approx_rows, pg_size_pretty(pg_total_relation_size(relid)) AS total_size
  FROM pg_stat_user_tables ORDER BY pg_total_relation_size(relid) DESC LIMIT 25;
SELECT 'legal_sources' AS t, count(*) FROM legal_sources
UNION ALL SELECT 'legal_authorities', count(*) FROM legal_authorities
UNION ALL SELECT 'authority_versions', count(*) FROM authority_versions;
SELECT to_regclass('public.authority_annotations') IS NOT NULL AS has_authority_annotations;
DO $$ BEGIN IF to_regclass('public.authority_annotations') IS NOT NULL THEN
  RAISE NOTICE 'authority_annotations rows: %', (SELECT count(*) FROM authority_annotations); END IF; END $$;
SELECT authority_type, count(*) AS authorities,
       count(*) FILTER (WHERE text IS NOT NULL AND text <> '') AS with_text
  FROM legal_authorities GROUP BY authority_type ORDER BY 2 DESC;
SELECT split_part(split_part(coalesce(source_url, ''), '://', 2), '/', 1) AS source_host, count(*)
  FROM legal_authorities GROUP BY 1 ORDER BY 2 DESC LIMIT 20;
SELECT id, left(name, 70) AS name, source_type, official, enabled FROM legal_sources ORDER BY id;
SELECT
  EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='legal_authorities' AND column_name='currency_status') AS m_20260927_legal_status,
  EXISTS (SELECT 1 FROM pg_constraint WHERE conname='ck_legal_authorities_currency_status') AS m_20261004_status_vocabulary,
  to_regclass('public.authority_annotations') IS NOT NULL AS m_20261004_annotations,
  to_regclass('public.ix_legal_authorities_fulltext') IS NOT NULL AS m_20261004_fulltext;
-- Spot check: newest three authorities of each type (no full text).
SELECT authority_type, citation, left(title, 70) AS title, length(text) AS text_chars, status, retrieved_at::date
  FROM (SELECT *, row_number() OVER (PARTITION BY authority_type ORDER BY id DESC) AS rn FROM legal_authorities) x
  WHERE rn <= 3 ORDER BY authority_type, id DESC;

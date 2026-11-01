-- Run WITHOUT --single-transaction: batches commit individually; CONCURRENTLY needs autocommit.
\timing on
SET statement_timeout = 0;
SET client_min_messages = warning;  -- silence "word is too long to be indexed"
-- 1) Batched backfill (each batch commits; live reads/writes are never blocked for long).
DO $$
DECLARE lo bigint; hi bigint; maxid bigint; step int := 3000; n bigint;
BEGIN
  SELECT coalesce(min(id),0), coalesce(max(id),0) INTO lo, maxid FROM legal_authorities WHERE search_vector IS NULL;
  WHILE lo <= maxid LOOP
    hi := lo + step;
    UPDATE legal_authorities SET search_vector = legal_authority_search_vector(citation, title, text)
     WHERE id >= lo AND id < hi AND search_vector IS NULL;
    GET DIAGNOSTICS n = ROW_COUNT;
    COMMIT;
    lo := hi;
  END LOOP;
END $$;
SELECT count(*) FILTER (WHERE search_vector IS NULL) AS still_null, count(*) AS total FROM legal_authorities;
-- 2) Drop any invalid leftover from an interrupted concurrent build, then build concurrently.
DO $$ BEGIN
  IF EXISTS (SELECT 1 FROM pg_index WHERE indexrelid = to_regclass('public.ix_legal_authorities_search_vector') AND NOT indisvalid) THEN
    RAISE WARNING 'dropping invalid ix_legal_authorities_search_vector'; EXECUTE 'DROP INDEX ix_legal_authorities_search_vector';
  END IF;
  IF EXISTS (SELECT 1 FROM pg_index WHERE indexrelid = to_regclass('public.ix_legal_authorities_type_citation') AND NOT indisvalid) THEN
    EXECUTE 'DROP INDEX ix_legal_authorities_type_citation';
  END IF;
END $$;
-- The old expression index is superseded (the app no longer uses that expression). Drop it
-- first so its space is free for the new index build (the volume is small).
DROP INDEX CONCURRENTLY IF EXISTS ix_legal_authorities_fulltext;
-- Serial build, in memory: a parallel GIN build spills large temp files.
SET max_parallel_maintenance_workers = 0;
SET maintenance_work_mem = '512MB';
CREATE INDEX CONCURRENTLY IF NOT EXISTS ix_legal_authorities_search_vector ON legal_authorities USING GIN (search_vector);
CREATE INDEX CONCURRENTLY IF NOT EXISTS ix_legal_authorities_type_citation ON legal_authorities (lower(authority_type), citation);
ANALYZE legal_authorities;

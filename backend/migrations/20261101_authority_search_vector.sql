-- Fast weighted full-text search: stored legal_authorities.search_vector maintained by a trigger.
-- Weights: citation + title = A, opening of the text (headings / catchline) = B, body = C.
-- Only the first 8,000 characters of text are indexed: whole statutes, and the syllabus / opening
-- of long opinions (keeps the vector and GIN index small enough for the database volume).
-- MUST match app/authority_search_service.SEARCH_VECTOR_SQL. Idempotent and additive.
-- ADD COLUMN without a default is metadata-only (no table rewrite). Existing rows are
-- backfilled in batches and the GIN index is built CONCURRENTLY by
-- .github/scripts/search-index.sql (db-maintenance action "search-index"), outside this transaction.

ALTER TABLE legal_authorities ADD COLUMN IF NOT EXISTS search_vector tsvector;

CREATE OR REPLACE FUNCTION legal_authority_search_vector(p_citation text, p_title text, p_text text)
RETURNS tsvector LANGUAGE sql IMMUTABLE PARALLEL SAFE AS $$
  SELECT setweight(to_tsvector('english'::regconfig, coalesce(p_citation, '') || ' ' || coalesce(p_title, '')), 'A')
      || setweight(to_tsvector('english'::regconfig, left(coalesce(p_text, ''), 600)), 'B')
      || setweight(to_tsvector('english'::regconfig, substr(coalesce(p_text, ''), 601, 7400)), 'C')
$$;
-- Bump when the expression changes; search-index.sql rebuilds stored vectors when it differs.
COMMENT ON FUNCTION legal_authority_search_vector(text, text, text) IS 'v2-8000';

CREATE OR REPLACE FUNCTION legal_authorities_search_vector_trigger() RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
  NEW.search_vector := legal_authority_search_vector(NEW.citation, NEW.title, NEW.text);
  RETURN NEW;
END $$;

DROP TRIGGER IF EXISTS trg_legal_authorities_search_vector ON legal_authorities;
CREATE TRIGGER trg_legal_authorities_search_vector
  BEFORE INSERT OR UPDATE OF citation, title, text ON legal_authorities
  FOR EACH ROW EXECUTE FUNCTION legal_authorities_search_vector_trigger();

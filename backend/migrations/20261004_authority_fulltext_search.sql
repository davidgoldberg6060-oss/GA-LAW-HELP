-- Issue #88 item 4: word-based full-text search over persisted Georgia authorities.
-- The expression MUST match app/authority_search_service.authority_document_expression()
-- so the planner can use this index. Idempotent.
-- On a large live table you may prefer running the CREATE INDEX with CONCURRENTLY
-- (outside a transaction block).

-- Superseded by 20261101_authority_search_vector.sql (stored weighted search_vector). Once that
-- column exists this legacy index is not rebuilt (search-index.sql drops it concurrently).
DO $$ BEGIN
  IF NOT EXISTS (SELECT 1 FROM information_schema.columns
                 WHERE table_name = 'legal_authorities' AND column_name = 'search_vector') THEN
    CREATE INDEX IF NOT EXISTS ix_legal_authorities_fulltext
        ON legal_authorities
        USING GIN (to_tsvector('english'::regconfig, ((COALESCE(citation, '') || ' ') || COALESCE(title, '') || ' ') || COALESCE(text, '')));
  END IF;
END $$;

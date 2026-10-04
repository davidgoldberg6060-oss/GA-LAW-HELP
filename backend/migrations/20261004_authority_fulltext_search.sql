-- Issue #88 item 4: word-based full-text search over persisted Georgia authorities.
-- The expression MUST match app/authority_search_service.authority_document_expression()
-- so the planner can use this index. Idempotent.
-- On a large live table you may prefer running the CREATE INDEX with CONCURRENTLY
-- (outside a transaction block).

CREATE INDEX IF NOT EXISTS ix_legal_authorities_fulltext
    ON legal_authorities
    USING GIN (to_tsvector('english'::regconfig, ((COALESCE(citation, '') || ' ') || COALESCE(title, '') || ' ') || COALESCE(text, '')));

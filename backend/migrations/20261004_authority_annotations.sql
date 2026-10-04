-- Editorial annotations + source hierarchy for imported authorities (OCGA releases).
-- Additive and idempotent: a new table only; nothing in the serving path reads it.
CREATE TABLE IF NOT EXISTS authority_annotations (
    id SERIAL PRIMARY KEY,
    authority_id INTEGER NOT NULL REFERENCES legal_authorities(id),
    content_sha256 VARCHAR(64) NOT NULL,
    release VARCHAR(100) NOT NULL,
    hierarchy VARCHAR(1000),
    annotations TEXT,
    source_url VARCHAR(1000) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT (now() AT TIME ZONE 'utc'),
    CONSTRAINT uq_authority_annotations_version UNIQUE (authority_id, content_sha256)
);
CREATE INDEX IF NOT EXISTS ix_authority_annotations_authority_id ON authority_annotations (authority_id);
COMMENT ON TABLE authority_annotations IS 'Editorial annotations (not enacted law) and hierarchy per stored authority version.';

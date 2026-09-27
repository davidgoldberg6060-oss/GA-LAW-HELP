-- Persist evidence-backed legal-status metadata used by grounded retrieval.
-- Defaults deliberately remain 'unknown'; ingestion must never infer currency or
-- precedential force merely because a source is official.

ALTER TABLE legal_authorities ADD COLUMN IF NOT EXISTS currency_status VARCHAR(40) NOT NULL DEFAULT 'unknown';
ALTER TABLE legal_authorities ADD COLUMN IF NOT EXISTS precedential_status VARCHAR(40) NOT NULL DEFAULT 'unknown';
ALTER TABLE legal_authorities ADD COLUMN IF NOT EXISTS status_checked_at TIMESTAMP NULL;
ALTER TABLE legal_authorities ADD COLUMN IF NOT EXISTS status_source_url VARCHAR(1000) NULL;
ALTER TABLE legal_authorities ADD COLUMN IF NOT EXISTS superseding_authority VARCHAR(500) NULL;
ALTER TABLE legal_authorities ADD COLUMN IF NOT EXISTS negative_treatment TEXT NULL;

-- Keep status vocabulary conservative and machine-checkable. Unknown is always
-- preferable to inventing a legal conclusion that the source evidence does not establish.
ALTER TABLE legal_authorities DROP CONSTRAINT IF EXISTS ck_legal_authorities_currency_status;
ALTER TABLE legal_authorities ADD CONSTRAINT ck_legal_authorities_currency_status
    CHECK (currency_status IN ('unknown', 'current', 'negative_treatment'));

ALTER TABLE legal_authorities DROP CONSTRAINT IF EXISTS ck_legal_authorities_precedential_status;
ALTER TABLE legal_authorities ADD CONSTRAINT ck_legal_authorities_precedential_status
    CHECK (precedential_status IN ('unknown', 'precedential', 'nonprecedential'));

COMMENT ON COLUMN legal_authorities.currency_status IS 'Evidence-backed currency status; unknown unless established by source evidence.';
COMMENT ON COLUMN legal_authorities.precedential_status IS 'Evidence-backed precedential status; unknown unless established by source evidence.';
COMMENT ON COLUMN legal_authorities.status_checked_at IS 'UTC time at which status evidence was checked.';
COMMENT ON COLUMN legal_authorities.status_source_url IS 'HTTPS source supporting the stored legal-status determination.';

-- Constrain stored legal-authority status metadata to the vocabulary the code writes
-- (backend/app/legal_status_vocabulary.py). Supersedes PR #71, whose constraint used values
-- ('negative_treatment', 'precedential') that the importer never writes and rejected values it
-- does write ('overruled', 'withdrawn', 'binding', ...).
--
-- Safe to run more than once. Existing rows are normalized only for case/whitespace/blank.
-- Unrecognized legacy values are NOT rewritten: the constraints are added NOT VALID (enforced
-- for new writes), and validated only when no existing row violates them.

UPDATE legal_authorities SET currency_status = lower(btrim(currency_status))
    WHERE currency_status IS NOT NULL AND currency_status <> lower(btrim(currency_status));
UPDATE legal_authorities SET precedential_status = lower(btrim(precedential_status))
    WHERE precedential_status IS NOT NULL AND precedential_status <> lower(btrim(precedential_status));
UPDATE legal_authorities SET currency_status = 'unknown' WHERE currency_status IS NULL OR currency_status = '';
UPDATE legal_authorities SET precedential_status = 'unknown' WHERE precedential_status IS NULL OR precedential_status = '';

ALTER TABLE legal_authorities DROP CONSTRAINT IF EXISTS ck_legal_authorities_currency_status;
ALTER TABLE legal_authorities ADD CONSTRAINT ck_legal_authorities_currency_status
    CHECK (lower(currency_status) IN ('current', 'overruled', 'repealed', 'superseded', 'unknown', 'vacated', 'withdrawn')) NOT VALID;

ALTER TABLE legal_authorities DROP CONSTRAINT IF EXISTS ck_legal_authorities_precedential_status;
ALTER TABLE legal_authorities ADD CONSTRAINT ck_legal_authorities_precedential_status
    CHECK (lower(precedential_status) IN ('binding', 'nonprecedential', 'overruled', 'repealed', 'superseded', 'unknown', 'vacated', 'withdrawn')) NOT VALID;

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM legal_authorities
        WHERE lower(currency_status) NOT IN ('current', 'overruled', 'repealed', 'superseded', 'unknown', 'vacated', 'withdrawn')
    ) THEN
        ALTER TABLE legal_authorities VALIDATE CONSTRAINT ck_legal_authorities_currency_status;
    ELSE
        RAISE NOTICE 'ck_legal_authorities_currency_status left NOT VALID: review rows with unrecognized currency_status';
    END IF;
    IF NOT EXISTS (
        SELECT 1 FROM legal_authorities
        WHERE lower(precedential_status) NOT IN ('binding', 'nonprecedential', 'overruled', 'repealed', 'superseded', 'unknown', 'vacated', 'withdrawn')
    ) THEN
        ALTER TABLE legal_authorities VALIDATE CONSTRAINT ck_legal_authorities_precedential_status;
    ELSE
        RAISE NOTICE 'ck_legal_authorities_precedential_status left NOT VALID: review rows with unrecognized precedential_status';
    END IF;
END $$;

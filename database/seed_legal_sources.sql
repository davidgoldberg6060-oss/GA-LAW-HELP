-- Initial authoritative source registry for GA.LAW.HELP.
INSERT INTO legal_sources(source_type,issuing_body,title,canonical_url,is_official,version_label)
VALUES
('statutes','Georgia General Assembly','Georgia General Assembly legislation and statutory materials','https://www.legis.ga.gov/',TRUE,'current'),
('opinions','Supreme Court of Georgia','Supreme Court of Georgia opinions','https://www.gasupreme.us/',TRUE,'current'),
('opinions','Court of Appeals of Georgia','Court of Appeals of Georgia opinions and court materials','https://www.gaappeals.us/',TRUE,'current'),
('court_rules','Supreme Court of Georgia','Supreme Court of Georgia Rules','https://www.gasupreme.us/rules/',TRUE,'current')
ON CONFLICT DO NOTHING;

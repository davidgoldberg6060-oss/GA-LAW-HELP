-- Court of Appeals of Georgia slip opinions fetched from the court's own e-filing host
-- (efast.gaappeals.gov) via the robots.txt-allowed opinion search. Idempotent and additive.
INSERT INTO verification_sources (id, source_key, source_name, source_url, edition, as_of_date, as_of_label, method) VALUES
 (5, 'ga_appeals_slip_opinions', 'Court of Appeals of Georgia slip opinions (official court PDF, efast.gaappeals.gov)',
     'https://www.gaappeals.gov/opinion-search/', 'slip opinion as issued', NULL,
     'slip opinion as issued by the court; may change on reconsideration or publication', 'official_source_provenance')
ON CONFLICT (id) DO NOTHING;

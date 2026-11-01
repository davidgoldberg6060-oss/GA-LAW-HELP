-- Prints stored text of high-use O.C.G.A. sections so they can be compared with a current public source.
\pset footer off
\pset format unaligned
SELECT '@@SECTION ' || citation || E'\n' || replace(left(text, 6000), E'\r', '') || E'\n@@END'
  FROM legal_authorities
 WHERE lower(authority_type)='statute' AND citation IN (
  'O.C.G.A. § 35-3-37','O.C.G.A. § 44-7-30','O.C.G.A. § 44-7-31','O.C.G.A. § 44-7-32','O.C.G.A. § 44-7-33',
  'O.C.G.A. § 44-7-34','O.C.G.A. § 44-7-35','O.C.G.A. § 44-7-36','O.C.G.A. § 44-7-37','O.C.G.A. § 44-7-50',
  'O.C.G.A. § 19-5-1','O.C.G.A. § 19-5-2','O.C.G.A. § 19-5-3','O.C.G.A. § 19-5-4','O.C.G.A. § 19-5-5',
  'O.C.G.A. § 40-6-391','O.C.G.A. § 16-13-30','O.C.G.A. § 17-5-1','O.C.G.A. § 17-5-21','O.C.G.A. § 17-5-30',
  'O.C.G.A. § 16-8-2','O.C.G.A. § 16-8-12','O.C.G.A. § 16-5-23','O.C.G.A. § 16-5-23.1','O.C.G.A. § 16-11-37',
  'O.C.G.A. § 16-11-126','O.C.G.A. § 9-3-31','O.C.G.A. § 9-3-33','O.C.G.A. § 15-10-2','O.C.G.A. § 44-7-7')
 ORDER BY citation;

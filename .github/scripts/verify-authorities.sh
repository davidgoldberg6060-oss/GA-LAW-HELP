#!/usr/bin/env bash
# Official-source provenance verification (db-maintenance action "verify-authorities").
# Inserts one small row per qualifying legal_authorities row into authority_verifications.
# Never UPDATEs legal_authorities (no rewrite of text/search_vector; trigger never fires).
# Batched by id range with a disk guard; idempotent (ON CONFLICT DO NOTHING); DRY_RUN=true = report only.
set -euo pipefail
: "${LIBPQ_URL:?}"
BATCH="${BATCH:-5000}"
MAX_GROWTH_MB="${MAX_GROWTH_MB:-150}"
DRY_RUN="${DRY_RUN:-true}"
q() { psql "$LIBPQ_URL" -X -v ON_ERROR_STOP=1 -At -c "$1"; }

# Qualifying rows (provenance + quality). Missing/garbled/empty text or no citation never qualify.
QUAL="
  WITH c AS (
    SELECT a.id,
      CASE
        WHEN lower(a.authority_type)='statute'
             AND a.source_url LIKE 'https://archive.org/download/gov.ga.ocga.2018/release86.2022.11/%'
             AND a.citation ~ '^O\.C\.G\.A\. § [0-9]+[A-Z]?-[0-9]+[A-Z]?-[0-9]+' THEN 1
        WHEN lower(a.authority_type)='regulation'
             AND a.source_url LIKE 'https://rules.sos.ga.gov/%'
             AND a.citation LIKE 'Ga. Comp. R. & Regs.%' THEN 2
        WHEN lower(a.authority_type) IN ('case_law','case','opinion')
             AND a.source_url LIKE 'https://www.courtlistener.com/%' THEN 3
        WHEN lower(a.authority_type)='court_rule'
             AND a.source_url ~ '^https://([a-z0-9-]+\.)*(gasupreme\.us|gaappeals\.gov|georgiacourts\.gov|gasupreme\.gov)/' THEN 4
      END AS source_id
    FROM legal_authorities a
    WHERE a.id >= :lo AND a.id < :hi
      AND lower(coalesce(a.jurisdiction,'')) = 'georgia'
      AND length(btrim(coalesce(a.citation,''))) >= 5
      AND length(btrim(coalesce(a.text,''))) >= CASE WHEN lower(a.authority_type) IN ('case_law','case','opinion') THEN 200 ELSE 40 END
      AND strpos(a.text, chr(65533)) = 0
      AND a.text !~ '[\x01-\x08\x0B\x0C\x0E-\x1F]'
      AND btrim(a.text) !~* '^(repealed|reserved)[ .]*\$'
      AND lower(coalesce(a.currency_status,'')) NOT IN ('repealed','superseded','withdrawn')
      AND lower(coalesce(a.precedential_status,'')) NOT IN ('overruled','vacated','withdrawn')
  ) SELECT id, source_id FROM c WHERE source_id IS NOT NULL"

sub() { local s="${QUAL//:lo/$1}"; echo "${s//:hi/$2}"; }

echo "== disk before"; q "SELECT pg_database_size(current_database()), pg_size_pretty(pg_database_size(current_database()))"
START=$(q "SELECT pg_database_size(current_database())")
MINID=$(q "SELECT coalesce(min(id),0) FROM legal_authorities"); MAXID=$(q "SELECT coalesce(max(id),0) FROM legal_authorities")
echo "== id range $MINID..$MAXID batch=$BATCH dry_run=$DRY_RUN"

echo "== rejected-by-quality profile (per type)"
psql "$LIBPQ_URL" -X -c "SELECT authority_type, count(*) total,
  count(*) FILTER (WHERE length(btrim(coalesce(text,'')))=0) empty_text,
  count(*) FILTER (WHERE length(btrim(coalesce(citation,'')))<5) no_citation,
  count(*) FILTER (WHERE strpos(coalesce(text,''), chr(65533))>0) replacement_chars,
  count(*) FILTER (WHERE lower(authority_type)='statute' AND source_url NOT LIKE 'https://archive.org/download/gov.ga.ocga.2018/release86.2022.11/%') statute_other_release
  FROM legal_authorities GROUP BY 1 ORDER BY 2 DESC"
psql "$LIBPQ_URL" -X -c "SELECT authority_type, left(source_url, 70) url_prefix FROM (SELECT DISTINCT ON (authority_type) authority_type, source_url FROM legal_authorities ORDER BY authority_type, id) x"

lo=$MINID
while [ "$lo" -le "$MAXID" ]; do
  hi=$((lo + BATCH))
  if [ "$DRY_RUN" = "true" ]; then
    q "SELECT source_id, count(*) FROM ($(sub $lo $hi)) z GROUP BY 1" | sed "s/^/batch $lo: /" >> /tmp/dry.txt
  else
    n=$(q "WITH ins AS (INSERT INTO authority_verifications(authority_id, source_id) $(sub $lo $hi) ON CONFLICT (authority_id) DO NOTHING RETURNING 1) SELECT count(*) FROM ins")
    NOW=$(q "SELECT pg_database_size(current_database())")
    echo "batch [$lo,$hi): +$n rows; db=$((NOW/1048576)) MB"
    if [ $(( (NOW - START) / 1048576 )) -gt "$MAX_GROWTH_MB" ]; then
      echo "::warning::database grew more than ${MAX_GROWTH_MB} MB; stopping safely at id $hi"; break
    fi
    if [ $(( (hi - MINID) / BATCH % 10 )) -eq 0 ]; then q "VACUUM (ANALYZE) authority_verifications" >/dev/null; fi
  fi
  lo=$hi
done
if [ "$DRY_RUN" = "true" ]; then
  echo "== dry run: qualifying rows by source_id"; awk '{split($3,a,"|"); s[a[1]]+=a[2]} END {for (k in s) print "source_id", k, s[k]}' /tmp/dry.txt
else
  q "VACUUM (ANALYZE) authority_verifications" >/dev/null
fi
if [ "$DRY_RUN" != "true" ]; then
echo "== verified rows by source"
psql "$LIBPQ_URL" -X -c "SELECT s.id, s.source_key, s.as_of_label, count(v.authority_id) verified FROM verification_sources s LEFT JOIN authority_verifications v ON v.source_id=s.id GROUP BY 1,2,3 ORDER BY 1"
psql "$LIBPQ_URL" -X -c "SELECT pg_size_pretty(pg_total_relation_size('authority_verifications')) side_table_size, pg_size_pretty(pg_database_size(current_database())) db_size"
fi

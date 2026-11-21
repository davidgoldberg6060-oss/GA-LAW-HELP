SELECT datname, pg_database_size(oid)/1048576 mb FROM pg_database ORDER BY 2 DESC;
SELECT datname, temp_files, temp_bytes/1048576 temp_mb FROM pg_stat_database WHERE datname IS NOT NULL;
SELECT name FROM pg_available_extensions WHERE name IN ('pgstattuple','pg_repack');
SELECT c.relname, t.relname toast, pg_relation_size(t.oid)/1048576 toast_heap_mb, st.n_live_tup, st.n_dead_tup, st.last_autovacuum
FROM pg_class c JOIN pg_class t ON t.oid=c.reltoastrelid LEFT JOIN pg_stat_all_tables st ON st.relid=t.oid
WHERE c.relname IN ('legal_authorities','authority_versions','authority_annotations');
SELECT rolsuper FROM pg_roles WHERE rolname=current_user;
SELECT current_setting('data_directory') datadir, current_setting('logging_collector') lc, current_setting('log_directory') logdir;
SELECT (SELECT coalesce(sum(size),0) FROM pg_ls_tmpdir())/1048576 tmp_mb;
-- orphan relation files in this database directory (not referenced by pg_class)
WITH f AS (SELECT name, (pg_stat_file('base/'||(SELECT oid FROM pg_database WHERE datname=current_database())||'/'||name)).size sz
           FROM pg_ls_dir('base/'||(SELECT oid FROM pg_database WHERE datname=current_database())) name)
SELECT count(*) orphan_files, sum(sz)/1048576 orphan_mb FROM f
WHERE name ~ '^[0-9]+' AND split_part(split_part(name,'.',1),'_',1)::oid NOT IN (SELECT pg_relation_filenode(oid) FROM pg_class WHERE pg_relation_filenode(oid) IS NOT NULL);
SELECT sum((pg_stat_file('base/'||(SELECT oid FROM pg_database WHERE datname=current_database())||'/'||name)).size)/1048576 dir_mb FROM pg_ls_dir('base/'||(SELECT oid FROM pg_database WHERE datname=current_database())) name;
SELECT name, (pg_stat_file(name)).size/1048576 mb, (pg_stat_file(name)).isdir FROM pg_ls_dir('.') name;
SELECT name, (pg_stat_file('/var/lib/postgresql/data/'||name)).size/1048576 mb, (pg_stat_file('/var/lib/postgresql/data/'||name)).isdir FROM pg_ls_dir('/var/lib/postgresql/data') name;
SELECT d, (SELECT sum((pg_stat_file(d||'/'||n)).size) FROM pg_ls_dir(d) n)/1048576 mb FROM unnest(array['pg_xact','pg_multixact/members','pg_multixact/offsets','pg_subtrans','pg_stat','pg_commit_ts','pg_logical','global']) d;
SELECT pid, backend_type, state, backend_start, xact_start, left(query,60) q FROM pg_stat_activity ORDER BY backend_start;
-- ===== Nov 20 space audit (read-only) =====
\pset footer off
SELECT pg_database_size(current_database())/1048576 AS db_mb;
SELECT n.nspname, c.relname, c.relkind,
       pg_total_relation_size(c.oid)/1048576 total_mb,
       pg_relation_size(c.oid)/1048576 heap_mb,
       pg_indexes_size(c.oid)/1048576 index_mb,
       coalesce(pg_total_relation_size(nullif(c.reltoastrelid,0)),0)/1048576 toast_mb,
       s.n_live_tup, s.n_dead_tup, s.last_autovacuum::date, s.last_vacuum::date, s.seq_scan, s.idx_scan
  FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace
  LEFT JOIN pg_stat_user_tables s ON s.relid=c.oid
 WHERE c.relkind IN ('r','m','p') AND n.nspname NOT IN ('pg_catalog','information_schema')
 ORDER BY pg_total_relation_size(c.oid) DESC LIMIT 40;
SELECT s.relname tbl, s.indexrelname idx, pg_relation_size(s.indexrelid)/1048576 mb, s.idx_scan, i.indisunique
  FROM pg_stat_user_indexes s JOIN pg_index i ON i.indexrelid=s.indexrelid
 ORDER BY pg_relation_size(s.indexrelid) DESC LIMIT 30;
SELECT table_name, column_name, data_type, udt_name FROM information_schema.columns
 WHERE table_schema='public' AND (udt_name IN ('vector','halfvec','tsvector','bytea') OR column_name ILIKE '%embed%');
SELECT extname, extversion FROM pg_extension;
SELECT authority_type, count(*) n, sum(pg_column_size(text))/1048576 text_mb, avg(length(text))::int avg_chars,
       min(effective_from) min_eff, max(effective_from) max_eff, min(retrieved_at)::date min_ret, max(retrieved_at)::date max_ret
  FROM legal_authorities GROUP BY 1 ORDER BY 3 DESC NULLS LAST;
SELECT authority_type, split_part(split_part(coalesce(source_url,''),'://',2),'/',1) host, count(*) n, sum(pg_column_size(text))/1048576 text_mb
  FROM legal_authorities GROUP BY 1,2 ORDER BY 4 DESC NULLS LAST LIMIT 30;
SELECT authority_type, currency_status, status, count(*) FROM legal_authorities GROUP BY 1,2,3 ORDER BY 4 DESC LIMIT 30;
-- Opinions by court (citation/title prefix heuristics) and year
SELECT CASE WHEN citation ~* '^S[0-9]{2}[A-Z]' OR source_url ILIKE '%gasupreme%' OR citation ~* 'Ga\.\s' AND citation !~* 'Ga\.\s*App' THEN 'supreme'
            WHEN citation ~* '^A[0-9]{2}[A-Z]' OR citation ~* 'Ga\.\s*App' OR source_url ILIKE '%gaappeals%' THEN 'appeals' ELSE 'other' END court,
       extract(year FROM effective_from)::int yr, count(*) n, sum(pg_column_size(text))/1048576 text_mb
  FROM legal_authorities WHERE authority_type NOT IN ('statute','regulation','court_rule','constitution')
 GROUP BY 1,2 ORDER BY 1,2;
-- authority_versions vs legal_authorities duplication
SELECT count(*) versions, count(DISTINCT authority_id) authorities_with_versions, sum(pg_column_size(text))/1048576 version_text_mb FROM authority_versions;
SELECT la.authority_type, count(*) n_versions, sum(pg_column_size(av.text))/1048576 mb,
       count(*) FILTER (WHERE av.text = la.text) same_as_current
  FROM authority_versions av JOIN legal_authorities la ON la.id=av.authority_id GROUP BY 1 ORDER BY 3 DESC;
SELECT version_label, count(*) FROM authority_versions GROUP BY 1 ORDER BY 2 DESC LIMIT 15;
-- duplicate authorities by (type, citation) and by identical text
SELECT authority_type, count(*) dup_rows, sum(pg_column_size(text))/1048576 dup_text_mb FROM (
  SELECT authority_type, text, row_number() OVER (PARTITION BY authority_type, lower(citation) ORDER BY id) rn FROM legal_authorities) x
 WHERE rn>1 GROUP BY 1 ORDER BY 3 DESC NULLS LAST;
SELECT count(*) dup_text_rows, sum(pg_column_size(text))/1048576 dup_text_mb FROM (
  SELECT text, row_number() OVER (PARTITION BY md5(text) ORDER BY id) rn FROM legal_authorities WHERE text IS NOT NULL AND length(text)>200) x WHERE rn>1;
-- statute edition / title coverage
SELECT split_part(citation,'-',1) title_part, count(*) n FROM legal_authorities WHERE authority_type='statute' GROUP BY 1 ORDER BY count(*) DESC LIMIT 60;
SELECT release, count(*), sum(pg_column_size(annotations))/1048576 mb FROM authority_annotations GROUP BY 1;
SELECT source_key, edition, as_of_label FROM verification_sources;
SELECT sum(pg_column_size(t.*))/1048576 approx_row_mb FROM legal_authorities t;

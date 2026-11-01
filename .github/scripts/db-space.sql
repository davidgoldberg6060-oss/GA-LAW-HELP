SELECT datname, pg_database_size(oid)/1048576 mb FROM pg_database ORDER BY 2 DESC;
SELECT datname, temp_files, temp_bytes/1048576 temp_mb FROM pg_stat_database WHERE datname IS NOT NULL;
SELECT name FROM pg_available_extensions WHERE name IN ('pgstattuple','pg_repack');
SELECT c.relname, t.relname toast, pg_relation_size(t.oid)/1048576 toast_heap_mb, st.n_live_tup, st.n_dead_tup, st.last_autovacuum
FROM pg_class c JOIN pg_class t ON t.oid=c.reltoastrelid LEFT JOIN pg_stat_all_tables st ON st.relid=t.oid
WHERE c.relname IN ('legal_authorities','authority_versions','authority_annotations');

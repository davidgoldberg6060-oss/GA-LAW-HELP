SELECT datname, pg_database_size(oid)/1048576 mb FROM pg_database ORDER BY 2 DESC;
SELECT datname, temp_files, temp_bytes/1048576 temp_mb FROM pg_stat_database WHERE datname IS NOT NULL;
SELECT name FROM pg_available_extensions WHERE name IN ('pgstattuple','pg_repack');
SELECT c.relname, t.relname toast, pg_relation_size(t.oid)/1048576 toast_heap_mb, st.n_live_tup, st.n_dead_tup, st.last_autovacuum
FROM pg_class c JOIN pg_class t ON t.oid=c.reltoastrelid LEFT JOIN pg_stat_all_tables st ON st.relid=t.oid
WHERE c.relname IN ('legal_authorities','authority_versions','authority_annotations');
SELECT rolsuper FROM pg_roles WHERE rolname=current_user;
SELECT current_setting('data_directory') datadir, current_setting('logging_collector') lc, current_setting('log_directory') logdir;
SELECT (SELECT coalesce(sum(size),0) FROM pg_ls_logdir())/1048576 log_mb, (SELECT coalesce(sum(size),0) FROM pg_ls_tmpdir())/1048576 tmp_mb;
-- orphan relation files in this database directory (not referenced by pg_class)
WITH f AS (SELECT name, (pg_stat_file('base/'||(SELECT oid FROM pg_database WHERE datname=current_database())||'/'||name)).size sz
           FROM pg_ls_dir('base/'||(SELECT oid FROM pg_database WHERE datname=current_database())) name)
SELECT count(*) orphan_files, sum(sz)/1048576 orphan_mb FROM f
WHERE name ~ '^[0-9]+' AND split_part(split_part(name,'.',1),'_',1)::oid NOT IN (SELECT pg_relation_filenode(oid) FROM pg_class WHERE pg_relation_filenode(oid) IS NOT NULL);
SELECT sum((pg_stat_file('base/'||(SELECT oid FROM pg_database WHERE datname=current_database())||'/'||name)).size)/1048576 dir_mb FROM pg_ls_dir('base/'||(SELECT oid FROM pg_database WHERE datname=current_database())) name;
SELECT name, (pg_stat_file(name)).size/1048576 mb, (pg_stat_file(name)).isdir FROM pg_ls_dir('.') name;

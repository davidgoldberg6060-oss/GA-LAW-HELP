-- Read-only search diagnostics. Run with PGOPTIONS='-c default_transaction_read_only=on'.
\pset footer off
\timing on
SET statement_timeout = '180s';
SELECT indexrelid::regclass AS index, pg_size_pretty(pg_relation_size(indexrelid)) AS size, indisvalid
  FROM pg_index WHERE indrelid = 'legal_authorities'::regclass;
SELECT pg_size_pretty(pg_total_relation_size('legal_authorities')) AS table_total,
       pg_size_pretty(pg_relation_size('legal_authorities')) AS heap,
       pg_size_pretty(pg_total_relation_size(reltoastrelid)) AS toast,
       pg_size_pretty(pg_indexes_size('legal_authorities')) AS indexes,
       pg_size_pretty(pg_database_size(current_database())) AS database
  FROM pg_class WHERE oid = 'legal_authorities'::regclass;
SELECT relname, n_live_tup, n_dead_tup, pg_size_pretty(pg_total_relation_size(relid)) AS total
  FROM pg_stat_user_tables ORDER BY pg_total_relation_size(relid) DESC LIMIT 8;
SELECT pg_size_pretty(sum(pg_column_size(search_vector))) AS search_vector_bytes FROM legal_authorities;
SELECT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='legal_authorities' AND column_name='search_vector') AS has_search_vector;
SELECT count(*) FILTER (WHERE search_vector IS NULL) AS sv_null, count(*) AS total FROM legal_authorities
  WHERE EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='legal_authorities' AND column_name='search_vector') \gset
\echo search_vector null/total: :sv_null / :total
-- Legacy query shape (expression tsvector, OR semantics, statutes filter)
EXPLAIN (ANALYZE, BUFFERS)
SELECT id, citation FROM legal_authorities
 WHERE jurisdiction ILIKE 'Georgia' AND lower(authority_type) IN ('statute','regulation')
   AND (to_tsvector('english'::regconfig, ((COALESCE(citation,'') || ' ') || COALESCE(title,'') || ' ') || COALESCE(text,''))
        @@ websearch_to_tsquery('english'::regconfig, 'tenant or rights or eviction or notice')
        OR citation ILIKE '%tenant rights eviction notice%')
 ORDER BY ts_rank_cd(to_tsvector('english'::regconfig, ((COALESCE(citation,'') || ' ') || COALESCE(title,'') || ' ') || COALESCE(text,'')),
          websearch_to_tsquery('english'::regconfig, 'tenant or rights or eviction or notice')) DESC
 LIMIT 25;
SELECT version();
SELECT pg_size_pretty(sum(size)) AS wal_size, count(*) AS wal_files FROM pg_ls_waldir();
SELECT slot_name, active, pg_size_pretty(pg_wal_lsn_diff(pg_current_wal_lsn(), restart_lsn)) AS retained FROM pg_replication_slots;
SELECT name, setting, unit FROM pg_settings WHERE name IN ('max_wal_size','min_wal_size','wal_keep_size','maintenance_work_mem','max_parallel_maintenance_workers','temp_file_limit','archive_mode','temp_tablespaces');
SELECT pg_size_pretty(sum((pg_stat_file('base/pgsql_tmp/' || f)).size)) AS tmp FROM pg_ls_dir('base/pgsql_tmp', true, false) f;

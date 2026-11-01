\pset pager off
SELECT pg_size_pretty(pg_database_size(current_database())) db_size, pg_database_size(current_database())/1048576 db_mb;
SELECT (SELECT sum(size) FROM pg_ls_waldir())/1048576 AS wal_mb;
SHOW max_wal_size; SHOW wal_keep_size;
SELECT slot_name, active, pg_size_pretty(pg_wal_lsn_diff(pg_current_wal_lsn(), restart_lsn)) retained FROM pg_replication_slots;
SELECT c.relname, c.relkind, pg_total_relation_size(c.oid)/1048576 total_mb, pg_relation_size(c.oid)/1048576 heap_mb,
  pg_indexes_size(c.oid)/1048576 idx_mb, COALESCE(pg_total_relation_size(c.reltoastrelid),0)/1048576 toast_mb,
  s.n_live_tup, s.n_dead_tup, s.last_autovacuum, s.last_vacuum
FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace LEFT JOIN pg_stat_user_tables s ON s.relid=c.oid
WHERE n.nspname NOT IN ('pg_catalog','information_schema') AND c.relkind IN ('r','m','p')
ORDER BY pg_total_relation_size(c.oid) DESC LIMIT 40;
SELECT s.relname, s.indexrelname, pg_relation_size(s.indexrelid)/1048576 mb, s.idx_scan, i.indisunique, i.indisprimary, pg_get_indexdef(s.indexrelid)
FROM pg_stat_user_indexes s JOIN pg_index i ON i.indexrelid=s.indexrelid ORDER BY pg_relation_size(s.indexrelid) DESC LIMIT 60;
-- duplicate indexes
SELECT indrelid::regclass, array_agg(indexrelid::regclass) FROM pg_index GROUP BY indrelid, indkey::text, indclass::text, COALESCE(indexprs::text,''), COALESCE(indpred::text,'') HAVING count(*)>1;
-- column sizes of big tables
SELECT 'legal_authorities' t, a.attname FROM pg_attribute a WHERE a.attrelid='legal_authorities'::regclass AND a.attnum>0 AND NOT a.attisdropped;

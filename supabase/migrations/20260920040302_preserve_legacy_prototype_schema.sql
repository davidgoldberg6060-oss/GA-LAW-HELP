begin;

-- Preserve the original empty Supabase/Auth prototype without deleting it.
-- The v1.3 FastAPI application owns authentication and database access, so its
-- bigint-backed production tables must occupy the public schema names.
create schema if not exists legacy;
revoke all on schema legacy from public;
revoke all on schema legacy from anon, authenticated;

alter table if exists public.research_messages set schema legacy;
alter table if exists public.research_threads set schema legacy;
alter table if exists public.case_documents set schema legacy;
alter table if exists public.cases set schema legacy;
alter table if exists public.legal_sources set schema legacy;

commit;

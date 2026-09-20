begin;

-- PostgreSQL does not automatically index the referencing side of foreign keys.
-- These indexes protect joins and ON DELETE CASCADE operations as data grows.
create index if not exists ix_evidence_findings_evidence_id on public.evidence_findings(evidence_id);
create index if not exists ix_upload_sessions_case_id on public.upload_sessions(case_id);
create index if not exists ix_upload_sessions_user_id on public.upload_sessions(user_id);
create index if not exists ix_analysis_jobs_evidence_id on public.analysis_jobs(evidence_id);
create index if not exists ix_authority_versions_authority_id on public.authority_versions(authority_id);
create index if not exists ix_case_authority_links_case_id on public.case_authority_links(case_id);
create index if not exists ix_case_authority_links_authority_id on public.case_authority_links(authority_id);
create index if not exists ix_case_authority_links_version_id on public.case_authority_links(authority_version_id);
create index if not exists ix_password_reset_tokens_user_id on public.password_reset_tokens(user_id);

-- The mobile client uses only the FastAPI boundary. Lock current and future
-- public objects against direct Data API access, including identity sequences.
revoke all on all sequences in schema public from anon, authenticated;
alter default privileges in schema public revoke all on tables from anon, authenticated;
alter default privileges in schema public revoke all on sequences from anon, authenticated;

commit;

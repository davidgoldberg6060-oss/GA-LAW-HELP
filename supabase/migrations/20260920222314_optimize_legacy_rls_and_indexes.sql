begin;

create index if not exists ix_legacy_case_documents_case_id
  on legacy.case_documents (case_id);
create index if not exists ix_legacy_case_documents_user_id
  on legacy.case_documents (user_id);
create index if not exists ix_legacy_cases_user_id
  on legacy.cases (user_id);
create index if not exists ix_legacy_research_messages_user_id
  on legacy.research_messages (user_id);
create index if not exists ix_legacy_research_threads_case_id
  on legacy.research_threads (case_id);
create index if not exists ix_legacy_research_threads_user_id
  on legacy.research_threads (user_id);

alter policy "own cases" on legacy.cases
  using ((select auth.uid()) = user_id)
  with check ((select auth.uid()) = user_id);
alter policy "own documents" on legacy.case_documents
  using ((select auth.uid()) = user_id)
  with check ((select auth.uid()) = user_id);
alter policy "own threads" on legacy.research_threads
  using ((select auth.uid()) = user_id)
  with check ((select auth.uid()) = user_id);
alter policy "own messages" on legacy.research_messages
  using ((select auth.uid()) = user_id)
  with check ((select auth.uid()) = user_id);

commit;

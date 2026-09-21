create table if not exists public.case_notes (
 id bigserial primary key,
 case_id bigint not null references public.cases(id) on delete cascade,
 owner_id bigint not null references public.users(id) on delete cascade,
 note_type varchar(40) not null default 'LEGAL_RESEARCH',
 title varchar(255) not null default 'Saved legal research',
 content text not null,
 language varchar(12) not null default 'en',
 created_at timestamp without time zone not null default timezone('utc', now()),
 updated_at timestamp without time zone not null default timezone('utc', now()),
 constraint case_notes_content_length check (char_length(content) between 1 and 100000)
);
create index if not exists ix_case_notes_case_id on public.case_notes(case_id);
create index if not exists ix_case_notes_owner_id on public.case_notes(owner_id);
alter table public.case_notes enable row level security;
revoke all on public.case_notes from anon, authenticated;

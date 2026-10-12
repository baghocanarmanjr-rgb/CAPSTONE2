-- PPMP review/approval workflow metadata.
-- Safe to run repeatedly.
alter table public.ppmp add column if not exists reviewed_by text;
alter table public.ppmp add column if not exists reviewed_at text;
alter table public.ppmp add column if not exists approved_by text;
alter table public.ppmp add column if not exists approved_at text;

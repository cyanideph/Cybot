-- Phase 3: durable room context, summaries, and semantic memory.
create extension if not exists vector with schema extensions;

create table if not exists public.uzzapbot_room_memory (
  id bigint generated always as identity primary key,
  room_name text not null,
  memory_type text not null default 'conversation',
  content text not null,
  embedding extensions.vector(768),
  source_message_id bigint,
  metadata jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now(),
  expires_at timestamptz
);

create index if not exists uzzapbot_room_memory_room_created_idx
  on public.uzzapbot_room_memory (room_name, created_at desc);

create table if not exists public.uzzapbot_room_summaries (
  room_name text primary key,
  summary text not null default '',
  topic text not null default 'GENERAL',
  message_count bigint not null default 0,
  source_through_message_id bigint,
  updated_at timestamptz not null default now()
);

alter table public.uzzapbot_room_memory enable row level security;
alter table public.uzzapbot_room_summaries enable row level security;

revoke all on public.uzzapbot_room_memory from anon, authenticated, public;
revoke all on public.uzzapbot_room_summaries from anon, authenticated, public;
grant select, insert, update, delete on public.uzzapbot_room_memory to service_role;
grant select, insert, update, delete on public.uzzapbot_room_summaries to service_role;

create index if not exists uzzapbot_room_memory_embedding_hnsw_idx
  on public.uzzapbot_room_memory
  using hnsw (embedding vector_cosine_ops)
  where embedding is not null;

create or replace function public.uzzapbot_match_room_memory(
  p_room_name text,
  p_query_embedding extensions.vector(768),
  p_match_threshold double precision default 0.72,
  p_match_count integer default 5
)
returns table (
  id bigint,
  room_name text,
  memory_type text,
  content text,
  metadata jsonb,
  created_at timestamptz,
  similarity double precision
)
language sql
stable
security definer
set search_path = ''
as $$
  select
    m.id,
    m.room_name,
    m.memory_type,
    m.content,
    m.metadata,
    m.created_at,
    1 - (m.embedding <=> p_query_embedding) as similarity
  from public.uzzapbot_room_memory m
  where m.room_name = p_room_name
    and m.embedding is not null
    and (m.expires_at is null or m.expires_at > now())
    and 1 - (m.embedding <=> p_query_embedding) >= p_match_threshold
  order by m.embedding <=> p_query_embedding asc
  limit least(greatest(p_match_count, 1), 20);
$$;

revoke execute on function public.uzzapbot_match_room_memory(text, extensions.vector(768), double precision, integer)
  from anon, authenticated, public;
grant execute on function public.uzzapbot_match_room_memory(text, extensions.vector(768), double precision, integer)
  to service_role;

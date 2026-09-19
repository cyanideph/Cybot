-- Phase 3D: room-memory lifecycle and monotonic summary updates.

create index if not exists uzzapbot_room_memory_room_expiry_idx
  on public.uzzapbot_room_memory (room_name, expires_at, created_at desc);

create unique index if not exists uzzapbot_room_memory_source_unique_idx
  on public.uzzapbot_room_memory (room_name, memory_type, source_message_id)
  where source_message_id is not null;

create or replace function public.uzzapbot_purge_expired_memory()
returns bigint
language sql
volatile
security definer
set search_path = ''
as $$
  with deleted as (
    delete from public.uzzapbot_room_memory
    where expires_at is not null
      and expires_at <= now()
    returning id
  )
  select count(*)::bigint from deleted;
$$;

revoke execute on function public.uzzapbot_purge_expired_memory()
  from anon, authenticated, public;
grant execute on function public.uzzapbot_purge_expired_memory()
  to service_role;

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
    1 - (m.embedding OPERATOR(extensions.<=>) p_query_embedding) as similarity
  from public.uzzapbot_room_memory m
  where m.room_name = p_room_name
    and m.embedding is not null
    and (m.expires_at is null or m.expires_at > now())
    and 1 - (m.embedding OPERATOR(extensions.<=>) p_query_embedding) >= p_match_threshold
  order by m.embedding OPERATOR(extensions.<=>) p_query_embedding asc
  limit least(greatest(p_match_count, 1), 20);
$$;

revoke execute on function public.uzzapbot_match_room_memory(text, extensions.vector(768), double precision, integer)
  from anon, authenticated, public;
grant execute on function public.uzzapbot_match_room_memory(text, extensions.vector(768), double precision, integer)
  to service_role;

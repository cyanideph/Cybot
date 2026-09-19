-- Phase 3C: durable AI usage accounting and memory lifecycle indexes.

create index if not exists uzzapbot_ai_events_room_created_idx
  on public.uzzapbot_ai_events (room_name, created_at desc);

create index if not exists uzzapbot_room_memory_room_expiry_idx
  on public.uzzapbot_room_memory (room_name, expires_at, created_at desc);

create or replace function public.uzzapbot_ai_usage(
  p_room_name text default null
)
returns table (
  requests_hour bigint,
  requests_day bigint,
  messages_hour bigint,
  messages_day bigint
)
language sql
stable
security definer
set search_path = ''
as $$
  select
    count(*) filter (
      where e.created_at >= now() - interval '1 hour'
        and e.event_type <> 'response_sent'
    ) as requests_hour,
    count(*) filter (
      where e.created_at >= date_trunc('day', now())
        and e.event_type <> 'response_sent'
    ) as requests_day,
    count(*) filter (
      where e.created_at >= now() - interval '1 hour'
        and e.event_type = 'response_sent'
    ) as messages_hour,
    count(*) filter (
      where e.created_at >= date_trunc('day', now())
        and e.event_type = 'response_sent'
    ) as messages_day
  from public.uzzapbot_ai_events e
  where p_room_name is null or e.room_name = p_room_name;
$$;

revoke execute on function public.uzzapbot_ai_usage(text)
  from anon, authenticated, public;
grant execute on function public.uzzapbot_ai_usage(text)
  to service_role;

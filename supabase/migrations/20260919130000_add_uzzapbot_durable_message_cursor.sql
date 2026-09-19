create table if not exists public.uzzapbot_cursor (
  bot_name text primary key,
  last_message_id bigint not null default 0 check (last_message_id >= 0),
  updated_at timestamptz not null default now()
);

alter table public.uzzapbot_cursor enable row level security;

revoke all on table public.uzzapbot_cursor from anon, authenticated;
grant select, insert, update on table public.uzzapbot_cursor to service_role;

create or replace function public.uzzapbot_get_cursor()
returns bigint
language plpgsql
security definer
set search_path to ''
as $function$
declare
  v_cursor bigint;
  v_latest bigint;
begin
  if auth.role() <> 'service_role' then
    raise exception 'service role required';
  end if;

  select last_message_id
    into v_cursor
    from public.uzzapbot_cursor
   where bot_name = 'default'
   for update;

  if found then
    return v_cursor;
  end if;

  select coalesce(max(id), 0)
    into v_latest
    from public.room_messages;

  insert into public.uzzapbot_cursor(bot_name, last_message_id)
  values ('default', v_latest)
  on conflict (bot_name) do nothing;

  select last_message_id
    into v_cursor
    from public.uzzapbot_cursor
   where bot_name = 'default';

  return coalesce(v_cursor, v_latest, 0);
end;
$function$;

create or replace function public.uzzapbot_advance_cursor(
  p_previous_id bigint,
  p_message_id bigint
)
returns boolean
language plpgsql
security definer
set search_path to ''
as $function$
begin
  if auth.role() <> 'service_role' then
    raise exception 'service role required';
  end if;

  if p_message_id <= p_previous_id then
    return false;
  end if;

  update public.uzzapbot_cursor
     set last_message_id = p_message_id,
         updated_at = now()
   where bot_name = 'default'
     and last_message_id = p_previous_id;

  return found;
end;
$function$;

revoke all on function public.uzzapbot_get_cursor() from public, anon, authenticated;
grant execute on function public.uzzapbot_get_cursor() to service_role;

revoke all on function public.uzzapbot_advance_cursor(bigint, bigint) from public, anon, authenticated;
grant execute on function public.uzzapbot_advance_cursor(bigint, bigint) to service_role;

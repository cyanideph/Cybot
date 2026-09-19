-- Durable welcome-bot deduplication.
-- The bot may restart, so in-memory `seen` state must not be the source of truth.
create table if not exists public.uzzapbot_welcomes (
  room_name text not null,
  username_key text not null,
  welcomed_at timestamptz not null default now(),
  primary key (room_name, username_key)
);

alter table public.uzzapbot_welcomes enable row level security;

revoke all on table public.uzzapbot_welcomes from anon, authenticated, public;
grant select, insert on table public.uzzapbot_welcomes to service_role;

create or replace function public.uzzapbot_claim_welcome(
  p_room_name text,
  p_username text
)
returns boolean
language plpgsql
security definer
set search_path to ''
as $function$
declare
  v_room text := nullif(trim(p_room_name), '');
  v_username text := nullif(trim(p_username), '');
  v_inserted boolean;
begin
  if v_room is null or v_username is null then
    return false;
  end if;

  insert into public.uzzapbot_welcomes (room_name, username_key)
  values (v_room, lower(v_username))
  on conflict (room_name, username_key) do nothing;

  get diagnostics v_inserted = row_count;
  return v_inserted;
end;
$function$;

revoke execute on function public.uzzapbot_claim_welcome(text, text) from anon, authenticated, public;
grant execute on function public.uzzapbot_claim_welcome(text, text) to service_role;

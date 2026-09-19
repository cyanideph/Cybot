-- AI pass gate diagnostics for production troubleshooting.
-- Stores only non-secret configuration state and the latest gate reached per room.
create table if not exists public.uzzapbot_ai_diagnostics (
  room_name text primary key,
  checked_at timestamptz not null default now(),
  stage text not null,
  reason text,
  details jsonb not null default '{}'::jsonb
);

alter table public.uzzapbot_ai_diagnostics enable row level security;

revoke all on table public.uzzapbot_ai_diagnostics from anon, authenticated, public;
grant select, insert, update, delete on table public.uzzapbot_ai_diagnostics to service_role;

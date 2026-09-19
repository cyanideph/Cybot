-- Phase 1: deterministic room activity state for UzzapBot AI.
-- AI remains disabled by default; this table stores only bot activity metadata.

create table if not exists public.uzzapbot_room_activity (
  room_name text primary key,
  enabled boolean not null default false,
  idle_threshold_seconds integer not null default 900,
  inactive_threshold_seconds integer not null default 3600,
  cooldown_seconds integer not null default 1800,
  max_messages_per_hour integer not null default 3,
  max_messages_per_day integer not null default 20,
  last_human_activity_at timestamptz,
  last_bot_activity_at timestamptz,
  activity_state text not null default 'INACTIVE',
  human_message_count_hour integer not null default 0,
  human_message_count_day integer not null default 0,
  updated_at timestamptz not null default now(),
  constraint uzzapbot_room_activity_state_check check (activity_state in ('ACTIVE','QUIET','INACTIVE')),
  constraint uzzapbot_room_activity_idle_check check (idle_threshold_seconds >= 60),
  constraint uzzapbot_room_activity_inactive_check check (inactive_threshold_seconds >= idle_threshold_seconds),
  constraint uzzapbot_room_activity_cooldown_check check (cooldown_seconds >= 0),
  constraint uzzapbot_room_activity_hour_check check (max_messages_per_hour >= 0),
  constraint uzzapbot_room_activity_day_check check (max_messages_per_day >= 0)
);

alter table public.uzzapbot_room_activity enable row level security;
revoke all on table public.uzzapbot_room_activity from anon, authenticated, public;
grant select, insert, update, delete on table public.uzzapbot_room_activity to service_role;

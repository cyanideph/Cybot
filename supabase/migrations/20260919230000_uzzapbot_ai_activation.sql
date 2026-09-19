-- Phase 4: explicit room-level AI activation.
-- AI remains globally opt-in and dry-run by default in Python config.
alter table public.uzzapbot_room_settings
  add column if not exists ai_enabled boolean not null default false;

comment on column public.uzzapbot_room_settings.ai_enabled is
  'Explicit per-room opt-in for UzzapBot AI analysis; global AI config still gates execution.';

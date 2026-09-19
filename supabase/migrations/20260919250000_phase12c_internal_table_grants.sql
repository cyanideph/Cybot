-- Phase 12C: keep UzzapBot internal settings service-role only.
-- RLS remains enabled; this also removes unnecessary API-role table grants.
revoke all on table public.uzzapbot_room_settings from anon;
revoke all on table public.uzzapbot_room_settings from authenticated;
grant select, insert, update, delete on table public.uzzapbot_room_settings to service_role;

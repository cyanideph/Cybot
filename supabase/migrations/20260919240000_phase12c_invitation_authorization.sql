-- Phase 12C: close a room-invitation authorization gap.
-- An authenticated caller must already belong to the target room (or be a moderator)
-- before creating an invitation. The previous function only verified that the room
-- existed, allowing any signed-in user to create invitations for arbitrary rooms.

create or replace function public.create_room_invitation(
  p_room_name text,
  p_invitee_username text
)
returns boolean
language plpgsql
security definer
set search_path = ''
as $$
declare
  inviter uuid := (select auth.uid());
  invitee uuid;
  room_ok boolean;
  inviter_name text;
  invitee_name text;
  inviter_allowed boolean;
begin
  if inviter is null then
    raise exception 'authentication_required';
  end if;

  select p.username into inviter_name
  from public.profiles p
  where p.owner_id = inviter
  limit 1;

  if inviter_name is null then
    raise exception 'profile_not_found';
  end if;

  select exists(
    select 1 from public.chat_rooms
    where name = trim(p_room_name)
  ) into room_ok;

  if not room_ok then
    return false;
  end if;

  select
    exists (
      select 1
      from public.room_participants rp
      where rp.room_name = trim(p_room_name)
        and rp.owner_id = inviter
        and rp.last_ping >= now() - interval '45 seconds'
    )
    or public.is_moderator()
  into inviter_allowed;

  if not inviter_allowed then
    return false;
  end if;

  select owner_id, username into invitee, invitee_name
  from public.profiles
  where lower(username) = lower(trim(p_invitee_username))
  limit 1;

  if invitee is null or invitee = inviter then
    return false;
  end if;

  insert into public.room_invitations(
    room_name, inviter_id, invitee_id, inviter_username, invitee_username
  ) values (
    trim(p_room_name), inviter, invitee, inviter_name, invitee_name
  ) on conflict do nothing;

  return true;
end;
$$;

revoke execute on function public.create_room_invitation(text, text)
  from anon;
grant execute on function public.create_room_invitation(text, text)
  to authenticated;

-- resolve_login_email is intentionally left unchanged here because the shared
-- Uzzap client may use it before authentication for username-based login.
-- It remains a separate email-enumeration risk to address in the authentication
-- design rather than breaking the existing login flow in this security phase.

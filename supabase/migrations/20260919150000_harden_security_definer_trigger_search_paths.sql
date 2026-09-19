-- Harden SECURITY DEFINER trigger functions by pinning search_path.
-- All referenced application objects are schema-qualified.

create or replace function public.apply_moderation_action_trigger()
returns trigger
language plpgsql
security definer
set search_path = ''
as $$
declare
  resolved_target uuid;
begin
  resolved_target := new.target_user_id;
  if resolved_target is null then
    select owner_id into resolved_target
    from public.profiles
    where lower(username)=lower(new.target_username)
    limit 1;
  end if;

  if new.action_type in ('mute','kick','ban') and resolved_target is not null then
    insert into public.room_sanctions(user_id,username,room_name,sanction,expires_at,reason,created_by)
    values(resolved_target,new.target_username,new.room_name,new.action_type,new.expires_at,left(coalesce(new.reason,''),500),new.moderator_id);
  elsif new.action_type in ('unmute','unkick','unban') and resolved_target is not null then
    update public.room_sanctions
    set active=false
    where user_id=resolved_target
      and sanction=case new.action_type when 'unmute' then 'mute' when 'unkick' then 'kick' else 'ban' end
      and active=true
      and (new.room_name is null or room_name=new.room_name);
  end if;
  return new;
end;
$$;

create or replace function public.enforce_direct_message_rate_limit()
returns trigger
language plpgsql
security definer
set search_path = ''
as $$
declare
  uid uuid := (select auth.uid());
  recent_short integer;
  recent_minute integer;
begin
  if uid is null then return new; end if;
  perform pg_catalog.pg_advisory_xact_lock(pg_catalog.hashtextextended(uid::text, 1));

  select count(*) into recent_short
  from public.direct_messages
  where sender_id = uid and created_at > now() - interval '10 seconds';

  if recent_short >= 5 then
    raise exception using errcode = 'P0001', message = 'DIRECT_MESSAGE_RATE_LIMIT_10S';
  end if;

  select count(*) into recent_minute
  from public.direct_messages
  where sender_id = uid and created_at > now() - interval '1 minute';

  if recent_minute >= 30 then
    raise exception using errcode = 'P0001', message = 'DIRECT_MESSAGE_RATE_LIMIT_1M';
  end if;
  return new;
end;
$$;

create or replace function public.enforce_message_rate_limit()
returns trigger
language plpgsql
security definer
set search_path = ''
as $$
declare
  uid uuid := (select auth.uid());
  recent_short integer;
  recent_minute integer;
begin
  if uid is null then return new; end if;
  perform pg_catalog.pg_advisory_xact_lock(pg_catalog.hashtextextended(uid::text, 0));

  select count(*) into recent_short
  from public.room_messages
  where sender_id = uid and created_at > now() - interval '10 seconds';

  if recent_short >= 5 then
    raise exception using errcode = 'P0001', message = 'MESSAGE_RATE_LIMIT_10S';
  end if;

  select count(*) into recent_minute
  from public.room_messages
  where sender_id = uid and created_at > now() - interval '1 minute';

  if recent_minute >= 30 then
    raise exception using errcode = 'P0001', message = 'MESSAGE_RATE_LIMIT_1M';
  end if;
  return new;
end;
$$;

create or replace function public.notify_buddy_request_push()
returns trigger
language plpgsql
security definer
set search_path = ''
as $$
begin
  perform net.http_post(
    url := 'https://hrjgblvxhtbopuyzyasu.supabase.co/functions/v1/send-push',
    body := jsonb_build_object(
      'type','INSERT','table','buddy_requests','schema','public',
      'record',jsonb_build_object(
        'id',new.id,'sender',new.requester_handle,'recipient',new.recipient_handle,
        'body',new.requester_handle || ' sent you a buddy request','created_at',new.created_at
      ),
      'old_record',null
    ),
    headers := '{"Content-Type":"application/json"}'::jsonb,
    timeout_milliseconds := 1000
  );
  return new;
end;
$$;

create or replace function public.notify_direct_message_push()
returns trigger
language plpgsql
security definer
set search_path = ''
as $$
begin
  perform net.http_post(
    url := 'https://hrjgblvxhtbopuyzyasu.supabase.co/functions/v1/send-push',
    body := jsonb_build_object(
      'type','INSERT','table','direct_messages','schema','public',
      'record',to_jsonb(new),'old_record',null
    ),
    headers := '{"Content-Type":"application/json"}'::jsonb,
    timeout_milliseconds := 1000
  );
  return new;
end;
$$;

create or replace function public.notify_room_invitation_push()
returns trigger
language plpgsql
security definer
set search_path = ''
as $$
begin
  perform net.http_post(
    url := 'https://hrjgblvxhtbopuyzyasu.supabase.co/functions/v1/send-push',
    body := jsonb_build_object(
      'type','INSERT','table','room_invitations','schema','public',
      'record',to_jsonb(new),'old_record',null
    ),
    headers := '{"Content-Type":"application/json"}'::jsonb,
    timeout_milliseconds := 1000
  );
  return new;
end;
$$;

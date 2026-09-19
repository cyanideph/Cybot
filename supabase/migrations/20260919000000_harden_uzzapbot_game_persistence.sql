alter table public.game_sessions
  add column if not exists state_json jsonb not null default '{}'::jsonb;

create or replace function public.uzzapbot_save_game_state(p_state jsonb)
returns bigint
language plpgsql
security definer
set search_path to ''
as $function$
declare
  v_room text;
  v_id bigint;
  v_player jsonb;
begin
  if p_state is null or jsonb_typeof(p_state) <> 'object' then
    raise exception 'Invalid game state';
  end if;

  v_room := nullif(trim(p_state->>'room'), '');
  if v_room is null then
    raise exception 'Game state room is required';
  end if;

  select id into v_id
  from public.game_sessions
  where room_name = v_room
  order by id
  limit 1
  for update;

  if v_id is null then
    insert into public.game_sessions (
      room_name, game, mode, current_game, points, limit_count, endless,
      paused, question_number, question, answer, clue_text, used_questions, state_json
    )
    values (
      v_room,
      coalesce(nullif(p_state->>'game',''),'math'),
      coalesce(nullif(p_state->>'mode',''), coalesce(nullif(p_state->>'game',''),'math')),
      coalesce(nullif(p_state->>'current_game',''), coalesce(nullif(p_state->>'game',''),'math')),
      coalesce((p_state->>'points')::integer,10),
      coalesce((p_state->>'limit')::integer,100),
      coalesce((p_state->>'endless')::boolean,false),
      coalesce((p_state->>'paused')::boolean,false),
      coalesce((p_state->>'number')::integer,0),
      coalesce(p_state->>'question',''),
      coalesce(p_state->>'answer',''),
      coalesce(p_state->>'clue_text',''),
      coalesce(p_state->'used_questions','[]'::jsonb),
      p_state
    )
    returning id into v_id;
  else
    update public.game_sessions
    set
      game = coalesce(nullif(p_state->>'game',''),'math'),
      mode = coalesce(nullif(p_state->>'mode',''), coalesce(nullif(p_state->>'game',''),'math')),
      current_game = coalesce(nullif(p_state->>'current_game',''), coalesce(nullif(p_state->>'game',''),'math')),
      points = coalesce((p_state->>'points')::integer,10),
      limit_count = coalesce((p_state->>'limit')::integer,100),
      endless = coalesce((p_state->>'endless')::boolean,false),
      paused = coalesce((p_state->>'paused')::boolean,false),
      question_number = coalesce((p_state->>'number')::integer,0),
      question = coalesce(p_state->>'question',''),
      answer = coalesce(p_state->>'answer',''),
      clue_text = coalesce(p_state->>'clue_text',''),
      used_questions = coalesce(p_state->'used_questions','[]'::jsonb),
      state_json = p_state,
      updated_at = now()
    where id = v_id;
  end if;

  delete from public.game_players where session_id = v_id;

  if jsonb_typeof(coalesce(p_state->'players','[]'::jsonb)) = 'array' then
    for v_player in select value from jsonb_array_elements(p_state->'players')
    loop
      insert into public.game_players (
        session_id, user_id, username, nickname, score, correct, attempts
      )
      values (
        v_id,
        nullif(v_player->>'user_id','')::uuid,
        coalesce(v_player->>'username',''),
        coalesce(v_player->>'nickname',''),
        coalesce((v_player->>'score')::integer,0),
        coalesce((v_player->>'correct')::integer,0),
        coalesce((v_player->>'attempts')::integer,0)
      );
    end loop;
  end if;

  return v_id;
end;
$function$;

revoke execute on function public.uzzapbot_save_game_state(jsonb) from anon, authenticated, public;
grant execute on function public.uzzapbot_save_game_state(jsonb) to service_role;

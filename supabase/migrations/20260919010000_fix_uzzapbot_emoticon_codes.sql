-- Return the legacy Uzzap emoticon text codes so Android's existing
-- emoticon parser can render the actual picker images. Do not return
-- internal asset names such as [emoticon-19].
create or replace function public.uzzapbot_random_emoticon()
returns text
language sql
set search_path to 'public', 'pg_temp'
as $function$
  select (array[
    ':)',
    ';)',
    ':(',
    ':D',
    ':e',
    '(:)',
    '>|',
    ':o',
    ':>',
    '>(|',
    ':DD',
    'o/',
    ':Oo',
    '>,',
    ':|',
    ':B,',
    ':OOo',
    ':Zz.',
    'O:)',
    '))(',
    '>><)',
    '<:D',
    '(cU)',
    '<:)',
    '(+)',
    ':-)',
    ':-(',
    '@};-'
  ])[floor(random() * 28)::int + 1];
$function$;

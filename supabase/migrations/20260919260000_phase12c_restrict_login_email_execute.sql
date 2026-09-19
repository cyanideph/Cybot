-- Phase 12C: prevent unauthenticated email enumeration through the username-login helper.
-- Keep authenticated execution for compatibility with the existing login flow.
revoke execute on function public.resolve_login_email(text) from anon;
grant execute on function public.resolve_login_email(text) to authenticated;

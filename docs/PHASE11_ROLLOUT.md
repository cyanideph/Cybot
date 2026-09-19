# Phase 11 — Production Readiness / Controlled Rollout

Phase 11 completes the AI safety lifecycle by defining a deterministic rollout gate.

## Rollout stages

1. **disabled** — default and emergency rollback state.
2. **dry_run** — evaluation-only; no user-facing AI action.
3. **canary** — explicitly gated, limited to 1–10% when all security gates pass.
4. **live** — requires global AI enablement, explicit live enablement, and dry-run disabled.

The Phase 11 gate is evaluation-only. It does not change runtime configuration, call Gemini, write to Supabase, send messages, or automatically enable AI.

## Production gate

A rollout is ready only when:
- the requested stage is valid;
- Phase 10 security validation passes;
- global AI enablement is explicitly present for canary/live;
- live mode has explicit live enablement;
- dry-run is disabled for canary/live;
- canary percentage is within the 1–10% bound.

Any invalid or incomplete configuration fails closed.

## Rollback

The emergency target is always **disabled**. Rollback must not delete Supabase data. The operator sets the rollout stage to disabled and restarts the bot.

## Operational rule

Merging Phase 11 does **not** activate AI. Production activation remains an explicit operational decision after deployment verification.

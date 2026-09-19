# Cybot / UzzapBot

UzzapBot is the Python game and room-assistant bot used with the Uzzap Android application.

It connects to Supabase, watches Uzzap room messages, handles game commands and gameplay, persists active game state, and sends bot responses back to Uzzap rooms.

## Features
- Uzzap room message polling
- Player join/leave tracking
- Multiple game modes
- Random game cycles
- Progressive clues
- Score and leaderboard tracking
- Game pause/resume/stop controls
- Admin-only room controls
- Welcome-bot support
- Challenge/mirror room support
- Randomized bot replies
- Legacy Uzzap emoticon codes
- Persistent game state through Supabase
- Message claiming support for multiple bot workers

## Repository layout

    Cybot/
    ├── UzzapBot/
    │   ├── bot.py
    │   ├── game_engine.py
    │   ├── database.py
    │   ├── config.py
    │   ├── requirements.txt
    │   └── tests
    └── supabase/
        └── migrations/

## Architecture

    Uzzap Android
         │
         ▼
    Supabase room_messages
         │
         ▼
    UzzapBot / database.py
         │
         ├── command handling
         ├── message claiming
         └── Supabase RPCs
         │
         ▼
    GameEngine
         │
         ├── questions
         ├── answers
         ├── clues
         ├── scores
         └── game cycles
         │
         ▼
    Supabase persistence

## Requirements
- Python 3.10+
- A Supabase project used by Uzzap
- Supabase Python client
- A server-side Supabase service-role key
- A configured bot sender UUID

Install dependencies:

    cd UzzapBot
    python -m pip install -r requirements.txt

## Configuration
Create UzzapBot/.env from .env.example:

    SUPABASE_URL=https://YOUR_PROJECT_REF.supabase.co
    SUPABASE_SERVICE_ROLE_KEY=YOUR_SUPABASE_SERVICE_ROLE_KEY
    BOT_NAME=uzzapbot
    BOT_SENDER_ID=YOUR_BOT_UUID
    ADMIN_IDS=YOUR_ADMIN_UUID
    POLL_SECONDS=1.0
    DEFAULT_POINTS=10
    DEFAULT_LIMIT=100

### Security
Never commit .env or a Supabase service-role key.
The service-role key is intended for the bot's server-side/Pydroid environment only. It must not be placed in the Android application, APK, README, GitHub Actions logs, or other client-side code.
Admin authorization is based on Supabase Auth user IDs, not usernames.

## Running the bot
From the UzzapBot directory:

    python bot.py

The bot restores persisted game sessions when it starts and then polls for new Uzzap room activity.

## Player commands
    /HELP
    /JOIN
    /LEAVE
    /PLAYERS
    /CLUE
    /REPOST
    /STATUS
    /SCORE
    /LEADERBOARD
    /VERSION
    /TT ON
    /MATH ON
    /TRIVIA ON
    /ANIME ON
    /LOGIC ON
    /ALGEBRA ON
    /PH ON
    /RANDOM QUIZ1
    /RANDOM QUIZ2
    /RANDOM QUIZ3
    /RANDOM GTA
    /GTA OPM
    /GTA FOREIGN
    /ENGLISH WORDHUNT
    /TAGALOG WORDHUNT

## Admin commands
    /STOP
    /PAUSE
    /RESUME
    /NEXT
    /REVEAL
    /ACTIVATE
    /LOCK
    /UNLOCK
    /WCBOT ON
    /WCBOT OFF
    /WMSG <message>
    /CHALLENGE <room>
    /CHALLENGE OFF

Only configured Supabase Auth user IDs in ADMIN_IDS can execute admin commands.

## Emoticons
The bot returns legacy Uzzap text emoticon codes rather than Android asset names. Android remains responsible for converting those codes into the appropriate picker images.
This keeps bot logic independent from Android resource filenames.

## Persistence
Active games can be persisted in Supabase and restored after a bot restart.
The persistence state includes the active room, game mode, question state, clue state, used questions, game cycles, reply history, and player scores.
Database migrations live under supabase/migrations/.

## Testing
    cd UzzapBot
    pytest

The tests cover command parsing, admin authorization, game modes, clues, answer matching, game cycles, persistence, and reply rotation.

## Important notes
Cybot is designed around the existing Uzzap database schema and Android client. Do not change bot message formatting, command names, Supabase RPC contracts, or emoticon codes without checking Android client compatibility.
For production deployment, keep the bot on a trusted server or controlled runtime and keep all server-side credentials outside the repository.

## License
This project is licensed under the MIT License. See LICENSE.
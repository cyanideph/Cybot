"""Supabase adapter used by the Pydroid bot."""
from __future__ import annotations
import logging
from typing import Any
from supabase import create_client
from config import SUPABASE_URL, SUPABASE_KEY, BOT_SENDER_ID, BOT_NAME

log = logging.getLogger("uzzapbot.database")

class Database:
    def __init__(self) -> None:
        self.client = create_client(SUPABASE_URL, SUPABASE_KEY)
        self.last_id = self._latest_id()
        log.info("Polling starts after room_messages id=%s", self.last_id)

    def _latest_id(self) -> int:
        r=self.client.table("room_messages").select("id").order("id",desc=True).limit(1).execute()
        rows=r.data or []
        return int(rows[0]["id"]) if rows else 0

    def poll_messages(self) -> list[dict[str,Any]]:
        r=(self.client.table("room_messages").select("id,room_name,sender,body,is_system,created_at,sender_id")
           .gt("id",self.last_id).order("id").limit(100).execute())
        rows=r.data or []
        if rows: self.last_id=max(int(x["id"]) for x in rows)
        result=[]
        for x in rows:
            sender=str(x.get("sender") or "")
            if str(x.get("sender_id") or "")==BOT_SENDER_ID or sender.casefold()==BOT_NAME.casefold(): continue
            result.append(x)
        return result

    def send(self,room_name:str,body:str)->None:
        log.info('SEND room="%s" body=%r',room_name,body)
        self.client.table("room_messages").insert({
            "room_name":room_name,"sender":BOT_NAME,"body":body,
            "is_system":True,"sender_id":BOT_SENDER_ID}).execute()

    def profile(self,user_id:str|None,username:str|None)->dict[str,Any]|None:
        if user_id:
            r=self.client.table("profiles").select("id,username,nickname").eq("id",user_id).limit(1).execute()
            if r.data:return r.data[0]
        if username:
            r=self.client.table("profiles").select("id,username,nickname").eq("username",username).limit(1).execute()
            if r.data:return r.data[0]
        return None

    def load_game_state(self)->list[dict[str,Any]]:
        sessions=self.client.table("game_sessions").select(
            "id,room_name,game,mode,current_game,points,limit_count,endless,paused,question_number,question,answer,clue_text,used_questions"
        ).order("id").execute().data or []
        if not sessions:return []
        players=self.client.table("game_players").select(
            "session_id,user_id,username,nickname,score,correct,attempts"
        ).order("id").execute().data or []
        by_session={}
        for p in players: by_session.setdefault(int(p["session_id"]),[]).append(p)
        for s in sessions:
            s["players"]=by_session.get(int(s["id"]),[])
        return sessions

    def save_game_state(self,state:dict[str,Any])->int:
        payload={
            "room_name":state["room"],"game":state["game"],"mode":state.get("mode") or state["game"],"current_game":state.get("current_game") or state["game"],
            "points":int(state["points"]),"limit_count":int(state["limit"]),
            "endless":bool(state.get("endless")),"paused":bool(state["paused"]),
            "question_number":int(state["number"]),"question":state["question"],
            "answer":state["answer"],"clue_text":state.get("clue_text",""),
            "used_questions":list(state.get("used_questions",[]))}
        existing=self.client.table("game_sessions").select("id").eq("room_name",state["room"]).limit(1).execute().data or []
        if existing:
            sid=int(existing[0]["id"])
            self.client.table("game_sessions").update(payload).eq("id",sid).execute()
        else:
            sid=int(self.client.table("game_sessions").insert(payload).execute().data[0]["id"])
        self.client.table("game_players").delete().eq("session_id",sid).execute()
        rows=[]
        for p in state.get("players",[]):
            rows.append({"session_id":sid,"user_id":p.get("user_id") or None,
                         "username":p["username"],"nickname":p["nickname"],
                         "score":int(p["score"]),"correct":int(p["correct"]),"attempts":int(p["attempts"])})
        if rows:self.client.table("game_players").insert(rows).execute()
        return sid

    def delete_game_state(self,room:str)->None:
        self.client.table("game_sessions").delete().eq("room_name",room).execute()

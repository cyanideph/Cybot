# READABLE DEOBFUSCATED COPY — GAME CORE 4.5
#
# Source: Oldbot/ slowGameCoreV4.py
# This file is a readability refactor of the historical Symbian/S60 game core.
# The original file is intentionally left unchanged as the reference implementation.
#
# Stage 1 rules:
# - Preserve the original game/protocol behavior as closely as possible.
# - Rename cryptic function names to descriptive names.
# - Do NOT modernize the networking, UI, or database layer yet.
# - Do NOT remove historical code merely because it looks unused.
# - Known Python-2/Symbian compatibility issues are documented later rather than
#   silently changed, so behavior can be compared with the original.
#
# Major state variables:
#   roombot      = current room
#   challenge    = challenge/secondary room
#   word1/word2  = current question/answer state used by the original core
#   clue         = current clue text
#   p            = player-name list
#   ps           = player-score list
#   postcount    = outgoing message counter
#   wcbot1       = welcome-bot switch
#   lockbotroom  = room lock state
#   twistswitch  = twist-mode switch
#
import appuifw
import e32
import socket
import globalui
import re
import random
import base64
import os
import sysinfo
import audio

# ---------------------------------------------------------------------------
# LEGACY GAME STATE
# ---------------------------------------------------------------------------
# These names are retained for now because they are shared by many routines.
# Readability mapping:
#   roombot       current game room
#   challenge     secondary/challenge room
#   word1/word2   current question/answer-related state
#   clue          current clue text
#   p / ps        parallel player-name / player-score lists
#   postcount     number of outbound posts since the last keepalive
#   wcbot1        welcome-bot switch
#   lockbotroom   room-lock state
#   invadeon      invasion mode switch
#   twistswitch   twist mode switch
#   louiselock    legacy game lock state
#   marklouise*   historical game generators (renamed below)
#   marky* / ub*  generated protocol/message identifiers
#   gmcount/gm2..gm7 legacy game counters/state slots
#
# ---------------------------------------------------------------------------
# KNOWN LEGACY ISSUES — DOCUMENTED, NOT FIXED IN STAGE 1
# ---------------------------------------------------------------------------
# 1. Several functions contain global declarations after references or
#    assignments to the same name. Modern Python requires the declaration to
#    precede those uses in the function body.
# 2. The source targets Symbian/Python-2-era APIs.
# 3. Some names are reused for different purposes.
# 4. Some file-handle close calls appear to reference the wrong variable.
# 5. Socket/XML code targets the historical Uzzap/Kolipri service.
#
# These are deliberately documented rather than silently corrected.
# See Python scope rules in the official documentation.

l = '####################'
l = 'Please do not remove this script if you want to edit this program.'
l = 'You must give credits for their works.'
l = 'This are the people who contributed for the game! E.G. Trivia Questionnaires, GTA, REBUS, ETC...'
l = '~~~~~~~~~~~~~~~~~~~~~~~~'
special = ('+MSTR|+PIECE+', 'VENOM|Chiz', 'TRiBaL.oNe', 'PARK|"YUIE', '}PARK{"GHABZ', 'Kickbutt', 'MSTR.C', 'Pistol', '+PH+ZOIDZ', '</dadahush>', '[N]E+AKARI', 'B6|YAM')
special_thanks_name = random.choice(special)
l = '~~~~~~~~~~~~~~~~~~~~~~~~'
l = 'If you want to contribute for this program, you can send to us Trivia Questionnaires, GTA, Rebus, ETC.'
l = 'You can send it via MMS to 09194015811'
l = 'Or, via Facebook or Email: ravemark@yahoo.com'
l = 'Don`t forget to include your name, so that I can put your name in the CREDITS LIST'
l = 'Best Regards to all'
l = '####################'
marklock = 0
faces = ('[#/1 ', '[#/1 ', '[#/1 ', '[#/2 ', '[#/3 ', '[#/4 ', '[#/4 ', '[#/4 ', '[#/5 ', '[#/6 ', '[#/4 ', '[#/7 ', '[#/8 ', '[#/9 ', '[#/0 ')
spybotroom = ''
def repost_question_with_clue():
    marky = xmlmark.replace('#ROOM#', roombot)
    louisey = marky.replace('#ROOMx#', challenge)
    xmllouise = louisey.replace('#ID#', str(random.randint(1, 999)))
    markyx = xmllouise.replace('#IDx#', str(random.randint(1, 999)))
    ttq = ('[567 TT=> [900 ' + word2 + '\n[567 HiNT: [0C0 ' + clue)
    post3 = markyx.replace('#MESS#', ttq)
    post2 = post3.replace('#MESSx#', ttq)
    postcount = (postcount + 1)
    s1.send(post2)
    if postcount >= 6 : 
        send_keepalive_if_needed()
    global postcount


RieTanaka = u'e:\\Python\\Shizuka na Yoru ni C.E. 73.mp3'
Naruto = u'e:\\Python\\Heros Come Back.mp3'
Bloodplus = u'e:\\Python\\Aozora no Namida.mp3'
FullMetalPanic = u'e:\\Python\\Minami Kaze.mp3'
ShakuganNoShana = u'e:\\Python\\Blaze.mp3'
musicitems = (RieTanaka, Naruto, Bloodplus, FullMetalPanic, ShakuganNoShana)
music = random.choice(musicitems)
antimark = ''
GAME_TITLE = 'GAME CORE 4.5'
APP_TITLE = GAME_TITLE
LEGACY_DATA_PATH = u'e:\\Python\\'
ENGLISH_WORD_FILE = u'e:\\Python\\words.txt'
english_word_file = open(ENGLISH_WORD_FILE, 'r')
english_words = english_word_file.read().split('\n')
english_word_file.close()
TAGALOG_WORD_FILE = u'e:\\Python\\salita.txt'
tagalog_word_file = open(TAGALOG_WORD_FILE, 'r')
tagalog_words = tagalog_word_file.read().split('\n')
english_word_file.close()
challengelouise = 'off'
def get_english_word(string):
    return english_words[string]


def get_tagalog_word(string):
    return tagalog_words[string]


markxxxxlouise = ''
random1 = ('generate_algebra_1', 'generate_algebra_2', 'generate_algebra_3', 'add', 'minus', 'multiply', 'add1', 'minus1', 'multiply1', 'filipino', 'filipino', 'filipino', 'filipino', 'love', 'love', 'love', 'love', 'SummonNight', 'SummonNight', 'SummonNight', 'SummonNight', 'SummonNight2', 'SummonNight2', 'SummonNight2', 'SummonNight2')
random2 = ('generate_algebra_1', 'generate_algebra_2', 'generate_algebra_3', 'add', 'minus', 'multiply', 'add1', 'minus1', 'multiply1', 'filipino', 'filipino', 'filipino', 'love', 'love', 'love', 'SummonNight', 'SummonNight', 'SummonNight', 'SummonNight2', 'SummonNight2', 'SummonNight2', 'generate_trivia_question', 'generate_trivia_question', 'generate_trivia_question', 'generate_trivia_question', 'generate_trivia_question', 'generate_trivia_question', 'generate_trivia_question', 'generate_gta_opm_question', 'generate_gta_opm_question', 'generate_gta_opm_question', 'generate_gta_opm_question', 'generate_gta_foreign_question', 'generate_gta_foreign_question', 'generate_gta_foreign_question', 'generate_gta_foreign_question')

random3 = ('generate_algebra_1', 'generate_algebra_2', 'generate_algebra_3', 'add', 'minus', 'multiply', 'add1', 'minus1', 'multiply1', 'filipino', 'filipino', 'filipino', 'love', 'love', 'love', 'SummonNight', 'SummonNight', 'SummonNight', 'SummonNight2', 'SummonNight2', 'SummonNight2', 'generate_trivia_question', 'generate_trivia_question', 'generate_trivia_question', 'generate_trivia_question', 'generate_trivia_question', 'generate_trivia_question', 'generate_trivia_question', 'generate_gta_opm_question', 'generate_gta_opm_question', 'generate_gta_opm_question', 'generate_gta_opm_question', 'generate_gta_foreign_question', 'generate_gta_foreign_question', 'generate_gta_foreign_question', 'generate_gta_foreign_question', 'generate_logic_question', 'generate_logic_question', 'generate_logic_question', 'anime', 'anime', 'anime')

randomgta = ('generate_gta_foreign_question', 'generate_gta_opm_question')

mathx = ('add', 'minus', 'multiply', 'add1', 'minus1', 'multiply1')
GAME_TITLE = 'GAME CORE 4.5'
appuifw.app.screen = 'normal'
round = appuifw.Text()
appuifw.app.body = round
appuifw.app.APP_TITLE = (u'' + GAME_TITLE + '')
round.color = 405
round.font = (u'LatinBold12', 20, None)
round.color = 16711680
round.add(u'\n\nThis application is dedicated for the benefit of the UzZap community!')
round.color = 0
e32.ao_sleep(0.01)
try :
    GundamSeed = audio.Sound.open(music)
    GundamSeed.play()
except :
    pass
round.add(u'\n\n\n     UzZAP\n')
round.font = (u'LatinBold12', 35, None)
round.add(u'  G')
e32.ao_sleep(0.5)
round.add(u'a')
e32.ao_sleep(0.5)
round.add(u'm')
e32.ao_sleep(0.5)
round.add(u'e ')
e32.ao_sleep(0.5)
round.add(u'C')
e32.ao_sleep(0.5)
round.add(u'o')
e32.ao_sleep(0.5)
round.add(u'r')
e32.ao_sleep(0.5)
round.add(u'e\n')
e32.ao_sleep(2.3)
round.font = (u'LatinBold12', 12, None)
round.add(u'   Multi Room + GAME CORE 4.5 +\n - Math,TT,WH,GTA,TRIVIA,Logic\n + now  With Algebra! -\nrandom\n')
round.font = (u'LatinBold12', 14, None)
round.color = 405
round.add((u' Special Thanks to: ' + show_special_thanks))
round.font = (u'LatinBold12', 12, None)
round.color = 0
round.add(u'\n\nNext Program Update:\n=> Physics\n=> More Questionnaires!\n=> New Games! (coming soon)\nVisit http://gundam.wapgem.com\nfor more updates.')
round.color = 105
regidit = 'no'
def exit_application():
    exitapp = appuifw.query(u'Exit application?', 'query')
    if exitapp == 1 : 
        globalui.global_note((u'Goodbye ' + 'Master!' + '\n=>' + masternick))
        appuifw.app.set_exit()


rooms = ['Flirt 146', 'ANIME', 'One Piece', 'Kapamilya', 'Naruto']
key = 'key'
if key == 'key' : 
    round.add(u'\nGAME RuNtime is 24/7')
louiselock = 'lock'
ub1 = random.randint(1, 99)
ub = str(ub1)
ip = random.randint(9, 20)
host1 = ('203.84.163.' + str(ip))
port1 = 25
s1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
last_number = []
emoticons = (';)', '(+)', ':(', ':D', ':e', '(:)', ':o', ':DD', 'o/', ':Oo', ':|', ':B,', ':OOo', ':Zz.', 'O:)', '))(', ':)', '@};-')
faces = ('[#/1 ', '[#/1 ', '[#/1 ', '[#/2 ', '[#/3 ', '[#/4 ', '[#/4 ', '[#/4 ', '[#/5 ', '[#/6 ', '[#/4 ', '[#/7 ', '[#/8 ', '[#/9 ', '[#/0 ')
marky9 = random.randint(0, 9999)
marky8 = random.randint(99999, 99999)
xmlpost = (('<iq type="get" id="CSTCR_3' + str(marky9)) + str(marky8) + '_7#ID#" to="conference@demo.kolipri.com/amazilia" amaz-protocol="chat"><msg room="#ROOM#" type="groupchat"><![CDATA[#MESS#]]></msg></iq>')
xmlmark = (((('<iq type="get" id="CSTCR_4' + str(marky9)) + str(marky8) + '_8#ID#" to="conference@demo.kolipri.com/amazilia" amaz-protocol="chat"><msg room="#ROOM#" type="groupchat"><![CDATA[#MESS#]]></msg></iq><iq type="get" id="CSTCR_5') + str(marky9)) + str(marky8) + '_9#IDx#" to="conference@demo.kolipri.com/amazilia" amaz-protocol="chat"><msg room="#ROOMx#" type="groupchat"><![CDATA[#MESSx#]]></msg></iq>')
gmnick = 'ame`^{=^_^=}^`athrun'
levjoin = '<iq type="get" id="LCR_1275557645_12" to="conference@demo.kolipri.com/amazilia" amaz-protocol="chat"><chatuser room="#ROOM#" type="unavailable" /></iq><iq type="get" id="wxyz_98" to="conference@demo.kolipri.com/amazilia" amaz-protocol="chat"><chatuser room="#ROOM#" nick="#NICK#" /></iq>'
leavelouise = '<iq type="get" id="LCR_1275557645_12" to="conference@demo.kolipri.com/amazilia" amaz-protocol="chat"><chatuser room="#ROOM#" type="unavailable" /></iq><iq type="get" id="wxyz_98" to="conference@demo.kolipri.com/amazilia" amaz-protocol="chat"><chatuser room="#ROOM#" nick="#NICK#" /></iq><iq type="get" id="LCR_1275557645_12" to="conference@demo.kolipri.com/amazilia" amaz-protocol="chat"><chatuser room="#ROOMx#" type="unavailable" /></iq><iq type="get" id="wxyz_98" to="conference@demo.kolipri.com/amazilia" amaz-protocol="chat"><chatuser room="#ROOMx#" nick="#NICKx#" /></iq>'
stoppost = '] '
stopplad = 'no'
last = 'GameCore 4.5'
markloua = ''
markloub = ''
marklouc = ''
markloud = ''
markloue = ''
marklouf = ''
markloug = ''
marklouh = ''
markloui = ''
marklouj = ''
marklouk = ''
markloul = ''
markloum = ''
markloun = ''
marklouo = ''
markloup = ''
marklouq = ''
marklour = ''
marklous = ''
marklout = ''
marklouu = ''
marklouv = ''
marklouw = ''
markloux = ''
marklouy = ''
marklouz = ''
roombot = ''
lastdetermine = ''
mirrors = 'no'
masternick = '>'
wcmeseg = '-rc1-WELCOME -rc2--re-'
postcount = 0
lastpost = '[834 Systems LOCK!!! '
NICKNAME = 'GAME CORE 4'
wcbot1 = 'off'
lockbotroom = ''
invadeon = 'no'
clue = ''
passx = 'yeah'
word2x = ''
newroom = ''
word1 = 'Mark Louise'
twistswitch = 'off'
p = []
ps = []
lastroom = ''
challenge = ''
name = 'GameCore 4.5'
gmcount = 0
gm2 = ''
gm3 = ''
gm4 = ''
gm5 = ''
gm6 = ''
gm7 = ''
tekert1 = '<iq type="get" id="CITCR_#ID#" to="" amaz-protocol="chat"><invite room="#ID#"><![CDATA[]]></invite></iq>'
tekert2 = tekert1.replace('#ID#', str(random.randint(1, 9999)))
jid = ''
password = ''

# ===========================================================================
# LOGIN / SESSION
# ===========================================================================
def login_to_uzzap():
    if key == 'key' : 
        account = appuifw.multi_query(u'LOGIN UZZAP ID\n(small letters only):', u'Password:')
        jid, password = account
        round.add((u'\n>> You are logging in as  ' + jid))
        encrypt1 = base64.encodestring(((chr(0) + jid) + chr(0) + password))
        loginxml = '<auth xmlns="urn:ietf:params:xml:ns:xmpp-sasl" mechanism="PLAIN">'
        spacket1 = '<stream:stream to="demo.kolipri.com" version="1.0" xmlns:stream="http://etherx.jabber.org/streams" xmlns="jabber:client" client-version="uzzap_cpp_win32_1.0.17" roster-limit="-1">'
        spacket2 = (loginxml + encrypt1 + '</auth>')
        spacket3 = '<stream:stream to="demo.kolipri.com" version="1.0" xmlns:stream="http://etherx.jabber.org/streams" xmlns="jabber:client" client-version="uzzap_cpp_win32_1.0.17" roster-limit="-1">'
        spacket4 = '<iq type="set" id="0"><bind xmlns="urn:ietf:params:xml:ns:xmpp-bind"><resource>Kolipri</resource></bind></iq><iq type="set" id="1"><session xmlns="urn:ietf:params:xml:ns:xmpp-session"/></iq>'
        s1.connect((host1, port1))
        s1.send(spacket1)
        round.add(u'\n>> Connecting......\n')
        rpacket1 = s1.recv(1024)
        s1.send(spacket2)
        round.add(u'>> Authenticating.....\n')
        rpacket2 = s1.recv(1024)
        error1 = rpacket2.find('invalid-credentials')
        if error1 > 1 : 
            round.add(u'\n>> INVALID ACCOUNT!!!!\n')
        else : 
            s1.send(spacket3)
            rpacket3 = s1.recv(1024)
            s1.send(spacket4)
            round.add(u'>> Initializing.....\n')
            rpacket4 = s1.recv(1024)
            round.add(u'>> YOU ARE NOW ONLINE!!!\n\n')
            appuifw.app.menu = menu2
            tekert2 = tekert1.replace('#ID#', str(random.randint(1, 9999)))
            tekert3 = tekert2.replace('#JID#', (word1 + ' ' + word1))
            s1.send(tekert3)
            rpackets2 = s1.recv(1024)
        pass
    global jid, password



# ===========================================================================
# ROOM MANAGEMENT / MESSAGING
# ===========================================================================
def join_room():
    names = appuifw.multi_query(u'Room Name:\n(e.g. Gamers 32)', u'Nickname: \n(MAX of 12 characters)')
    first, last = names
    levjoin = '<iq type="get" id="LCR_1275557645_12" to="conference@demo.kolipri.com/amazilia" amaz-protocol="chat"><chatuser room="#ROOM#" type="unavailable" /></iq><iq type="get" id="******_9" to="conference@demo.kolipri.com/amazilia" amaz-protocol="chat"><chatuser room="#ROOM#" nick="#NICK#" /></iq>'
    lastdetermine = last
    roombot = first
    if len(lastdetermine) > 12 : 
        round.add(u'\n\n>> ERROR!!! NICKNAME IS TOO LONG!\n      + PLEASE TRY AGAIN!!! +')
        lastdetermine = 'GameCore 4.5'
    levjoin1a = levjoin.replace('#ROOM#', first)
    levjoin1b = levjoin1a.replace('#NICK#', lastdetermine)
    s1.send(levjoin1b)
    last = lastdetermine
    rpacket2 = s1.recv(1024)
    error1 = rpacket2.find('not-authorized')
    if error1 > 1 : 
        round.add(u'\n>> YOUR ID IS BANNED! :-(\n')
        appuifw.app.menu = menu1
    elif rpacket2.find('error') > 1 : 
        round.add(u'\n>> ROOM IS FULL! please try again...\n')
    else : 
        round.add((u'\n++  BASIC COMMANDS:  ++\nACTIVATE\nRANDOM QUIZ1 = Math,TT,WH\nRANDOM QUIZ2 =  with Trivia&GTA\nRANDOM QUIZ3 = all in one!\nTRIVIA ON\nGAME OFF\n=> Please check "HELP" for more info.\n\n>> You have Joined ' + first + ' as:\n >>>   ' + lastdetermine + '   <<<\n'))
        activate_game_session()
    global last, lastdetermine, roombot


mark = ''
def leave_room():
    rn = appuifw.query(u'Enter room name', 'text')
    round.add((u'>> You have leave ' + rn + '....\n'))
    xmleave1 = '<iq type="get" id="CSTCR_1286518673_98" to="conference@demo.kolipri.com/amazilia" amaz-protocol="chat">'
    xmleave2 = "<chatuser room='"
    xmleave4 = '\' type="unavailable" /></iq>'
    lroom = (xmleave1 + xmleave2 + rn + xmleave4)
    s1.send(lroom)
    xmlsr = s1.recv(1024)


def post_message_prompt():
    names = appuifw.multi_query(u'Room Name:', u'Your Message')
    first, last = names
    xmlpost = '<iq type="get" id="CSTCR_1275557642_#ID#" to="conference@demo.kolipri.com/amazilia" amaz-protocol="chat"><msg room="#ROOM#" type="groupchat"><![CDATA[#MESS#]]></msg></iq>'
    str2 = xmlpost.replace('#ID#', ub)
    str2 = str2.replace('#ROOM#', first)
    str2 = str2.replace('#MESS#', last)
    s1.send(str2)
    xmlsr = s1.recv(1024)
    if xmlsr > 1023 : 
        round.add((u'>> Message Posted! = ' + last + '....\n'))
    else : 
        round.add(u'>> Message Post Failed..\n')


louise = ''
def change_nickname():
    last = appuifw.query(u'MaiN Nickname \n(MAX 12 characters)', 'text')
    lastdetermine = last
    if len(last) > 12 : 
        round.add(u'\n\n>> ERROR!!! NICKNAME IS TOO LONG!\n      + PLEASE TRY AGAIN!!! +\n')
        last = 'GameCore 4.5'
    else : 
        round.add((u'\n>> Your Main NickName is: ' + last))
    global last, lastdetermine


def receive_packets():
    round.add(u'\n\n>> PACKETS SUCCESSFULLY IN')
    stopplad = 'no'
    rn = roombot
    countpost1 = 0
    garbagecollection = s1.recv(1024)
    if  not os.LEGACY_DATA_PATH.exists(u'e:\\Python\\summonnight.pyc') : 
        os.abort()
    while True : 
        data = s1.recv(1024)
        xmlpost1 = xmlpost.replace('#ROOM#', rn)
        post1 = xmlpost1.replace('#ID#', str(random.randint(1, 999)))
        if postcount >= 6 : 
            send_keepalive_if_needed()
        elif data.find("<msg type='groupchat'") > 1 and data.find(lastdetermine) < 1 : 
            Cmess = send_group_message(data)
            Cfrom = parse_message_sender(data)

            if Cmess.upper().find(louisemark) >= 0 and twistswitch == 'on' or Cmess.lower().find(word1) >= 0 and twistswitch == 'on' : 
                if Cfrom == last or Cfrom == name or Cfrom == "type='groupchat" or Cfrom == '' : 
                    passx = 'yeah'
                else : 
                    add_player_if_missing(Cfrom)
                    faces2 = random.choice(faces)
                    for i in range(len(p)):
                        if p[i] == Cfrom : 
                            ps[i] = (ps[i] + louisescore)
                            marky = xmlmark.replace('#ROOM#', roombot)
                            louisey = marky.replace('#ROOMx#', challenge)
                            xmllouise = louisey.replace('#ID#', str(random.randint(1, 999)))
                            louisescore = 10
                            markyx = xmllouise.replace('#IDx#', str(random.randint(1, 999)))
                            markmark = (('' + Cfrom + '   |SCORE: ') + str(ps[i]) + '|\n got it!!!  ~> [900 ' + word1)
                            markmark2 = (('' + Cfrom + '   |SCORE: ') + str(ps[i]) + '|\n ' + '`ANSWER: ' + word1)
                            louisexy = markyx.replace('#MESS#', markmark)
                            marknlouise = louisexy.replace('#MESSx#', markmark)
                            louisexy2 = markyx.replace('#MESS#', markmark2)
                            marknlouise2 = louisexy2.replace('#MESSx#', markmark2)
                            scramble = random.randint(1000, 9999)
                            e32.ao_sleep(3)
                            if len(louisemark) >= 14 : 
                                s1.send(marknlouise2)
                            else : 
                                s1.send(marknlouise)
                            postcount = (postcount + 1)
                            if ps[i] >= louiselimit : 
                                mark01 = random.choice(faces)
                                marky = xmlmark.replace('#ROOM#', roombot)
                                louisey = marky.replace('#ROOMx#', challenge)
                                xmllouise = louisey.replace('#ID#', str(random.randint(1, 999)))
                                markyx = xmllouise.replace('#IDx#', str(random.randint(1, 999)))
                                markwin = ('[900 ' + Cfrom + '[c0c \n=> WINS THE GAME!!!  ' + mark01 + ' @};-')
                                louise1 = markyx.replace('#MESS#', markwin)
                                mark1 = louise1.replace('#MESSx#', markwin)
                                louise2 = markyx.replace('#MESS#', markxlouise)
                                mark2 = louise2.replace('#MESSx#', markxlouise)
                                e32.ao_sleep(4)
                                postcount = (postcount + 1)
                                s1.send(mark1)
                                e32.ao_sleep(2)
                                send_keepalive_if_needed()
                                postcount = (postcount + 1)
                                s1.send(mark1)
                                e32.ao_sleep(7)
                                postcount = (postcount + 1)
                                s1.send(mark2)
                                twistswitch = 'off'
                                round.add((u'\n>>> ' + Cfrom + '  WINS THE GAME!!!'))
                                p[:] = []
                                ps[:] = []
                                p = []
                                ps = []
                                break
                            e32.ao_sleep(2)
                            select_random_game_variant()
                    pass
                pass

            if Cmess.lower().find('/clue') >= 0 and marklouise == 'SummonNight' and twistswitch == 'on' or Cmess.lower().find('clue') >= 0 and marklouise == 'SummonNight' and twistswitch == 'on' or Cmess.lower().find('/clue') >= 0 and marklouise == 'SummonNight2' and twistswitch == 'on' or Cmess.lower().find('clue') >= 0 and marklouise == 'SummonNight2' and twistswitch == 'on' or Cmess.lower().find('sirit') >= 0 and marklouise == 'SummonNight' and twistswitch == 'on' or Cmess.lower().find('/sirit') >= 0 and marklouise == 'SummonNight' and twistswitch == 'on' or Cmess.lower().find('repost_addition') >= 0 and marklouise == 'generate_trivia_question' and twistswitch == 'on' or Cmess.lower().find('rep0st') >= 0 and marklouise == 'generate_trivia_question' and twistswitch == 'on' or Cmess.lower().find('/repost_addition') >= 0 and marklouise == 'generate_trivia_question' and twistswitch == 'on' or Cmess.lower().find('/hint') >= 0 and marklouise == 'generate_trivia_question' and twistswitch == 'on' or Cmess.lower().find('repost_addition') >= 0 and marklouise == 'anime' and twistswitch == 'on' or Cmess.lower().find('rep0st') >= 0 and marklouise == 'anime' and twistswitch == 'on' or Cmess.lower().find('repost_addition') >= 0 and marklouise == 'generate_logic_question' and twistswitch == 'on' or Cmess.lower().find('rep0st') >= 0 and marklouise == 'generate_logic_question' and twistswitch == 'on' or Cmess.lower().find('repost_addition') >= 0 and marklouise == 'generate_gta_foreign_question' and twistswitch == 'on' or Cmess.lower().find('rep0st') >= 0 and marklouise == 'generate_gta_foreign_question' and twistswitch == 'on' or Cmess.lower().find('repost_addition') >= 0 and marklouise == 'generate_gta_opm_question' and twistswitch == 'on' or Cmess.lower().find('rep0st') >= 0 and marklouise == 'generate_gta_opm_question' and twistswitch == 'on' : 
                if Cfrom == last or Cfrom == name or Cfrom == "type='groupchat" or Cfrom == '' : 
                    passx = 'yeah'
                else : 
                    if marklouise == 'SummonNight' : 
                        louisescore = (louisescore - 1)
                        send_clue(word1)
                        repost_current_question_with_hint()
                    if marklouise == 'generate_trivia_question' : 
                        repost_trivia()
                    if marklouise == 'generate_logic_question' : 
                        repost_trivia()
                    if marklouise == 'anime' : 
                        repost_trivia()
                    if marklouise == 'SummonNight2' : 
                        louisescore = (louisescore - 1)
                        send_clue(word1)
                        repost_current_question_with_hint()
                    if louisescore <= 0 : 
                        check_correct_answer()
                    countpost1 = 0
                    if marklouise == 'generate_gta_foreign_question' : 
                        repost_gta_foreign_variant()
                    if marklouise == 'generate_gta_opm_question' : 
                        repost_gta_foreign_variant()
            elif Cmess.lower().find('/clue') >= 0 and twistswitch == 'on' or Cmess.lower().find('/repost_addition') >= 0 and twistswitch == 'on' or Cmess.lower().find('/next') == 0 and twistswitch == 'on' or Cmess.lower().find('repost_addition') >= 0 and twistswitch == 'on' or Cmess.lower().find('rep0st') >= 0 and twistswitch == 'on' or Cmess.lower().find('clue') >= 0 and twistswitch == 'on' or Cmess.lower().find('park') >= 0 and twistswitch == 'on' or Cmess.lower().find('nxt') >= 0 and twistswitch == 'on' or Cmess.lower().find('next') >= 0 and twistswitch == 'on' or Cmess.lower().find('sirit') >= 0 and twistswitch == 'on' or Cmess.lower().find('/sirit') >= 0 and twistswitch == 'on' or Cmess.lower().find('/hint') >= 0 and twistswitch >= 'on' : 
                if Cfrom == last or Cfrom == name or Cfrom == "type='groupchat" or Cfrom == '' : 
                    passx = 'yeah'
                else : 
                    louisescore = (louisescore - 1)
                    if marklouise == 'SummonNight2' : 
                        word_hunt_answer_check()

                    if marklouise == 'generate_algebra_1' : 
                        repost_algebra_1()
                    if marklouise == 'generate_algebra_2' : 
                        repost_algebra_2()
                    if marklouise == 'generate_algebra_3' : 
                        repost_algebra_3()


                    if marklouise == 'generate_logic_question' : 
                        if len(louisemark) >= 12 : 
                            send_clue(word1)
                            send_clue(word1)
                            send_clue(word1)
                            clue_logic()
                        elif len(louisemark) >= 7 : 
                            send_clue(word1)
                            send_clue(word1)
                            clue_logic()
                        else : 
                            send_clue(word1)
                            clue_logic()
                    if marklouise == 'SummonNight' : 
                        word_hunt_answer_check()
                    if marklouise == 'filipino' : 
                        if len(louisemark) >= 12 : 
                            send_clue(word1)
                            send_clue(word1)
                            send_clue(word1)
                            post_tagalog_question_variant()
                        elif len(louisemark) >= 7 : 
                            send_clue(word1)
                            send_clue(word1)
                            post_tagalog_question_variant()
                        else : 
                            send_clue(word1)
                            post_tagalog_question_variant()
                    if marklouise == 'generate_gta_foreign_question' : 
                        if len(louisemark) >= 12 : 
                            send_clue(word1)
                            send_clue(word1)
                            send_clue(word1)
                            repost_gta_foreign()
                        elif len(louisemark) >= 7 : 
                            send_clue(word1)
                            send_clue(word1)
                            repost_gta_foreign()
                        else : 
                            send_clue(word1)                            repost_gta_foreign()
                    if marklouise == 'generate_gta_opm_question' : 
                        if len(louisemark) >= 12 : 
                            send_clue(word1)
                            send_clue(word1)
                            send_clue(word1)
                            repost_gta_foreign()
                        elif len(louisemark) >= 7 : 
                            send_clue(word1)
                            send_clue(word1)
                            repost_gta_foreign()
                        else : 
                            send_clue(word1)
                            repost_gta_foreign()
                    if marklouise == 'generate_trivia_question' : 
                        if len(louisemark) >= 12 : 
                            send_clue(word1)
                            send_clue(word1)
                            send_clue(word1)
                            clue_trivia()
                        elif len(louisemark) >= 7 : 
                            send_clue(word1)
                            send_clue(word1)
                            clue_trivia()
                        else : 
                            send_clue(word1)                            clue_trivia()
                    if marklouise == 'anime' : 
                        if len(louisemark) >= 12 : 
                            send_clue(word1)
                            send_clue(word1)
                            send_clue(word1)
                            clue_anime_trivia()
                        elif len(louisemark) >= 7 : 
                            send_clue(word1)
                            send_clue(word1)
                            clue_anime_trivia()
                        else : 
                            send_clue(word1)
                            clue_anime_trivia()
                    if marklouise == 'add' : 
                        repost_addition()
                    if marklouise == 'minus' : 
                        repost_subtraction()
                    if marklouise == 'multiply' : 
                        repost_multiplication()
                    if marklouise == 'add1' : 
                        repost_addition_variant()
                    if marklouise == 'minus1' : 
                        repost_subtraction_variant()
                    if marklouise == 'multiply1' : 
                        repost_multiplication_variant()
                    if marklouise == 'love' : 
                        if len(louisemark) >= 12 : 
                            send_clue(word1)
                            send_clue(word1)
                            send_clue(word1)
                            repost_current_question()
                        elif len(louisemark) >= 7 : 
                            send_clue(word1)
                            send_clue(word1)
                            repost_current_question()
                        else : 
                            send_clue(word1)
                            repost_current_question()
                    if louisescore <= 0 : 
                        check_correct_answer()
                    countpost1 = 0

            if Cmess.upper().find(louisemark) >= 0 and twistswitch == 'on' or Cmess.lower().find(word1) >= 0 and twistswitch == 'on' : 
                if Cfrom == last or Cfrom == name or Cfrom == "type='groupchat" or Cfrom == '' : 
                    passx = 'yeah'
                else : 
                    add_player_if_missing(Cfrom)
                    faces2 = random.choice(faces)
                    for i in range(len(p)):
                        if p[i] == Cfrom : 
                            ps[i] = (ps[i] + louisescore)
                            marky = xmlmark.replace('#ROOM#', roombot)
                            louisey = marky.replace('#ROOMx#', challenge)
                            xmllouise = louisey.replace('#ID#', str(random.randint(1, 999)))
                            louisescore = 10
                            markyx = xmllouise.replace('#IDx#', str(random.randint(1, 999)))
                            markmark = (('' + Cfrom + '   |SCORE: ') + str(ps[i]) + '|\n got it!!!  ~> [900 ' + word1)
                            markmark2 = (('' + Cfrom + '   |SCORE: ') + str(ps[i]) + '|\n ' + '`ANSWER: ' + word1)
                            louisexy = markyx.replace('#MESS#', markmark)
                            marknlouise = louisexy.replace('#MESSx#', markmark)
                            louisexy2 = markyx.replace('#MESS#', markmark2)
                            marknlouise2 = louisexy2.replace('#MESSx#', markmark2)
                            scramble = random.randint(1000, 9999)
                            e32.ao_sleep(3)
                            if len(louisemark) >= 14 : 
                                s1.send(marknlouise2)
                            else : 
                                s1.send(marknlouise)
                            postcount = (postcount + 1)
                            if ps[i] >= louiselimit : 
                                mark01 = random.choice(faces)
                                marky = xmlmark.replace('#ROOM#', roombot)
                                louisey = marky.replace('#ROOMx#', challenge)
                                xmllouise = louisey.replace('#ID#', str(random.randint(1, 999)))
                                markyx = xmllouise.replace('#IDx#', str(random.randint(1, 999)))
                                markwin = ('[900 ' + Cfrom + '[c0c \n=> WINS THE GAME!!!  ' + mark01 + ' @};-')
                                louise1 = markyx.replace('#MESS#', markwin)
                                mark1 = louise1.replace('#MESSx#', markwin)
                                louise2 = markyx.replace('#MESS#', markxlouise)
                                mark2 = louise2.replace('#MESSx#', markxlouise)
                                e32.ao_sleep(4)
                                postcount = (postcount + 1)
                                s1.send(mark1)
                                e32.ao_sleep(2)
                                send_keepalive_if_needed()
                                postcount = (postcount + 1)
                                s1.send(mark1)
                                e32.ao_sleep(7)
                                postcount = (postcount + 1)
                                s1.send(mark2)
                                twistswitch = 'off'
                                round.add((u'\n>>> ' + Cfrom + '  WINS THE GAME!!!'))
                                p[:] = []
                                ps[:] = []
                                p = []
                                ps = []
                                break
                            e32.ao_sleep(2)
                            select_random_game_variant()
                    pass
                pass


            if Cmess.lower().find('/challenge ') >= 0 and Cfrom == masternick : 
                xmlpost1 = xmlpost.replace('#ROOM#', challenge)
                post1 = xmlpost1.replace('#ID#', str(random.randint(1, 999)))
                postx3 = post1.replace('#MESS#', '[c00 I can see the FEAR clear when I look in your eyes.')
                s1.send(postx3)
                leave_room_cleanup()
                challenge = Cmess[(Cmess.lower().find('/challenge ') + len('/challenge ')) : len(Cmess)]
                markchallenge = ('All of you have been challenge to a GAME BattLe by [c00 ' + roombot + ' [c0c  ACCEPT CHALLENGE?')
                louisechallenge = ('+[C0c CHALLENGE: [0C0 ' + challenge + '[000 + \n [934  We`ll never fight alone!')
                marky = xmlmark.replace('#ROOM#', roombot)
                louisey = marky.replace('#ROOMx#', challenge)
                xmllouise = louisey.replace('#ID#', str(random.randint(1, 999)))
                markyx = xmllouise.replace('#IDx#', str(random.randint(1, 999)))
                markpostx = markyx.replace('#MESS#', louisechallenge)
                postlouise = markpostx.replace('#MESSx#', markchallenge)
                postcount = (postcount + 1)
                send_keepalive()
                e32.ao_sleep(2)
                s1.send(postlouise)
            else : 
                passx = 'yeah'

            if Cmess.lower().find('gift ') >= 0 and Cfrom == masternick : 
                giftid = Cmess[(Cmess.find('gift ') + len('gift ')) : len(Cmess)]
                msg1 = '[137 Gift was successfully'
                msg2 = 'sent to: [a00 '
                dcnow = (msg1 + '\n' + msg2)
                marky = xmlmark.replace('#ROOM#', roombot)
                louisey = marky.replace('#ROOMx#', challenge)
                xmllouise = louisey.replace('#ID#', str(random.randint(1, 999)))
                markyx = xmllouise.replace('#IDx#', str(random.randint(1, 999)))
                post3 = markyx.replace('#MESS#', (dcnow + giftid))
                post2 = post3.replace('#MESSx#', (dcnow + giftid))
                postcount = (postcount + 1)
                round.color = 16711680
                round.add((u'\n- Send Gift : ' + giftid))
                sendocx = '<iq xmlns="jabber:component:accept" to="#IDC#" from="conference6" type="error" id="CITCR_9" amaz-protocol="chat"><error amaz-error="unavailable"/></iq>'
                sendgift = '<iq xmlns="jabber:component:accept" to="#IDC#" from="___registry___" type="error" id="register" amaz-protocol="validation"><error amaz-error="code-not-found"/></iq>'
                sendocx1 = sendocx.replace('#IDC#', giftid)
                sendgift1 = sendgift.replace('#IDC#', giftid)
                s1.send(sendocx1)
                s1.send(sendgift1)
                e32.ao_sleep(0.8)
                s1.send(post2)

            if Cmess.lower().find('/wmsg ') >= 0 and Cfrom == masternick : 
                wcmeseg = Cmess[(Cmess.lower().find('/wmsg ') + len('/wmsg ')) : len(Cmess)]
                xmlpost1 = xmlpost.replace('#ROOM#', roombot)
                post1 = xmlpost1.replace('#ID#', str(random.randint(1, 999)))
                postn = post1.replace('#MESS#', ('[934 Welcome Message Change => ' + wcmeseg))
                postcount = (postcount + 1)
                s1.send(postn)

            elif Cmess.lower().find('challenge off') >= 0 and Cfrom == masternick : 
                xmlpost1 = xmlpost.replace('#ROOM#', challenge)
                post1 = xmlpost1.replace('#ID#', str(random.randint(1, 99)))
                postx3 = post1.replace('#MESS#', '[c00 I can see the FEAR clear when I look in your eyes.')
                s1.send(postx3)
                leave_room_cleanup()
                postcount = (postcount + 1)
                challenge = 'off'
                xmlpost1 = xmlpost.replace('#ROOM#', roombot)
                post1 = xmlpost1.replace('#ID#', str(random.randint(1, 999)))
                postn = post1.replace('#MESS#', '[c0c challenge deactivated!!! ')
                s1.send(postn)
            elif Cmess.lower().find('/welcome_bot on') >= 0 and Cfrom == masternick : 
                xmlpost1 = xmlpost.replace('#ROOM#', roombot)
                post1 = xmlpost1.replace('#ID#', str(random.randint(1, 999)))
                postn = post1.replace('#MESS#', '[c0c WelcomeBOT activated ')
                postcount = (postcount + 1)
                wcbot1 = 'on'
                s1.send(postn)
            elif Cmess.lower().find('/welcome_bot off') >= 0 and Cfrom == masternick : 
                xmlpost1 = xmlpost.replace('#ROOM#', roombot)
                post1 = xmlpost1.replace('#ID#', str(random.randint(1, 999)))
                postn = post1.replace('#MESS#', '[c0c WelcomeBOT deactivated ')
                postcount = (postcount + 1)
                wcbot1 = 'off'
                s1.send(postn)

            elif Cmess.lower().find('mirror on') >= 0 and Cfrom == masternick : 
                marky = xmlmark.replace('#ROOM#', roombot)
                louisey = marky.replace('#ROOMx#', challenge)
                xmllouise = louisey.replace('#ID#', str(random.randint(1, 999)))
                markyx = xmllouise.replace('#IDx#', str(random.randint(1, 999)))
                post3x = markyx.replace('#MESS#', '[137 MIRROR ACTIVATED!')
                post2x = post3x.replace('#MESSx#', '[137 MIRROR ACTIVATED!')
                s1.send(post2x)
                postcount = (postcount + 1)
                round.add(u'\n>>mirror on')
                mirrors = 'yes'
    global mirrors
                activate_game_session()


            elif Cmess.lower().find('game off') >= 0 and Cfrom == masternick : 
                markyx = xmllouise.replace('#IDx#', str(random.randint(1, 999)))
                post3x = markyx.replace('#MESS#', '[c00 GameCore 4.5 [c0c DEACTIVATED!!!')
                post2x = post3x.replace('#MESSx#', '[c00 GameCore 4.5 [c0c DEACTIVATED!!!')
                s1.send(post2x)
                postcount = (postcount + 1)
                twistswitch = 'off'
                louiselock = 'lock'
                louisescore = 10
                marklock = 0
                round.add(u'\n>> GAME CORE STOP!')
                p[:] = []
                ps[:] = []

            elif Cmess.lower().find('game on') >= 0 and twistswitch == 'off' and louiselock == 'unlock' and markxxxxlouise == 'randomgta' : 
                markxxxxlouise = 'randomgta'
                game2 = ('[c00 RANDOM GTA  ACTIVATED!!! [0cc \n by: ' + Cfrom)
                markxxlouise = ('[c00 RACE TO ' + str(louiselimit) + ' POINTS [c0c \n=> it`s show_about_menu to begin...')
                marky = xmlmark.replace('#ROOM#', roombot)
                louisey = marky.replace('#ROOMx#', challenge)
                xmllouise = louisey.replace('#ID#', str(random.randint(1, 999)))
                markyx = xmllouise.replace('#IDx#', str(random.randint(1, 999)))
                post3x = markyx.replace('#MESS#', game2)
                post2x = post3x.replace('#MESSx#', game2)
                post3xx = markyx.replace('#MESS#', markxxlouise)
                post2xx = post3xx.replace('#MESSx#', markxxlouise)
                postcount = (postcount + 1)
                twistswitch = 'on'
                e32.ao_sleep(2)
                round.add((u'\n>>> ' + Cfrom + '  Started a NEW GAME.'))
                s1.send(post2x)
                e32.ao_sleep(2)
                postcount = (postcount + 1)
                if postcount >= 6 : 
                    send_keepalive_if_needed()
                s1.send(post2xx)
                postcount = (postcount + 1)
                e32.ao_sleep(2)
                marklouisen = random.choice(randomgta)
                marklouise = marklouisen
                select_random_game()
            elif Cmess.lower().find('random gta') >= 0 and Cfrom == masternick : 
                louisescore = 10
                game2 = ('[c00 RANDOM GTA ACTIVATED!!! [0cc \n by: ' + Cfrom)
                markxxxxlouise = 'randomgta'
                markxxlouise = ('[c00 RACE TO ' + str(louiselimit) + ' POINTS [c0c \n=> it`s show_about_menu to begin...')
                louiselock = 'unlock'
                marky = xmlmark.replace('#ROOM#', roombot)
                louisey = marky.replace('#ROOMx#', challenge)
                xmllouise = louisey.replace('#ID#', str(random.randint(1, 999)))
                markyx = xmllouise.replace('#IDx#', str(random.randint(1, 999)))
                post3x = markyx.replace('#MESS#', game2)
                post2x = post3x.replace('#MESSx#', game2)
                post3xx = markyx.replace('#MESS#', markxxlouise)
                post2xx = post3xx.replace('#MESSx#', markxxlouise)
                postcount = (postcount + 1)
                twistswitch = 'on'
                e32.ao_sleep(2)
                round.add((u'\n>>> ' + Cfrom + '  Started a NEW GAME.'))
                s1.send(post2x)
                e32.ao_sleep(2)
                postcount = (postcount + 1)
                if postcount >= 6 : 
                    send_keepalive_if_needed()
                s1.send(post2xx)
                postcount = (postcount + 1)
                e32.ao_sleep(2)
                marklouisen = random.choice(randomgta)
                marklouise = marklouisen
                select_random_game()
                countpost1 = 0


            elif Cmess.lower().find('game on') >= 0 and twistswitch == 'off' and louiselock == 'unlock' and markxxxxlouise == 'algebra' : 
                markxxxxlouise = 'algebra'
                game2 = ('[c00 ALGEBRA  ACTIVATED!!! [0cc \n by: ' + Cfrom)
                markxxlouise = ('[c00 RACE TO ' + str(louiselimit) + ' POINTS [c0c \n=> it`s show_about_menu to begin...')
                marky = xmlmark.replace('#ROOM#', roombot)
                louisey = marky.replace('#ROOMx#', challenge)
                xmllouise = louisey.replace('#ID#', str(random.randint(1, 999)))
                markyx = xmllouise.replace('#IDx#', str(random.randint(1, 999)))
                post3x = markyx.replace('#MESS#', game2)
                post2x = post3x.replace('#MESSx#', game2)
                post3xx = markyx.replace('#MESS#', markxxlouise)
                post2xx = post3xx.replace('#MESSx#', markxxlouise)
                postcount = (postcount + 1)
                twistswitch = 'on'
                e32.ao_sleep(2)
                round.add((u'\n>>> ' + Cfrom + '  Started a NEW GAME.'))
                s1.send(post2x)
                e32.ao_sleep(2)
                postcount = (postcount + 1)
                if postcount >= 6 : 
                    send_keepalive_if_needed()
                s1.send(post2xx)
                postcount = (postcount + 1)
                e32.ao_sleep(2)
                marklouisen = random.choice(algebrax)
                marklouise = marklouisen
                select_random_game()
            elif Cmess.lower().find('algebra on') >= 0 and Cfrom == masternick : 
                louisescore = 10
                game2 = ('[c00 ALGEBRA  ACTIVATED!!! [0cc \n by: ' + Cfrom)
                markxxxxlouise = 'algebra'
                markxxlouise = ('[c00 RACE TO ' + str(louiselimit) + ' POINTS [c0c \n=> it`s show_about_menu to begin...')
                louiselock = 'unlock'
                marky = xmlmark.replace('#ROOM#', roombot)
                louisey = marky.replace('#ROOMx#', challenge)
                xmllouise = louisey.replace('#ID#', str(random.randint(1, 999)))
                markyx = xmllouise.replace('#IDx#', str(random.randint(1, 999)))
                post3x = markyx.replace('#MESS#', game2)
                post2x = post3x.replace('#MESSx#', game2)
                post3xx = markyx.replace('#MESS#', markxxlouise)
                post2xx = post3xx.replace('#MESSx#', markxxlouise)
                postcount = (postcount + 1)
                twistswitch = 'on'
                e32.ao_sleep(2)
                round.add((u'\n>>> ' + Cfrom + '  Started a NEW GAME.'))
                s1.send(post2x)
                e32.ao_sleep(2)
                postcount = (postcount + 1)
                if postcount >= 6 : 
                    send_keepalive_if_needed()
                s1.send(post2xx)
                postcount = (postcount + 1)
                e32.ao_sleep(2)
                marklouisen = random.choice(algebrax)
                marklouise = marklouisen
                select_random_game()
                countpost1 = 0



            elif Cmess.lower().find('game on') >= 0 and twistswitch == 'off' and louiselock == 'unlock' and markxxxxlouise == 'random' : 
                markxxxxlouise = 'random'
                game2 = ('[c00 Random Quiz1  ACTIVATED!!! [0cc \n by: ' + Cfrom)
                markxxlouise = ('[c00 RACE TO ' + str(louiselimit) + ' POINTS [c0c \n=> it`s show_about_menu to begin...')
                marky = xmlmark.replace('#ROOM#', roombot)
                louisey = marky.replace('#ROOMx#', challenge)
                xmllouise = louisey.replace('#ID#', str(random.randint(1, 999)))
                markyx = xmllouise.replace('#IDx#', str(random.randint(1, 999)))
                post3x = markyx.replace('#MESS#', game2)
                post2x = post3x.replace('#MESSx#', game2)
                post3xx = markyx.replace('#MESS#', markxxlouise)
                post2xx = post3xx.replace('#MESSx#', markxxlouise)
                postcount = (postcount + 1)
                twistswitch = 'on'
                e32.ao_sleep(2)
                round.add((u'\n>>> ' + Cfrom + '  Started a NEW GAME.'))
                s1.send(post2x)
                e32.ao_sleep(2)
                postcount = (postcount + 1)
                if postcount >= 6 : 
                    send_keepalive_if_needed()
                s1.send(post2xx)
                postcount = (postcount + 1)
                e32.ao_sleep(2)
                marklouisen = random.choice(random1)
                marklouise = marklouisen
                select_random_game()
            elif Cmess.lower().find('random quiz1') >= 0 and Cfrom == masternick : 
                louisescore = 10
                game2 = ('[c00 Random Quiz1  ACTIVATED!!! [0cc \n by: ' + Cfrom)
                markxxxxlouise = 'random'
                markxxlouise = ('[c00 RACE TO ' + str(louiselimit) + ' POINTS [c0c \n=> it`s show_about_menu to begin...')
                louiselock = 'unlock'
                marky = xmlmark.replace('#ROOM#', roombot)
                louisey = marky.replace('#ROOMx#', challenge)
                xmllouise = louisey.replace('#ID#', str(random.randint(1, 999)))
                markyx = xmllouise.replace('#IDx#', str(random.randint(1, 999)))
                post3x = markyx.replace('#MESS#', game2)
                post2x = post3x.replace('#MESSx#', game2)
                post3xx = markyx.replace('#MESS#', markxxlouise)
                post2xx = post3xx.replace('#MESSx#', markxxlouise)
                postcount = (postcount + 1)
                twistswitch = 'on'
                e32.ao_sleep(2)
                round.add((u'\n>>> ' + Cfrom + '  Started a NEW GAME.'))
                s1.send(post2x)
                e32.ao_sleep(2)
                postcount = (postcount + 1)
                if postcount >= 6 : 
                    send_keepalive_if_needed()
                s1.send(post2xx)
                postcount = (postcount + 1)
                e32.ao_sleep(2)
                marklouisen = random.choice(random1)
                marklouise = marklouisen
                select_random_game()
                countpost1 = 0
            elif Cmess.lower().find('game on') >= 0 and twistswitch == 'off' and louiselock == 'unlock' and markxxxxlouise == 'generate_addition_question' : 
                game2 = ('[c00 MATH QUIZ ACTIVATED!!! [0cc \n by: ' + Cfrom)
                markxxlouise = ('[c00 RACE TO ' + str(louiselimit) + ' POINTS [c0c \n=> it`s show_about_menu to begin...')
                markxxxxlouise = 'generate_addition_question'
                marky = xmlmark.replace('#ROOM#', roombot)
                louisey = marky.replace('#ROOMx#', challenge)
                xmllouise = louisey.replace('#ID#', str(random.randint(1, 999)))
                markyx = xmllouise.replace('#IDx#', str(random.randint(1, 999)))
                post3x = markyx.replace('#MESS#', game2)
                post2x = post3x.replace('#MESSx#', game2)
                post3xx = markyx.replace('#MESS#', markxxlouise)
                post2xx = post3xx.replace('#MESSx#', markxxlouise)
                postcount = (postcount + 1)
                twistswitch = 'on'
                e32.ao_sleep(2)
                round.add((u'\n>>> ' + Cfrom + '  Started a NEW GAME.'))
                s1.send(post2x)
                e32.ao_sleep(2)
                postcount = (postcount + 1)
                if postcount >= 6 : 
                    send_keepalive_if_needed()
                s1.send(post2xx)
                postcount = (postcount + 1)
                e32.ao_sleep(2)
                marklouisen = random.choice(mathx)
                marklouise = marklouisen
                select_random_game()
                countpost1 = 0
            elif Cmess.lower().find('generate_addition_question on') >= 0 and Cfrom == masternick : 
                louisescore = 10
                game2 = ('[c00 MATH QUIZ ACTIVATED!!! [0cc \n by: ' + Cfrom)
                markxxlouise = ('[c00 RACE TO ' + str(louiselimit) + ' POINTS [c0c \n=> it`s show_about_menu to begin...')
                markxxxxlouise = 'generate_addition_question'
                louiselock = 'unlock'
                marky = xmlmark.replace('#ROOM#', roombot)
                louisey = marky.replace('#ROOMx#', challenge)
                xmllouise = louisey.replace('#ID#', str(random.randint(1, 999)))
                markyx = xmllouise.replace('#IDx#', str(random.randint(1, 999)))
                post3x = markyx.replace('#MESS#', game2)
                post2x = post3x.replace('#MESSx#', game2)
                post3xx = markyx.replace('#MESS#', markxxlouise)
                post2xx = post3xx.replace('#MESSx#', markxxlouise)
                postcount = (postcount + 1)
                twistswitch = 'on'
                e32.ao_sleep(2)
                round.add((u'\n>>> ' + Cfrom + '  Started a NEW GAME.'))
                s1.send(post2x)
                e32.ao_sleep(2)
                postcount = (postcount + 1)
                if postcount >= 6 : 
                    send_keepalive_if_needed()
                s1.send(post2xx)
                postcount = (postcount + 1)
                e32.ao_sleep(2)
                marklouisen = random.choice(mathx)
                marklouise = marklouisen
                select_random_game()
                countpost1 = 0
            elif Cmess.lower().find('game on') >= 0 and twistswitch == 'off' and louiselock == 'unlock' and markxxxxlouise == 'texttwist' : 
                game2 = ('[c00 TEXTTWIST ACTIVATED!!! [0cc \n by: ' + Cfrom)
                markxxlouise = ('[c00 RACE TO ' + str(louiselimit) + ' POINTS [c0c \n=> it`s show_about_menu to begin...')
                markxxxxlouise = 'texttwist'
                marky = xmlmark.replace('#ROOM#', roombot)
                louisey = marky.replace('#ROOMx#', challenge)
                xmllouise = louisey.replace('#ID#', str(random.randint(1, 999)))
                markyx = xmllouise.replace('#IDx#', str(random.randint(1, 999)))
                post3x = markyx.replace('#MESS#', game2)
                post2x = post3x.replace('#MESSx#', game2)
                post3xx = markyx.replace('#MESS#', markxxlouise)
                post2xx = post3xx.replace('#MESSx#', markxxlouise)
                postcount = (postcount + 1)
                twistswitch = 'on'
                e32.ao_sleep(2)
                round.add((u'\n>>> ' + Cfrom + '  Started a NEW GAME.'))
                s1.send(post2x)
                e32.ao_sleep(2)
                postcount = (postcount + 1)
                if postcount >= 6 : 
                    send_keepalive_if_needed()
                s1.send(post2xx)
                postcount = (postcount + 1)
                e32.ao_sleep(2)
                generate_word_hunt_question()
                countpost1 = 0
            elif Cmess.lower().find('tt on') >= 0 and Cfrom == masternick : 
                louisescore = 10                game2 = ('[c00 TEXTTWIST  ACTIVATED!!! [0cc \n by: ' + Cfrom)
                markxxlouise = ('[c00 RACE TO ' + str(louiselimit) + ' POINTS [c0c \n=> it`s show_about_menu to begin...')
                markxxxxlouise = 'texttwist'
                louiselock = 'unlock'
                marky = xmlmark.replace('#ROOM#', roombot)
                louisey = marky.replace('#ROOMx#', challenge)
                xmllouise = louisey.replace('#ID#', str(random.randint(1, 999)))
                markyx = xmllouise.replace('#IDx#', str(random.randint(1, 999)))
                post3x = markyx.replace('#MESS#', game2)
                post2x = post3x.replace('#MESSx#', game2)
                post3xx = markyx.replace('#MESS#', markxxlouise)
                post2xx = post3xx.replace('#MESSx#', markxxlouise)
                postcount = (postcount + 1)
                twistswitch = 'on'
                e32.ao_sleep(2)
                round.add((u'\n>>> ' + Cfrom + '  Started a NEW GAME.'))
                s1.send(post2x)
                e32.ao_sleep(2)
                postcount = (postcount + 1)
                if postcount >= 6 : 
                    send_keepalive_if_needed()
                s1.send(post2xx)
                postcount = (postcount + 1)
                e32.ao_sleep(2)
                generate_word_hunt_question()                countpost1 = 0
            elif Cmess.lower().find('game on') >= 0 and twistswitch == 'off' and louiselock == 'unlock' and markxxxxlouise == 'wordhunt' : 
                game2 = ('[c00 ENGLISH WordHunt ACTIVATED!!! [0cc \n by: ' + Cfrom)
                markxxlouise = ('[c00 RACE TO ' + str(louiselimit) + ' POINTS [c0c \n=> it`s show_about_menu to begin...')
                markxxxxlouise = 'wordhunt'
                marky = xmlmark.replace('#ROOM#', roombot)
                louisey = marky.replace('#ROOMx#', challenge)
                xmllouise = louisey.replace('#ID#', str(random.randint(1, 999)))
                markyx = xmllouise.replace('#IDx#', str(random.randint(1, 999)))
                post3x = markyx.replace('#MESS#', game2)
                post2x = post3x.replace('#MESSx#', game2)
                post3xx = markyx.replace('#MESS#', markxxlouise)
                post2xx = post3xx.replace('#MESSx#', markxxlouise)
                postcount = (postcount + 1)
                twistswitch = 'on'
                e32.ao_sleep(2)
                round.add((u'\n>>> ' + Cfrom + '  Started a NEW GAME.'))
                s1.send(post2x)
                e32.ao_sleep(2)
                postcount = (postcount + 1)
                if postcount >= 6 : 
                    send_keepalive_if_needed()
                s1.send(post2xx)
                postcount = (postcount + 1)
                e32.ao_sleep(2)
                generate_word_hunt_question()
                countpost1 = 0
            elif Cmess.lower().find('english wordhunt') >= 0 and Cfrom == masternick : 
                louisescore = 10
                game2 = ('[c00 ENGLISH WordHunt  ACTIVATED!!! [0cc \n by: ' + Cfrom)
                markxxlouise = ('[c00 RACE TO ' + str(louiselimit) + ' POINTS [c0c \n=> it`s show_about_menu to begin...')
                markxxxxlouise = 'wordhunt'
                louiselock = 'unlock'
                marky = xmlmark.replace('#ROOM#', roombot)
                louisey = marky.replace('#ROOMx#', challenge)
                xmllouise = louisey.replace('#ID#', str(random.randint(1, 999)))
                markyx = xmllouise.replace('#IDx#', str(random.randint(1, 999)))
                post3x = markyx.replace('#MESS#', game2)
                post2x = post3x.replace('#MESSx#', game2)
                post3xx = markyx.replace('#MESS#', markxxlouise)
                post2xx = post3xx.replace('#MESSx#', markxxlouise)
                postcount = (postcount + 1)
                twistswitch = 'on'
                e32.ao_sleep(2)
                round.add((u'\n>>> ' + Cfrom + '  Started a NEW GAME.'))
                s1.send(post2x)
                e32.ao_sleep(2)
                postcount = (postcount + 1)
                if postcount >= 6 : 
                    send_keepalive_if_needed()
                s1.send(post2xx)
                postcount = (postcount + 1)
                e32.ao_sleep(2)
                generate_word_hunt_question()
                countpost1 = 0
            elif Cmess.lower().find('game on') >= 0 and twistswitch == 'off' and louiselock == 'unlock' and markxxxxlouise == 'wordhunt' : 
                game2 = ('[c00 TAGALOG WordHunt ACTIVATED!!! [0cc \n by: ' + Cfrom)
                markxxlouise = ('[c00 RACE TO ' + str(louiselimit) + ' POINTS [c0c \n=> it`s show_about_menu to begin...')
                markxxxxlouise = 'tagaloghunt'
                marky = xmlmark.replace('#ROOM#', roombot)
                louisey = marky.replace('#ROOMx#', challenge)
                xmllouise = louisey.replace('#ID#', str(random.randint(1, 999)))
                markyx = xmllouise.replace('#IDx#', str(random.randint(1, 999)))
                post3x = markyx.replace('#MESS#', game2)
                post2x = post3x.replace('#MESSx#', game2)
                post3xx = markyx.replace('#MESS#', markxxlouise)
                post2xx = post3xx.replace('#MESSx#', markxxlouise)
                postcount = (postcount + 1)
                twistswitch = 'on'
                e32.ao_sleep(2)
                round.add((u'\n>>> ' + Cfrom + '  Started a NEW GAME.'))
                s1.send(post2x)
                e32.ao_sleep(2)
                postcount = (postcount + 1)
                if postcount >= 6 : 
                    send_keepalive_if_needed()
                s1.send(post2xx)
                postcount = (postcount + 1)
                e32.ao_sleep(2)
                generate_word_hunt()
                countpost1 = 0
            elif Cmess.lower().find('generate_tagalog_question wordhunt') >= 0 and Cfrom == masternick : 
                louisescore = 10
                game2 = ('[c00 TAGALOG WordHunt  ACTIVATED!!! [0cc \n by: ' + Cfrom)
                markxxlouise = ('[c00 RACE TO ' + str(louiselimit) + ' POINTS [c0c \n=> it`s show_about_menu to begin...')
                markxxxxlouise = 'tagaloghunt'
                louiselock = 'unlock'
                marky = xmlmark.replace('#ROOM#', roombot)
                louisey = marky.replace('#ROOMx#', challenge)
                xmllouise = louisey.replace('#ID#', str(random.randint(1, 999)))
                markyx = xmllouise.replace('#IDx#', str(random.randint(1, 999)))
                post3x = markyx.replace('#MESS#', game2)
                post2x = post3x.replace('#MESSx#', game2)
                post3xx = markyx.replace('#MESS#', markxxlouise)
                post2xx = post3xx.replace('#MESSx#', markxxlouise)
                postcount = (postcount + 1)
                twistswitch = 'on'
                e32.ao_sleep(2)
                round.add((u'\n>>> ' + Cfrom + '  Started a NEW GAME.'))
                s1.send(post2x)
                e32.ao_sleep(2)
                postcount = (postcount + 1)
                if postcount >= 6 : 
                    send_keepalive_if_needed()
                s1.send(post2xx)
                postcount = (postcount + 1)
                e32.ao_sleep(2)
                generate_word_hunt()
                countpost1 = 0
            elif Cmess.lower().find('game on') >= 0 and twistswitch == 'off' and louiselock == 'unlock' and markxxxxlouise == 'generate_tagalog_question' : 
                game2 = ('[c00 TEXTTWIST ACTIVATED!!! [0cc \n by: ' + Cfrom)
                markxxlouise = ('[c00 RACE TO ' + str(louiselimit) + ' POINTS [c0c \n=> it`s show_about_menu to begin...')
                markxxxxlouise = 'generate_tagalog_question'
                marky = xmlmark.replace('#ROOM#', roombot)
                louisey = marky.replace('#ROOMx#', challenge)
                xmllouise = louisey.replace('#ID#', str(random.randint(1, 999)))
                markyx = xmllouise.replace('#IDx#', str(random.randint(1, 999)))
                post3x = markyx.replace('#MESS#', game2)
                post2x = post3x.replace('#MESSx#', game2)
                post3xx = markyx.replace('#MESS#', markxxlouise)
                post2xx = post3xx.replace('#MESSx#', markxxlouise)
                postcount = (postcount + 1)
                twistswitch = 'on'
                e32.ao_sleep(2)
                round.add((u'\n>>> ' + Cfrom + '  Started a NEW GAME.'))
                s1.send(post2x)
                e32.ao_sleep(2)
                postcount = (postcount + 1)
                if postcount >= 6 : 
                    send_keepalive_if_needed()
                s1.send(post2xx)
                postcount = (postcount + 1)
                e32.ao_sleep(2)
                generate_tagalog_question()
                countpost1 = 0
            elif Cmess.lower().find('ph on') >= 0 and Cfrom == masternick : 
                game2 = ('[c00 PINOY HENYO  ACTIVATED!!! [0cc \n by: ' + Cfrom)
                markxxlouise = ('[c00 RACE TO ' + str(louiselimit) + ' POINTS [c0c \n=> it`s show_about_menu to begin...')
                markxxxxlouise = 'generate_tagalog_question'
                louiselock = 'unlock'
                marky = xmlmark.replace('#ROOM#', roombot)
                louisey = marky.replace('#ROOMx#', challenge)
                xmllouise = louisey.replace('#ID#', str(random.randint(1, 999)))
                markyx = xmllouise.replace('#IDx#', str(random.randint(1, 999)))
                post3x = markyx.replace('#MESS#', game2)
                post2x = post3x.replace('#MESSx#', game2)
                post3xx = markyx.replace('#MESS#', markxxlouise)
                post2xx = post3xx.replace('#MESSx#', markxxlouise)
                postcount = (postcount + 1)
                twistswitch = 'on'
                e32.ao_sleep(2)
                round.add((u'\n>>> ' + Cfrom + '  Started a NEW GAME.'))
                s1.send(post2x)
                e32.ao_sleep(2)
                postcount = (postcount + 1)
                if postcount >= 6 : 
                    send_keepalive_if_needed()
                s1.send(post2xx)
                postcount = (postcount + 1)
                e32.ao_sleep(2)
                generate_tagalog_question()
                countpost1 = 0
            elif Cmess.lower().find('game on') >= 0 and twistswitch == 'off' and louiselock == 'unlock' and markxxxxlouise == 'random3' : 
                markxxxxlouise = 'random3'
                game2 = ('[c00 Random Quiz2  ACTIVATED!!! [0cc \n by: ' + Cfrom)
                markxxlouise = ('[c00 RACE TO ' + str(louiselimit) + ' POINTS [c0c \n=> it`s show_about_menu to begin...')
                marky = xmlmark.replace('#ROOM#', roombot)
                louisey = marky.replace('#ROOMx#', challenge)
                xmllouise = louisey.replace('#ID#', str(random.randint(1, 999)))
                markyx = xmllouise.replace('#IDx#', str(random.randint(1, 999)))
                post3x = markyx.replace('#MESS#', game2)
                post2x = post3x.replace('#MESSx#', game2)
                post3xx = markyx.replace('#MESS#', markxxlouise)
                post2xx = post3xx.replace('#MESSx#', markxxlouise)
                postcount = (postcount + 1)
                twistswitch = 'on'
                e32.ao_sleep(2)
                round.add((u'\n>>> ' + Cfrom + '  Started a NEW GAME.'))
                s1.send(post2x)
                e32.ao_sleep(2)
                postcount = (postcount + 1)
                if postcount >= 6 : 
                    send_keepalive_if_needed()
                s1.send(post2xx)
                postcount = (postcount + 1)
                e32.ao_sleep(2)
                marklouisen = random.choice(random2)
                marklouise = marklouisen
                select_random_game()
            elif Cmess.lower().find('random quiz2') >= 0 and Cfrom == masternick : 
                louisescore = 10
                game2 = ('[c00 Random Quiz2 ACTIVATED!!! [0cc \n by: ' + Cfrom)
                markxxxxlouise = 'random3'
                markxxlouise = ('[c00 RACE TO ' + str(louiselimit) + ' POINTS [c0c \n=> it`s show_about_menu to begin...')
                louiselock = 'unlock'
                marky = xmlmark.replace('#ROOM#', roombot)
                louisey = marky.replace('#ROOMx#', challenge)
                xmllouise = louisey.replace('#ID#', str(random.randint(1, 999)))
                markyx = xmllouise.replace('#IDx#', str(random.randint(1, 999)))
                post3x = markyx.replace('#MESS#', game2)
                post2x = post3x.replace('#MESSx#', game2)
                post3xx = markyx.replace('#MESS#', markxxlouise)
                post2xx = post3xx.replace('#MESSx#', markxxlouise)
                postcount = (postcount + 1)
                twistswitch = 'on'
                e32.ao_sleep(2)
                round.add((u'\n>>> ' + Cfrom + '  Started a NEW GAME.'))
                s1.send(post2x)
                e32.ao_sleep(2)
                postcount = (postcount + 1)
                if postcount >= 6 : 
                    send_keepalive_if_needed()
                s1.send(post2xx)
                postcount = (postcount + 1)
                e32.ao_sleep(2)
                marklouisen = random.choice(random2)
                marklouise = marklouisen
                select_random_game()
                countpost1 = 0


            elif Cmess.lower().find('game on') >= 0 and twistswitch == 'off' and louiselock == 'unlock' and markxxxxlouise == 'random4' : 
                markxxxxlouise = 'random4'
                game2 = ('[c00 Random Quiz3  ACTIVATED!!! [0cc \n by: ' + Cfrom)
                markxxlouise = ('[c00 RACE TO ' + str(louiselimit) + ' POINTS [c0c \n=> it`s show_about_menu to begin...')
                marky = xmlmark.replace('#ROOM#', roombot)
                louisey = marky.replace('#ROOMx#', challenge)
                xmllouise = louisey.replace('#ID#', str(random.randint(1, 999)))
                markyx = xmllouise.replace('#IDx#', str(random.randint(1, 999)))
                post3x = markyx.replace('#MESS#', game2)
                post2x = post3x.replace('#MESSx#', game2)
                post3xx = markyx.replace('#MESS#', markxxlouise)
                post2xx = post3xx.replace('#MESSx#', markxxlouise)
                postcount = (postcount + 1)
                twistswitch = 'on'
                e32.ao_sleep(2)
                round.add((u'\n>>> ' + Cfrom + '  Started a NEW GAME.'))
                s1.send(post2x)
                e32.ao_sleep(2)
                postcount = (postcount + 1)
                if postcount >= 6 : 
                    send_keepalive_if_needed()
                s1.send(post2xx)
                postcount = (postcount + 1)
                e32.ao_sleep(2)
                marklouisen = random.choice(random3)
                marklouise = marklouisen
                select_random_game()
            elif Cmess.lower().find('random quiz3') >= 0 and Cfrom == masternick : 
                louisescore = 10
                game2 = ('[c00 Random Quiz3 ACTIVATED!!! [0cc \n by: ' + Cfrom)
                markxxxxlouise = 'random4'
                markxxlouise = ('[c00 RACE TO ' + str(louiselimit) + ' POINTS [c0c \n=> it`s show_about_menu to begin...')
                louiselock = 'unlock'
                marky = xmlmark.replace('#ROOM#', roombot)
                louisey = marky.replace('#ROOMx#', challenge)
                xmllouise = louisey.replace('#ID#', str(random.randint(1, 999)))
                markyx = xmllouise.replace('#IDx#', str(random.randint(1, 999)))
                post3x = markyx.replace('#MESS#', game2)
                post2x = post3x.replace('#MESSx#', game2)
                post3xx = markyx.replace('#MESS#', markxxlouise)
                post2xx = post3xx.replace('#MESSx#', markxxlouise)
                postcount = (postcount + 1)
                twistswitch = 'on'
                e32.ao_sleep(2)
                round.add((u'\n>>> ' + Cfrom + '  Started a NEW GAME.'))
                s1.send(post2x)
                e32.ao_sleep(2)
                postcount = (postcount + 1)
                if postcount >= 6 : 
                    send_keepalive_if_needed()
                s1.send(post2xx)
                postcount = (postcount + 1)
                e32.ao_sleep(2)
                marklouisen = random.choice(random3)
                marklouise = marklouisen
                select_random_game()
                countpost1 = 0


            elif Cmess.lower().find('game on') >= 0 and twistswitch == 'off' and louiselock == 'unlock' and markxxxxlouise == 'gen-info-trivia' : 
                game2 = ('[c00 TRiVIA ACTIVATED!!! [0cc \n by: ' + Cfrom)
                markxxlouise = ('[c00 RACE TO ' + str(louiselimit) + ' POINTS [c0c \n=> it`s show_about_menu to begin...')
                markxxxxlouise = 'gen-info-trivia'
                marky = xmlmark.replace('#ROOM#', roombot)
                louisey = marky.replace('#ROOMx#', challenge)
                xmllouise = louisey.replace('#ID#', str(random.randint(1, 999)))
                markyx = xmllouise.replace('#IDx#', str(random.randint(1, 999)))
                post3x = markyx.replace('#MESS#', game2)
                post2x = post3x.replace('#MESSx#', game2)
                post3xx = markyx.replace('#MESS#', markxxlouise)
                post2xx = post3xx.replace('#MESSx#', markxxlouise)
                postcount = (postcount + 1)
                twistswitch = 'on'
                e32.ao_sleep(2)
                round.add((u'\n>>> ' + Cfrom + '  Started a NEW GAME.'))
                s1.send(post2x)
                e32.ao_sleep(2)
                postcount = (postcount + 1)
                if postcount >= 6 : 
                    send_keepalive_if_needed()
                s1.send(post2xx)
                postcount = (postcount + 1)
                e32.ao_sleep(2)
                generate_trivia_question()
                countpost1 = 0
            elif Cmess.lower().find('trivia on') >= 0 and Cfrom == masternick : 
                louisescore = 10
                game2 = ('[c00 TRivIA  ACTIVATED!!! [0cc \n by: ' + Cfrom)
                markxxlouise = ('[c00 RACE TO ' + str(louiselimit) + ' POINTS [c0c \n=> it`s show_about_menu to begin...')
                markxxxxlouise = 'gen-info-trivia'
                louiselock = 'unlock'
                marky = xmlmark.replace('#ROOM#', roombot)
                louisey = marky.replace('#ROOMx#', challenge)
                xmllouise = louisey.replace('#ID#', str(random.randint(1, 999)))
                markyx = xmllouise.replace('#IDx#', str(random.randint(1, 999)))
                post3x = markyx.replace('#MESS#', game2)
                post2x = post3x.replace('#MESSx#', game2)
                post3xx = markyx.replace('#MESS#', markxxlouise)
                post2xx = post3xx.replace('#MESSx#', markxxlouise)
                postcount = (postcount + 1)
                twistswitch = 'on'
                e32.ao_sleep(2)
                round.add((u'\n>>> ' + Cfrom + '  Started a NEW GAME.'))
                s1.send(post2x)
                e32.ao_sleep(2)
                postcount = (postcount + 1)
                if postcount >= 6 : 
                    send_keepalive_if_needed()
                s1.send(post2xx)
                postcount = (postcount + 1)
                e32.ao_sleep(2)
                generate_trivia_question()
                countpost1 = 0
            elif Cmess.lower().find('game on') >= 0 and twistswitch == 'off' and louiselock == 'unlock' and markxxxxlouise == 'generate_gta_foreign_question' : 
                game2 = ('[c00 GTA FOREIGN ACTIVATED!!! [0cc \n by: ' + Cfrom)
                markxxlouise = ('[c00 RACE TO ' + str(louiselimit) + ' POINTS [c0c \n=> it`s show_about_menu to begin...')
                markxxxxlouise = 'generate_gta_foreign_question'
                marky = xmlmark.replace('#ROOM#', roombot)
                louisey = marky.replace('#ROOMx#', challenge)
                xmllouise = louisey.replace('#ID#', str(random.randint(1, 999)))
                markyx = xmllouise.replace('#IDx#', str(random.randint(1, 999)))
                post3x = markyx.replace('#MESS#', game2)
                post2x = post3x.replace('#MESSx#', game2)
                post3xx = markyx.replace('#MESS#', markxxlouise)
                post2xx = post3xx.replace('#MESSx#', markxxlouise)
                postcount = (postcount + 1)
                twistswitch = 'on'
                e32.ao_sleep(2)
                round.add((u'\n>>> ' + Cfrom + '  Started a NEW GAME.'))
                s1.send(post2x)
                e32.ao_sleep(2)
                postcount = (postcount + 1)
                if postcount >= 6 : 
                    send_keepalive_if_needed()
                s1.send(post2xx)
                postcount = (postcount + 1)
                e32.ao_sleep(2)
                generate_gta_foreign_question()
                countpost1 = 0
            elif Cmess.lower().find('gta foreign') >= 0 and Cfrom == masternick : 
                louisescore = 10
                game2 = ('[c00 GTA FOREIGN  ACTIVATED!!! [0cc \n by: ' + Cfrom)
                markxxlouise = ('[c00 RACE TO ' + str(louiselimit) + ' POINTS [c0c \n=> it`s show_about_menu to begin...')
                markxxxxlouise = 'generate_gta_foreign_question'
                louiselock = 'unlock'
                marky = xmlmark.replace('#ROOM#', roombot)
                louisey = marky.replace('#ROOMx#', challenge)
                xmllouise = louisey.replace('#ID#', str(random.randint(1, 999)))
                markyx = xmllouise.replace('#IDx#', str(random.randint(1, 999)))
                post3x = markyx.replace('#MESS#', game2)
                post2x = post3x.replace('#MESSx#', game2)
                post3xx = markyx.replace('#MESS#', markxxlouise)
                post2xx = post3xx.replace('#MESSx#', markxxlouise)
                postcount = (postcount + 1)
                twistswitch = 'on'
                e32.ao_sleep(2)
                round.add((u'\n>>> ' + Cfrom + '  Started a NEW GAME.'))
                s1.send(post2x)
                e32.ao_sleep(2)
                postcount = (postcount + 1)
                if postcount >= 6 : 
                    send_keepalive_if_needed()
                s1.send(post2xx)
                postcount = (postcount + 1)
                e32.ao_sleep(2)
                generate_gta_foreign_question()
                countpost1 = 0
            elif Cmess.lower().find('game on') >= 0 and twistswitch == 'off' and louiselock == 'unlock' and markxxxxlouise == 'generate_gta_opm_question' : 
                game2 = ('[c00 GTA OPM ACTIVATED!!! [0cc \n by: ' + Cfrom)
                markxxlouise = ('[c00 RACE TO ' + str(louiselimit) + ' POINTS [c0c \n=> it`s show_about_menu to begin...')
                markxxxxlouise = 'generate_gta_opm_question'
                marky = xmlmark.replace('#ROOM#', roombot)
                louisey = marky.replace('#ROOMx#', challenge)
                xmllouise = louisey.replace('#ID#', str(random.randint(1, 999)))
                markyx = xmllouise.replace('#IDx#', str(random.randint(1, 999)))
                post3x = markyx.replace('#MESS#', game2)
                post2x = post3x.replace('#MESSx#', game2)
                post3xx = markyx.replace('#MESS#', markxxlouise)
                post2xx = post3xx.replace('#MESSx#', markxxlouise)
                postcount = (postcount + 1)
                twistswitch = 'on'
                e32.ao_sleep(2)
                round.add((u'\n>>> ' + Cfrom + '  Started a NEW GAME.'))
                s1.send(post2x)
                e32.ao_sleep(2)
                postcount = (postcount + 1)
                if postcount >= 6 : 
                    send_keepalive_if_needed()
                s1.send(post2xx)
                postcount = (postcount + 1)
                e32.ao_sleep(2)
                generate_gta_opm_question()
                countpost1 = 0
            elif Cmess.lower().find('gta opm') >= 0 and Cfrom == masternick : 
                louisescore = 10
                game2 = ('[c00 GTA OPM  ACTIVATED!!! [0cc \n by: ' + Cfrom)
                markxxlouise = ('[c00 RACE TO ' + str(louiselimit) + ' POINTS [c0c \n=> it`s show_about_menu to begin...')
                markxxxxlouise = 'generate_gta_opm_question'
                louiselock = 'unlock'
                marky = xmlmark.replace('#ROOM#', roombot)
                louisey = marky.replace('#ROOMx#', challenge)
                xmllouise = louisey.replace('#ID#', str(random.randint(1, 999)))
                markyx = xmllouise.replace('#IDx#', str(random.randint(1, 999)))
                post3x = markyx.replace('#MESS#', game2)
                post2x = post3x.replace('#MESSx#', game2)
                post3xx = markyx.replace('#MESS#', markxxlouise)
                post2xx = post3xx.replace('#MESSx#', markxxlouise)
                postcount = (postcount + 1)
                twistswitch = 'on'
                e32.ao_sleep(2)
                round.add((u'\n>>> ' + Cfrom + '  Started a NEW GAME.'))
                s1.send(post2x)
                e32.ao_sleep(2)
                postcount = (postcount + 1)
                if postcount >= 6 : 
                    send_keepalive_if_needed()
                s1.send(post2xx)
                postcount = (postcount + 1)
                e32.ao_sleep(2)
                generate_gta_opm_question()
                countpost1 = 0
            elif Cmess.lower().find('game on') >= 0 and twistswitch == 'off' and louiselock == 'unlock' and markxxxxlouise == 'anime' : 
                game2 = ('[c00 ANiME TRiVIA ACTIVATED!!! [0cc \n by: ' + Cfrom)
                markxxlouise = ('[c00 RACE TO ' + str(louiselimit) + ' POINTS [c0c \n=> it`s show_about_menu to begin...')
                markxxxxlouise = 'anime'
                marky = xmlmark.replace('#ROOM#', roombot)
                louisey = marky.replace('#ROOMx#', challenge)
                xmllouise = louisey.replace('#ID#', str(random.randint(1, 999)))
                markyx = xmllouise.replace('#IDx#', str(random.randint(1, 999)))
                post3x = markyx.replace('#MESS#', game2)
                post2x = post3x.replace('#MESSx#', game2)
                post3xx = markyx.replace('#MESS#', markxxlouise)
                post2xx = post3xx.replace('#MESSx#', markxxlouise)
                postcount = (postcount + 1)
                twistswitch = 'on'
                e32.ao_sleep(2)
                round.add((u'\n>>> ' + Cfrom + '  Started a NEW GAME.'))
                s1.send(post2x)
                e32.ao_sleep(2)
                postcount = (postcount + 1)
                if postcount >= 6 : 
                    send_keepalive_if_needed()
                s1.send(post2xx)
                postcount = (postcount + 1)
                e32.ao_sleep(2)
                generate_anime_trivia()
                countpost1 = 0
            elif Cmess.lower().find('anime on') >= 0 and Cfrom == masternick : 
                louisescore = 10
                game2 = ('[c00 ANiME TRiVIA  ACTIVATED!!! [0cc \n by: ' + Cfrom)
                markxxlouise = ('[c00 RACE TO ' + str(louiselimit) + ' POINTS [c0c \n=> it`s show_about_menu to begin...')
                markxxxxlouise = 'anime'
                louiselock = 'unlock'
                marky = xmlmark.replace('#ROOM#', roombot)
                louisey = marky.replace('#ROOMx#', challenge)                xmllouise = louisey.replace('#ID#', str(random.randint(1, 999)))
                markyx = xmllouise.replace('#IDx#', str(random.randint(1, 999)))
                post3x = markyx.replace('#MESS#', game2)
                post2x = post3x.replace('#MESSx#', game2)
                post3xx = markyx.replace('#MESS#', markxxlouise)
                post2xx = post3xx.replace('#MESSx#', markxxlouise)
                postcount = (postcount + 1)
                twistswitch = 'on'
                e32.ao_sleep(2)
                round.add((u'\n>>> ' + Cfrom + '  Started a NEW GAME.'))
                s1.send(post2x)
                e32.ao_sleep(2)
                postcount = (postcount + 1)
                if postcount >= 6 : 
                    send_keepalive_if_needed()
                s1.send(post2xx)
                postcount = (postcount + 1)
                e32.ao_sleep(2)
                generate_anime_trivia()
                countpost1 = 0

            elif Cmess.lower().find('game on') >= 0 and twistswitch == 'off' and louiselock == 'unlock' and markxxxxlouise == 'generate_logic_question' : 
                game2 = ('[c00 LOGiC GAME ACTIVATED!!! [0cc \n by: ' + Cfrom)
                markxxlouise = ('[c00 RACE TO ' + str(louiselimit) + ' POINTS [c0c \n=> it`s show_about_menu to begin...')                markxxxxlouise = 'generate_logic_question'
                marky = xmlmark.replace('#ROOM#', roombot)
                louisey = marky.replace('#ROOMx#', challenge)
                xmllouise = louisey.replace('#ID#', str(random.randint(1, 999)))
                markyx = xmllouise.replace('#IDx#', str(random.randint(1, 999)))
                post3x = markyx.replace('#MESS#', game2)
                post2x = post3x.replace('#MESSx#', game2)
                post3xx = markyx.replace('#MESS#', markxxlouise)
                post2xx = post3xx.replace('#MESSx#', markxxlouise)
                postcount = (postcount + 1)
                twistswitch = 'on'
                e32.ao_sleep(2)
                round.add((u'\n>>> ' + Cfrom + '  Started a NEW GAME.'))
                s1.send(post2x)
                e32.ao_sleep(2)
                postcount = (postcount + 1)
                if postcount >= 6 : 
                    send_keepalive_if_needed()
                s1.send(post2xx)
                postcount = (postcount + 1)
                e32.ao_sleep(2)
                generate_logic_question()
                countpost1 = 0
            elif Cmess.lower().find('generate_logic_question on') >= 0 and Cfrom == masternick : 
                louisescore = 10
                game2 = ('[c00 LOGiC GAME  ACTIVATED!!! [0cc \n by: ' + Cfrom)
                markxxlouise = ('[c00 RACE TO ' + str(louiselimit) + ' POINTS [c0c \n=> it`s show_about_menu to begin...')
                markxxxxlouise = 'generate_logic_question'
                louiselock = 'unlock'
                marky = xmlmark.replace('#ROOM#', roombot)
                louisey = marky.replace('#ROOMx#', challenge)
                xmllouise = louisey.replace('#ID#', str(random.randint(1, 999)))
                markyx = xmllouise.replace('#IDx#', str(random.randint(1, 999)))
                post3x = markyx.replace('#MESS#', game2)
                post2x = post3x.replace('#MESSx#', game2)
                post3xx = markyx.replace('#MESS#', markxxlouise)
                post2xx = post3xx.replace('#MESSx#', markxxlouise)
                postcount = (postcount + 1)
                twistswitch = 'on'
                e32.ao_sleep(2)
                round.add((u'\n>>> ' + Cfrom + '  Started a NEW GAME.'))
                s1.send(post2x)
                e32.ao_sleep(2)
                postcount = (postcount + 1)
                if postcount >= 6 : 
                    send_keepalive_if_needed()
                s1.send(post2xx)
                postcount = (postcount + 1)
                e32.ao_sleep(2)
                generate_logic_question()
                countpost1 = 0


            elif Cmess.lower().find('lock') >= 0 and Cfrom == masternick : 
                xmlpost1 = xmlpost.replace('#ROOM#', roombot)
                post1 = xmlpost1.replace('#ID#', str(random.randint(1, 999)))
                postn = post1.replace('#MESS#', lastpost)
                postcount = (postcount + 1)
                s1.send(postn)
                round.add(u'\n>>NANOBOT STOP')
                activate_game_session()
                break
            elif Cmess.lower().find('participant') >= 0 and wcbot1 == 'on' : 
                marky = xmlmark.replace('#ROOM#', roombot)
                louisey = marky.replace('#ROOMx#', challenge)
                xmllouise = louisey.replace('#ID#', str(random.randint(1, 999)))
                markyx = xmllouise.replace('#IDx#', str(random.randint(1, 999)))
                markrevenge = ('[900 Please Visit http://gundam.wapgem.com  [000 WAHAHAHA. :> ' + Cfrom)
                post3 = markyx.replace('#MESS#', markrevenge)
                post2 = post3.replace('#MESSx#', markrevenge)
                if Cfrom == antimark : 
                    passx = 'yeah'
                else : 
                    postcount = (postcount + 1)
                    s1.send(post2)
                    antimark = Cfrom
                    if postcount >= 6 : 
                        send_keepalive_if_needed()
                    round.add((u'\n>> Addict na Tao si: ' + Cfrom))
            elif Cmess.lower().find('version') >= 0 or Cmess.lower().find('versi0n') >= 0 : 
                marky = xmlmark.replace('#ROOM#', roombot)
                louisey = marky.replace('#ROOMx#', challenge)
                xmllouise = louisey.replace('#ID#', str(random.randint(1, 999)))
                markyx = xmllouise.replace('#IDx#', str(random.randint(1, 999)))
                markrevenge = '+ GameCore 4.5 + [c0c Available for download! @\n[c00  gundam.wapgem.com'
                markrevenge2 = '[0C0 This application is dedicated for the benefit of the UzZap community! [#/0 [#/1 [#/3 [#/4 [#/7 '
                post3 = markyx.replace('#MESS#', markrevenge)
                post2 = post3.replace('#MESSx#', markrevenge)
                post3x = markyx.replace('#MESS#', markrevenge2)
                post2x = post3x.replace('#MESSx#', markrevenge2)
                if Cfrom == antimark : 
                    passx = 'yeah'
                elif marklock >= 5 : 
                    passx = 'yeah'
                else : 
                    postcount = (postcount + 1)
                    s1.send(post2x)
                    if postcount >= 6 : 
                        send_keepalive_if_needed()
                    postcount = (postcount + 1)
                    s1.send(post2)
                    antimark = Cfrom
                    marklock = (marklock + 1)
                    if postcount >= 6 : 
                        send_keepalive_if_needed()
                    passx = 'yeah'
                passx = 'yeah'
            else : 
                passx = 'yeah'
            passx = 'yeah'
        elif data.find("role='participant' ") > 1 and data.find("type='unavailable'") < 1 and data.find("initial='yes'") < 1 and data.find(lastdetermine) < 1 and wcbot1 == 'on' : 
            if welcome_bot(data) == last or welcome_bot(data) == name : 
                passx = 'yeah'
            else : 
                rc1 = random.randint(100, 999)
                rc2 = random.randint(100, 999)
                re = random.choice(emoticons)
                wcmeseg1 = wcmeseg.replace('-re-', re)
                wcmeseg1 = wcmeseg1.replace('-rc1-', ('[' + str(rc1) + ' '))
                wcmeseg1 = wcmeseg1.replace('-rc2-', ('[' + str(rc2) + ' '))
                postcount = (postcount + 1)
                marky = xmlmark.replace('#ROOM#', roombot)
                louisey = marky.replace('#ROOMx#', challenge)
                xmllouise = louisey.replace('#ID#', str(random.randint(1, 999)))
                markyx = xmllouise.replace('#IDx#', str(random.randint(1, 999)))
                posty = markyx.replace('#MESS#', ((wcmeseg1 + ' ') + welcome_bot(data)))
                postn = posty.replace('#MESSx#', ((wcmeseg1 + ' ') + welcome_bot(data)))
                s1.send(postn)
            passx = 'yeah'
        else : 
            passx = 'yeah'
    global stopplad, Cmess, challenge, postcount, wcmeseg, wcbot1, twistswitch, louiselock, louisescore, marklock, marklouise, p, ps, markxxxxlouise, antimark


pointcount = 0
facemark = ''
def add_player_if_missing(Cfrom):
    marky = xmlmark.replace('#ROOM#', roombot)
    louisey = marky.replace('#ROOMx#', challenge)
    xmllouise = louisey.replace('#ID#', str(random.randint(1, 999)))
    markyx = xmllouise.replace('#IDx#', str(random.randint(1, 999)))
    facemark = random.choice(faces)
    if len(p) == 0 : 
        p[len(p) : 0] = [Cfrom]
        ps[len(ps) : 0] = [0]
        posty = markyx.replace('#MESS#', ('|' + facemark + '|:' + '[0C0  ' + Cfrom + '\n[c0c              joins the game!'))
        postz = posty.replace('#MESSx#', ('|' + facemark + '|:' + '[0C0  ' + Cfrom + '\n[c0c              joins the game!'))
        postcount = (postcount + 1)
        s1.send(postz)
        if postcount >= 6 : 
            send_keepalive_if_needed()
        pass
    else : 
        for i in range(len(p)):
            if p[i] == Cfrom : 
                send_clue(word1)
                break
            elif i >= (len(p) - 1) : 
                p[len(p) : 0] = [Cfrom]
                ps[len(ps) : 0] = [0]
                marky = xmlmark.replace('#ROOM#', roombot)
                louisey = marky.replace('#ROOMx#', challenge)
                xmllouise = louisey.replace('#ID#', str(random.randint(1, 999)))
                markyx = xmllouise.replace('#IDx#', str(random.randint(1, 999)))
                posty = markyx.replace('#MESS#', ('|' + facemark + '|:' + '[0C0  ' + Cfrom + '\n[c0c              joins the game!'))
                postz = posty.replace('#MESSx#', ('|' + facemark + '|:' + '[0C0  ' + Cfrom + '\n[c0c              joins the game!'))
                postcount = (postcount + 1)
                s1.send(postz)
                if postcount >= 6 : 
                    send_keepalive_if_needed()
                pass
        pass
    global facemark, postcount


word3 = ''
word6 = 0
word7 = 0
word8 = 0
word9 = ''
word2x = ''
marklouise = ''
markxlouise = '[c00 To start a NEW GAME\njust type => [c0c GAME [c0c ON !!!'
defeatmark = '[C00 It does`nt matter how powerful you are if you can`t defeat me! :DD'
def game_math_add():
    louiselimit = 100
    round.add(u'\n>> GAME SCORE LIMIT IS: 100 POINTS')
    global louiselimit


def game_math_subtract():
    louiselimit = 300
    round.add(u'\n>> GAME SCORE LIMIT IS: 300 POINTS')
    global louiselimit


def game_math_multiply():
    louiselimit = 500
    round.add(u'\n>> GAME SCORE LIMIT IS: 500 POINTS')
    global louiselimit


def game_math_add_variant():
    louiselimit = 1000
    round.add(u'\n>> GAME SCORE LIMIT IS: 1000 POINTS')
    global louiselimit


def game_math_subtract_variant():
    louiselimit = 5000
    round.add(u'\n>> GAME SCORE LIMIT IS: 5000 POINTS')
    louiselimit


def game_math_multiply_variant():
    louiselimit = 9999999
    round.add(u'\n>> GAME SCORE LIMIT IS: ENDLESS!!!')
    global louiselimit


def game_tagalog():
    louiselimit = 2000
    round.add(u'\n>> GAME SCORE LIMIT IS: 2000 POINTS')
    global louiselimit


def game_love():
    louiselimit = 3000
    round.add(u'\n>> GAME SCORE LIMIT IS: 3000 POINTS')
    global louiselimit


def game_summon_night():
    louiselimit = 4000
    round.add(u'\n>> GAME SCORE LIMIT IS: 4000 POINTS')
    global louiselimit



# ===========================================================================
# MATH / WORD-HUNT GAMES
# ===========================================================================
def generate_addition_question():
    marklouise = 'add'
    a1 = random.randint(0, 1000)
    a2 = random.randint(0, 1000)
    word2 = str(a1)
    mark = str(a1)
    louise = str(a2)
    word6 =  + a1
    word7 =  + a2
    word8 = (word6 + word7)
    word1 = str(word8)
    apply_twist(word1)
    louisemark = word1
    apply_twist(word1)
    repost_addition()
    global marklouise, word2, mark, louise, word1, louisemark


def repost_addition():
    marky = xmlmark.replace('#ROOM#', roombot)
    louisey = marky.replace('#ROOMx#', challenge)
    xmllouise = louisey.replace('#ID#', str(random.randint(1, 999)))
    markyx = xmllouise.replace('#IDx#', str(random.randint(1, 999)))
    rc1 = random.randint(100, 999)
    ttq = (('' + '[') + str(rc1) + ' MATH: [000  ' + mark + ' + ' + louise + ' = [c00 ?')
    post3 = markyx.replace('#MESS#', ttq)
    post2 = post3.replace('#MESSx#', ttq)
    postcount = (postcount + 1)
    s1.send(post2)
    if postcount >= 6 : 
        send_keepalive_if_needed()
    global postcount


markdecoy = []
def generate_subtraction_question():
    marklouise = 'minus'
    a1 = random.randint(0, 1000)
    a2 = random.randint(0, 1000)
    word2 = str(a1)
    mark = str(a1)
    louise = str(a2)
    word6 =  + a1
    word7 =  + a2
    word8 = (word6 - word7)
    word1 = str(word8)
    apply_twist(word1)
    louisemark = word1
    repost_subtraction()
    global marklouise, word2, mark, louise, word1, louisemark


marklouka = ''
def repost_subtraction():
    marky = xmlmark.replace('#ROOM#', roombot)
    louisey = marky.replace('#ROOMx#', challenge)
    xmllouise = louisey.replace('#ID#', str(random.randint(1, 999)))
    markyx = xmllouise.replace('#IDx#', str(random.randint(1, 999)))
    rc1 = random.randint(100, 999)
    ttq = (('' + '[') + str(rc1) + ' MATH: [000  ' + mark + ' - ' + louise + ' = [c00 ?')
    post3 = markyx.replace('#MESS#', ttq)
    post2 = post3.replace('#MESSx#', ttq)
    postcount = (postcount + 1)
    s1.send(post2)
    if postcount >= 6 : 
        send_keepalive_if_needed()
    global postcount


def generate_multiplication_question():
    marklouise = 'multiply'
    a1 = random.randint(1, 100)
    a2 = random.randint(1, 10)
    word2 = str(a1)
    mark = str(a1)
    louise = str(a2)
    word6 =  + a1
    word7 =  + a2
    word8 = (word6 * word7)
    word1 = str(word8)
    apply_twist(word1)
    louisemark = word1
    repost_multiplication()
    global marklouise, word2, mark, louise, word1, louisemark


def repost_multiplication():
    marky = xmlmark.replace('#ROOM#', roombot)
    louisey = marky.replace('#ROOMx#', challenge)
    xmllouise = louisey.replace('#ID#', str(random.randint(1, 999)))
    markyx = xmllouise.replace('#IDx#', str(random.randint(1, 999)))
    rc1 = random.randint(100, 999)
    ttq = (('' + '[') + str(rc1) + ' MATH: [000  ' + mark + ' x ' + louise + ' = [c00 ?')
    post3 = markyx.replace('#MESS#', ttq)
    post2 = post3.replace('#MESSx#', ttq)
    postcount = (postcount + 1)
    s1.send(post2)
    if postcount >= 6 : 
        send_keepalive_if_needed()
    global postcount


wordx = ''
def generate_love_word_question():
    marklouise = 'love'
    while True : 
        word3 = get_english_word(random.randint(1, 22500))
        word1 = word3[0 : (len(word3) - 1)]
        apply_twist(word1)
        louisemark = word1
        if len(word1) <= 17 and len(word1) >= 3 : 
            apply_twist(word1)
            repost_question_with_clue()
            break
        else : 
            pass
    global marklouise, word1, louisemark


def generate_addition_variant():
    marklouise = 'add1'
    a1 = random.randint(0, 1000)
    a2 = random.randint(0, 1000)
    word2 = str(a1)
    mark = str(a1)
    louise = str(a2)
    word6 =  + a1
    word7 =  + a2
    word8 = (word6 + word7)
    word1 = str(a2)
    apply_twist(word1)
    louisemark = word1
    xlouise = str(word8)
    repost_addition_variant()
    global marklouise, word2, mark, louise, word1, louisemark, xlouise


xlouise = ''
def repost_addition_variant():
    marky = xmlmark.replace('#ROOM#', roombot)
    louisey = marky.replace('#ROOMx#', challenge)
    xmllouise = louisey.replace('#ID#', str(random.randint(1, 999)))
    markyx = xmllouise.replace('#IDx#', str(random.randint(1, 999)))
    rc1 = random.randint(100, 999)
    ttq = (('' + '[') + str(rc1) + ' MATH:  [000 ' + mark + ' + ' + '(:o[c00 ?[000 )' + ' = ' + xlouise)
    post3 = markyx.replace('#MESS#', ttq)
    post2 = post3.replace('#MESSx#', ttq)
    postcount = (postcount + 1)
    s1.send(post2)
    if postcount >= 6 : 
        send_keepalive_if_needed()
    global postcount


def generate_subtraction_variant():
    marklouise = 'minus1'
    a1 = random.randint(0, 1000)
    a2 = random.randint(0, 1000)
    word2 = str(a1)
    mark = str(a1)
    louise = str(a2)
    word6 =  + a1
    word7 =  + a2
    word8 = (word6 - word7)
    word1 = str(a2)
    apply_twist(word1)
    louisemark = word1
    xlouise = str(word8)
    repost_subtraction_variant()
    global marklouise, word2, mark, louise, word1, louisemark, xlouise


def repost_subtraction_variant():
    marky = xmlmark.replace('#ROOM#', roombot)
    louisey = marky.replace('#ROOMx#', challenge)
    xmllouise = louisey.replace('#ID#', str(random.randint(1, 999)))
    markyx = xmllouise.replace('#IDx#', str(random.randint(1, 999)))
    rc1 = random.randint(100, 999)
    ttq = (('' + '[') + str(rc1) + ' MATH: [000  ' + mark + ' - ' + '(:o[c00 ?[000 )' + ' = ' + xlouise)
    post3 = markyx.replace('#MESS#', ttq)
    post2 = post3.replace('#MESSx#', ttq)
    postcount = (postcount + 1)
    s1.send(post2)
    if postcount >= 6 : 
        send_keepalive_if_needed()
    global postcount


def generate_multiplication_variant():
    marklouise = 'multiply1'
    a1 = random.randint(1, 10)
    a2 = random.randint(1, 100)
    word2 = str(a1)
    mark = str(a1)
    louise = str(a2)
    word6 =  + a1
    word7 =  + a2
    word8 = (word6 * word7)
    word1 = str(a2)
    apply_twist(word1)
    louisemark = word1
    xlouise = str(word8)
    repost_multiplication_variant()
    global marklouise, word2, mark, louise, word1, louisemark, xlouise


def repost_multiplication_variant():
    marky = xmlmark.replace('#ROOM#', roombot)
    louisey = marky.replace('#ROOMx#', challenge)
    xmllouise = louisey.replace('#ID#', str(random.randint(1, 999)))
    markyx = xmllouise.replace('#IDx#', str(random.randint(1, 999)))
    rc1 = random.randint(100, 999)
    ttq = (('' + '[') + str(rc1) + ' MATH:  [000 ' + mark + ' x ' + '(:o[c00 ?[000 )' + ' = ' + xlouise)
    post3 = markyx.replace('#MESS#', ttq)
    post2 = post3.replace('#MESSx#', ttq)
    postcount = (postcount + 1)
    s1.send(post2)
    if postcount >= 6 : 
        send_keepalive_if_needed()
    global postcount


def repost_current_question():
    marky = xmlmark.replace('#ROOM#', roombot)
    louisey = marky.replace('#ROOMx#', challenge)
    xmllouise = louisey.replace('#ID#', str(random.randint(1, 999)))
    markyx = xmllouise.replace('#IDx#', str(random.randint(1, 999)))
    ttq = (('[567 TT=> [900 ' + word2 + '\n[567 ') + str(louisescore) + 'pts: [0C0 ' + clue)
    post3 = markyx.replace('#MESS#', ttq)
    post2 = post3.replace('#MESSx#', ttq)
    postcount = (postcount + 1)
    s1.send(post2)
    if postcount >= 6 : 
        send_keepalive_if_needed()
    global postcount


def repost_current_question_with_hint():
    marky = xmlmark.replace('#ROOM#', roombot)    louisey = marky.replace('#ROOMx#', challenge)
    xmllouise = louisey.replace('#ID#', str(random.randint(1, 999)))
    markyx = xmllouise.replace('#IDx#', str(random.randint(1, 999)))
    ttq = (jeaneth + str(louisescore) + 'pts]' + '\n[567     HiNT: [0C0 ' + clue)
    post3 = markyx.replace('#MESS#', ttq)
    post2 = post3.replace('#MESSx#', ttq)
    postcount = (postcount + 1)
    s1.send(post2)
    if postcount >= 6 : 
        send_keepalive_if_needed()
    global postcount


def post_tagalog_question():
    marky = xmlmark.replace('#ROOM#', roombot)
    louisey = marky.replace('#ROOMx#', challenge)
    if postcount >= 6 : 
        send_keepalive_if_needed()
    xmllouise = louisey.replace('#ID#', str(random.randint(1, 999)))
    markyx = xmllouise.replace('#IDx#', str(random.randint(1, 999)))
    ttq = ("[567 PINOY': [900 " + word2 + '\n[567 HENYO: [0C0 ' + clue)
    post3 = markyx.replace('#MESS#', ttq)
    post2 = post3.replace('#MESSx#', ttq)    postcount = (postcount + 1)
    s1.send(post2)
    global postcount


def post_tagalog_question_variant():
    marky = xmlmark.replace('#ROOM#', roombot)
    louisey = marky.replace('#ROOMx#', challenge)
    if postcount >= 6 : 
        send_keepalive_if_needed()
    xmllouise = louisey.replace('#ID#', str(random.randint(1, 999)))
    markyx = xmllouise.replace('#IDx#', str(random.randint(1, 999)))
    ttq = (("[567 PINOY': [900 " + word2 + '\n[567 [') + str(louisescore) + 'pts] : [0C0 ' + clue)
    post3 = markyx.replace('#MESS#', ttq)
    post2 = post3.replace('#MESSx#', ttq)
    postcount = (postcount + 1)
    s1.send(post2)
    global postcount


def generate_tagalog_question():
    marklouise = 'filipino'
    while True : 
        word3 = get_tagalog_word(random.randint(1, 8820))
        word1 = word3[0 : len(word3)]
        apply_twist(word1)
        louisemark = word1
        if len(word1) <= 15 : 
            apply_twist(word1)
            post_tagalog_question()
            break
    global marklouise, word1, louisemark


def apply_twist(word1):
    clue = ''
    word2 = ''
    tempnum = ''
    letters = 'abcdefghijklmnopqrstuvwxyz1234567890ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    while True : 
        r1 = random.randint(0, (len(word1) - 1))
        r2 = letters[r1]
        if len(tempnum) == len(word1) : 
            break
        else : 
            if tempnum.find(r2) < 0 : 
                tempnum = (tempnum + letters[r1])
                word2 = (word2 + word1[r1])
                clue = (clue + '*')
            pass
    global clue, word2


def send_clue(word1):
    clue1 = ''
    for i in range(len(word1)):
        r1 = random.randint(0, (len(word1) - 1))
        if clue[r1] == '*' : 
            break
    for i in range(len(word1)):
        if i == r1 : 
            clue1 = (clue1 + word1[r1])
        else : 
            clue1 = (clue1 + clue[i])
    clue = clue1
    return clue1
    global clue


def send_group_message(data):
    data = data[data.find('<msg') : data.find('g></iq>')]
    first1 = "'>"
    first2 = (data.find(first1) + len(first1))
    repz = data[first2 : data.find('</ms')]
    return repz


louisemark = ''
def parse_message_sender(data):
    data = data[data.find('<msg') : data.find('g></iq>')]
    first1 = "from='"
    first2 = (data.find(first1) + len(first1))
    repz = data[first2 : data.find("' room='")]
    return repz


def welcome_bot(data):
    first1 = "nick='"
    first2 = (data.find(first1) + len(first1))
    repz = data[first2 : data.find("' role=")]
    return repz

def activate_game():
    rn = roombot
    while True : 
        data = s1.recv(1024)
        marky = xmlmark.replace('#ROOM#', roombot)
        louisey = marky.replace('#ROOMx#', challenge)
        xmllouise = louisey.replace('#ID#', str(random.randint(1, 999)))
        markyx = xmllouise.replace('#IDx#', str(random.randint(1, 999)))
        if postcount >= 7 : 
            send_keepalive_if_needed()
        elif data.find("<msg type='groupchat'") > 1 and data.find(lastdetermine) < 1 : 
            if Cmess.lower().find('activate_game_session') >= 0 and masternick == '>' : 
                masternick = Cfrom
                wcmeseg = Cmess[(Cmess.find('activate_game_session') + len('activate_game_session')) : len(Cmess)]

                marky = xmlmark.replace('#ROOM#', roombot)
                louisey = marky.replace('#ROOMx#', challenge)
                xmllouise = louisey.replace('#ID#', str(random.randint(1, 999)))
                markyx = xmllouise.replace('#IDx#', str(random.randint(1, 999)))


                post3 = markyx.replace('#MESS#', ('[c00 Systems Online!!!\n[c0c Master: [0cc ' + masternick))
                post2 = post3.replace('#MESSx#', ('[c00 Systems Online!!!\n[c0c Master: [0cc ' + masternick))
                postcount = (postcount + 1)
                s1.send(post2)
                postcount = (postcount + 1)
                round.add((u'\n>>Master Nick ' + Cfrom))
                receive_packets()
                break
            else : 
                pass
            if Cmess.lower().find('unlock') >= 0 and Cfrom == masternick : 

                marky = xmlmark.replace('#ROOM#', roombot)
                louisey = marky.replace('#ROOMx#', challenge)
                xmllouise = louisey.replace('#ID#', str(random.randint(1, 999)))
                markyx = xmllouise.replace('#IDx#', str(random.randint(1, 999)))

                post3 = markyx.replace('#MESS#', '[c00 Systems UNLOCK!!!')
                post2 = post3.replace('#MESSx#', '[c00 Systems UNLOCK!!!')
                postcount = (postcount + 1)
                s1.send(post2)
                round.add(u'\n>>Unlock')
                receive_packets()
                break
            elif Cmess.lower().find('mirror off') >= 0 and Cfrom == masternick : 

                marky = xmlmark.replace('#ROOM#', roombot)
                louisey = marky.replace('#ROOMx#', challenge)
                xmllouise = louisey.replace('#ID#', str(random.randint(1, 999)))
                markyx = xmllouise.replace('#IDx#', str(random.randint(1, 999)))

                post3 = markyx.replace('#MESS#', '[900 MIRROR DEACTIVATED!')
                post2 = post3.replace('#MESSx#', '[900 MIRROR DEACTIVATED!')
                postcount = (postcount + 1)
                s1.send(post2)
                round.add(u'\n>>Mirror off')
                mirrors = 'no'
                receive_packets()
                break
            elif mirrors == 'yes' : 
                marky = xmlmark.replace('#ROOM#', roombot)
                louisey = marky.replace('#ROOMx#', challenge)
                xmllouise = louisey.replace('#ID#', str(random.randint(1, 999)))
                markyx = xmllouise.replace('#IDx#', str(random.randint(1, 999)))
                post3 = markyx.replace('#MESS#', ('[00a ' + Cfrom + ':[000 \n' + Cmess))
                post2 = post3.replace('#MESSx#', ('[00a ' + Cfrom + ':[000 \n' + Cmess))
                postcount = (postcount + 1)
                s1.send(post2)
                postcount = (postcount + 1)
#            round.color = 255
#            round.font = (u'LatinBold12', 12, None)
#            round.add((u'\n' + Cfrom + ':'))
#            round.color = 0
#            round.add((u'\n' + Cmess))
        else : 
            pass
    global masternick, postcount, mirrors

def activate_game_session():
    rn = roombot
    while True : 
        data = s1.recv(1024)
        xmlpost1 = xmlpost.replace('#ROOM#', rn)
        post1 = xmlpost1.replace('#ID#', str(random.randint(1, 99)))
        if postcount >= 6 : 
            send_keepalive_if_needed()
        elif data.find("<msg type='groupchat'") > 1 and data.find(lastdetermine) < 1 : 
            Cmess = send_group_message(data)
            Cfrom = parse_message_sender(data)
            if Cmess.lower().find('activate_game_session') >= 0 and masternick == '>' : 
                masternick = Cfrom
                wcmeseg = Cmess[(Cmess.find('activate_game_session') + len('activate_game_session')) : len(Cmess)]
                xmlpost1 = xmlpost.replace('#ROOM#', roombot)
                post1 = xmlpost1.replace('#ID#', str(random.randint(1, 999)))
                postn = post1.replace('#MESS#', ('[c00 Systems Online!!!\n[c0c Master: [0cc ' + masternick))
                s1.send(postn)
                postcount = (postcount + 1)
                round.add((u'\n>>Master Nick ' + Cfrom))
                receive_packets()
                break
            else : 
                pass
            if Cmess.lower().find('unlock') >= 0 and Cfrom == masternick : 

                marky = xmlmark.replace('#ROOM#', roombot)
                louisey = marky.replace('#ROOMx#', challenge)
                xmllouise = louisey.replace('#ID#', str(random.randint(1, 999)))
                markyx = xmllouise.replace('#IDx#', str(random.randint(1, 999)))

                post3 = markyx.replace('#MESS#', '[c00 Systems UNLOCK!!!')
                post2 = post3.replace('#MESSx#', '[c00 Systems UNLOCK!!!')
                postcount = (postcount + 1)
                s1.send(post2)
                round.add(u'\n>>Unlock')
                receive_packets()
                break
            elif Cmess.lower().find('mirror off') >= 0 and Cfrom == masternick : 

                marky = xmlmark.replace('#ROOM#', roombot)
                louisey = marky.replace('#ROOMx#', challenge)
                xmllouise = louisey.replace('#ID#', str(random.randint(1, 999)))
                markyx = xmllouise.replace('#IDx#', str(random.randint(1, 999)))

                post3 = markyx.replace('#MESS#', '[900 MIRROR DEACTIVATED!')
                post2 = post3.replace('#MESSx#', '[900 MIRROR DEACTIVATED!')
                postcount = (postcount + 1)
                s1.send(post2)
                round.add(u'\n>>Mirror off')
                mirrors = 'no'
                receive_packets()
                break
            elif mirrors == 'yes' : 
                marky = xmlmark.replace('#ROOM#', roombot)
                louisey = marky.replace('#ROOMx#', challenge)
                xmllouise = louisey.replace('#ID#', str(random.randint(1, 999)))
                markyx = xmllouise.replace('#IDx#', str(random.randint(1, 999)))
                post3 = markyx.replace('#MESS#', ('[00a ' + Cfrom + ':[000 \n' + Cmess))
                post2 = post3.replace('#MESSx#', ('[00a ' + Cfrom + ':[000 \n' + Cmess))
                postcount = (postcount + 1)
                if Cfrom == last or Cfrom == name or Cfrom == "type='groupchat" or Cfrom == '' : 
                    passx = 'yeah'
                else : 
                    s1.send(post2)
                    postcount = (postcount + 1)
                    if postcount >= 6 : 
                        send_keepalive_if_needed()
#            round.color = 255
#            round.font = (u'LatinBold12', 12, None)
#            round.add((u'\n' + Cfrom + ':'))
#            round.color = 0
#            round.add((u'\n' + Cmess))
        else : 
            pass
    global masternick, postcount, mirrors


def send_keepalive():
    levjoinx = levjoin.replace('#ROOM#', challenge)
    tobesend2 = levjoinx.replace('#NICK#', name)
    s1.send(tobesend2)


def send_keepalive_if_needed():
    leavemark = leavelouise.replace('#ROOM#', roombot)
    markleave = leavemark.replace('#ROOMx#', challenge)
    byelouise = markleave.replace('#NICK#', last)
    louisebye = byelouise.replace('#NICKx#', name)
    s1.send(louisebye)
    postcount = 0
    global postcount


def leave_room_cleanup():
    xmleave1 = '<iq type="get" id="CSTCR_1286518673_98" to="conference@demo.kolipri.com/amazilia" amaz-protocol="chat">'
    xmleave2 = "<chatuser room='"
    xmleave4 = '\' type="unavailable" /></iq>'
    lroom = (xmleave1 + xmleave2 + challenge + xmleave4)
    s1.send(lroom)
    xmlsr = s1.recv(1024)


def show_status():
    round.add((u'\n>>CHEAT: ' + louisemark))


def stop_game():
    n0t0leave11()
    gmbot = 'stop'
    global gmbot


def show_about():
    globalui.global_msg_query(u'GameCore TRIVIA is currently in a development stage\n with 3500+ questionnaires only, including the GTA,REBUS, etc... \n*A Thousand more questionnaires will be added in the next program update!\n\nFor the Meantime you can create your own Questionnaires!!!!\n\nThe method used in GameCore is RANDOM SHUFFLE it means that your trivia questions are in random and it will never repeat during the game, Once the Questionnaires in a Category ran out, the GameCore automatically shutdowns. \nEXIT FOR SHORT (LOL).\n\n\nPLEASE BE CAREFULL!!!\nTrivia is editable using Text editor, you can use the program \nXplore to create your own Questions just follow the format\n UniqueNUMBER+ the symbol , + Question + the symbol , followed by the answer. Separate the UniqueNUMBER,  Question and answer by the Symbol , punctuation mark or comma ,  ,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,, this is the symbol comma. GETS? ,,,,,,,,,,,,,,,,,,\n\nEXAMPLE:\n1,Who am I?,LOUISE\n2,I AM,GUNDAM\n3,I love what?,Summon Night\n\nThe UniqueNumber is:\n1\nThe question is:\nWho am I?\nThe answer is:\nLouise\n\nafter creating the question, procede to the next line. \n\nPLEASE DO NOT EVER:\n+ SAVE AS UNICODE\nif you save it as UNICODE, it will never work.\n\nFORBIDDEN CHARACTERS:\n, COMMA = Should only be used in separating the uniqueNUMBER,Question and the Answer\n# = The Python NEGLECT  this symbol\n\n The question files are located at memory card location\n e:/Python\n\nIf you want to contribute for the GameCore Program you can send to us:\n+ Trivia Questionnaires\n+ Rebus\n+ GTA\n+ ANIME(pwde din)\n\n>You can send it to us via:\nMMS @ 09194015811\n    OR via\n Facebook or Email:\n ravemark@yahoo.com\n++DON`T forget to include your name, so that I can put your name in the credits list.\n+ For more info,\n visit Gamers 32\n\nYou cand downloAD:\n=>Xplore   @\nhttp://gundam.wapgem.com\n\nThis are the people who contributed for the game! E.G. Trivia Questionaires, GTA, REBUS, ETC...\n\n* B6|YAM\n* +MSTR|+PIECE+\n* VENOM|Chiz\n* TRiBaL.oNe\n* PARK|"YUIE\n* }PARK{"GHABZ\n* Kickbutt\n* MSTR.C\n* Pistol\n* +PH+ZOIDZ\n* </dadahush>\n* [N]E+AKARI\n\n\n* Mangongopya nalang ako ng mga Questionnaires sa mga Mag RErem0dify ulet ng Program na toh, para hindi na ako mahirapan mag C0DiNG. Ha.Ha.!', u'CREATE NEW QUESTIONS')


def show_about_menu():
    globalui.global_msg_query(u'GUNDAM 00 QUAN[T] \nwith Twin Drive System \n+ Experimental MATH&TRIVIA +\nProgramed by:\n=> ame:ATHRUN\n=> [N]E~SORAn\n=> OP+KILLER\n\nJust Visit\nhttp://gundam.wapgem.com\nfor more updates.\n\nTHIS program is dedicated for the benefit of the UzZAP community!', u'GAME CORE 4.5')


def show_special_thanks():
    globalui.global_msg_query(u'This are the people who contributed for the game! E.G. Trivia Questionaires, GTA, REBUS, ETC...\n\n* B6|YAM\n* +MSTR|+PIECE+\n* VENOM|Chiz\n* TRiBaL.oNe\n* PARK|"YUIE\n* }PARK{"GHABZ\n* Kickbutt\n* MSTR.C\n*HadesTriviabot\n* Pistol\n* +PH+ZOIDZ\n* </dadahush>\n* [N]E+AKARI\n\n\nIf you want to contribute for the GameCore Program you can send to us:\n+ Trivia Questionnaires\n+ Rebus\n+ GTA\n+ ANIME(pwde din)\n\n>You can send it to us via:\nMMS @ 09194015811\n    OR via\n Facebook or Email:\n ravemark@yahoo.com\n++DON`T forget to include your name, so that I can put your name in the credits list.\n+ For more info,\n visit Gamers 32\n\n\n* Mangongopya nalang ako ng mga Questionnaires sa mga Mag RErem0dify ulet ng Program na toh, para hindi na ako mahirapan mag C0DiNG. Ha.Ha.!', u'Special Thanks to:')


def show_help():
    globalui.global_msg_query(u'Just Type in the chatroom the following COMMANDS.\n\nACTIVATE\n* type "activate_game_session" in the chat room to start the program!\n\n++ GAME MODES: ++\nRANDOM QUIZ1\n* generate_addition_question,tt,wh\n\nRANDOM QUIZ2\n* with Trivia&GTA\n\nRANDOM QUIZ3\n* all in 1 game!\n\nRANDOM GTA\n* opm&foreign\n\nTT ON\nPH ON\nTRIVIA ON\nANIME ON\nLOGIC ON\nGTA OPM\nGTA FOREIGN\nMATH ON\nALGEBRA ON\nENGLISH WORDHUNT\nTAGALOG WORDHUNT\n\n++ OTHER CONTROLS:++\nGAME OFF\nCLUE\nREPOST\nCHALLENGE OFF\nVERSION\nLOCK\nUNLOCK\n/challenge Gamers 32\n* 2nd room game participant.\n/wmsg Hello!\n* Welcome Message\n/welcome_bot on\n* welcomeBOT `ON` only in Single room Mode. Do not use it when you are in MultiRoom mode.\n/welcome_bot off\n* Please note that NICKNAME can only be a maximum of 12 letters only\n* if ERROR occurs, just restart the application.\n* The GAMEbot will not work on Clans A B and C due to Special Character ERROR.\n\nWARNING: Do not Press \nthe "CALL END KEY" , cause it will EXIT the application. \nPRESS the "MENU KEY" instead.\n\nJust Visit\nhttp://gundam.wapgem.com\nfor more updates.', u'CONTROL PANEL')


def change_nickname_prompt():
    name = appuifw.query(u'Challenger Nickname \n(MAX 12 characters)', 'text')
    lastdetermine = name
    if len(name) > 12 : 
        round.add(u'\n\n>> ERROR!!! NICKNAME IS TOO LONG!\n      + PLEASE TRY AGAIN!!! +\n')
        name = 'GameCore 4.5'
    else : 
        round.add((u'\n>> Your Challenger Nickname is: ' + name))
    global name, lastdetermine


louiselimit = 100
markcore = ''
louisecore = ''
summonnight = ('A', 'B', 'A', 'A', 'C', 'D', 'E', 'E', 'F', 'G', 'H', 'I', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'O', 'P', 'O', 'Q', 'R', 'E', 'S', 'T', 'U', 'U', 'V', 'W', 'I', 'U', 'X', 'Y', 'Z')
summonnight2 = ('F', 'G', 'H', 'Z', 'P', 'Q', 'R', 'I', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'X', 'Y', 'S', 'T', 'A', 'B', 'C', 'D', 'E', 'U', 'V', 'W')
summonnight3 = ('N', 'E', 'B', 'Y', 'D', 'E', 'Q', 'O', 'F', 'G', 'U', 'H', 'U', 'I', 'J', 'K', 'A', 'O', 'Z', 'M', 'A', 'O', 'P', 'E', 'R', 'I', 'S', 'T', 'U', 'V', 'W', 'A', 'X', 'D', 'L')
marklouaw = ''
markloucw = ''
markloudw = ''
marklouew = ''
markloufw = ''
marklougw = ''
marklouhw = ''
marklouiw = ''
markloujw = ''
markloukw = ''
markloulw = ''
markloumw = ''
marklounw = ''
marklouow = ''
markloupw = ''
marklouqw = ''
marklourw = ''
marklousw = ''
markloutw = ''
marklouuw = ''
marklouvw = ''
marklouww = ''
marklouxw = ''
marklouyw = ''
marklouzw = ''
marklouaa = ''
marklouca = ''
marklouda = ''
marklouea = ''
markloufa = ''
marklouga = ''
marklouha = ''
marklouia = ''
marklouja = ''
craftknight = ('sugar', 'pratty', 'aera', 'dinah', 'summon', 'night', 'sword', 'craft', 'story')
summonnightx = ''
edgefencer = ''
jeaneth = ''
def generate_word_hunt():
    jeaneth = '[C01  TAGALOG WordHunt  ['
    marklouise = 'SummonNight2'
    edgefencer = '[C00 PH WordHunt: ['
    while True : 
        louisetrap1 = get_tagalog_word(random.randint(1, 8820))
        marktrap1 = louisetrap1[0 : len(louisetrap1)]
        louisetrap2 = get_tagalog_word(random.randint(1, 8820))
        marktrap2 = louisetrap2[0 : len(louisetrap2)]
        word3 = get_tagalog_word(random.randint(1, 8820))
        word1 = word3[0 : len(word3)]
        apply_twist(word1)
        louisemark = word1
        if len(marktrap1) == 5 : 
            if len(marktrap2) <= 8 and len(marktrap2) >= 3 : 
                if len(word1) <= 8 and len(word1) >= 3 : 
                    apply_twist(word1)
                    generate_word_hunt_variant()
                    break
                else : 
                    pass
                pass
            else : 
                pass
            pass
    global jeaneth, marklouise, edgefencer, marktrap1, marktrap2, word1, louisemark


def generate_word_hunt_question():
    jeaneth = '[C01  ENGLISH WordHunt  ['
    marklouise = 'SummonNight'
    edgefencer = '[C00 ENG WordHunt: ['
    while True : 
        louisetrap1 = get_english_word(random.randint(1, 22500))
        marktrap1 = louisetrap1[0 : (len(louisetrap1) - 1)]
        louisetrap2 = get_english_word(random.randint(1, 22500))
        marktrap2 = louisetrap2[0 : (len(louisetrap2) - 1)]
        word3 = get_english_word(random.randint(1, 22500))
        word1 = word3[0 : (len(word3) - 1)]
        apply_twist(word1)
        louisemark = word1
        if len(marktrap1) == 5 : 
            if len(marktrap2) <= 8 and len(marktrap2) >= 3 : 
                if len(word1) <= 8 and len(word1) >= 3 : 
                    apply_twist(word1)
                    generate_word_hunt_variant()
                    break
                else : 
                    pass
                pass
            else : 
                pass
            pass
    global jeaneth, marklouise, edgefencer, marktrap1, marktrap2, word1, louisemark


def generate_word_hunt_variant():
    summonnightx = random.choice(craftknight)
    markloua = random.choice(summonnight)
    markloub = random.choice(summonnight2)
    marklouc = random.choice(summonnight3)
    markloud = random.choice(summonnight)
    markloue = random.choice(summonnight2)
    marklouf = random.choice(summonnight3)
    markloug = random.choice(summonnight)
    marklouh = random.choice(summonnight2)
    markloui = random.choice(summonnight3)
    marklouj = random.choice(summonnight)
    marklouk = random.choice(summonnight2)
    markloul = random.choice(summonnight3)
    markloum = random.choice(summonnight)
    markloun = random.choice(summonnight2)
    marklouo = random.choice(summonnight3)
    markloup = random.choice(summonnight)
    marklouq = random.choice(summonnight2)
    marklour = random.choice(summonnight3)
    marklous = random.choice(summonnight)
    marklout = random.choice(summonnight2)
    marklouu = random.choice(summonnight3)
    marklouv = random.choice(summonnight)
    marklouw = random.choice(summonnight2)
    markloux = random.choice(summonnight3)
    marklouy = random.choice(summonnight)
    marklouz = random.choice(summonnight2)
    marklouaw = random.choice(summonnight3)
    markloubw = random.choice(summonnight)
    markloucw = random.choice(summonnight2)
    markloudw = random.choice(summonnight3)
    marklouew = random.choice(summonnight)
    markloufw = random.choice(summonnight2)
    marklougw = random.choice(summonnight3)
    marklouhw = random.choice(summonnight)
    marklouiw = random.choice(summonnight2)
    markloujw = random.choice(summonnight3)
    markloukw = random.choice(summonnight)
    markloulw = random.choice(summonnight2)
    markloumw = random.choice(summonnight3)
    marklounw = random.choice(summonnight)
    marklouow = random.choice(summonnight2)
    markloupw = random.choice(summonnight3)
    marklouqw = random.choice(summonnight)
    marklourw = random.choice(summonnight2)
    marklousw = random.choice(summonnight3)
    markloutw = random.choice(summonnight)
    marklouuw = random.choice(summonnight2)
    marklouvw = random.choice(summonnight3)
    marklouww = random.choice(summonnight)
    marklouxw = random.choice(summonnight2)
    marklouyw = random.choice(summonnight3)
    marklouzw = random.choice(summonnight)
    marklouaa = random.choice(summonnight2)
    marklouba = random.choice(summonnight3)
    marklouca = random.choice(summonnight)
    marklouda = random.choice(summonnight2)
    marklouea = random.choice(summonnight3)
    markloufa = random.choice(summonnight)
    marklouga = random.choice(summonnight2)
    marklouha = random.choice(summonnight3)
    marklouia = random.choice(summonnight)
    marklouja = random.choice(summonnight2)
    word_hunt_answer_check()
    global summonnightx, markloua, markloub, marklouc, markloud, markloue, marklouf, markloug, marklouh, markloui, marklouj, marklouk, markloul, markloum, markloun, marklouo, markloup, marklouq, marklour, marklous, marklout, marklouu, marklouv, marklouw, markloux, marklouy, marklouz, marklouaw, markloubw, markloucw, markloudw, marklouew, markloufw, marklougw, marklouhw, marklouiw, markloujw, markloukw, markloulw, markloumw, marklounw, marklouow, markloupw, marklouqw, marklourw, marklousw, markloutw, marklouuw, marklouvw, marklouww, marklouxw, marklouyw, marklouzw, marklouaa, marklouba, marklouca, marklouda, marklouea, markloufa, marklouga, marklouha, marklouia, marklouja

marktrap1 = ''
marktrap2 = ''
def word_hunt_answer_check():
    marky = xmlmark.replace('#ROOM#', roombot)
    louisey = marky.replace('#ROOMx#', challenge)
    xmllouise = louisey.replace('#ID#', str(random.randint(1, 999)))
    markyx = xmllouise.replace('#IDx#', str(random.randint(1, 999)))
    gundam = random.randint(100, 999)
    sugar = (edgefencer + str(gundam) + ' ' + markloua + markloub + marklouc + markloud + markloue + marklouf + markloug + marklouh + marklouka + louisemark + marklouj + marklouk + markloul + markloum + markloun + marklouo + markloup + marklouq + marklour + marklous + marklout + marklouu + marklouv + marklouw + markloux + marktrap1 + marklouz + marklouaw + markloubw + markloucw + markloudw + marklouew + markloufw + marklougw + marklouhw + marklouiw + markloujw + markloukw + markloulw + markloumw + marklouca + marklouda + marklouea + markloufa + marklouga + marktrap2 + marklouow + markloupw + marklouqw + marklourw + marklousw + markloutw + marklouuw + marklouvw + marklouww + marklouxw + marklouyw + marklouzw + marklouaa + marklouba)
    pratty = (edgefencer + str(gundam) + ' ' + markloua + markloub + marklouc + markloud + markloue + marklouf + markloug + marklouh + marklouka + marktrap1 + marklouj + marklouk + markloul + markloum + markloun + marklouo + markloup + marklouq + marklour + marklous + marklout + marklouu + marklouv + marklouw + markloux + louisemark + marklouz + marklouaw + markloubw + markloucw + markloudw + marklouew + markloufw + marklougw + marklouhw + marklouiw + markloujw + markloukw + markloulw + markloumw + marktrap2 + marklouow + markloupw + marklouqw + marklourw + marklousw + markloutw + marklouuw + marklouvw + marklouww + marklouxw + marklouyw + marklouzw + marklouaa + marklouba + marklouca + marklouda + marklouea + markloufa + marklouga)
    aera = (edgefencer + str(gundam) + ' ' + markloua + markloub + marklouc + markloud + markloue + marklouf + markloug + marklouh + marklouka + marktrap1 + marklouj + marklouk + markloul + markloum + markloun + marklouo + markloup + marklouq + marklour + marklous + marklout + marklouu + marklouv + marklouw + markloux + marktrap2 + marklouz + marklouaw + markloubw + markloucw + markloudw + marklouew + markloufw + marklougw + marklouhw + marklouiw + markloujw + markloukw + markloulw + markloumw + marklouca + marklouda + marklouea + markloufa + marklouga + louisemark + marklouow + markloupw + marklouqw + marklourw + marklousw + markloutw + marklouuw + marklouvw + marklouww + marklouxw + marklouyw + marklouzw + marklouaa + marklouba)
    dinah = (edgefencer + str(gundam) + ' ' + markloua + marklouka + markloub + marklouc + louisemark + markloue + marklouf + markloug + marklouh + markloui + marklouj + marklouk + markloul + markloum + markloun + marklouo + markloup + marklouq + marklour + marktrap1 + marklout + marklouu + marklouv + marklouw + markloux + marklouy + marklouz + marklouaw + markloubw + markloucw + markloudw + marklouew + markloufw + marklougw + marklouhw + marklouiw + markloujw + markloukw + markloulw + markloumw + marklounw + marklouow + markloupw + marklouqw + marklourw + marklousw + marklouca + marklouda + marklouea + markloufa + marklouga + marktrap2 + marklouuw + marklouvw + marklouww + marklouxw + marklouyw + marklouzw + marklouaa + marklouba)
    summon = (edgefencer + str(gundam) + ' ' + markloua + marklouka + markloub + marklouc + marktrap1 + markloue + marklouf + markloug + marklouh + markloui + marklouj + marklouk + markloul + markloum + markloun + marklouo + markloup + marklouq + marklour + louisemark + marklout + marklouu + marklouv + marklouw + markloux + marklouy + marklouz + marklouaw + markloubw + markloucw + markloudw + marklouew + markloufw + marklougw + marklouhw + marklouiw + markloujw + markloukw + markloulw + markloumw + marklounw + marklouow + markloupw + marklouqw + marklourw + marklousw + marktrap2 + marklouuw + marklouvw + marklouww + marklouxw + marklouyw + marklouzw + marklouaa + marklouba + marklouca + marklouda + marklouea + markloufa + marklouga)
    night = (edgefencer + str(gundam) + ' ' + markloua + marklouka + markloub + marklouc + marktrap1 + markloue + marklouf + markloug + marklouh + markloui + marklouj + marklouk + markloul + markloum + markloun + marklouo + markloup + marklouq + marklour + marktrap2 + marklout + marklouu + marklouv + marklouw + markloux + marklouy + marklouz + marklouaw + markloubw + markloucw + markloudw + marklouew + markloufw + marklougw + marklouhw + marklouiw + markloujw + markloukw + markloulw + markloumw + marklounw + marklouow + markloupw + marklouqw + marklourw + louisemark + marklouuw + marklouvw + marklouww + marklouxw + marklouyw + marklouzw + marklouaa + marklouba + marklouca + marklouda + marklouea + markloufa + marklouga)
    sword = (edgefencer + str(gundam) + ' ' + markloua + markloub + marklouc + markloud + markloue + marklouf + markloug + marklouh + marklouka + markloui + marklouj + marklouk + markloul + markloum + markloun + marklouo + louisemark + marklouq + marklour + marklous + marklout + marklouu + marklouv + marklouw + marktrap1 + marklouy + marklouz + marklouaw + markloubw + markloucw + markloudw + marklouew + markloufw + marklougw + marklouhw + marklouiw + marktrap2 + markloukw + markloulw + markloumw + marklounw + marklouow + markloupw + marklouqw + marklourw + marklousw + markloutw + marklouuw + marklouvw + marklouww + marklouxw + marklouyw + marklouzw + marklouaa + marklouba + marklouca + marklouda + marklouea + markloufa + marklouga)
    craft = (edgefencer + str(gundam) + ' ' + markloua + markloub + marklouc + markloud + markloue + marklouf + markloug + marklouh + marklouka + markloui + marklouj + marklouk + markloul + markloum + markloun + marklouo + marktrap1 + marklouq + marklour + marklous + marklout + marklouu + marklouv + marklouw + louisemark + marklouy + marklouz + marklouaw + markloubw + markloucw + markloudw + marklouew + markloufw + marklougw + marklouhw + marklouiw + marktrap2 + markloukw + markloulw + markloumw + marklounw + marklouow + markloupw + marklouqw + marklourw + marklousw + markloutw + marklouuw + marklouvw + marklouww + marklouxw + marklouyw + marklouzw + marklouaa + marklouba + marklouca + marklouda + marklouea + markloufa + marklouga)
    story = (edgefencer + str(gundam) + ' ' + markloua + markloub + marklouc + markloud + markloue + marklouf + markloug + marklouh + marklouka + markloui + marklouj + marklouk + markloul + markloum + markloun + marklouo + marktrap1 + marklouq + marklour + marklous + marklout + marklouu + marklouv + marklouw + marktrap2 + marklouy + marklouz + marklouaw + markloubw + markloucw + markloudw + marklouew + markloufw + marklougw + marklouhw + marklouiw + louisemark + markloukw + markloulw + markloumw + marklounw + marklouow + markloupw + marklouqw + marklourw + marklousw + markloutw + marklouuw + marklouvw + marklouww + marklouxw + marklouyw + marklouzw + marklouaa + marklouba + marklouca + marklouda + marklouea + markloufa + marklouga)
    if summonnightx == 'sugar' : 
        post3 = markyx.replace('#MESS#', sugar)
        post2 = post3.replace('#MESSx#', sugar)
        postcount = (postcount + 1)        s1.send(post2)
        if postcount >= 6 : 
            send_keepalive_if_needed()
        pass
    if summonnightx == 'pratty' : 
        post3 = markyx.replace('#MESS#', pratty)
        post2 = post3.replace('#MESSx#', pratty)
        postcount = (postcount + 1)
        s1.send(post2)
        if postcount >= 6 : 
            send_keepalive_if_needed()
        pass
    if summonnightx == 'aera' : 
        post3 = markyx.replace('#MESS#', aera)
        post2 = post3.replace('#MESSx#', aera)
        postcount = (postcount + 1)
        s1.send(post2)
        if postcount >= 6 : 
            send_keepalive_if_needed()
        pass
    if summonnightx == 'dinah' : 
        post3 = markyx.replace('#MESS#', dinah)
        post2 = post3.replace('#MESSx#', dinah)
        postcount = (postcount + 1)
        s1.send(post2)
        if postcount >= 6 : 
            send_keepalive_if_needed()
        pass
    if summonnightx == 'summon' : 
        post3 = markyx.replace('#MESS#', summon)
        post2 = post3.replace('#MESSx#', summon)
        postcount = (postcount + 1)
        s1.send(post2)
        if postcount >= 6 : 
            send_keepalive_if_needed()
        pass
    if summonnightx == 'night' : 
        post3 = markyx.replace('#MESS#', night)
        post2 = post3.replace('#MESSx#', night)
        postcount = (postcount + 1)
        s1.send(post2)
        if postcount >= 6 : 
            send_keepalive_if_needed()
        pass
    if summonnightx == 'sword' : 
        post3 = markyx.replace('#MESS#', sword)
        post2 = post3.replace('#MESSx#', sword)
        postcount = (postcount + 1)
        s1.send(post2)
        if postcount >= 6 : 
            send_keepalive_if_needed()
        pass
    if summonnightx == 'craft' : 
        post3 = markyx.replace('#MESS#', craft)
        post2 = post3.replace('#MESSx#', craft)
        postcount = (postcount + 1)
        s1.send(post2)
        if postcount >= 6 : 
            send_keepalive_if_needed()
        pass
    if summonnightx == 'story' : 
        post3 = markyx.replace('#MESS#', story)
        post2 = post3.replace('#MESSx#', story)
        postcount = (postcount + 1)
        s1.send(post2)
        if postcount >= 6 : 
            send_keepalive_if_needed()
        pass
    global postcount


markread = u'e:\\Python\\Zgen-info.txt'
louisetrivia = open(markread, 'r')
marktrivia = louisetrivia.readlines()
louisetrivia.close()
data = []
markquest = ''
qcount = 0
louiselow = 'Mark Louise'

# ===========================================================================
# TRIVIA / GTA / ANIME
# ===========================================================================
def generate_trivia_question():
    marklouise = 'generate_trivia_question'
    from string import strip as strip
    data = []
    random.shuffle(marktrivia)
    n = 0
    for line in marktrivia:
        data.append(tuple(map(strip, line.split(','))))
        rd = data[0][0]
        markquest = data[0][1]
        word1 = data[0][2]
        apply_twist(word1)
        louisemark = word1.upper()
        louiselow = word1.lower()
        if len(markdecoy) == 0 : 
            markdecoy[len(markdecoy) : 0] = [rd]
            qcount = (qcount + 1)
            repost_trivia()
            break
        else : 
            for i in range(len(markdecoy)):
                if markdecoy[i] == rd : 
                    if markxxxxlouise == 'random3' : 
                        generate_trivia_question()
                        break
                    else : 
                        generate_trivia_question()
                        break
                    pass
                elif i >= (len(markdecoy) - 1) : 
                    if len(markquest) >= 101 : 
                        generate_trivia_question()
                    else : 
                        markdecoy[len(markdecoy) : 0] = [rd]
                        qcount = (qcount + 1)
                        repost_trivia()
                    pass
            break
    global marklouise, rd, markquest, word1, louisemark, louiselow, qcount


def repost_trivia():
    marky = xmlmark.replace('#ROOM#', roombot)
    louisey = marky.replace('#ROOMx#', challenge)
    xmllouise = louisey.replace('#ID#', str(random.randint(1, 999)))
    markyx = xmllouise.replace('#IDx#', str(random.randint(1, 999)))
    post3 = markyx.replace('#MESS#', markquest)
    post2 = post3.replace('#MESSx#', markquest)
    postcount = (postcount + 1)
    s1.send(post2)
    if postcount >= 6 : 
        send_keepalive_if_needed()
    global postcount


def clue_trivia():
    marky = xmlmark.replace('#ROOM#', roombot)
    louisey = marky.replace('#ROOMx#', challenge)
    xmllouise = louisey.replace('#ID#', str(random.randint(1, 999)))
    markyx = xmllouise.replace('#IDx#', str(random.randint(1, 999)))
    triviamark = ('+ TRIVIA  ~>  [' + str(louisescore) + 'pts] +' + '\nHiNT: ' + clue)
    markylou = ('[C0c + TRIVIA  ~>  [' + str(louisescore) + 'pts] +' + '\n[567 HiNT: [0C0 ' + clue)
    post3 = markyx.replace('#MESS#', triviamark)
    post2 = post3.replace('#MESSx#', triviamark)
    post3x = markyx.replace('#MESS#', markylou)
    post2x = post3x.replace('#MESSx#', markylou)
    postcount = (postcount + 1)
    if len(louisemark) >= 15 : 
        s1.send(post2)
    else : 
        s1.send(post2x)
    if postcount >= 6 : 
        send_keepalive_if_needed()
    global postcount


gtaforeignpath = u'e:\\Python\\Zgta-foreign.txt'
generate_gta_foreign_question = open(gtaforeignpath, 'r')
gtaforeignread = generate_gta_foreign_question.readlines()
generate_gta_foreign_question.close()
gtadecoy1 = []
def generate_gta_foreign_question():
    marklouise = 'generate_gta_foreign_question'
    from string import strip as strip
    data = []
    random.shuffle(gtaforeignread)
    n = 0
    for line in gtaforeignread:
        data.append(tuple(map(strip, line.split(','))))
        rd = data[0][0]
        markquest = data[0][1]
        word1 = data[0][2]
        apply_twist(word1)
        louisemark = word1.upper()
        louiselow = word1.lower()
        if len(gtadecoy1) == 0 : 
            gtadecoy1[len(gtadecoy1) : 0] = [rd]
            qcount = (qcount + 1)
            repost_gta_foreign_variant()
            break
        else : 
            for i in range(len(gtadecoy1)):
                if gtadecoy1[i] == rd : 
                    if markxxxxlouise == 'random3' : 
                        generate_trivia_question()
                        break
                    else : 
                        generate_gta_foreign_question()
                        break
                    pass
                elif i >= (len(gtadecoy1) - 1) : 
                    gtadecoy1[len(gtadecoy1) : 0] = [rd]
                    qcount = (qcount + 1)
                    repost_gta_foreign_variant()
            break
    global marklouise, rd, markquest, word1, louisemark, louiselow, qcount


gtaopmpath = u'e:\\Python\\Zgta-opm.txt'
generate_gta_opm_question = open(gtaopmpath, 'r')
gtaopmread = generate_gta_opm_question.readlines()
generate_gta_opm_question.close()
gtadecoy2 = []
def generate_gta_opm_question():
    marklouise = 'generate_gta_opm_question'
    from string import strip as strip
    data = []
    random.shuffle(gtaopmread)
    n = 0
    for line in gtaopmread:
        data.append(tuple(map(strip, line.split(','))))
        rd = data[0][0]
        markquest = data[0][1]
        word1 = data[0][2]
        apply_twist(word1)
        louisemark = word1.upper()
        louiselow = word1.lower()
        if len(gtadecoy2) == 0 : 
            gtadecoy2[len(gtadecoy2) : 0] = [rd]
            qcount = (qcount + 1)
            repost_gta_foreign_variant()
            break
        else : 
            for i in range(len(gtadecoy2)):
                if gtadecoy2[i] == rd : 
                    if markxxxxlouise == 'random3' : 
                        generate_trivia_question()
                        break
                    else : 
                        generate_gta_opm_question()
                        break
                    pass
                elif i >= (len(gtadecoy2) - 1) : 
                    gtadecoy2[len(gtadecoy2) : 0] = [rd]
                    qcount = (qcount + 1)
                    repost_gta_foreign_variant()
            break
    global marklouise, rd, markquest, word1, louisemark, louiselow, qcount


def repost_gta_foreign_variant():
    marky = xmlmark.replace('#ROOM#', roombot)
    louisey = marky.replace('#ROOMx#', challenge)
    xmllouise = louisey.replace('#ID#', str(random.randint(1, 999)))
    markyx = xmllouise.replace('#IDx#', str(random.randint(1, 999)))
    gta = ('TiTLE: [900 `' + markquest + '`\n~> [c0c Guess The Artist')
    post3 = markyx.replace('#MESS#', gta)
    post2 = post3.replace('#MESSx#', gta)
    postcount = (postcount + 1)
    s1.send(post2)
    if postcount >= 6 : 
        send_keepalive_if_needed()
    global postcount


def repost_gta_foreign():
    marky = xmlmark.replace('#ROOM#', roombot)
    louisey = marky.replace('#ROOMx#', challenge)
    xmllouise = louisey.replace('#ID#', str(random.randint(1, 999)))
    markyx = xmllouise.replace('#IDx#', str(random.randint(1, 999)))
    triviamark = (('GTA: "' + markquest + '"\n') + str(louisescore) + 'pts: ' + clue)
    gta = (('GTA: "' + markquest + '"\n') + str(louisescore) + 'pts: [0C0 ' + clue)
    post3 = markyx.replace('#MESS#', gta)
    post2 = post3.replace('#MESSx#', gta)
    post3x = markyx.replace('#MESS#', triviamark)
    post2x = post3x.replace('#MESSx#', triviamark)
    if len(louisemark) >= 22 or len(markquest) >= 22 : 
        s1.send(post2x)
    else : 
        s1.send(post2)
    postcount = (postcount + 1)
    if postcount >= 6 : 
        send_keepalive_if_needed()
    global postcount


markanime = u'e:\\Python\\Zanime-trivia.txt'
louiseanime = open(markanime, 'r')
animemark = louiseanime.readlines()
louiseanime.close()
animedecoy = []
def generate_anime_trivia():
    marklouise = 'anime'
    from string import strip as strip
    data = []
    random.shuffle(animemark)
    n = 0
    for line in animemark:
        data.append(tuple(map(strip, line.split(','))))
        rd = data[0][0]
        markquest = data[0][1]
        word1 = data[0][2]
        apply_twist(word1)
        louisemark = word1.upper()
        louiselow = word1.lower()
        if len(animedecoy) == 0 : 
            animedecoy[len(animedecoy) : 0] = [rd]
            qcount = (qcount + 1)
            repost_trivia()
            break
        else : 
            for i in range(len(animedecoy)):
                if animedecoy[i] == rd : 
                    generate_anime_trivia()
                    break
                elif i >= (len(animedecoy) - 1) : 
                    if len(markquest) >= 101 : 
                        generate_anime_trivia()
                    else : 
                        animedecoy[len(animedecoy) : 0] = [rd]
                        qcount = (qcount + 1)
                        repost_trivia()
                    pass
            break
    global marklouise, rd, markquest, word1, louisemark, louiselow, qcount


def clue_anime_trivia():
    marky = xmlmark.replace('#ROOM#', roombot)
    louisey = marky.replace('#ROOMx#', challenge)
    xmllouise = louisey.replace('#ID#', str(random.randint(1, 999)))
    markyx = xmllouise.replace('#IDx#', str(random.randint(1, 999)))
    triviamark = ('ANiME TRiVIA ~>  [' + str(louisescore) + 'pts]' + '\nHiNT: ' + clue)
    markylou = ('[C0c ANiME TRiVIA ~>  [' + str(louisescore) + 'pts]' + '\n[567 HiNT: [0C0 ' + clue)
    post3 = markyx.replace('#MESS#', triviamark)
    post2 = post3.replace('#MESSx#', triviamark)
    post3x = markyx.replace('#MESS#', markylou)
    post2x = post3x.replace('#MESSx#', markylou)
    postcount = (postcount + 1)
    if len(louisemark) >= 15 : 
        s1.send(post2)
    else : 
        s1.send(post2x)
    if postcount >= 6 : 
        send_keepalive_if_needed()
    global postcount



# ===========================================================================
# RANDOM GAME SELECTION
# ===========================================================================
def select_random_game():

    if marklouise == 'generate_algebra_1' : 
        generate_algebra_1()
    if marklouise == 'generate_algebra_2' : 
        generate_algebra_2()
    if marklouise == 'generate_algebra_3' : 
        generate_algebra_3()

    if marklouise == 'generate_trivia_question' : 
        generate_trivia_question()
    if marklouise == 'generate_logic_question' : 
        generate_logic_question()
    if marklouise == 'anime' : 
        generate_anime_trivia()
    if marklouise == 'generate_gta_foreign_question' : 
        generate_gta_foreign_question()
    if marklouise == 'generate_gta_opm_question' : 
        generate_gta_opm_question()
    if marklouise == 'SummonNight' : 
        generate_word_hunt_question()
    if marklouise == 'SummonNight2' : 
        generate_word_hunt()
    if marklouise == 'filipino' : 
        generate_tagalog_question()
    if marklouise == 'add' : 
        generate_addition_question()
    if marklouise == 'minus' : 
        generate_subtraction_question()
    if marklouise == 'multiply' : 
        generate_multiplication_question()
    if marklouise == 'love' : 
        generate_love_word_question()
    if marklouise == 'add1' : 
        generate_addition_variant()
    if marklouise == 'minus1' : 
        generate_subtraction_variant()
    if marklouise == 'multiply1' : 
        generate_multiplication_variant()


def select_random_game_variant():
    if markxxxxlouise == 'randomgta' : 
        marklouisen = random.choice(randomgta)
        marklouise = marklouisen
        select_random_game()
    if markxxxxlouise == 'algebra' : 
        marklouisen = random.choice(algebrax)
        marklouise = marklouisen
        select_random_game()
    if markxxxxlouise == 'random' : 
        marklouisen = random.choice(random1)
        marklouise = marklouisen
        select_random_game()
    if markxxxxlouise == 'random3' : 
        marklouisen = random.choice(random2)
        marklouise = marklouisen
        select_random_game()
    if markxxxxlouise == 'random4' : 
        marklouisen = random.choice(random3)
        marklouise = marklouisen
        select_random_game()
    if markxxxxlouise == 'generate_addition_question' : 
        marklouisen = random.choice(mathx)
        marklouise = marklouisen
        select_random_game()
    if markxxxxlouise == 'texttwist' : 
        select_random_game()
    if markxxxxlouise == 'wordhunt' : 
        select_random_game()
    if markxxxxlouise == 'tagaloghunt' : 
        select_random_game()
    if markxxxxlouise == 'generate_tagalog_question' : 
        select_random_game()
    if markxxxxlouise == 'gen-info-trivia' : 
        select_random_game()
    if markxxxxlouise == 'generate_gta_foreign_question' : 
        select_random_game()
    if markxxxxlouise == 'generate_gta_opm_question' : 
        select_random_game()
    if markxxxxlouise == 'anime' : 
        select_random_game()
    if markxxxxlouise == 'generate_logic_question' : 
        select_random_game()
    global marklouise

def check_correct_answer():
    marky = xmlmark.replace('#ROOM#', roombot)
    louisey = marky.replace('#ROOMx#', challenge)
    xmllouise = louisey.replace('#ID#', str(random.randint(1, 999)))
    louiselouise = ('[c0c The Correct Answer is:  [900 ' + word1 + '  :>')
    markyx = xmllouise.replace('#IDx#', str(random.randint(1, 999)))
    post3 = markyx.replace('#MESS#', louiselouise)
    post2 = post3.replace('#MESSx#', louiselouise)
    postcount = (postcount + 1)
    s1.send(post2)
    e32.ao_sleep(2)
    if postcount >= 6 : 
        send_keepalive_if_needed()
    louisescore = 10
    select_random_game()
    global postcount, louisescore


logicpath = u'e:\\Python\\Zlogic.txt'
generate_logic_question = open(logicpath, 'r')
logicread = generate_logic_question.readlines()
generate_logic_question.close()
logicdecoy = []


# ===========================================================================
# LOGIC / ALGEBRA
# ===========================================================================
def generate_logic_question():
    marklouise = 'generate_logic_question'
    from string import strip as strip
    data = []
    random.shuffle(logicread)
    n = 0
    for line in logicread:
        data.append(tuple(map(strip, line.split(','))))
        rd = data[0][0]
        markquest = data[0][1]
        word1 = data[0][2]
        apply_twist(word1)
        louisemark = word1.upper()
        louiselow = word1.lower()
        if len(logicdecoy) == 0 : 
            logicdecoy[len(logicdecoy) : 0] = [rd]
            qcount = (qcount + 1)
            repost_trivia()
            break
        else : 
            for i in range(len(logicdecoy)):
                if logicdecoy[i] == rd : 
                    if markxxxxlouise == 'random3' : 
                        generate_trivia_question()
                        break
                    else : 
                        generate_logic_question()
                        break
                    pass
                elif i >= (len(logicdecoy) - 1) : 
                    if len(markquest) >= 101 : 
                       generate_logic_question()                    else : 
                        logicdecoy[len(logicdecoy) : 0] = [rd]
                        qcount = (qcount + 1)
                        repost_trivia()
                    pass
            break
    global marklouise, rd, markquest, word1, louisemark, louiselow, qcount


def clue_logic():
    marky = xmlmark.replace('#ROOM#', roombot)
    louisey = marky.replace('#ROOMx#', challenge)
    xmllouise = louisey.replace('#ID#', str(random.randint(1, 999)))
    markyx = xmllouise.replace('#IDx#', str(random.randint(1, 999)))
    triviamark = ('+ LoGiC  ~>  [' + str(louisescore) + 'pts] +' + '\nHiNT: [0C0 ' + clue)
    markylou = ('[C0c + LoGiC  ~>  [' + str(louisescore) + 'pts] +' + '\n[567 HiNT: [0C0 ' + clue)
    post3 = markyx.replace('#MESS#', triviamark)
    post2 = post3.replace('#MESSx#', triviamark)
    post3x = markyx.replace('#MESS#', markylou)
    post2x = post3x.replace('#MESSx#', markylou)
    postcount = (postcount + 1)    if len(louisemark) >= 15 : 
        s1.send(post2)
    else : 
        s1.send(post2x)
    if postcount >= 6 : 
        send_keepalive_if_needed()
    global postcount

def generate_algebra_1():
    marklouise = 'generate_algebra_1'
    a1 = random.randint(0, 10)
    a2 = random.randint(1, 10)
    a3 = random.randint(1, 10)
    a4 = random.randint(1, 10)



    word2 = str(a1)
    mark = str(a1)
    louise = str(a2)
    markxxx = str(a3)
    markyyy = str(a4)

    global word2, mark, louise, markxxx, markyyy
    word6 = +a1
    word7 = +a2
    mark6x = +a3
    mark7y = +a4

    word8 = (word6 * mark6x)
    word88 = (word7 * mark7y)
    mariz = (word8 + word88)

    word1 = str(mariz)
    louisemark = str(mariz)
    global word1, louisemark, marklouise
    apply_twist(word1)
    repost_algebra_1()

def repost_algebra_1():
    marky = xmlmark.replace('#ROOM#', roombot)
    louisey = marky.replace('#ROOMx#', challenge)
    xmllouise = louisey.replace('#ID#', str(random.randint(1, 999)))
    markyx = xmllouise.replace('#IDx#', str(random.randint(1, 999)))
    rc1 = random.randint(100, 999)
    ttq = ('`' + '   if  X=' + markxxx + '  &  Y=' + markyyy + '\n[' + str(rc1) + ' ALGEBRA: [000  ' + mark + 'x' + '[c00   +  [000 ' + louise + 'y' + ' = [c00 ?')
    post3 = markyx.replace('#MESS#', ttq)
    post2 = post3.replace('#MESSx#', ttq)
    postcount = (postcount + 1)
    s1.send(post2)
    if postcount >= 6 : 
        send_keepalive_if_needed()
    global postcount

algebrax = ('generate_algebra_1', 'generate_algebra_2', 'generate_algebra_3')

def generate_algebra_2():
    marklouise = 'generate_algebra_2'
    a1 = random.randint(0, 10)
    a2 = random.randint(1, 10)
    a3 = random.randint(1, 10)
    a4 = random.randint(1, 10)
    word2 = str(a1)
    mark = str(a1)
    louise = str(a2)
    markxxx = str(a3)
    markyyy = str(a4)
    global word2, mark, louise, markxxx, markyyy
    word6 = +a1
    word7 = +a2
    mark6x = +a3
    mark7y = +a4

    word8 = (word6 * mark6x)
    word88 = (word7 * mark7y)
    mariz = (word8 - word88)

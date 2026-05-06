import streamlit as st
import pandas as pd
import random, os
from datetime import date

# ── 페이지 설정 (사이드바 기본 표시로 변경) ──────────────────────────────────────────────
st.set_page_config(page_title="두류 테니스", page_icon="🎾",
                    layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;600;700;900&display=swap');
html,body,[class*="css"],button,input{font-family:'Noto Sans KR',sans-serif!important}
.block-container{padding:1.5rem 2rem 2rem!important;max-width:100%!important}

/* 사이드바 스타일링 */
[data-testid="stSidebar"] {
    background-color: #f8f9fa;
    border-right: 1px solid #e9ecef;
}
[data-testid="stSidebar"] .stRadio > div {
    gap: 10px;
}
/* 사이드바 메뉴 버튼처럼 보이게 */
div[data-testid="stSidebar"] .stRadio label {
    background: white;
    border: 1px solid #dee2e6;
    border-radius: 10px;
    padding: 10px 15px !important;
    margin-bottom: 5px;
    transition: all 0.2s;
    font-weight: 600 !important;
    color: #444 !important;
}
div[data-testid="stSidebar"] .stRadio label:hover {
    border-color: #1e88e5;
    background: #f0f7ff;
}
div[data-testid="stSidebar"] .stRadio div[role="radiogroup"] > div[data-bv-tab="true"] {
    background: transparent !important;
}

/* 탭 스타일 */
button[data-baseweb="tab"]{font-size:1.05rem!important;font-weight:700!important;padding:10px 20px!important;border-radius:10px 10px 0 0!important;white-space:nowrap!important}
button[data-baseweb="tab"][aria-selected="true"]{background:linear-gradient(135deg,#1565c0,#1e88e5)!important;color:#fff!important}

/* 버튼 */
.stButton>button{border-radius:10px!important;font-weight:700!important;transition:all .2s!important}
.stButton>button:hover{transform:translateY(-1px);box-shadow:0 4px 12px rgba(0,0,0,.15)!important}

/* 숫자 입력 가운데 */
input[type="number"]{text-align:center!important;font-size:1.2rem!important;font-weight:700!important}
div[data-testid="stNumberInput"] input{font-size:1.3rem!important;font-weight:900!important;text-align:center!important}

/* 테이블 가운데 */
th,td{text-align:center!important;vertical-align:middle!important}

/* 타이틀 */
.main-title{text-align:left;font-size:clamp(1.4rem,5vw,2.2rem);font-weight:900;
  background:linear-gradient(135deg,#1565c0,#42a5f5);-webkit-background-clip:text;
  -webkit-text-fill-color:transparent;background-clip:text;margin-bottom:1.5rem}
.sec-title{font-size:clamp(.95rem,3.5vw,1.2rem);font-weight:900;color:#1565c0;
  border-left:5px solid #42a5f5;padding-left:11px;margin:14px 0 8px}

/* 팀 도형 */
.team-shape-wrap{display:flex;flex-direction:column;align-items:center;gap:5px;padding:8px 4px}
.team-shape{border-radius:14px;padding:9px 13px;text-align:center;font-weight:800;
  font-size:clamp(.76rem,2.4vw,.98rem);box-shadow:0 4px 12px rgba(0,0,0,.13);
  min-width:86px;line-height:1.4;word-break:keep-all}
.sg{background:linear-gradient(135deg,#43a047,#1b5e20);color:#fff}
.sb{background:linear-gradient(135deg,#1e88e5,#0d47a1);color:#fff}
.so{background:linear-gradient(135deg,#fb8c00,#e65100);color:#fff}
.sp{background:linear-gradient(135deg,#8e24aa,#4a148c);color:#fff}
.sr{background:linear-gradient(135deg,#e53935,#b71c1c);color:#fff}
.st{background:linear-gradient(135deg,#00897b,#004d40);color:#fff}
.vs-badge{background:linear-gradient(135deg,#e53935,#b71c1c);color:#fff;border-radius:50%;
  width:34px;height:34px;display:flex;align-items:center;justify-content:center;
  font-weight:900;font-size:.82rem;margin:3px auto;box-shadow:0 3px 8px rgba(229,57,53,.4)}
.round-hdr{background:linear-gradient(90deg,#1565c0,#42a5f5);color:#fff;border-radius:9px;
  padding:6px 15px;font-size:clamp(.84rem,2.8vw,.98rem);font-weight:800;
  margin:13px 0 7px;text-align:center}
.match-wrap{background:#fff;border-radius:13px;padding:9px 7px 11px;margin:5px 0;
  box-shadow:0 3px 10px rgba(0,0,0,.09);border:1.5px solid #e3eaf5}

/* 참가확인 카드 */
.acard{background:#f0f7ff;border:1.5px solid #90caf9;border-radius:11px;padding:9px 13px;
  margin:3px 0;display:flex;align-items:center;gap:9px;
  font-size:clamp(.86rem,2.8vw,.98rem);font-weight:600}
.aok{border-color:#66bb6a;background:#f1f8e9}
.ano{border-color:#ef9a9a;background:#fff3f3}
.matrix-wrap{overflow-x:auto;-webkit-overflow-scrolling:touch}
@media(max-width:640px){
  .block-container{padding:.5rem .5rem 2rem!important}
  .team-shape{min-width:68px;padding:7px 7px}
}
</style>
""", unsafe_allow_html=True)

# ── 파일 초기화 ──────────────────────────────────────────────
RANK_FILE = "ranking_master.csv"
HIST_FILE = "history_master.csv"
TOUR_FILE = "tournaments.csv"
ATND_FILE = "attendance.csv"

for f, cols in [
    (RANK_FILE, ["이름","현재포인트","이전포인트"]),
    (HIST_FILE, ["날짜","대회명","그룹","이름","그룹순위","획득포인트"]),
    (TOUR_FILE, ["대회명","날짜","장소","방식","상태"]),
    (ATND_FILE, ["대회명","이름","참가확인"]),
]:
    if not os.path.exists(f):
        pd.DataFrame(columns=cols).to_csv(f, index=False)

# ── 데이터 함수 ──────────────────────────────────────────────
def load_rank():
    df = pd.read_csv(RANK_FILE)
    for c in ["현재포인트","이전포인트"]:
        df[c] = pd.to_numeric(df.get(c,0), errors="coerce").fillna(0).astype(int)
    return df

def save_rank(df):
    df.sort_values("현재포인트",ascending=False).reset_index(drop=True).to_csv(RANK_FILE,index=False)

def load_hist(): return pd.read_csv(HIST_FILE)
def save_hist(df): df.to_csv(HIST_FILE,index=False)
def load_tour(): return pd.read_csv(TOUR_FILE)
def save_tour(df): df.to_csv(TOUR_FILE,index=False)

# ── 컬럼 유연 인식 ────────────────────────────────────────────
NAME_KW  = ["이름","name","선수","player","성명","회원","member","참가자","닉네임","nick"]
PT_KW    = ["포인트","point","pts","점수","score","랭킹","ranking","현재","current"]
PREV_KW  = ["이전","prev","before","old","기존","previous","지난"]

def find_col(cols, kws):
    for kw in kws:
        for c in cols:
            if kw in c: return c
    return None

def smart_read(file):
    try:
        df = pd.read_csv(file,encoding_errors="replace") if file.name.endswith(".csv") else pd.read_excel(file)
    except Exception as e:
        st.error(f"파일 읽기 실패: {e}"); return None
    orig = list(df.columns)
    df.columns = [str(c).lower().strip().replace(" ","") for c in df.columns]
    norm = list(df.columns)
    nc = find_col(norm, NAME_KW)
    pc, prc = None, None
    for c in norm:
        is_prev = any(kw in c for kw in PREV_KW)
        is_pt   = any(kw in c for kw in PT_KW)
        if is_pt:
            if is_prev: prc = c
            elif pc is None: pc = c
            elif prc is None: prc = c
    with st.expander("📋 컬럼 인식 결과"):
        st.write(f"원본: {orig}")
        st.write(f"이름→[{nc}] | 현재포인트→[{pc}] | 이전포인트→[{prc}]")
    if nc is None:
        st.error(f"❌ 이름 컬럼 없음. 컬럼: {orig}")
        st.info("컬럼명에 '이름','name','선수','회원' 중 하나를 포함하세요."); return None
    df["이름"]     = df[nc].astype(str).str.strip().str.replace(" ","")
    df["현재포인트"] = pd.to_numeric(df[pc],errors="coerce").fillna(0).astype(int) if pc else 0
    df["이전포인트"] = pd.to_numeric(df[prc],errors="coerce").fillna(0).astype(int) if prc else 0
    df = df[["이름","현재포인트","이전포인트"]]
    df = df[df["이름"].str.len()>0][df["이름"]!="nan"].drop_duplicates("이름")
    return df

# ── 한울 KDK 데이터 ───────────────────────────────────────────
HANUL = {
    3:{4:["14:23","13:24","12:34"],8:["12:34","56:78","18:27","36:45","14:58","23:67"]},
    4:{5:["12:34","13:25","14:35","15:24","23:45"],6:["13:24","15:46","23:56","14:35","26:34","16:25"],
       7:["12:34","56:17","23:57","14:67","35:24","16:25","46:37"],
       8:["12:34","56:78","13:57","24:68","15:26","37:48","16:38","25:47"],
       9:["12:34","56:78","19:57","23:68","49:38","15:26","36:45","17:89","24:79"],
       10:["12:35","67:8A","23:46","78:19","34:57","89:2A","45:68","13:9A","56:79","1A:24"],
       11:["12:35","67:8A","49:1B","23:68","45:7A","9B:26","13:7B","48:59","1A:28","47:6B","39:5A"]},
}

def spl(s,n):
    res=[]; i=0
    while i<len(s):
        c=s[i]
        if c=='A': res.append(9);i+=1
        elif c=='B': res.append(10);i+=1
        elif c=='C': res.append(11);i+=1
        elif i+1<len(s) and s[i:i+2].isdigit() and 10<=int(s[i:i+2])<=n:
            res.append(int(s[i:i+2])-1);i+=2
        else: res.append(int(c)-1);i+=1
    return res

def make_kdk_hanul(players, gc):
    data = HANUL.get(gc,{}).get(len(players))
    if not data: return None
    sh = random.sample(players,len(players))
    rounds=[]
    for ms in data:
        l,r=ms.split(":")
        rounds.append([([sh[i] for i in spl(l,len(players))],[sh[i] for i in spl(r,len(players))])])
    return rounds

def make_rr(teams):
    teams=[list(t) for t in teams]
    matches=[(teams[i],teams[j]) for i in range(len(teams)) for j in range(i+1,len(teams))]
    random.shuffle(matches)
    rounds=[]
    while matches:
        used,r=set(),[]
        for m in matches[:]:
            flat=tuple(sum(m,[]))
            if not(set(flat)&used): r.append(m);used.update(flat);matches.remove(m)
        if not r: break
        rounds.append(r)
    return rounds

# ── 유틸 ─────────────────────────────────────────────────────
GCLS = ["sg","sb","so","sp","sr","st"]
GLBL = ["🟢","🔵","🟠","🟣","🔴","🩵"]
GHEX = ["#43a047","#1e88e5","#fb8c00","#8e24aa","#e53935","#00897b"]
POINT_TABLE = {1:7,2:5,3:3}; ATTEND_PT=1

def gcol(i): return GCLS[i%len(GCLS)]
def ghex(i): return GHEX[i%len(GHEX)]
def tname(t): t=list(t); return " & ".join(t) if len(t)>1 else t[0]
def clean(x): return str(x).strip().replace(" ","")
def calc_pt(rank): return POINT_TABLE.get(rank,ATTEND_PT)

def shape_html(players,cls):
    return f'<div class="team-shape {cls}">{"<br>".join(players)}</div>'

# ── 상태 초기화 ───────────────────────────────────────────────
def init():
    defaults={"players":[],"groups":{},"modes":{},"game_counts":{},"schedule":{},
              "scores":{},"is_admin":False,"t_name":"정기 대회",
              "t_date":str(date.today()),"t_place":"","attendance":{}}
    for k,v in defaults.items():
        if k not in st.session_state: st.session_state[k]=v
init()
S=st.session_state

# ── 매트릭스 그리기 ───────────────────────────────────────────
def draw_matrix(g, gidx):
    sched=S.schedule.get(g,[])
    teams_list,seen=[],set()
    for rd in sched:
        for t1,t2 in rd:
            for t in [tuple(t1),tuple(t2)]:
                if t not in seen: teams_list.append(t);seen.add(t)
    stats={t:{"승":0,"패":0,"득실":0} for t in teams_list}
    matrix={t:{o:"-" for o in teams_list if o!=t} for t in teams_list}
    for sd in S.scores.values():
        if sd.get("group")!=g: continue
        t1,t2=tuple(sd["t1"]),tuple(sd["t2"]); s1,s2=sd["s1"],sd["s2"]
        for my,op,ms,os_ in [(t1,t2,s1,s2),(t2,t1,s2,s1)]:
            if my in stats:
                if ms>os_: stats[my]["승"]+=1
                else: stats[my]["패"]+=1
                stats[my]["득실"]+=(ms-os_)
            if my in matrix and op in matrix[my]: matrix[my][op]=f"{ms}:{os_}"
    ranked=sorted(teams_list,key=lambda t:(-stats[t]["승"],-stats[t]["득실"]))
    labels=[tname(t) for t in ranked]
    mdf=pd.DataFrame({tname(t):{tname(o):("●" if o==t else matrix[t].get(o,"-")) for o in ranked} for t in ranked}).T
    rdf=pd.DataFrame([{"순위":["🥇","🥈","🥉"][i] if i<3 else i+1,
                        "팀명":tname(t),"승":stats[t]["승"],"패":stats[t]["패"],
                        "득실":f'{stats[t]["득실"]:+d}'} for i,t in enumerate(ranked)])
    hx=ghex(gidx)
    st.markdown(f"<div style='background:{hx}18;border-left:5px solid {hx};border-radius:9px;"
                f"padding:7px 13px;margin-bottom:9px;font-weight:900;color:{hx}'>"
                f"{GLBL[gidx%len(GLBL)]} 그룹 {g} — 전적 현황</div>",unsafe_allow_html=True)
    c1,c2=st.columns([3,2])
    with c1:
        st.markdown("**📋 상대별 전적 매트릭스**")
        st.markdown('<div class="matrix-wrap">',unsafe_allow_html=True)
        st.dataframe(mdf,use_container_width=True)
        st.markdown('</div>',unsafe_allow_html=True)
    with c2:
        st.markdown("**🏅 그룹 순위**")
        st.dataframe(rdf,use_container_width=True,hide_index=True)

# ── 왼쪽 사이드바 네비게이션 (이동된 부분) ──────────────────────────
with st.sidebar:
    st.markdown("<h2 style='text-align:center; color:#1565c0;'>🎾 Duryu Tennis</h2>", unsafe_allow_html=True)
    st.image("https://cdn-icons-png.flaticon.com/512/2853/2853361.png", width=80)
    st.divider()
    
    MENUS={"ranking":"🏆 실시간 랭킹","schedule":"📅 대진표/전적","result":"📊 경기 결과",
           "attend":"✅ 참가확인","admin":"⚙️ 관리자 센터"}
    
    # 딕셔너리 키-값 쌍을 이용해 라디오 버튼 생성
    selected_menu_label = st.radio(
        "MENU",
        options=list(MENUS.values()),
        index=list(MENUS.keys()).index(S.get("menu", "ranking")),
        label_visibility="collapsed"
    )
    
    # 라벨을 다시 키값으로 변환하여 세션 상태 저장
    for k, v in MENUS.items():
        if v == selected_menu_label:
            S["menu"] = k
            break
            
    st.divider()
    st.caption(f"오늘 날짜: {date.today()}")
    st.info(f"현재 대회: {S.t_name}")

menu=S["menu"]

# ════════════════════════════════════════════════════════════
# 🏆 랭킹 (메인 화면 시작)
# ════════════════════════════════════════════════════════════
if menu=="ranking":
    st.markdown("<div class='main-title'>🏆 실시간 통합 랭킹</div>",unsafe_allow_html=True)
    df=load_rank()
    if df.empty: st.info("관리자에서 랭킹 데이터를 업로드하세요.")
    else:
        df=df.sort_values("현재포인트",ascending=False).reset_index(drop=True)
        icons=["🥇","🥈","🥉"]; df.insert(0,"순위",[icons[i] if i<3 else i+1 for i in df.index])
        df["변동"]=(df["현재포인트"]-df["이전포인트"]).apply(lambda x:f"▲{int(x)}" if x>0 else(f"▼{int(abs(x))}" if x<0 else"—"))
        df["그래프"]=df["현재포인트"].apply(lambda p:"■"*min(int(p//10),10)+"□"*(10-min(int(p//10),10)))
        st.dataframe(df[["순위","이름","현재포인트","변동","그래프"]],use_container_width=True,hide_index=True)

# ════════════════════════════════════════════════════════════
# 📅 대진표 (읽기전용 — 점수 표시만)
# ════════════════════════════════════════════════════════════
elif menu=="schedule":
    st.markdown("<div class='main-title'>📅 대진표 및 전적</div>",unsafe_allow_html=True)
    if not S.schedule: st.warning("⚠️ 관리자에서 대진을 먼저 생성하세요.")
    else:
        gnames=list(S.schedule.keys())
        tabs=st.tabs([f"{GLBL[i%len(GLBL)]} 그룹 {g}" for i,g in enumerate(gnames)])
        for tidx,g in enumerate(gnames):
            with tabs[tidx]:
                draw_matrix(g,tidx)
                st.divider()
                cls=gcol(tidx)
                for ri,rd in enumerate(S.schedule[g]):
                    st.markdown(f'<div class="round-hdr">🏸 Round {ri+1}</div>',unsafe_allow_html=True)
                    ccols=st.columns(min(len(rd),2))
                    for mi,(t1,t2) in enumerate(rd):
                        t1,t2=list(t1),list(t2)
                        with ccols[mi%2]:
                            sd=S.scores.get(f"{g}_{ri}_{mi}",{})
                            s1,s2=sd.get("s1",0),sd.get("s2",0)
                            st.markdown(f"""<div class="match-wrap">
                              <div class="team-shape-wrap">
                                {shape_html(t1,cls)}
                                <div class="vs-badge">VS</div>
                                {shape_html(t2,cls)}
                              </div></div>""",unsafe_allow_html=True)
                            if s1>0 or s2>0:
                                st.markdown(f"<div style='text-align:center;font-size:1.2rem;font-weight:900;color:#1565c0'>"
                                            f"{tname(t1)} <span style='color:#e53935'>{s1}:{s2}</span> {tname(t2)}</div>",
                                            unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════
# 📊 경기 결과
# ════════════════════════════════════════════════════════════
elif menu=="result":
    st.markdown("<div class='main-title'>📊 전체 경기 결과</div>",unsafe_allow_html=True)
    if not S.scores: st.info("아직 입력된 점수가 없습니다.")
    else:
        gnames=list(S.schedule.keys()) if S.schedule else []
        tabs=st.tabs([f"{GLBL[i%len(GLBL)]} 그룹 {g}" for i,g in enumerate(gnames)])
        for tidx,g in enumerate(gnames):
            with tabs[tidx]:
                sched=S.schedule.get(g,[])
                teams_list,seen=[],set()
                for rd in sched:
                    for t1,t2 in rd:
                        for t in [tuple(t1),tuple(t2)]:
                            if t not in seen: teams_list.append(t);seen.add(t)
                stats={t:{"승":0,"패":0,"득실":0} for t in teams_list}
                mrows=[]
                for sd in S.scores.values():
                    if sd.get("group")!=g: continue
                    t1,t2=tuple(sd["t1"]),tuple(sd["t2"]); s1,s2=sd["s1"],sd["s2"]
                    n1,n2=tname(list(t1)),tname(list(t2))
                    if s1>s2: res=f"🏆 {n1} 승"; stats[t1]["승"]+=1; stats[t2]["패"]+=1
                    elif s2>s1: res=f"🏆 {n2} 승"; stats[t2]["승"]+=1; stats[t1]["패"]+=1
                    else: res="🤝 무승부"
                    stats[t1]["득실"]+=(s1-s2); stats[t2]["득실"]+=(s2-s1)
                    mrows.append({"팀1":n1,"점수1":s1,"점수2":s2,"팀2":n2,"결과":res})
                if mrows:
                    st.markdown("**📋 전체 경기 결과**")
                    st.dataframe(pd.DataFrame(mrows),use_container_width=True,hide_index=True)
                ranked=sorted(teams_list,key=lambda t:(-stats[t]["승"],-stats[t]["득실"]))
                rrows=[{"순위":["🥇","🥈","🥉"][i] if i<3 else i+1,
                         "팀명":tname(list(t)),"승":stats[t]["승"],"패":stats[t]["패"],
                         "득실":f'{stats[t]["득실"]:+d}',"획득포인트":calc_pt(i+1)} for i,t in enumerate(ranked)]
                st.markdown("**🏅 그룹 순위 (승 → 득실)**")
                st.dataframe(pd.DataFrame(rrows),use_container_width=True,hide_index=True)

# ════════════════════════════════════════════════════════════
# ✅ 참가 확인
# ════════════════════════════════════════════════════════════
elif menu=="attend":
    st.markdown("<div class='main-title'>✅ 대회 참가 확인</div>",unsafe_allow_html=True)
    st.markdown(f"""<div style='background:linear-gradient(135deg,#e3f2fd,#bbdefb);
        border:2px solid #42a5f5;border-radius:13px;padding:13px 17px;margin-bottom:13px'>
        <div style='font-size:1.2rem;font-weight:900;color:#1565c0'>🏆 {S.t_name}</div>
        <div style='color:#555;margin-top:3px'>📅 {S.t_date} &nbsp;|&nbsp; 📍 {S.t_place or "장소 미정"}</div>
    </div>""",unsafe_allow_html=True)
    if not S.players: st.info("관리자에서 참가자를 먼저 등록하세요.")
    else:
        st.markdown('<div class="sec-title">참가자 명단 및 체크인</div>',unsafe_allow_html=True)
        st.caption("✏️ 본인 이름 옆 체크박스를 눌러 참가를 확정하세요.")
        attend=S.attendance; confirmed=0
        for pi,pname in enumerate(S.players):
            is_ok=attend.get(pname,False)
            c1,c2=st.columns([5,1])
            with c1:
                cls2="aok" if is_ok else "ano"
                icon="✅" if is_ok else "⬜"
                st.markdown(f'<div class="acard {cls2}">{icon} <span style="color:#888;font-size:.83rem">No.{pi+1}</span>'
                            f' <span style="font-size:1rem;font-weight:700">{pname}</span></div>',unsafe_allow_html=True)
            with c2:
                nv=st.checkbox("참가",value=is_ok,key=f"atd_{pname}",label_visibility="collapsed")
                if nv!=is_ok: S.attendance[pname]=nv; st.rerun()
            if is_ok: confirmed+=1
        st.divider()
        st.markdown(f"<div style='text-align:center;font-size:1.05rem;font-weight:700;color:#1565c0;"
                    f"padding:8px;background:#e3f2fd;border-radius:9px'>✅ 현재 참가 확인: {confirmed}명 / 전체: {len(S.players)}명</div>",
                    unsafe_allow_html=True)
        if st.button("💾 참가 현황 저장",use_container_width=True):
            rows=[{"대회명":S.t_name,"이름":p,"참가확인":attend.get(p,False)} for p in S.players]
            pd.DataFrame(rows).to_csv(ATND_FILE,index=False)
            st.success("✅ 참가 현황 저장 완료")

# ════════════════════════════════════════════════════════════
# ⚙️ 관리자
# ════════════════════════════════════════════════════════════
elif menu=="admin":
    st.markdown("<div class='main-title'>⚙️ 관리자 센터</div>",unsafe_allow_html=True)
    pw=st.text_input("🔒 보안 비밀번호",type="password",placeholder="관리자 비밀번호를 입력하세요")
    if pw=="0502": S.is_admin=True
    if not S.is_admin: st.stop()
    st.success("✅ 관리자 권한이 승인되었습니다.")

    tabs=st.tabs(["🏆 대회 생성","📂 랭킹 관리","🎯 대진 생성","🎮 점수 입력","💾 결과 반영"])

    # ── 탭1: 대회 생성 ────────────────────────────────────────
    with tabs[0]:
        st.markdown('<div class="sec-title">새 대회 만들기</div>',unsafe_allow_html=True)
        with st.form("f_tour"):
            tn=st.text_input("대회명",value=S.t_name,placeholder="예: 5월 정기 대회")
            td=st.date_input("날짜",value=date.today())
            tp=st.text_input("장소",value=S.t_place,placeholder="예: 두류테니스장 A코트")
            tm=st.selectbox("방식",["리그전(풀리그)","KDK","고정페어","혼합"])
            if st.form_submit_button("✅ 대회 생성",use_container_width=True,type="primary"):
                if not tn.strip(): st.error("대회명을 입력하세요")
                else:
                    S.t_name=tn.strip(); S.t_date=str(td); S.t_place=tp.strip()
                    for k in ["players","groups","modes","schedule","scores","attendance"]:
                        S[k]=[] if k=="players" else {}
                    tdf=load_tour()
                    tdf=pd.concat([tdf,pd.DataFrame([[tn.strip(),str(td),tp.strip(),tm,"진행중"]],
                                   columns=["대회명","날짜","장소","방식","상태"])],ignore_index=True)
                    save_tour(tdf); st.success(f"🎉 '{tn}' 대회 생성 완료!"); st.rerun()

        st.markdown('<div class="sec-title">기존 대회 목록</div>',unsafe_allow_html=True)
        tdf=load_tour()
        if tdf.empty: st.info("생성된 대회 없음")
        else:
            for i,row in tdf.iterrows():
                sc={"진행중":"#fb8c00","완료":"#43a047","예정":"#1e88e5"}.get(row["상태"],"#888")
                st.markdown(f"<div style='background:#f8f9fa;border:1.5px solid #e0e0e0;border-radius:11px;"
                            f"padding:9px 13px;margin:5px 0'><span style='font-weight:900'>{row['대회명']}</span>"
                            f" <span style='font-size:.83rem;color:#555'>📅{row['날짜']} | 📍{row['장소']} | {row['방식']}</span>"
                            f" <span style='color:{sc};font-weight:800'>[{row['상태']}]</span></div>",unsafe_allow_html=True)
                ca,cb=st.columns(2)
                with ca:
                    if st.button("✅ 완료 처리",key=f"dn{i}",use_container_width=True):
                        tdf.loc[i,"상태"]="완료"; save_tour(tdf); st.rerun()
                with cb:
                    if st.button("🗑 삭제하기",key=f"dl{i}",use_container_width=True):
                        save_tour(tdf.drop(index=i).reset_index(drop=True)); st.rerun()

    # ── 탭2: 랭킹 관리 ────────────────────────────────────────
    with tabs[1]:
        st.markdown('<div class="sec-title">랭킹 데이터 마스터 업로드</div>',unsafe_allow_html=True)
        st.caption("컬럼명에 '이름/name/선수/회원', '포인트/point/pts/점수' 등이 포함되면 자동 인식합니다.")
        f=st.file_uploader("엑셀(XLSX) 또는 CSV 파일 선택",type=["csv","xlsx"])
        if f:
            df_up=smart_read(f)
            if df_up is not None:
                st.dataframe(df_up.head(15),use_container_width=True,hide_index=True)
                if st.button("💾 데이터베이스에 저장",use_container_width=True,type="primary"):
                    save_rank(df_up); st.success("✅ 랭킹 정보 저장 완료!")
        st.markdown('<div class="sec-title">현재 저장된 전체 랭킹</div>',unsafe_allow_html=True)
        cur=load_rank()
        if not cur.empty:
            cur=cur.sort_values("현재포인트",ascending=False).reset_index(drop=True)
            cur.insert(0,"순위",cur.index+1)
            st.dataframe(cur,use_container_width=True,hide_index=True)
        else: st.info("랭킹 데이터 없음")

    # ── 탭3: 대진 생성 ────────────────────────────────────────
    with tabs[2]:
        st.markdown('<div class="sec-title">1단계: 참가 선수 명단 확정</div>',unsafe_allow_html=True)
        raw=st.text_area("참가자 명단 (쉼표로 구분하여 입력)",value=", ".join(S.players),height=80)
        if st.button("📝 명단 등록/수정",use_container_width=True):
            S.players=[clean(p) for p in raw.split(",") if p.strip()]
            S.attendance={p:S.attendance.get(p,False) for p in S.players}
            st.success(f"✅ {len(S.players)}명 선수단 구성 완료")
        if S.players: st.markdown(f"**현재 등록 선수: {len(S.players)}명** — {', '.join(S.players)}")
        st.divider()
        st.markdown('<div class="sec-title">2단계: 그룹 및 경기 방식 구성</div>',unsafe_allow_html=True)
        gcnt=st.number_input("그룹 수 설정",1,6,1)
        gns=list("ABCDEF")[:gcnt]
        gcfg={}
        for gi,gn in enumerate(gns):
            hx=ghex(gi)
            st.markdown(f"<div style='background:{hx}18;border-left:5px solid {hx};border-radius:8px;"
                        f"padding:6px 13px;margin:7px 0;font-weight:800;color:{hx}'>{GLBL[gi%len(GLBL)]} 그룹 {gn} 설정</div>",
                        unsafe_allow_html=True)
            cc=st.columns(3)
            dfsz=max(2,len(S.players)//gcnt) if S.players else 4
            with cc[0]: sz=st.number_input("참가인원",2,30,dfsz,key=f"sz{gn}")
            with cc[1]: md=st.selectbox("진행방식",["KDK","고정페어","단식"],key=f"md{gn}")
            with cc[2]: gc=st.selectbox("개인별 게임수",[3,4,5,6],index=1,key=f"gc{gn}")
            gcfg[gn]=(sz,md,gc)
        tsz=sum(c[0] for c in gcfg.values())
        if S.players:
            d=len(S.players)-tsz
            (st.success if d==0 else st.warning)(f"{'✅' if d==0 else '⚠️'} 전체 명단 {len(S.players)}명 / 그룹 배정 {tsz}명{f' (차이 {d:+d}명)' if d else ''}")
        if st.button("🎲 대진표 자동 생성 시작",use_container_width=True,type="primary"):
            pl=S.players[:]
            if len(pl)<tsz: st.error(f"배정 인원이 명단보다 많습니다. 인원 설정을 확인하세요.")
            else:
                rdf=load_rank(); rm=dict(zip(rdf["이름"],rdf["현재포인트"]))
                pl.sort(key=lambda x:rm.get(x,0),reverse=True)
                S.groups={}; S.modes={}; S.game_counts={}; S.schedule={}; S.scores={}
                curr=0
                for gn,(sz,md,gc) in gcfg.items():
                    gp=pl[curr:curr+sz]; S.groups[gn]=gp; S.modes[gn]=md; S.game_counts[gn]=gc
                    if md=="KDK":
                        h=make_kdk_hanul(gp,gc)
                        if h: S.schedule[gn]=h; st.info(f"그룹 {gn}: 한울KDK 방식 생성됨")
                        else:
                            sh=random.sample(gp,len(gp))
                            pairs=[sh[i:i+2] for i in range(0,len(sh)-1,2)]
                            if len(sh)%2==1: pairs.append([sh[-1]])
                            S.schedule[gn]=make_rr(pairs); st.warning(f"그룹 {gn}: 한울DB 없음 → 랜덤페어 리그전 생성")
                    elif md=="고정페어":
                        n=len(gp); pairs=[[gp[i],gp[n-1-i]] for i in range(n//2)]
                        if n%2==1: pairs.append([gp[n//2]])
                        S.schedule[gn]=make_rr(pairs)
                    else:
                        S.schedule[gn]=make_rr([[p] for p in gp])
                    curr+=sz
                st.success("✅ 대진 생성이 완료되었습니다! 왼쪽 메뉴의 '대진표'에서 확인하세요."); st.rerun()

    # ── 탭4: 점수 입력 (관리자 전용) ─────────────────────────
    with tabs[3]:
        st.markdown('<div class="sec-title">전적 기록실</div>',unsafe_allow_html=True)
        if not S.schedule: st.warning("대진표를 먼저 생성해야 점수 입력이 가능합니다.")
        else:
            gnames=list(S.schedule.keys())
            stabs=st.tabs([f"{GLBL[i%len(GLBL)]} 그룹 {g}" for i,g in enumerate(gnames)])
            for tidx,g in enumerate(gnames):
                with stabs[tidx]:
                    cls=gcol(tidx)
                    for ri,rd in enumerate(S.schedule[g]):
                        st.markdown(f'<div class="round-hdr">🏸 Round {ri+1}</div>',unsafe_allow_html=True)
                        ccols=st.columns(min(len(rd),2))
                        for mi,(t1,t2) in enumerate(rd):
                            t1,t2=list(t1),list(t2)
                            with ccols[mi%2]:
                                key=f"{g}_{ri}_{mi}"
                                ex=S.scores.get(key,{}); es1=ex.get("s1",0); es2=ex.get("s2",0)
                                n1,n2=tname(t1),tname(t2)
                                st.markdown(f"""<div class="match-wrap"><div class="team-shape-wrap">
                                  {shape_html(t1,cls)}<div class="vs-badge">VS</div>{shape_html(t2,cls)}
                                </div></div>""",unsafe_allow_html=True)
                                sc1,sc2=st.columns(2)
                                with sc1: s1=st.number_input(n1,0,50,es1,key=f"{key}s1")
                                with sc2: s2=st.number_input(n2,0,50,es2,key=f"{key}s2")
                                if st.button("💾 점수 저장",key=f"{key}btn",use_container_width=True):
                                    S.scores[key]={"group":g,"t1":t1,"t2":t2,"s1":s1,"s2":s2}
                                    r=(f"🏆 {n1} 승" if s1>s2 else(f"🏆 {n2} 승" if s2>s1 else"🤝 무승부"))
                                    st.success(f"{n1} {s1}:{s2} {n2} — {r}"); st.rerun()

    # ── 탭5: 결과 반영 ────────────────────────────────────────
    with tabs[4]:
        st.markdown('<div class="sec-title">최종 결과 확정 및 랭킹 포인트 반영</div>',unsafe_allow_html=True)
        st.caption("공식 포인트 기준: 1위(+7) | 2위(+5) | 3위(+3) | 기타 참가(+1)")
        if not S.scores: st.warning("입력된 경기 결과가 없습니다.")
        else:
            rdf=load_rank(); earn={}
            for p in S.players: earn[p]=ATTEND_PT
            prev_rows=[]
            for g,sched in S.schedule.items():
                tl,seen=[],set()
                for rd in sched:
                    for t1,t2 in rd:
                        for t in [tuple(t1),tuple(t2)]:
                            if t not in seen: tl.append(t);seen.add(t)
                st2={t:{"승":0,"득실":0} for t in tl}
                for sd in S.scores.values():
                    if sd.get("group")!=g: continue
                    t1,t2=tuple(sd["t1"]),tuple(sd["t2"]); s1,s2=sd["s1"],sd["s2"]
                    if s1>s2:
                        if t1 in st2: st2[t1]["승"]+=1; st2[t1]["득실"]+=(s1-s2)
                        if t2 in st2: st2[t2]["득실"]+=(s2-s1)
                    elif s2>s1:
                        if t2 in st2: st2[t2]["승"]+=1; st2[t2]["득실"]+=(s2-s1)
                        if t1 in st2: st2[t1]["득실"]+=(s1-s2)
                ranked=sorted(tl,key=lambda t:(-st2[t]["승"],-st2[t]["득실"]))
                for ri2,t in enumerate(ranked):
                    bonus=calc_pt(ri2+1)-ATTEND_PT
                    for p in list(t):
                        earn[p]=earn.get(p,ATTEND_PT)+bonus
                        prev_rows.append({"그룹":g,"팀":tname(list(t)),
                                          "그룹순위":["🥇","🥈","🥉"][ri2] if ri2<3 else ri2+1,
                                          "이름":p,"획득포인트":earn[p]})
            if prev_rows:
                st.markdown("**📋 반영될 포인트 미리보기**")
                st.dataframe(pd.DataFrame(prev_rows),use_container_width=True,hide_index=True)
            c1,c2=st.columns(2)
            with c1:
                if st.button("🏆 최종 랭킹 반영",use_container_width=True,type="primary"):
                    rdf["이전포인트"]=rdf["현재포인트"]
                    for p,pt in earn.items():
                        if p in rdf["이름"].values: rdf.loc[rdf["이름"]==p,"현재포인트"]+=pt
                        else: rdf=pd.concat([rdf,pd.DataFrame([[p,pt,0]],columns=["이름","현재포인트","이전포인트"])],ignore_index=True)
                    save_rank(rdf)
                    hdf=load_hist()
                    new_h=pd.DataFrame([{"날짜":S.t_date,"대회명":S.t_name,"그룹":r["그룹"],
                                         "이름":r["이름"],"그룹순위":r["그룹순위"],"획득포인트":r["획득포인트"]} for r in prev_rows])
                    save_hist(pd.concat([hdf,new_h],ignore_index=True))
                    tdf=load_tour(); tdf.loc[tdf["대회명"]==S.t_name,"상태"]="완료"; save_tour(tdf)
                    st.success("✅ 포인트 반영 및 기록 저장이 완료되었습니다!"); st.rerun()
            with c2:
                if st.button("🗑 경기 기록만 초기화",use_container_width=True):
                    S.scores={}; st.success("✅ 경기 기록이 초기화되었습니다."); st.rerun()
            st.divider()
            st.markdown('<div class="sec-title">📜 역대 대회 히스토리</div>',unsafe_allow_html=True)
            hdf=load_hist()
            if not hdf.empty: st.dataframe(hdf.sort_values("날짜",ascending=False).reset_index(drop=True),use_container_width=True,hide_index=True)
            else: st.info("아직 저장된 히스토리가 없습니다.")

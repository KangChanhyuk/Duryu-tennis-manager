import streamlit as st
import pandas as pd
import random, os, json
from datetime import date
from io import BytesIO

# ══════════════════════════════════════════════════════════════
# 앱 설정
# ══════════════════════════════════════════════════════════════
st.set_page_config(page_title="두류 랭킹 관리 시스템", page_icon="🎾",
                   layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;600;700;900&display=swap');
html, body, [class*="css"], button, input, select, textarea {
    font-family: 'Noto Sans KR', sans-serif !important;
}
.block-container { padding: 0 0.6rem 2rem !important; max-width: 100% !important; }

/* 네비게이션 바 */
section.main [data-testid="stHorizontalBlock"]:first-of-type .stButton > button {
    background: transparent !important;
    color: rgba(255,255,255,0.72) !important;
    border: none !important; border-radius: 0 !important;
    font-size: clamp(0.78rem, 2.2vw, 1rem) !important;
    font-weight: 700 !important;
    padding: 18px 6px 14px !important;
    line-height: 1.45 !important;
    white-space: pre-line !important;
    box-shadow: none !important;
    min-height: 62px !important;
    border-bottom: 4px solid transparent !important;
}
section.main [data-testid="stHorizontalBlock"]:first-of-type .stButton > button:hover {
    background: rgba(255,255,255,0.12) !important;
    color: #fff !important;
}
section.main [data-testid="stHorizontalBlock"]:first-of-type .stButton > button[kind="primary"] {
    background: rgba(255,255,255,0.2) !important;
    color: #fff !important;
    font-weight: 900 !important;
    border-bottom: 4px solid #A5D6A7 !important;
}

/* 공통 헤더 */
.main-hdr {
    background: linear-gradient(135deg,#1D5B2E,#388E3C);
    color:#fff; padding:1rem 1.4rem; border-radius:14px;
    margin-bottom:1rem; font-size:clamp(1.1rem,4vw,1.8rem);
    font-weight:900; text-align:center;
    box-shadow:0 6px 18px rgba(0,0,0,0.14);
}
.sec {
    font-size:1.02rem; font-weight:900; color:#1D5B2E;
    border-left:5px solid #66BB6A; padding-left:10px; margin:14px 0 8px;
}

/* 탭 */
button[data-baseweb="tab"] {
    font-size:0.95rem!important; font-weight:700!important;
    padding:10px 16px!important; border-radius:8px 8px 0 0!important;
}
button[data-baseweb="tab"][aria-selected="true"] {
    background:linear-gradient(135deg,#1D5B2E,#388E3C)!important; color:#fff!important;
}

/* 테이블 가운데 정렬 */
th, td, [data-testid="stDataFrame"] td, [data-testid="stDataFrame"] th,
[data-testid="stDataEditor"] td, [data-testid="stDataEditor"] th,
.dataframe th, .dataframe td {
    text-align: center !important;
    vertical-align: middle !important;
}

/* 팀 도형 */
.team-box {
    border-radius:12px; padding:9px 13px; font-weight:800;
    font-size:clamp(.82rem,2.4vw,1rem); text-align:center;
    margin:3px 0; box-shadow:0 3px 8px rgba(0,0,0,.12); line-height:1.4;
}
.tg{background:linear-gradient(135deg,#2E7D32,#1B5E20);color:#fff}
.tb{background:linear-gradient(135deg,#1565C0,#0D47A1);color:#fff}
.to{background:linear-gradient(135deg,#E65100,#BF360C);color:#fff}
.tp{background:linear-gradient(135deg,#6A1B9A,#4A148C);color:#fff}
.tr{background:linear-gradient(135deg,#C62828,#B71C1C);color:#fff}
.tt{background:linear-gradient(135deg,#00695C,#004D40);color:#fff}

.vs-circle {
    background:#E53935; color:#fff; border-radius:50%;
    width:40px; height:40px; display:flex; align-items:center;
    justify-content:center; font-weight:900; font-size:.9rem;
    margin:0 auto; box-shadow:0 2px 8px rgba(229,57,53,.4);
}

/* 라운드 카드 */
.round-card {
    background: linear-gradient(135deg, #ffffff, #f8f9fa);
    border: 1px solid #e0e0e0;
    border-radius: 16px;
    padding: 16px;
    margin: 12px 0;
    box-shadow: 0 4px 12px rgba(0,0,0,0.08);
    transition: transform 0.2s;
}
.round-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 16px rgba(0,0,0,0.12);
}
.round-title {
    background: linear-gradient(90deg,#1D5B2E,#43A047);
    color: white;
    border-radius: 12px;
    padding: 8px 16px;
    font-weight: 800;
    text-align: center;
    margin-bottom: 16px;
    font-size: 1rem;
}
.match-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 12px;
    margin: 12px 0;
}
.team-cell {
    flex: 2;
    text-align: center;
}
.score-cell {
    flex: 0.5;
    text-align: center;
    font-weight: 900;
    font-size: 1.3rem;
    background: #f5f5f5;
    border-radius: 12px;
    padding: 6px;
}
.vs-cell {
    flex: 0.3;
    text-align: center;
}

.tour-card {
    background:#F9FBF9; border:1.5px solid #C8E6C9; border-radius:12px;
    padding:10px 14px; margin:6px 0;
}
.p-tag {
    display:inline-block; background:#E8F5E9; border:1.5px solid #66BB6A;
    border-radius:20px; padding:4px 12px; margin:3px 4px;
    font-size:.92rem; font-weight:700; color:#1D5B2E;
}
.rank-card {
    background:#fff; border:1.5px solid #C8E6C9; border-radius:14px;
    padding:18px 20px; height:100%;
    box-shadow:0 3px 12px rgba(0,0,0,0.07);
}
.rank-card-title {
    font-size:1rem; font-weight:900; color:#1D5B2E;
    border-bottom:2px solid #A5D6A7; padding-bottom:8px; margin-bottom:14px;
    text-align:center;
}
.matrix-card {
    background: #fff;
    border-radius: 12px;
    padding: 12px;
    border: 1px solid #C8E6C9;
}
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# 파일 경로 / 상수
# ══════════════════════════════════════════════════════════════
RANK_FILE   = "ranking_master.csv"
MEMBER_FILE = "member_roster.json"
TOUR_FILE   = "tournaments.json"
ADMIN_PW    = "0502"
COLS_RANK   = ["랭킹","이름","현재포인트","3월 포인트","결과","부과점","그룹","비고"]

GCLS = ["tg","tb","to","tp","tr","tt"]
GHEX = ["#2E7D32","#1565C0","#E65100","#6A1B9A","#C62828","#00695C"]
GLBL = ["🟢","🔵","🟠","🟣","🔴","🩵"]

KDK_BP = {
    3:{4:[(1,4,2,3),(1,3,2,4),(1,2,3,4)],
       8:[(1,2,3,4),(5,6,7,8),(1,8,2,7),(3,6,4,5),(1,4,5,8),(2,3,6,7)],
       12:[(1,2,3,4),(5,6,7,8),(9,10,11,12),(1,3,5,7),(2,4,6,8),
           (9,11,1,5),(4,8,9,12),(6,7,10,11),(10,12,2,3)]},
    4:{5:[(1,2,3,4),(1,3,2,5),(1,4,3,5),(1,5,2,4),(2,3,4,5)],
       6:[(1,3,2,4),(1,5,4,6),(2,3,5,6),(1,4,3,5),(2,6,3,4),(1,6,2,5)],
       7:[(1,2,3,4),(5,6,1,7),(2,3,5,7),(1,4,6,7),(3,5,2,4),(1,6,2,5),(4,6,3,7)],
       8:[(1,2,3,4),(5,6,7,8),(1,3,5,7),(2,4,6,8),(1,5,2,6),(3,7,4,8),(1,6,3,8),(2,5,4,7)],
       9:[(1,2,3,4),(5,6,7,8),(1,9,5,7),(2,3,6,8),(4,9,3,8),(1,5,2,6),(3,6,4,5),(1,7,8,9),(2,4,7,9)],
       10:[(1,2,3,5),(6,7,8,10),(2,3,4,6),(7,8,1,9),(3,4,5,7),(8,9,2,10),
           (4,5,6,8),(1,3,9,10),(5,6,7,9),(1,10,2,4)],
       11:[(1,2,3,5),(6,7,8,10),(4,9,1,11),(2,3,6,8),(4,5,7,10),(9,11,2,6),
           (1,3,7,11),(4,8,5,9),(1,10,2,8),(4,7,6,11),(3,9,5,10)]},
}

# ══════════════════════════════════════════════════════════════
# 데이터 함수
# ══════════════════════════════════════════════════════════════
def load_rank():
    if not os.path.exists(RANK_FILE):
        return pd.DataFrame(columns=COLS_RANK)
    df = pd.read_csv(RANK_FILE)
    for c in ["현재포인트","3월 포인트","부과점"]:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0)
    if "현재포인트" in df.columns:
        df = df.sort_values("현재포인트", ascending=False).reset_index(drop=True)
        df["랭킹"] = df.index + 1
    return df.fillna("")

def save_rank(df):
    if "현재포인트" in df.columns:
        df = df.sort_values("현재포인트", ascending=False).reset_index(drop=True)
        df["랭킹"] = df.index + 1
    df.to_csv(RANK_FILE, index=False)

def load_members():
    if os.path.exists(MEMBER_FILE):
        with open(MEMBER_FILE,"r",encoding="utf-8") as f:
            return json.load(f)
    df = load_rank()
    return df["이름"].tolist() if not df.empty else []

def save_members(names: list):
    with open(MEMBER_FILE,"w",encoding="utf-8") as f:
        json.dump(names, f, ensure_ascii=False, indent=2)

def load_tours():
    if os.path.exists(TOUR_FILE):
        with open(TOUR_FILE,"r",encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_tours(d):
    with open(TOUR_FILE,"w",encoding="utf-8") as f:
        json.dump(d, f, ensure_ascii=False, indent=2)

def to_excel(df):
    buf = BytesIO()
    df.to_excel(buf, index=False)
    return buf.getvalue()

def tname(t):
    return " & ".join(t) if len(t)>1 else t[0]

def group_stats(matches):
    stats = {}
    for m in matches:
        t1,t2 = tuple(m["t1"]),tuple(m["t2"])
        for t in [t1,t2]:
            if t not in stats: stats[t]={"승":0,"패":0,"득실":0}
        s1,s2 = int(m["s1"]),int(m["s2"])
        if s1>s2:   stats[t1]["승"]+=1; stats[t2]["패"]+=1
        elif s2>s1: stats[t2]["승"]+=1; stats[t1]["패"]+=1
        stats[t1]["득실"]+=(s1-s2)
        stats[t2]["득실"]+=(s2-s1)
    return stats

def rank_pts(rank, mode):
    if mode=="고정페어": return {1:7,2:5,3:3}.get(rank,1)
    else: return {1:7,2:7,3:5,4:5,5:3,6:3}.get(rank,1)

def make_kdk(players, gc):
    bp = KDK_BP.get(gc,{}).get(len(players))
    if not bp: return None
    sh = random.sample(players, len(players))
    return [{"t1":[sh[a-1],sh[b-1]],"t2":[sh[c-1],sh[d-1]],"s1":0,"s2":0} for a,b,c,d in bp]

def make_fixed(players):
    n = len(players)
    pairs = [(players[i],players[n-1-i]) for i in range(n//2)]
    ms = []
    for i in range(len(pairs)):
        for j in range(i+1,len(pairs)):
            ms.append({"t1":list(pairs[i]),"t2":list(pairs[j]),"s1":0,"s2":0})
    random.shuffle(ms); return ms

def make_singles(players):
    pl=players[:]; random.shuffle(pl)
    ms=[(pl[i],pl[j]) for i in range(len(pl)) for j in range(i+1,len(pl))]
    random.shuffle(ms)
    return [{"t1":[a],"t2":[b],"s1":0,"s2":0} for a,b in ms]

# ══════════════════════════════════════════════════════════════
# 세션 초기화
# ══════════════════════════════════════════════════════════════
if "is_admin" not in st.session_state: st.session_state.is_admin = False
if "menu"     not in st.session_state: st.session_state.menu     = "ranking"
if "participants" not in st.session_state: st.session_state.participants = []

# ══════════════════════════════════════════════════════════════
# 네비게이션 바
# ══════════════════════════════════════════════════════════════
MENU_DEFS = [
    ("ranking",  "🏆\n두류 랭킹"),
    ("schedule", "📅\n대진·경기현황"),
    ("result",   "📊\n경기 결과"),
    ("archive",  "📂\n지난 대회"),
    ("admin",    "⚙️\n관리자"),
]

st.markdown("""
<div style="background:#1D5B2E;padding:14px 16px 0 16px;
    border-radius:0 0 0 0;margin:0 -0.6rem 0 -0.6rem;">
  <div style="text-align:center;color:rgba(255,255,255,0.55);
      font-size:0.78rem;letter-spacing:2px;font-weight:600;
      margin-bottom:6px">🎾 두류 테니스 클럽</div>
</div>
""", unsafe_allow_html=True)

nav_cols = st.columns(len(MENU_DEFS))
for col, (key, label) in zip(nav_cols, MENU_DEFS):
    is_active = st.session_state.menu == key
    with col:
        btn_type = "primary" if is_active else "secondary"
        if st.button(label, key=f"nav_{key}",
                     use_container_width=True, type=btn_type):
            st.session_state.menu = key
            st.rerun()

st.markdown("""
<div style="background:#1D5B2E;height:10px;border-radius:0 0 16px 16px;
    margin:0 -0.6rem 16px -0.6rem;
    box-shadow:0 6px 16px rgba(0,0,0,0.2)"></div>
""", unsafe_allow_html=True)

M = st.session_state.menu

# ══════════════════════════════════════════════════════════════
# 1. 🏆 두류 랭킹
# ══════════════════════════════════════════════════════════════
if M == "ranking":
    st.markdown("<div class='main-hdr'>🏆 두류 랭킹 관리 시스템</div>", unsafe_allow_html=True)
    df = load_rank()
    if df.empty:
        st.info("📋 등록된 랭킹이 없습니다. 관리자 → 랭킹 관리에서 엑셀을 업로드하세요.")
    else:
        icons = ["🥇","🥈","🥉"]
        disp  = df.copy()
        disp.insert(0,"순위",[icons[i] if i<3 else str(i+1) for i in range(len(disp))])
        st.dataframe(disp, use_container_width=True, hide_index=True)
        st.download_button(
            "📥 랭킹 엑셀 다운로드", data=to_excel(df),
            file_name=f"두류랭킹_{date.today()}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True)

# ══════════════════════════════════════════════════════════════
# 2. 📅 대진 및 경기 현황 (개선된 UI)
# ══════════════════════════════════════════════════════════════
elif M == "schedule":
    tours  = load_tours()
    active = [k for k,v in tours.items() if v.get("status")=="진행중"]
    if not active:
        st.warning("⚠️ 진행 중인 대회가 없습니다. 관리자에서 대회를 생성하세요.")
        st.stop()
    tid  = active[-1]; tour = tours[tid]
    st.markdown(f"<div class='main-hdr'>📅 {tour['title']}</div>", unsafe_allow_html=True)
    st.caption(f"📅 {tour.get('date','')}  |  📍 {tour.get('place','')}  |  코트 {tour.get('courts',2)}면")

    gnames = list(tour["groups"].keys())
    if not gnames:
        st.info("관리자에서 대진을 생성하세요.")
        st.stop()

    tabs = st.tabs([f"{GLBL[i%len(GLBL)]} {g}" for i,g in enumerate(gnames)])
    for ti,g in enumerate(gnames):
        with tabs[ti]:
            ginfo   = tour["groups"][g]
            matches = ginfo["matches"]
            mode    = ginfo["mode"]
            cls     = GCLS[ti%len(GCLS)]
            stats   = group_stats(matches)
            teams   = list(stats.keys())

            # 상단: 매트릭스 + 순위 테이블 (2컬럼)
            col_left, col_right = st.columns([3, 2], gap="medium")
            
            with col_left:
                st.markdown("**📋 상대별 전적 매트릭스**")
                if teams:
                    lab = {t: tname(list(t)) for t in teams}
                    mat = {lab[t]: {lab[o]: ("■" if t==o else "–") for o in teams} for t in teams}
                    for m in matches:
                        t1, t2 = tuple(m["t1"]), tuple(m["t2"])
                        s1, s2 = int(m["s1"]), int(m["s2"])
                        if s1 > 0 or s2 > 0:
                            mat[lab[t1]][lab[t2]] = f"{s1}:{s2}"
                            mat[lab[t2]][lab[t1]] = f"{s2}:{s1}"
                    mdf = pd.DataFrame(mat).T
                    # 가운데 정렬 스타일 적용 (applymap 대신 HTML로)
                    st.markdown('<div class="matrix-card">', unsafe_allow_html=True)
                    st.dataframe(mdf, use_container_width=True)
                    st.markdown('</div>', unsafe_allow_html=True)
                else:
                    st.info("경기 데이터가 없습니다.")
            
            with col_right:
                st.markdown("**🏅 현재 순위**")
                if teams:
                    ranked = sorted(teams, key=lambda t: (-stats[t]["승"], -stats[t]["득실"]))
                    rdf = pd.DataFrame([{
                        "순위": ["🥇","🥈","🥉"][i] if i<3 else i+1,
                        "팀/선수": tname(list(t)),
                        "승": stats[t]["승"],
                        "패": stats[t]["패"],
                        "득실": f'{stats[t]["득실"]:+d}'
                    } for i, t in enumerate(ranked)])
                    st.dataframe(rdf, use_container_width=True, hide_index=True)
                else:
                    st.info("순위 정보가 없습니다.")
            
            st.divider()
            
            # 하단: 라운드별 카드 형태로 경기 표시
            st.markdown("**🎾 경기 입력 (카드 형태)**")
            
            changed = False
            # 경기를 라운드별로 그룹화 (고정페어/KDK 방식에 따라)
            round_size = max(1, len(matches) // 3) if len(matches) > 6 else len(matches)
            
            for round_idx in range(0, len(matches), round_size):
                round_matches = matches[round_idx:round_idx+round_size]
                with st.container():
                    st.markdown(f'<div class="round-title">📍 ROUND {round_idx//round_size + 1}</div>', unsafe_allow_html=True)
                    st.markdown('<div class="round-card">', unsafe_allow_html=True)
                    
                    for mi, m in enumerate(round_matches):
                        actual_idx = round_idx + mi
                        t1, t2 = m["t1"], m["t2"]
                        n1, n2 = tname(t1), tname(t2)
                        
                        # 3컬럼 레이아웃 (팀1 - VS - 팀2)
                        c1, c2, c3 = st.columns([4, 1, 4])
                        
                        with c1:
                            st.markdown(f'<div class="team-box {cls}" style="font-size:1rem;">{n1}</div>', unsafe_allow_html=True)
                            s1 = st.number_input(
                                f"점수_{actual_idx}", 0, 50, int(m["s1"]),
                                key=f"{tid}_{g}_{actual_idx}_s1",
                                label_visibility="collapsed",
                                step=1
                            )
                        
                        with c2:
                            st.markdown('<div class="vs-circle">VS</div>', unsafe_allow_html=True)
                        
                        with c3:
                            st.markdown(f'<div class="team-box {cls}" style="font-size:1rem;">{n2}</div>', unsafe_allow_html=True)
                            s2 = st.number_input(
                                f"점수_{actual_idx}_2", 0, 50, int(m["s2"]),
                                key=f"{tid}_{g}_{actual_idx}_s2",
                                label_visibility="collapsed",
                                step=1
                            )
                        
                        if s1 != int(m["s1"]) or s2 != int(m["s2"]):
                            tour["groups"][g]["matches"][actual_idx]["s1"] = s1
                            tour["groups"][g]["matches"][actual_idx]["s2"] = s2
                            changed = True
                        
                        if actual_idx < len(matches) - 1:
                            st.markdown("<hr style='margin: 8px 0;'>", unsafe_allow_html=True)
                    
                    st.markdown('</div>', unsafe_allow_html=True)
            
            if changed:
                tours[tid] = tour
                save_tours(tours)
                st.toast("✅ 점수가 저장되었습니다!", icon="✅")

# ══════════════════════════════════════════════════════════════
# 3. 📊 경기 결과 (상세 매트릭스 포함)
# ══════════════════════════════════════════════════════════════
elif M == "result":
    tours  = load_tours()
    active = [k for k,v in tours.items() if v.get("status")=="진행중"]
    if not active: st.warning("⚠️ 진행 중인 대회가 없습니다."); st.stop()
    tid=active[-1]; tour=tours[tid]
    st.markdown(f"<div class='main-hdr'>📊 {tour['title']} — 경기 결과</div>", unsafe_allow_html=True)

    for g,ginfo in tour["groups"].items():
        mode=ginfo["mode"]; matches=ginfo["matches"]
        stats=group_stats(matches)
        ranked=sorted(stats.keys(),key=lambda t:(-stats[t]["승"],-stats[t]["득실"]))
        
        st.markdown(f'<div class="sec">{g} 그룹 ({mode})</div>', unsafe_allow_html=True)
        
        # 상세 매트릭스 표시 (확대된 버전)
        if stats:
            lab = {t: tname(list(t)) for t in stats.keys()}
            mat = {lab[t]: {lab[o]: ("■" if t==o else "–") for o in stats.keys()} for t in stats.keys()}
            for m in matches:
                t1, t2 = tuple(m["t1"]), tuple(m["t2"])
                s1, s2 = int(m["s1"]), int(m["s2"])
                if s1 > 0 or s2 > 0:
                    mat[lab[t1]][lab[t2]] = f"{s1}:{s2}"
                    mat[lab[t2]][lab[t1]] = f"{s2}:{s1}"
            mdf = pd.DataFrame(mat).T
            st.markdown("**📊 상세 경기 매트릭스**")
            st.dataframe(mdf, use_container_width=True)
        
        st.markdown("**🏆 최종 순위**")
        rows=[]
        if mode=="고정페어":
            for ri,t in enumerate(ranked):
                rows.append({"순위":["🥇","🥈","🥉"][ri] if ri<3 else ri+1,
                    "팀":tname(list(t)),"승":stats[t]["승"],"패":stats[t]["패"],
                    "득실":f'{stats[t]["득실"]:+d}',"부과점":rank_pts(ri+1,mode),
                    "등급":["우승","준우승","3위"][ri] if ri<3 else "참가"})
        else:
            G=["우승","우승","준우승","준우승","3위","3위"]
            for ri,t in enumerate(ranked):
                rows.append({"순위":ri+1,"선수":tname(list(t)),"승":stats[t]["승"],"패":stats[t]["패"],
                    "득실":f'{stats[t]["득실"]:+d}',"부과점":rank_pts(ri+1,mode),
                    "등급":G[ri] if ri<len(G) else "참가"})
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
        
        # 모든 경기 결과 상세 표시
        with st.expander(f"📋 {g} 전체 경기 결과 상세보기"):
            mrows=[{"팀1":tname(m["t1"]),"점수1":int(m["s1"]),"점수2":int(m["s2"]),
                    "팀2":tname(m["t2"]),"결과":(
                        "🏆 "+tname(m["t1"])+" 승" if int(m["s1"])>int(m["s2"]) else
                        "🏆 "+tname(m["t2"])+" 승" if int(m["s2"])>int(m["s1"]) else "🤝 무승부")}
                   for m in matches]
            st.dataframe(pd.DataFrame(mrows), use_container_width=True, hide_index=True)

# ══════════════════════════════════════════════════════════════
# 4. 📂 지난 대회 아카이브
# ══════════════════════════════════════════════════════════════
elif M == "archive":
    st.markdown("<div class='main-hdr'>📂 지난 대회 아카이브</div>", unsafe_allow_html=True)
    tours = load_tours()
    past  = {k:v for k,v in tours.items() if v.get("status")!="진행중"}
    if not past: st.info("완료된 대회 기록이 없습니다."); st.stop()

    sel  = st.selectbox("대회 선택", list(past.keys()),
        format_func=lambda k: f"{past[k]['title']}  ({past[k].get('date','날짜없음')})")
    tour = past[sel]
    st.markdown(f"**🏆 {tour['title']}** &nbsp; 📅 {tour.get('date','')} | 📍 {tour.get('place','')}")
    st.divider()
    if not tour.get("groups"): st.info("대진 정보가 없습니다."); st.stop()

    G=["우승","우승","준우승","준우승","3위","3위"]
    for g,ginfo in tour["groups"].items():
        mode=ginfo["mode"]; matches=ginfo["matches"]
        stats=group_stats(matches)
        ranked=sorted(stats.keys(),key=lambda t:(-stats[t]["승"],-stats[t]["득실"]))
        st.markdown(f'<div class="sec">{g} 그룹 ({mode})</div>', unsafe_allow_html=True)
        
        # 매트릭스 표시
        if stats:
            lab = {t: tname(list(t)) for t in stats.keys()}
            mat = {lab[t]: {lab[o]: ("■" if t==o else "–") for o in stats.keys()} for t in stats.keys()}
            for m in matches:
                t1, t2 = tuple(m["t1"]), tuple(m["t2"])
                s1, s2 = int(m["s1"]), int(m["s2"])
                if s1 > 0 or s2 > 0:
                    mat[lab[t1]][lab[t2]] = f"{s1}:{s2}"
                    mat[lab[t2]][lab[t1]] = f"{s2}:{s1}"
            mdf = pd.DataFrame(mat).T
            st.dataframe(mdf, use_container_width=True)
        
        rows=[{"순위":["🥇","🥈","🥉"][ri] if ri<3 else ri+1,
               "팀/선수":tname(list(t)),"승":stats[t]["승"],"패":stats[t]["패"],
               "득실":f'{stats[t]["득실"]:+d}',"부과점":rank_pts(ri+1,mode),
               "등급":(["우승","준우승","3위"][ri] if mode=="고정페어" and ri<3
                        else G[ri] if ri<len(G) else "참가")}
              for ri,t in enumerate(ranked)]
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
        with st.expander(f"📋 {g} 전체 경기 결과"):
            mrows=[{"팀1":tname(m["t1"]),"점수1":int(m["s1"]),"점수2":int(m["s2"]),
                    "팀2":tname(m["t2"]),"결과":(
                        "🏆 "+tname(m["t1"])+" 승" if int(m["s1"])>int(m["s2"]) else
                        "🏆 "+tname(m["t2"])+" 승" if int(m["s2"])>int(m["s1"]) else "🤝 무승부")}
                   for m in matches]
            st.dataframe(pd.DataFrame(mrows), use_container_width=True, hide_index=True)

# ══════════════════════════════════════════════════════════════
# 5. ⚙️ 관리자
# ══════════════════════════════════════════════════════════════
elif M == "admin":
    st.markdown("<div class='main-hdr'>⚙️ 관리자 센터</div>", unsafe_allow_html=True)
    pw = st.text_input("🔒 관리자 비밀번호", type="password", placeholder="비밀번호 입력")
    if pw == ADMIN_PW: st.session_state.is_admin = True
    if not st.session_state.is_admin:
        if pw and pw!=ADMIN_PW: st.error("❌ 비밀번호가 틀렸습니다.")
        st.stop()
    st.success("✅ 관리자 모드 활성화")

    adm = st.tabs(["🏆 대회 관리","👥 참가자·대진","📋 랭킹 관리","💾 결과 반영"])

    # ── 탭1: 대회 관리 ─────────────────────────────────────────
    with adm[0]:
        st.markdown('<div class="sec">새 대회 생성</div>', unsafe_allow_html=True)
        with st.form("f_new_tour"):
            c1,c2 = st.columns(2)
            tn=c1.text_input("대회명", placeholder="예: 5월 정기전")
            td=c2.date_input("날짜", value=date.today())
            c3,c4 = st.columns(2)
            tp    =c3.text_input("장소", placeholder="예: 두류공원 테니스장")
            courts=c4.selectbox("코트 수",[1,2,3],index=1)
            if st.form_submit_button("✅ 대회 생성", type="primary", use_container_width=True):
                if not tn.strip(): st.error("대회명을 입력하세요.")
                else:
                    tours=load_tours(); tid=f"{td}_{tn.strip()}"
                    if tid in tours: st.warning("같은 날짜·이름의 대회가 이미 있습니다.")
                    else:
                        tours[tid]={"title":tn.strip(),"date":str(td),"place":tp,
                                    "courts":courts,"status":"진행중","groups":{}}
                        save_tours(tours); st.success(f"🎉 '{tn}' 대회 생성!"); st.rerun()

        st.divider()
        st.markdown('<div class="sec">대회 목록 (수정·삭제)</div>', unsafe_allow_html=True)
        tours=load_tours()
        if not tours: st.info("생성된 대회가 없습니다.")
        else:
            SC={"진행중":"#FB8C00","완료":"#43A047","예정":"#1E88E5"}
            for tid2,tv in list(tours.items()):
                sc=SC.get(tv.get("status",""),"#888")
                st.markdown(f"""<div class="tour-card">
                  <span style="font-weight:900">{tv['title']}</span>&nbsp;
                  <span style="font-size:.83rem;color:#555">📅{tv.get('date','')} 📍{tv.get('place','')} 코트{tv.get('courts',2)}면</span>
                  <span style="color:{sc};font-weight:800;margin-left:8px">[{tv.get('status','')}]</span>
                </div>""", unsafe_allow_html=True)
                ca,cb,cc,cd=st.columns([2,3,2,2])
                with ca:
                    new_st=st.selectbox("상태",["진행중","완료","예정"],
                        index=["진행중","완료","예정"].index(tv.get("status","진행중")),
                        key=f"st_{tid2}",label_visibility="collapsed")
                with cb:
                    new_title=st.text_input("대회명",tv["title"],
                        key=f"tt_{tid2}",label_visibility="collapsed")
                with cc:
                    if st.button("💾 수정",key=f"edit_{tid2}",use_container_width=True):
                        tours[tid2]["title"]=new_title; tours[tid2]["status"]=new_st
                        save_tours(tours); st.rerun()
                with cd:
                    if st.button("🗑 삭제",key=f"del_{tid2}",use_container_width=True):
                        del tours[tid2]; save_tours(tours); st.rerun()

    # ── 탭2: 참가자·대진 ───────────────────────────────────────
    with adm[1]:
        tours=load_tours()
        active=[k for k,v in tours.items() if v.get("status")=="진행중"]
        if not active: st.warning("진행 중인 대회를 먼저 생성하세요."); st.stop()

        sel_tid=st.selectbox("진행 중 대회",active,
            format_func=lambda k:f"{tours[k]['title']} ({tours[k].get('date','')})")
        tour=tours[sel_tid]
        st.info(f"현재 대회: **{tour['title']}** | 코트 {tour.get('courts',2)}면")

        # ── 참가자 입력 ──────────────────────────────────────
        st.markdown('<div class="sec">참가자 입력</div>', unsafe_allow_html=True)

        member_roster = load_members()
        st.caption("이름을 쉼표(,) 또는 줄바꿈으로 구분해서 입력하고 **저장** 버튼을 누르세요.")

        default_text = ", ".join(tour.get("players", st.session_state.participants))
        part_input = st.text_area(
            "참가자 명단",
            value=default_text,
            height=100,
            placeholder="예) 홍길동, 이순신, 장보고\n또는 한 줄에 한 명씩 입력",
            help="이름 사이를 쉼표(,) 또는 줄바꿈으로 구분하세요."
        )

        save_col, clear_col = st.columns([2,1])
        with save_col:
            if st.button("✅ 참가자 저장", use_container_width=True, type="primary"):
                raw_names = part_input.replace("\n",",").split(",")
                parsed = [n.strip() for n in raw_names if n.strip()]
                roster_order = {nm:i for i,nm in enumerate(member_roster)}
                parsed_sorted = sorted(set(parsed),
                    key=lambda x: roster_order.get(x, len(member_roster)+1))
                st.session_state.participants = parsed_sorted
                tours[sel_tid]["players"] = parsed_sorted
                save_tours(tours)
                st.success(f"✅ {len(parsed_sorted)}명 저장 완료! (랭킹순 정렬됨)")
                st.rerun()
        with clear_col:
            if st.button("🗑 초기화", use_container_width=True):
                st.session_state.participants=[]
                tours[sel_tid]["players"]=[]
                save_tours(tours); st.rerun()

        sel_names = tour.get("players", st.session_state.participants)
        if sel_names:
            st.markdown(f"**현재 참가자 {len(sel_names)}명 (랭킹순):**")
            tags_html = "".join([f'<span class="p-tag">{n}</span>' for n in sel_names])
            st.markdown(f"<div style='line-height:2.2'>{tags_html}</div>", unsafe_allow_html=True)

            not_in_roster = [n for n in sel_names if n not in member_roster]
            if not_in_roster:
                st.warning(f"⚠️ 회원명부에 없는 참가자: {', '.join(not_in_roster)}")
        else:
            st.info("참가자를 입력하고 저장 버튼을 눌러주세요.")

        st.divider()

        # ── 대진 설정 ─────────────────────────────────────────
        st.markdown('<div class="sec">그룹·대진 설정 <small>(A,B,C 순서대로 랭킹 높은 순 배정)</small></div>',
                    unsafe_allow_html=True)
        if not sel_names:
            st.warning("먼저 참가자를 저장하세요."); st.stop()

        gcnt=st.number_input("그룹 수",1,6,min(4,max(1,len(sel_names)//8)))
        gns=list("ABCDEF")[:gcnt]; gcfg={}
        for i,gn in enumerate(gns):
            hx=GHEX[i%len(GHEX)]
            st.markdown(f"<div style='background:{hx}18;border-left:4px solid {hx};"
                        f"border-radius:7px;padding:5px 12px;margin:6px 0;"
                        f"font-weight:800;color:{hx}'>{GLBL[i%len(GLBL)]} 그룹 {gn}</div>",
                        unsafe_allow_html=True)
            cc=st.columns(4)
            dfsz=max(2,len(sel_names)//gcnt)
            with cc[0]: nm2=st.text_input("그룹명",gn,key=f"gn{i}")
            with cc[1]: sz =st.number_input("인원",2,30,dfsz,key=f"sz{i}")
            with cc[2]: md =st.selectbox("방식",["고정페어","KDK","단식"],key=f"md{i}")
            with cc[3]: gc =st.selectbox("1인 게임수",[3,4,5],index=1,key=f"gc{i}")
            gcfg[nm2]=(sz,md,gc)

        total=sum(c[0] for c in gcfg.values())
        diff=len(sel_names)-total
        (st.success if diff==0 else st.warning)(
            f"{'✅' if diff==0 else '⚠️'} 참가자 {len(sel_names)}명 / 배정 {total}명"
            +(f" (차이 {diff:+d}명)" if diff else ""))

        if st.button("🎲 대진 생성", type="primary", use_container_width=True):
            players_sorted = sel_names
            ptr=0; new_groups={}
            group_order = list(gcfg.keys())
            for gn in group_order:
                sz, md, gc = gcfg[gn]
                gp = players_sorted[ptr:ptr+sz]; ptr+=sz
                st.info(f"📌 {gn} 그룹: {', '.join(gp[:3])}{'...' if len(gp)>3 else ''} ({len(gp)}명)")
                if md=="고정페어": ms=make_fixed(gp)
                elif md=="KDK":
                    ms=make_kdk(gp,gc)
                    if not ms:
                        sh=random.sample(gp,len(gp))
                        pairs=[sh[i:i+2] for i in range(0,len(sh)-1,2)]
                        ms=[{"t1":list(a),"t2":list(b),"s1":0,"s2":0}
                            for x,a in enumerate(pairs) for b in pairs[x+1:]]
                        st.warning(f"그룹 {gn}: 한울 KDK 없음 → 랜덤 리그")
                else: ms=make_singles(gp)
                new_groups[gn]={"players":gp,"mode":md,"games":gc,"matches":ms}
            tours[sel_tid]["groups"]=new_groups; save_tours(tours)
            st.success("✅ 대진 생성 완료! (랭킹 높은 순 → A → B → C 그룹 순서로 배정됨)")
            st.rerun()

    # ── 탭3: 랭킹 관리 ─────────────────────────────────────────
    with adm[2]:
        st.markdown('<div class="sec">📁 엑셀 업로드 / 다운로드</div>', unsafe_allow_html=True)

        left_col, right_col = st.columns(2, gap="medium")

        with left_col:
            st.markdown("""
            <div class="rank-card">
              <div class="rank-card-title">📥 엑셀 업로드</div>
            </div>""", unsafe_allow_html=True)
            st.caption("컬럼: 랭킹 · 이름 · 현재포인트 · 3월 포인트 · 결과 · 부과점 · 그룹 · 비고")
            up = st.file_uploader("엑셀 또는 CSV 선택", type=["xlsx","csv"],
                                  key="rank_uploader", label_visibility="collapsed")
            if up:
                try:
                    df_up = (pd.read_excel(up) if up.name.endswith("xlsx")
                             else pd.read_csv(up, encoding_errors="replace"))
                    df_up.columns = [str(c).strip() for c in df_up.columns]
                    if "현재포인트" in df_up.columns:
                        df_up["현재포인트"] = pd.to_numeric(
                            df_up["현재포인트"], errors="coerce").fillna(0)
                        df_up = df_up.sort_values(
                            "현재포인트", ascending=False).reset_index(drop=True)
                        df_up["랭킹"] = df_up.index + 1
                    st.success(f"✅ 파일 인식 완료 — {len(df_up)}명")
                    st.dataframe(df_up, use_container_width=True, hide_index=True)
                    if st.button("💾 랭킹 저장 + 회원명부 등록",
                                 type="primary", use_container_width=True, key="btn_upload_save"):
                        save_rank(df_up)
                        if "이름" in df_up.columns:
                            save_members(df_up["이름"].astype(str).str.strip().tolist())
                        st.success(f"✅ {len(df_up)}명 저장 완료!")
                        st.rerun()
                except Exception as e:
                    st.error(f"파일 오류: {e}")
            else:
                st.markdown("""
                <div style='text-align:center;color:#aaa;padding:28px 0;font-size:.93rem'>
                    여기에 파일을 드래그하거나 클릭하여 업로드하세요
                </div>""", unsafe_allow_html=True)

        with right_col:
            st.markdown("""
            <div class="rank-card">
              <div class="rank-card-title">📊 현재 랭킹 미리보기</div>
            </div>""", unsafe_allow_html=True)
            df_cur = load_rank()
            if df_cur.empty:
                st.info("아직 업로드된 랭킹이 없습니다.")
            else:
                icons = ["🥇","🥈","🥉"]
                disp = df_cur.copy()
                disp.insert(0,"순위",[icons[i] if i<3 else str(i+1) for i in range(len(disp))])
                st.dataframe(disp, use_container_width=True, hide_index=True, height=320)
                st.download_button(
                    "📥 현재 랭킹 엑셀 다운로드",
                    data=to_excel(df_cur),
                    file_name=f"두류랭킹_{date.today()}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True,
                    key="btn_rank_dl")

        st.divider()
        st.markdown('<div class="sec">✏️ 랭킹 직접 수정</div>', unsafe_allow_html=True)
        st.caption("셀을 클릭해서 바로 수정하세요. 수정 후 반드시 저장 버튼을 눌러주세요.")

        df_edit = load_rank()
        if df_edit.empty:
            st.info("업로드된 랭킹 데이터가 없습니다.")
        else:
            edited = st.data_editor(
                df_edit, use_container_width=True, hide_index=True,
                num_rows="dynamic", key="rank_editor",
                column_config={
                    "랭킹":        st.column_config.NumberColumn("랭킹", width="small"),
                    "이름":        st.column_config.TextColumn("이름", width="medium"),
                    "현재포인트":  st.column_config.NumberColumn("현재포인트", width="medium"),
                    "3월 포인트":  st.column_config.NumberColumn("3월 포인트", width="medium"),
                    "결과":        st.column_config.TextColumn("결과", width="small"),
                    "부과점":      st.column_config.NumberColumn("부과점", width="small"),
                    "그룹":        st.column_config.TextColumn("그룹", width="small"),
                    "비고":        st.column_config.TextColumn("비고", width="large"),
                }
            )
            s1, s2 = st.columns(2, gap="medium")
            with s1:
                if st.button("💾 수정 내용 저장", type="primary",
                             use_container_width=True, key="btn_edit_save"):
                    save_rank(edited)
                    if "이름" in edited.columns:
                        save_members(edited["이름"].astype(str).str.strip().tolist())
                    st.success("✅ 저장 완료!")
                    st.rerun()
            with s2:
                st.download_button(
                    "📥 수정본 엑셀 다운로드",
                    data=to_excel(edited),
                    file_name=f"두류랭킹_수정_{date.today()}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True,
                    key="btn_edit_dl")

    # ── 탭4: 결과 반영 ─────────────────────────────────────────
    with adm[3]:
        tours=load_tours()
        active=[k for k,v in tours.items() if v.get("status")=="진행중"]
        if not active: st.warning("진행 중인 대회가 없습니다."); st.stop()

        sel_tid2=st.selectbox("반영할 대회",active,
            format_func=lambda k:f"{tours[k]['title']} ({tours[k].get('date','')})")
        tour3=tours[sel_tid2]
        st.markdown(f'<div class="sec">"{tour3["title"]}" 결과 → 랭킹 반영</div>', unsafe_allow_html=True)
        st.caption("고정페어: 1위+7 / 2위+5 / 3위+3 / 참가+1 │ KDK·단식: 1~2위+7 / 3~4위+5 / 5~6위+3 / 참가+1")

        if not tour3.get("groups"): st.warning("대진이 생성되지 않았습니다."); st.stop()

        earn={}; prev_rows=[]
        GRADE=["우승","우승","준우승","준우승","3위","3위"]
        for g,ginfo in tour3["groups"].items():
            mode=ginfo["mode"]; matches=ginfo["matches"]
            stats=group_stats(matches)
            ranked=sorted(stats.keys(),key=lambda t:(-stats[t]["승"],-stats[t]["득실"]))
            for ri,t in enumerate(ranked):
                pt=rank_pts(ri+1,mode)
                grade=(["우승","준우승","3위"][ri] if mode=="고정페어" and ri<3
                        else GRADE[ri] if ri<len(GRADE) else "참가")
                for p in list(t):
                    earn[p]=pt
                    prev_rows.append({"그룹":g,"팀/선수":tname(list(t)),
                                      "등급":grade,"이름":p,"부과점":pt})

        if prev_rows:
            st.dataframe(pd.DataFrame(prev_rows), use_container_width=True, hide_index=True)

        c1,c2=st.columns(2)
        with c1:
            if st.button("🏆 랭킹에 반영", type="primary", use_container_width=True):
                df_r=load_rank()
                if df_r.empty: df_r=pd.DataFrame(columns=COLS_RANK)
                if "현재포인트" in df_r.columns:
                    df_r["3월 포인트"]=pd.to_numeric(df_r["현재포인트"],errors="coerce").fillna(0)
                for p,pt in earn.items():
                    if p in df_r["이름"].values:
                        cur=pd.to_numeric(df_r.loc[df_r["이름"]==p,"현재포인트"],
                                          errors="coerce").fillna(0).values[0]
                        df_r.loc[df_r["이름"]==p,"현재포인트"]=cur+pt
                        df_r.loc[df_r["이름"]==p,"부과점"]=pt
                    else:
                        nr={c:"" for c in COLS_RANK}
                        nr.update({"이름":p,"현재포인트":pt,"3월 포인트":0,"부과점":pt})
                        df_r=pd.concat([df_r,pd.DataFrame([nr])],ignore_index=True)
                save_rank(df_r)
                if "이름" in df_r.columns:
                    save_members(df_r["이름"].astype(str).str.strip().tolist())
                tours[sel_tid2]["status"]="완료"; save_tours(tours)
                st.success("✅ 랭킹 반영 완료!"); st.rerun()
        with c2:
            if st.button("🗑 점수 초기화", use_container_width=True):
                for g in tour3["groups"]:
                    for m in tour3["groups"][g]["matches"]:
                        m["s1"]=0; m["s2"]=0
                tours[sel_tid2]=tour3; save_tours(tours)
                st.success("✅ 점수 초기화"); st.rerun()

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

# UI 개선 CSS - 가운데 정렬 강화
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;600;700;900&display=swap');
* {
    font-family: 'Noto Sans KR', sans-serif !important;
}
.block-container { padding: 0 0.8rem 2rem !important; max-width: 100% !important; }

/* 네비게이션 바 */
section.main [data-testid="stHorizontalBlock"]:first-of-type .stButton > button {
    background: transparent !important;
    color: rgba(255,255,255,0.72) !important;
    border: none !important; border-radius: 0 !important;
    font-size: clamp(0.85rem, 2.2vw, 1.05rem) !important;
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
    margin-bottom:1rem; font-size:clamp(1.2rem,4vw,1.8rem);
    font-weight:900; text-align:center;
    box-shadow:0 6px 18px rgba(0,0,0,0.14);
}
.sec {
    font-size:1.1rem; font-weight:900; color:#1D5B2E;
    border-left:5px solid #66BB6A; padding-left:12px; margin:16px 0 10px;
}

/* 탭 */
button[data-baseweb="tab"] {
    font-size:1rem!important; font-weight:700!important;
    padding:10px 20px!important; border-radius:8px 8px 0 0!important;
}
button[data-baseweb="tab"][aria-selected="true"] {
    background:linear-gradient(135deg,#1D5B2E,#388E3C)!important; color:#fff!important;
}

/* ================================================================
   ★★★★★ 강력한 가운데 정렬 - 모든 테이블 ★★★★★
   ================================================================ */
div[data-testid="stDataFrame"] table,
div[data-testid="stDataEditor"] table,
.stDataFrame table,
.stDataEditor table,
table.dataframe,
.dataframe {
    width: 100% !important;
}

div[data-testid="stDataFrame"] table th,
div[data-testid="stDataFrame"] table td,
div[data-testid="stDataEditor"] table th,
div[data-testid="stDataEditor"] table td,
.stDataFrame th, .stDataFrame td,
.stDataEditor th, .stDataEditor td,
table th, table td,
.dataframe th, .dataframe td {
    text-align: center !important;
    vertical-align: middle !important;
    padding: 10px 8px !important;
}

/* 숫자 입력 필드 가운데 정렬 */
input[type="number"] {
    text-align: center !important;
    font-size: 1.1rem !important;
    font-weight: 700 !important;
}
div[data-testid="stNumberInput"] input {
    text-align: center !important;
    font-weight: 700 !important;
    font-size: 1.1rem !important;
    padding: 8px !important;
}

/* 텍스트 입력 필드 가운데 정렬 */
input[type="text"], textarea {
    text-align: center !important;
}

/* 드롭다운 가운데 정렬 */
select {
    text-align: center !important;
    text-align-last: center !important;
}

/* 경기 입력 행 전체 가운데 정렬 */
div[data-testid="column"] {
    display: flex;
    flex-direction: column;
    align-items: center;
}

/* 팀 도형 */
.team-box {
    border-radius:14px; 
    padding: 12px 16px !important; 
    font-weight: 800 !important;
    font-size: 1rem !important;
    text-align: center;
    margin: 5px 0;
    box-shadow: 0 3px 10px rgba(0,0,0,.1);
    line-height: 1.4;
    min-height: 55px;
    display: flex;
    align-items: center;
    justify-content: center;
    width: 100%;
}
.tg{background:linear-gradient(135deg,#66BB6A,#43A047);color:#fff}
.tb{background:linear-gradient(135deg,#42A5F5,#1E88E5);color:#fff}
.to{background:linear-gradient(135deg,#FFA726,#FB8C00);color:#fff}
.tp{background:linear-gradient(135deg,#AB47BC,#8E24AA);color:#fff}
.tr{background:linear-gradient(135deg,#EF5350,#E53935);color:#fff}
.tt{background:linear-gradient(135deg,#26A69A,#00897B);color:#fff}

/* 경기별 색상 클래스 */
.match-color-0 { background: linear-gradient(135deg,#66BB6A,#43A047) !important; color:#fff; }
.match-color-1 { background: linear-gradient(135deg,#42A5F5,#1E88E5) !important; color:#fff; }
.match-color-2 { background: linear-gradient(135deg,#FFA726,#FB8C00) !important; color:#fff; }

/* VS 원 */
.vs-circle {
    background:#FFB74D; 
    color:#fff; 
    border-radius:50%;
    width: 48px !important;
    height: 48px !important;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 900;
    font-size: 1rem;
    margin: 0 auto;
    box-shadow: 0 3px 10px rgba(255,183,77,.4);
}

/* 구분선 */
hr {
    margin: 15px 0;
    border-color: #ddd;
}

/* 참가자 태그 */
.p-tag {
    display:inline-block; 
    background:#E8F5E9; 
    border:1.5px solid #66BB6A;
    border-radius:25px; 
    padding:6px 14px; 
    margin:4px 6px;
    font-size:0.95rem; 
    font-weight:700; 
    color:#1D5B2E;
}

/* 카드 스타일 */
.tour-card, .rank-card {
    background:#fff; 
    border:1.5px solid #C8E6C9; 
    border-radius:14px;
    padding:12px 18px; 
    margin:8px 0;
    box-shadow:0 3px 12px rgba(0,0,0,0.07);
}
.rank-card-title {
    font-size:1.05rem; 
    font-weight:900; 
    color:#1D5B2E;
    border-bottom:2px solid #A5D6A7; 
    padding-bottom:10px; 
    margin-bottom:16px;
    text-align:center;
}

/* 매트릭스 테이블 */
.matrix-table {
    width: 100%;
    border-collapse: collapse;
    text-align: center;
    margin: 0 auto;
}
.matrix-table th, .matrix-table td {
    padding: 10px;
    text-align: center;
    border: 1px solid #ddd;
    font-size: 0.9rem;
}
.matrix-table th {
    background-color: #f5f5f5;
    font-weight: 700;
}
.matrix-grey {
    background-color: #d0d0d0;
    color: #d0d0d0;
}
.matrix-x {
    color: #999;
    font-weight: normal;
}

/* KDK 대진표 스타일 */
.kdk-bracket {
    background: #f5f5f5;
    border-radius: 12px;
    padding: 15px;
    margin: 10px 0;
    font-size: 0.9rem;
    overflow-x: auto;
}
.kdk-bracket table {
    width: 100%;
    border-collapse: collapse;
}
.kdk-bracket th, .kdk-bracket td {
    padding: 8px;
    text-align: center;
    border: 1px solid #ddd;
}
.kdk-bracket th {
    background-color: #e8f5e9;
}

/* 버튼 스타일 */
.stButton > button {
    border-radius: 10px !important;
    font-weight: 700 !important;
    font-size: 0.95rem !important;
    padding: 0.5rem 1rem !important;
    transition: all 0.2s ease !important;
}
.stButton > button:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0,0,0,0.15);
}

/* 데이터프레임 내부 글자 크기 및 가운데 정렬 */
.dataframe td, .dataframe th {
    font-size: 0.9rem !important;
    text-align: center !important;
}

/* 스트림릿 기본 테이블도 가운데 정렬 */
.stTable td, .stTable th {
    text-align: center !important;
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
GHEX = ["#66BB6A","#42A5F5","#FFA726","#AB47BC","#EF5350","#26A69A"]
GLBL = ["🟢","🔵","🟠","🟣","🔴","🩵"]

# ══════════════════════════════════════════════════════════════
# KDK 대진표 (1인 3게임)
# ══════════════════════════════════════════════════════════════
KDK_3G = {
    4: [(1,4,2,3), (1,3,2,4), (1,2,3,4)],
    8: [(1,2,3,4), (5,6,7,8), (1,8,2,7), (3,6,4,5), (1,4,5,8), (2,3,6,7)],
    12: [(1,2,3,4), (5,6,7,8), (9,10,11,12), (1,3,5,7), (2,4,6,8),
         (9,11,1,5), (4,8,9,12), (6,7,10,11), (10,12,2,3)]
}

# ══════════════════════════════════════════════════════════════
# KDK 대진표 (1인 4게임)
# ══════════════════════════════════════════════════════════════
KDK_4G = {
    5: [(1,2,3,4), (1,3,2,5), (1,4,3,5), (1,5,2,4), (2,3,4,5)],
    6: [(1,3,2,4), (1,5,4,6), (2,3,5,6), (1,4,3,5), (2,6,3,4), (1,6,2,5)],
    7: [(1,2,3,4), (5,6,1,7), (2,3,5,7), (1,4,6,7), (3,5,2,4), (1,6,2,5), (4,6,3,7)],
    8: [(1,2,3,4), (5,6,7,8), (1,3,5,7), (2,4,6,8), (1,5,2,6), (3,7,4,8), (1,6,3,8), (2,5,4,7)],
    9: [(1,2,3,4), (5,6,7,8), (1,9,5,7), (2,3,6,8), (4,9,3,8), (1,5,2,6), (3,6,4,5), (1,7,8,9), (2,4,7,9)],
    10: [(1,2,3,5), (6,7,8,10), (2,3,4,6), (7,8,1,9), (3,4,5,7), (8,9,2,10),
         (4,5,6,8), (1,3,9,10), (5,6,7,9), (1,10,2,4)],
    11: [(1,2,3,5), (6,7,8,10), (4,9,1,11), (2,3,6,8), (4,5,7,10), (9,11,2,6),
         (1,3,7,11), (4,8,5,9), (1,10,2,8), (4,7,6,11), (3,9,5,10)]
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

def group_stats_fixed(matches):
    stats = {}
    for m in matches:
        t1 = tuple(m["t1"])
        t2 = tuple(m["t2"])
        for t in [t1, t2]:
            if t not in stats:
                stats[t] = {"승": 0, "패": 0, "득실": 0}
        s1, s2 = int(m["s1"]), int(m["s2"])
        if s1 > s2:
            stats[t1]["승"] += 1
            stats[t2]["패"] += 1
        elif s2 > s1:
            stats[t2]["승"] += 1
            stats[t1]["패"] += 1
        stats[t1]["득실"] += (s1 - s2)
        stats[t2]["득실"] += (s2 - s1)
    return stats

def group_stats_kdk(matches):
    stats = {}
    for m in matches:
        players1 = m["t1"]
        players2 = m["t2"]
        
        for p in players1 + players2:
            if p not in stats:
                stats[p] = {"승": 0, "패": 0, "득실": 0}
        
        s1, s2 = int(m["s1"]), int(m["s2"])
        if s1 > s2:
            for p in players1:
                stats[p]["승"] += 1
            for p in players2:
                stats[p]["패"] += 1
        elif s2 > s1:
            for p in players2:
                stats[p]["승"] += 1
            for p in players1:
                stats[p]["패"] += 1
        
        for p in players1:
            stats[p]["득실"] += (s1 - s2)
        for p in players2:
            stats[p]["득실"] += (s2 - s1)
    return stats

def rank_pts(rank, mode):
    if mode == "고정페어":
        return {1:7, 2:5, 3:3}.get(rank, 1)
    else:
        if rank <= 2:
            return 7
        elif rank <= 4:
            return 5
        elif rank <= 6:
            return 3
        else:
            return 1

def get_grade_kdk(rank):
    if rank <= 2:
        return "우승"
    elif rank <= 4:
        return "준우승"
    elif rank <= 6:
        return "3위"
    else:
        return "참가"

# ══════════════════════════════════════════════════════════════
# KDK 대진 생성 함수
# ══════════════════════════════════════════════════════════════
def make_kdk(players, games_per_person):
    n = len(players)
    
    if games_per_person == 3:
        bp = KDK_3G.get(n)
    else:
        bp = KDK_4G.get(n)
    
    if not bp:
        return None, {}
    
    shuffled = random.sample(players, n)
    player_with_number = {shuffled[i]: i+1 for i in range(n)}
    number_to_player = {i+1: shuffled[i] for i in range(n)}
    
    matches = []
    for a, b, c, d in bp:
        matches.append({
            "t1": [number_to_player[a], number_to_player[b]],
            "t2": [number_to_player[c], number_to_player[d]],
            "s1": 0,
            "s2": 0
        })
    
    return matches, player_with_number

def make_fixed(players):
    n = len(players)
    pairs = [(players[i], players[n-1-i]) for i in range(n//2)]
    ms = []
    for i in range(len(pairs)):
        for j in range(i+1, len(pairs)):
            ms.append({"t1": list(pairs[i]), "t2": list(pairs[j]), "s1": 0, "s2": 0})
    random.shuffle(ms)
    return ms, {}

def make_singles(players):
    pl = players[:]
    random.shuffle(pl)
    ms = [(pl[i], pl[j]) for i in range(len(pl)) for j in range(i+1, len(pl))]
    random.shuffle(ms)
    return [{"t1": [a], "t2": [b], "s1": 0, "s2": 0} for a, b in ms], {}

# ══════════════════════════════════════════════════════════════
# KDK 대진표 표시 함수
# ══════════════════════════════════════════════════════════════
def display_kdk_bracket(n, games_per_person, player_with_number):
    if games_per_person == 3:
        bracket = KDK_3G.get(n)
        title = f"📋 KDK (한울방식) 1인 3게임 기준 - {n}명"
    else:
        bracket = KDK_4G.get(n)
        title = f"📋 KDK (한울방식) 1인 4게임 기준 - {n}명"
    
    if not bracket:
        return
    
    number_to_name = {v: k for k, v in player_with_number.items()}
    
    st.markdown(f'<div class="kdk-bracket"><strong>{title}</strong>', unsafe_allow_html=True)
    
    html = '<table>'
    html += '<thead></td><th>순서</th><th>대진 번호</th><th>대진 (참가자)</th></tr></thead><tbody>'
    
    for idx, (a, b, c, d) in enumerate(bracket):
        team1 = f"{number_to_name.get(a, a)}({a}) & {number_to_name.get(b, b)}({b})"
        team2 = f"{number_to_name.get(c, c)}({c}) & {number_to_name.get(d, d)}({d})"
        html += f'<tr><td>{idx+1}</td><td>{a}{b}:{c}{d}</td><td>{team1} vs {team2}</td></tr>'
    
    html += '</tbody></table></div>'
    st.markdown(html, unsafe_allow_html=True)

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
      font-size:0.85rem;letter-spacing:2px;font-weight:600;
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
        disp = df.copy()
        disp.insert(0, "순위", [icons[i] if i<3 else str(i+1) for i in range(len(disp))])
        st.dataframe(disp, use_container_width=True, hide_index=True)
        st.download_button(
            "📥 랭킹 엑셀 다운로드", data=to_excel(df),
            file_name=f"두류랭킹_{date.today()}.xlsx",
            use_container_width=True)

# ══════════════════════════════════════════════════════════════
# 2. 📅 대진 및 경기 현황
# ══════════════════════════════════════════════════════════════
elif M == "schedule":
    tours = load_tours()
    active = [k for k,v in tours.items() if v.get("status")=="진행중"]
    if not active:
        st.warning("⚠️ 진행 중인 대회가 없습니다. 관리자에서 대회를 생성하세요.")
        st.stop()
    tid = active[-1]
    tour = tours[tid]
    st.markdown(f"<div class='main-hdr'>📅 {tour['title']}</div>", unsafe_allow_html=True)
    st.caption(f"📅 {tour.get('date','')}  |  📍 {tour.get('place','')}  |  코트 {tour.get('courts',2)}면")

    gnames = list(tour["groups"].keys())
    if not gnames:
        st.info("관리자에서 대진을 생성하세요.")
        st.stop()

    # 그룹명을 A그룹, B그룹, C그룹 형식으로 표시
    tabs = st.tabs([f"{GLBL[i%len(GLBL)]} {gn}{'그룹' if not gn.endswith('그룹') else ''}" for i, gn in enumerate(gnames)])
    for ti, g in enumerate(gnames):
        with tabs[ti]:
            ginfo = tour["groups"][g]
            matches = ginfo["matches"]
            mode = ginfo["mode"]
            cls = GCLS[ti % len(GCLS)]
            player_with_number = ginfo.get("player_with_number", {})
            
            is_fixed = (mode == "고정페어")
            is_kdk = (mode == "KDK")
            
            # 순위 계산
            if is_fixed:
                stats = group_stats_fixed(matches)
                rank_items = list(stats.keys())
                rank_display_name = "팀"
            else:
                stats = group_stats_kdk(matches)
                rank_items = list(stats.keys())
                rank_display_name = "선수"
            
            # 상대별 전적 매트릭스
            st.markdown("**📋 상대별 전적 매트릭스**")
            if matches:
                if is_fixed:
                    all_teams = list(set([tuple(m["t1"]) for m in matches] + [tuple(m["t2"]) for m in matches]))
                    lab = {t: " & ".join(list(t)) for t in all_teams}
                else:
                    all_players = list(set([p for m in matches for p in m["t1"] + m["t2"]]))
                    lab = {p: f"{p}({player_with_number.get(p, '?')})" for p in all_players}
                
                mat = {lab[t]: {lab[o]: ("■" if t==o else "X") for o in lab.keys()} for t in lab.keys()}
                for m in matches:
                    if is_fixed:
                        t1 = tuple(m["t1"])
                        t2 = tuple(m["t2"])
                    else:
                        players1 = m["t1"]
                        players2 = m["t2"]
                    s1, s2 = int(m["s1"]), int(m["s2"])
                    if s1 > 0 or s2 > 0:
                        if is_fixed:
                            mat[lab[t1]][lab[t2]] = f"{s1}:{s2}"
                            mat[lab[t2]][lab[t1]] = f"{s2}:{s1}"
                        else:
                            for p1 in players1:
                                for p2 in players2:
                                    mat[lab[p1]][lab[p2]] = f"{s1}:{s2}"
                                    mat[lab[p2]][lab[p1]] = f"{s2}:{s1}"
                mdf = pd.DataFrame(mat).T
                
                html_table = '<table class="matrix-table">'
                html_table += '<thead><tr><th></th>'
                for col in mdf.columns:
                    html_table += f'<th>{col}</th>'
                html_table += '</tr></thead><tbody>'
                for idx, row in mdf.iterrows():
                    html_table += f'<tr><th><strong>{idx}</strong></th>'
                    for col in mdf.columns:
                        val = row[col]
                        if val == '■':
                            html_table += f'<td class="matrix-grey">■</td>'
                        elif val == 'X':
                            html_table += f'<td class="matrix-x">X</td>'
                        else:
                            html_table += f'<td>{val}</td>'
                    html_table += '</tr>'
                html_table += '</tbody></table>'
                st.markdown(html_table, unsafe_allow_html=True)
            else:
                st.info("경기 데이터가 없습니다.")
            
            # KDK 대진표
            if is_kdk and player_with_number:
                st.divider()
                n = len(player_with_number)
                gc = ginfo.get("games", 3)
                display_kdk_bracket(n, gc, player_with_number)
            
            # 현재 순위
            st.divider()
            st.markdown(f"**🏅 현재 순위 ({rank_display_name} 단위)**")
            if rank_items:
                ranked = sorted(rank_items, key=lambda x: (-stats[x]["승"], -stats[x]["득실"]))
                
                rows = []
                for i, item in enumerate(ranked):
                    if is_fixed:
                        grade = ["우승","준우승","3위"][i] if i<3 else "참가"
                        rows.append({
                            "순위": ["🥇","🥈","🥉"][i] if i<3 else i+1,
                            "팀": " & ".join(list(item)),
                            "승": stats[item]["승"],
                            "패": stats[item]["패"],
                            "득실": f'{stats[item]["득실"]:+d}',
                            "비고": grade
                        })
                    else:
                        grade = get_grade_kdk(i+1)
                        rows.append({
                            "순위": ["🥇","🥈","🥉"][i] if i<3 else i+1,
                            "선수": item,
                            "승": stats[item]["승"],
                            "패": stats[item]["패"],
                            "득실": f'{stats[item]["득실"]:+d}',
                            "비고": grade
                        })
                rdf = pd.DataFrame(rows)
                st.dataframe(rdf, use_container_width=True, hide_index=True)
            else:
                st.info("순위 정보가 없습니다.")
            
            st.divider()
            
            # 경기 입력
            st.markdown(f"**🎾 경기 입력 (페어 단위)**")
            
            changed = False
            for mi, m in enumerate(matches):
                t1 = " & ".join(m["t1"])
                t2 = " & ".join(m["t2"])
                
                color_idx = mi % 3
                color_class = ["match-color-0", "match-color-1", "match-color-2"][color_idx]
                
                c1, c2, c3 = st.columns([4, 1, 4], gap="medium")
                
                with c1:
                    st.markdown(f'<div class="team-box {color_class}" style="font-size:1rem;">{t1}</div>', unsafe_allow_html=True)
                    s1 = st.number_input(f"점수_{mi}", 0, 50, int(m["s1"]),
                                         key=f"{tid}_{g}_{mi}_s1",
                                         label_visibility="collapsed",
                                         step=1)
                
                with c2:
                    st.markdown('<div class="vs-circle">VS</div>', unsafe_allow_html=True)
                
                with c3:
                    st.markdown(f'<div class="team-box {color_class}" style="font-size:1rem;">{t2}</div>', unsafe_allow_html=True)
                    s2 = st.number_input(f"점수_{mi}_2", 0, 50, int(m["s2"]),
                                         key=f"{tid}_{g}_{mi}_s2",
                                         label_visibility="collapsed",
                                         step=1)
                
                if s1 != int(m["s1"]) or s2 != int(m["s2"]):
                    tour["groups"][g]["matches"][mi]["s1"] = s1
                    tour["groups"][g]["matches"][mi]["s2"] = s2
                    changed = True
                
                if mi < len(matches) - 1:
                    st.markdown("<hr>", unsafe_allow_html=True)
            
            if changed:
                tours[tid] = tour
                save_tours(tours)
                st.toast("✅ 점수가 저장되었습니다!", icon="✅")

# ══════════════════════════════════════════════════════════════
# 3. 📊 경기 결과
# ══════════════════════════════════════════════════════════════
elif M == "result":
    tours = load_tours()
    active = [k for k,v in tours.items() if v.get("status")=="진행중"]
    if not active:
        st.warning("⚠️ 진행 중인 대회가 없습니다.")
        st.stop()
    tid = active[-1]
    tour = tours[tid]
    st.markdown(f"<div class='main-hdr'>📊 {tour['title']} — 경기 결과</div>", unsafe_allow_html=True)

    for g, ginfo in tour["groups"].items():
        mode = ginfo["mode"]
        matches = ginfo["matches"]
        player_with_number = ginfo.get("player_with_number", {})
        
        is_fixed = (mode == "고정페어")
        is_kdk = (mode == "KDK")
        
        if is_fixed:
            stats = group_stats_fixed(matches)
            items = list(stats.keys())
            ranked = sorted(items, key=lambda t: (-stats[t]["승"], -stats[t]["득실"]))
            display_name = "팀"
        else:
            stats = group_stats_kdk(matches)
            items = list(stats.keys())
            ranked = sorted(items, key=lambda p: (-stats[p]["승"], -stats[p]["득실"]))
            display_name = "선수"
        
        # 그룹명 표시
        group_display = g if g.endswith('그룹') else f"{g}그룹"
        st.markdown(f'<div class="sec">{group_display} ({mode})</div>', unsafe_allow_html=True)
        
        # KDK 대진표
        if is_kdk and player_with_number:
            n = len(player_with_number)
            gc = ginfo.get("games", 3)
            display_kdk_bracket(n, gc, player_with_number)
            st.divider()
        
        # 최종 순위
        st.markdown(f"**🏆 최종 순위 ({display_name} 단위)**")
        rows = []
        
        for i, item in enumerate(ranked):
            pt = rank_pts(i+1, mode)
            
            if is_fixed:
                grade = ["우승","준우승","3위"][i] if i<3 else "참가"
                rows.append({
                    "순위": ["🥇","🥈","🥉"][i] if i<3 else i+1,
                    "팀": " & ".join(list(item)),
                    "승": stats[item]["승"],
                    "패": stats[item]["패"],
                    "득실": f'{stats[item]["득실"]:+d}',
                    "부과점": pt,
                    "등급": grade
                })
            else:
                grade = get_grade_kdk(i+1)
                rows.append({
                    "순위": i+1,
                    "선수": item,
                    "승": stats[item]["승"],
                    "패": stats[item]["패"],
                    "득실": f'{stats[item]["득실"]:+d}',
                    "부과점": pt,
                    "비고": grade
                })
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
        
        with st.expander(f"📋 {group_display} 전체 경기 결과 상세보기"):
            mrows = []
            for m in matches:
                t1 = " & ".join(m["t1"])
                t2 = " & ".join(m["t2"])
                s1, s2 = int(m["s1"]), int(m["s2"])
                result = "🏆 " + t1 + " 승" if s1 > s2 else "🏆 " + t2 + " 승" if s2 > s1 else "🤝 무승부"
                mrows.append({
                    "페어1": t1,
                    "점수1": s1,
                    "점수2": s2,
                    "페어2": t2,
                    "결과": result
                })
            st.dataframe(pd.DataFrame(mrows), use_container_width=True, hide_index=True)

# ══════════════════════════════════════════════════════════════
# 4. 📂 지난 대회 아카이브
# ══════════════════════════════════════════════════════════════
elif M == "archive":
    st.markdown("<div class='main-hdr'>📂 지난 대회 아카이브</div>", unsafe_allow_html=True)
    tours = load_tours()
    past = {k:v for k,v in tours.items() if v.get("status")!="진행중"}
    if not past:
        st.info("완료된 대회 기록이 없습니다.")
        st.stop()

    sel = st.selectbox("대회 선택", list(past.keys()),
        format_func=lambda k: f"{past[k]['title']}  ({past[k].get('date','날짜없음')})")
    tour = past[sel]
    st.markdown(f"**🏆 {tour['title']}** &nbsp; 📅 {tour.get('date','')} | 📍 {tour.get('place','')}")
    st.divider()
    if not tour.get("groups"):
        st.info("대진 정보가 없습니다.")
        st.stop()

    for g, ginfo in tour["groups"].items():
        mode = ginfo["mode"]
        matches = ginfo["matches"]
        player_with_number = ginfo.get("player_with_number", {})
        
        is_fixed = (mode == "고정페어")
        is_kdk = (mode == "KDK")
        
        if is_fixed:
            stats = group_stats_fixed(matches)
            items = list(stats.keys())
            ranked = sorted(items, key=lambda t: (-stats[t]["승"], -stats[t]["득실"]))
            display_name = "팀"
        else:
            stats = group_stats_kdk(matches)
            items = list(stats.keys())
            ranked = sorted(items, key=lambda p: (-stats[p]["승"], -stats[p]["득실"]))
            display_name = "선수"
        
        group_display = g if g.endswith('그룹') else f"{g}그룹"
        st.markdown(f'<div class="sec">{group_display} ({mode})</div>', unsafe_allow_html=True)
        
        # KDK 대진표
        if is_kdk and player_with_number:
            n = len(player_with_number)
            gc = ginfo.get("games", 3)
            display_kdk_bracket(n, gc, player_with_number)
            st.divider()
        
        st.markdown(f"**🏆 최종 순위 ({display_name} 단위)**")
        rows = []
        for i, item in enumerate(ranked):
            pt = rank_pts(i+1, mode)
            if is_fixed:
                grade = ["우승","준우승","3위"][i] if i<3 else "참가"
                rows.append({
                    "순위": ["🥇","🥈","🥉"][i] if i<3 else i+1,
                    "팀/선수": " & ".join(list(item)),
                    "승": stats[item]["승"],
                    "패": stats[item]["패"],
                    "득실": f'{stats[item]["득실"]:+d}',
                    "부과점": pt,
                    "등급": grade
                })
            else:
                grade = get_grade_kdk(i+1)
                rows.append({
                    "순위": i+1,
                    "선수": item,
                    "승": stats[item]["승"],
                    "패": stats[item]["패"],
                    "득실": f'{stats[item]["득실"]:+d}',
                    "부과점": pt,
                    "비고": grade
                })
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
        
        with st.expander(f"📋 {group_display} 전체 경기 결과"):
            mrows = []
            for m in matches:
                t1 = " & ".join(m["t1"])
                t2 = " & ".join(m["t2"])
                s1, s2 = int(m["s1"]), int(m["s2"])
                result = "🏆 " + t1 + " 승" if s1 > s2 else "🏆 " + t2 + " 승" if s2 > s1 else "🤝 무승부"
                mrows.append({
                    "페어1": t1,
                    "점수1": s1,
                    "점수2": s2,
                    "페어2": t2,
                    "결과": result
                })
            st.dataframe(pd.DataFrame(mrows), use_container_width=True, hide_index=True)

# ══════════════════════════════════════════════════════════════
# 5. ⚙️ 관리자
# ══════════════════════════════════════════════════════════════
elif M == "admin":
    st.markdown("<div class='main-hdr'>⚙️ 관리자 센터</div>", unsafe_allow_html=True)
    pw = st.text_input("🔒 관리자 비밀번호", type="password", placeholder="비밀번호 입력")
    if pw == ADMIN_PW:
        st.session_state.is_admin = True
    if not st.session_state.is_admin:
        if pw and pw != ADMIN_PW:
            st.error("❌ 비밀번호가 틀렸습니다.")
        st.stop()
    st.success("✅ 관리자 모드 활성화")

    adm = st.tabs(["🏆 대회 관리", "👥 참가자·대진", "📋 랭킹 관리", "💾 결과 반영"])

    # 탭1: 대회 관리
    with adm[0]:
        st.markdown('<div class="sec">새 대회 생성</div>', unsafe_allow_html=True)
        with st.form("f_new_tour"):
            c1, c2 = st.columns(2)
            tn = c1.text_input("대회명", placeholder="예: 5월 정기전")
            td = c2.date_input("날짜", value=date.today())
            c3, c4 = st.columns(2)
            tp = c3.text_input("장소", placeholder="예: 두류공원 테니스장")
            courts = c4.selectbox("코트 수", [1,2,3], index=1)
            if st.form_submit_button("✅ 대회 생성", type="primary", use_container_width=True):
                if not tn.strip():
                    st.error("대회명을 입력하세요.")
                else:
                    tours = load_tours()
                    tid = f"{td}_{tn.strip()}"
                    if tid in tours:
                        st.warning("같은 날짜·이름의 대회가 이미 있습니다.")
                    else:
                        tours[tid] = {
                            "title": tn.strip(),
                            "date": str(td),
                            "place": tp,
                            "courts": courts,
                            "status": "진행중",
                            "groups": {}
                        }
                        save_tours(tours)
                        st.success(f"🎉 '{tn}' 대회 생성!")
                        st.rerun()
        st.divider()
        st.markdown('<div class="sec">대회 목록 (수정·삭제)</div>', unsafe_allow_html=True)
        tours = load_tours()
        if not tours:
            st.info("생성된 대회가 없습니다.")
        else:
            SC = {"진행중": "#FB8C00", "완료": "#43A047", "예정": "#1E88E5"}
            for tid2, tv in list(tours.items()):
                sc = SC.get(tv.get("status", ""), "#888")
                st.markdown(f"""
                <div class="tour-card">
                  <span style="font-weight:900">{tv['title']}</span>&nbsp;
                  <span style="font-size:.9rem;color:#555">📅{tv.get('date','')} 📍{tv.get('place','')} 코트{tv.get('courts',2)}면</span>
                  <span style="color:{sc};font-weight:800;margin-left:8px">[{tv.get('status','')}]</span>
                </div>
                """, unsafe_allow_html=True)
                ca, cb, cc, cd = st.columns([2,3,2,2])
                with ca:
                    new_st = st.selectbox("상태", ["진행중","완료","예정"],
                        index=["진행중","완료","예정"].index(tv.get("status","진행중")),
                        key=f"st_{tid2}", label_visibility="collapsed")
                with cb:
                    new_title = st.text_input("대회명", tv["title"],
                        key=f"tt_{tid2}", label_visibility="collapsed")
                with cc:
                    if st.button("💾 수정", key=f"edit_{tid2}", use_container_width=True):
                        tours[tid2]["title"] = new_title
                        tours[tid2]["status"] = new_st
                        save_tours(tours)
                        st.rerun()
                with cd:
                    if st.button("🗑 삭제", key=f"del_{tid2}", use_container_width=True):
                        del tours[tid2]
                        save_tours(tours)
                        st.rerun()

    # 탭2: 참가자·대진
    with adm[1]:
        tours = load_tours()
        active = [k for k,v in tours.items() if v.get("status") == "진행중"]
        if not active:
            st.warning("진행 중인 대회를 먼저 생성하세요.")
            st.stop()

        sel_tid = st.selectbox("진행 중 대회", active,
            format_func=lambda k: f"{tours[k]['title']} ({tours[k].get('date','')})")
        tour = tours[sel_tid]
        st.info(f"현재 대회: **{tour['title']}** | 코트 {tour.get('courts',2)}면")

        st.markdown('<div class="sec">참가자 입력</div>', unsafe_allow_html=True)

        member_roster = load_members()
        st.caption("이름을 쉼표(,) 또는 줄바꿈으로 구분해서 입력하고 **저장** 버튼을 누르세요.")

        default_text = ", ".join(tour.get("players", st.session_state.participants))
        part_input = st.text_area(
            "참가자 명단",
            value=default_text,
            height=100,
            placeholder="예) 홍길동, 이순신, 장보고\n또는 한 줄에 한 명씩 입력"
        )

        save_col, clear_col = st.columns([2,1])
        with save_col:
            if st.button("✅ 참가자 저장", use_container_width=True, type="primary"):
                raw_names = part_input.replace("\n", ",").split(",")
                parsed = [n.strip() for n in raw_names if n.strip()]
                roster_order = {nm: i for i, nm in enumerate(member_roster)}
                parsed_sorted = sorted(set(parsed),
                    key=lambda x: roster_order.get(x, len(member_roster)+1))
                st.session_state.participants = parsed_sorted
                tours[sel_tid]["players"] = parsed_sorted
                save_tours(tours)
                st.success(f"✅ {len(parsed_sorted)}명 저장 완료! (랭킹순 정렬됨)")
                st.rerun()
        with clear_col:
            if st.button("🗑 초기화", use_container_width=True):
                st.session_state.participants = []
                tours[sel_tid]["players"] = []
                save_tours(tours)
                st.rerun()

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

        # ============================================================
        # 개별 참가자 수정 섹션 (대진 완성 후에도 수정 가능)
        # ============================================================
        st.markdown('<div class="sec">✏️ 개별 참가자 수정 (대진 유지)</div>', unsafe_allow_html=True)
        st.caption("대진이 이미 생성된 후에도 참가자를 개별적으로 수정할 수 있습니다. 랭킹 순서와 상관없이 원하는 그룹에 배정할 수 있습니다.")
        
        if tour.get("groups"):
            # 현재 그룹 목록 표시
            groups = list(tour["groups"].keys())
            if groups:
                col_sel_group, col_sel_player, col_action = st.columns([2, 2, 1])
                
                with col_sel_group:
                    selected_group = st.selectbox("수정할 그룹 선택", groups, 
                                                   format_func=lambda x: f"{x}그룹" if not x.endswith('그룹') else x)
                
                # 해당 그룹의 현재 참가자 목록
                current_players = tour["groups"][selected_group]["players"]
                
                with col_sel_player:
                    selected_player = st.selectbox("수정할 참가자 선택", current_players if current_players else ["없음"])
                
                with col_action:
                    if st.button("🗑 해당 참가자 삭제", use_container_width=True):
                        if selected_player != "없음" and selected_player in current_players:
                            # 참가자 삭제
                            new_players = [p for p in current_players if p != selected_player]
                            tour["groups"][selected_group]["players"] = new_players
                            # 대진에서도 해당 참가자 제거
                            new_matches = []
                            for m in tour["groups"][selected_group]["matches"]:
                                if selected_player in m["t1"] or selected_player in m["t2"]:
                                    continue  # 해당 경기 제거
                                new_matches.append(m)
                            tour["groups"][selected_group]["matches"] = new_matches
                            
                            # 전체 players 목록에서도 제거
                            if selected_player in tour.get("players", []):
                                tour["players"].remove(selected_player)
                            
                            save_tours(tours)
                            st.success(f"✅ '{selected_player}' 님이 삭제되었습니다!")
                            st.rerun()
                
                st.markdown("---")
                
                # 새 참가자 추가
                st.markdown("**➕ 새 참가자 추가**")
                col_new_name, col_new_group, col_add = st.columns([2, 2, 1])
                
                with col_new_name:
                    new_player_name = st.text_input("새 참가자 이름", placeholder="예: 홍길동", key="new_player_name")
                
                with col_new_group:
                    target_group = st.selectbox("추가할 그룹", groups,
                                                format_func=lambda x: f"{x}그룹" if not x.endswith('그룹') else x,
                                                key="target_group")
                
                with col_add:
                    if st.button("➕ 추가", use_container_width=True, type="primary"):
                        if new_player_name and new_player_name.strip():
                            new_name = new_player_name.strip()
                            if new_name not in tour["groups"][target_group]["players"]:
                                # 참가자 추가
                                tour["groups"][target_group]["players"].append(new_name)
                                # 전체 players 목록에도 추가
                                if "players" not in tour:
                                    tour["players"] = []
                                if new_name not in tour["players"]:
                                    tour["players"].append(new_name)
                                
                                # 모드에 따라 대진 재생성
                                mode = tour["groups"][target_group]["mode"]
                                gc = tour["groups"][target_group].get("games", 3)
                                
                                if mode == "고정페어":
                                    new_ms, _ = make_fixed(tour["groups"][target_group]["players"])
                                elif mode == "KDK":
                                    new_ms, new_pwn = make_kdk(tour["groups"][target_group]["players"], gc)
                                    tour["groups"][target_group]["player_with_number"] = new_pwn
                                else:
                                    new_ms, _ = make_singles(tour["groups"][target_group]["players"])
                                
                                tour["groups"][target_group]["matches"] = new_ms
                                save_tours(tours)
                                st.success(f"✅ '{new_name}' 님이 {target_group}그룹에 추가되었습니다!")
                                st.rerun()
                            else:
                                st.warning(f"'{new_name}' 님은 이미 {target_group}그룹에 있습니다.")
                        else:
                            st.warning("이름을 입력하세요.")
                
                st.markdown("---")
                
                # 참가자 이동
                st.markdown("**🔄 참가자 그룹 이동**")
                col_move_player, col_move_from, col_move_to, col_move_btn = st.columns([2, 1.5, 1.5, 1])
                
                with col_move_player:
                    all_players = []
                    for g in groups:
                        for p in tour["groups"][g]["players"]:
                            all_players.append((p, g))
                    if all_players:
                        move_player = st.selectbox("이동할 참가자", [p[0] for p in all_players], key="move_player")
                        current_group = next((g for p, g in all_players if p == move_player), groups[0])
                    else:
                        move_player = None
                        current_group = groups[0] if groups else None
                
                with col_move_from:
                    st.write(f"현재: **{current_group}그룹**" if current_group else "없음")
                
                with col_move_to:
                    new_group = st.selectbox("이동할 그룹", groups, 
                                            format_func=lambda x: f"{x}그룹" if not x.endswith('그룹') else x,
                                            key="move_target")
                
                with col_move_btn:
                    if st.button("🔄 이동", use_container_width=True):
                        if move_player and current_group != new_group:
                            # 현재 그룹에서 제거
                            tour["groups"][current_group]["players"].remove(move_player)
                            # 새 그룹에 추가
                            tour["groups"][new_group]["players"].append(move_player)
                            
                            # 두 그룹의 대진 모두 재생성
                            for grp in [current_group, new_group]:
                                mode = tour["groups"][grp]["mode"]
                                gc = tour["groups"][grp].get("games", 3)
                                if mode == "고정페어":
                                    new_ms, _ = make_fixed(tour["groups"][grp]["players"])
                                elif mode == "KDK":
                                    new_ms, new_pwn = make_kdk(tour["groups"][grp]["players"], gc)
                                    tour["groups"][grp]["player_with_number"] = new_pwn
                                else:
                                    new_ms, _ = make_singles(tour["groups"][grp]["players"])
                                tour["groups"][grp]["matches"] = new_ms
                            
                            save_tours(tours)
                            st.success(f"✅ '{move_player}' 님이 {new_group}그룹으로 이동했습니다!")
                            st.rerun()
                        elif move_player and current_group == new_group:
                            st.warning("같은 그룹으로 이동할 수 없습니다.")
                
                st.divider()
            else:
                st.info("아직 생성된 그룹이 없습니다. 먼저 대진을 생성하세요.")
        else:
            st.info("아직 생성된 대진이 없습니다. 먼저 '대진 설정'에서 대진을 생성하세요.")
        
        # ============================================================
        # 기존 대진 설정 섹션
        # ============================================================
        st.markdown('<div class="sec">🎲 그룹·대진 설정 (새로 생성)</div>', unsafe_allow_html=True)
        st.caption("※ 주의: 새로 대진을 생성하면 기존 대진과 점수가 초기화됩니다.")
        
        if not sel_names:
            st.warning("먼저 참가자를 저장하세요.")
        else:
            gcnt = st.number_input("그룹 수", 1, 6, min(4, max(1, len(sel_names)//8)), key="gcnt_input")
            gns = list("ABCDEF")[:gcnt]
            gcfg = {}
            for i, gn in enumerate(gns):
                hx = GHEX[i % len(GHEX)]
                st.markdown(f"<div style='background:{hx}18;border-left:4px solid {hx};"
                            f"border-radius:7px;padding:5px 12px;margin:6px 0;"
                            f"font-weight:800;color:{hx}'>{GLBL[i%len(GLBL)]} {gn}그룹</div>",
                            unsafe_allow_html=True)
                cc = st.columns(4)
                dfsz = max(2, len(sel_names)//gcnt)
                with cc[0]:
                    nm2 = st.text_input("그룹명", f"{gn}그룹", key=f"gn_{i}")
                with cc[1]:
                    sz = st.number_input("인원", 2, 30, dfsz, key=f"sz_{i}")
                with cc[2]:
                    md = st.selectbox("방식", ["고정페어","KDK","단식"], key=f"md_{i}")
                with cc[3]:
                    gc = st.selectbox("1인 게임수", [3,4,5], index=1, key=f"gc_{i}")
                gcfg[nm2] = (sz, md, gc)

            total = sum(c[0] for c in gcfg.values())
            diff = len(sel_names) - total
            if diff == 0:
                st.success(f"✅ 참가자 {len(sel_names)}명 / 배정 {total}명")
            else:
                st.warning(f"⚠️ 참가자 {len(sel_names)}명 / 배정 {total}명 (차이 {diff:+d}명)")

            if st.button("🎲 대진 생성 (기존 데이터 초기화)", type="primary", use_container_width=True):
                players_sorted = sel_names
                ptr = 0
                new_groups = {}
                group_order = list(gcfg.keys())
                for gn in group_order:
                    sz, md, gc = gcfg[gn]
                    gp = players_sorted[ptr:ptr+sz]
                    ptr += sz
                    st.info(f"📌 {gn}: {', '.join(gp[:3])}{'...' if len(gp)>3 else ''} ({len(gp)}명)")
                    if md == "고정페어":
                        ms, _ = make_fixed(gp)
                        player_with_number = {}
                    elif md == "KDK":
                        ms, player_with_number = make_kdk(gp, gc)
                        if not ms:
                            st.warning(f"{gn}: {gc}게임 기준 {len(gp)}명은 지원하지 않습니다. 단식 리그로 대체합니다.")
                            ms, _ = make_singles(gp)
                            player_with_number = {}
                    else:
                        ms, _ = make_singles(gp)
                        player_with_number = {}
                    new_groups[gn] = {"players": gp, "mode": md, "games": gc, "matches": ms, "player_with_number": player_with_number}
                tours[sel_tid]["groups"] = new_groups
                # 전체 players 목록 업데이트
                tours[sel_tid]["players"] = sel_names
                save_tours(tours)
                st.success("✅ 대진 생성 완료! (랭킹 높은 순 → A → B → C 그룹 순서로 배정됨)")
                st.rerun()

    # 탭3: 랭킹 관리
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
                disp.insert(0, "순위", [icons[i] if i<3 else str(i+1) for i in range(len(disp))])
                st.dataframe(disp, use_container_width=True, hide_index=True, height=320)
                st.download_button(
                    "📥 현재 랭킹 엑셀 다운로드",
                    data=to_excel(df_cur),
                    file_name=f"두류랭킹_{date.today()}.xlsx",
                    use_container_width=True,
                    key="btn_rank_dl")

        st.divider()
        st.markdown('<div class="sec">✏️ 랭킹 직접 수정</div>', unsafe_allow_html=True)

        df_edit = load_rank()
        if df_edit.empty:
            st.info("업로드된 랭킹 데이터가 없습니다.")
        else:
            edited = st.data_editor(
                df_edit, use_container_width=True, hide_index=True,
                num_rows="dynamic", key="rank_editor",
                column_config={
                    "랭킹": st.column_config.NumberColumn("랭킹", width="small"),
                    "이름": st.column_config.TextColumn("이름", width="medium"),
                    "현재포인트": st.column_config.NumberColumn("현재포인트", width="medium"),
                    "3월 포인트": st.column_config.NumberColumn("3월 포인트", width="medium"),
                    "결과": st.column_config.TextColumn("결과", width="small"),
                    "부과점": st.column_config.NumberColumn("부과점", width="small"),
                    "그룹": st.column_config.TextColumn("그룹", width="small"),
                    "비고": st.column_config.TextColumn("비고", width="large"),
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
                    use_container_width=True,
                    key="btn_edit_dl")

    # 탭4: 결과 반영
    with adm[3]:
        tours = load_tours()
        active = [k for k,v in tours.items() if v.get("status") == "진행중"]
        if not active:
            st.warning("진행 중인 대회가 없습니다.")
            st.stop()

        sel_tid2 = st.selectbox("반영할 대회", active,
            format_func=lambda k: f"{tours[k]['title']} ({tours[k].get('date','')})")
        tour3 = tours[sel_tid2]
        st.markdown(f'<div class="sec">"{tour3["title"]}" 결과 → 랭킹 반영</div>', unsafe_allow_html=True)
        st.caption("고정페어: 1위+7 / 2위+5 / 3위+3 / 참가+1 | KDK·단식: 1~2위+7 / 3~4위+5 / 5~6위+3 / 참가+1")

        if not tour3.get("groups"):
            st.warning("대진이 생성되지 않았습니다.")
            st.stop()

        earn = {}
        prev_rows = []
        for g, ginfo in tour3["groups"].items():
            mode = ginfo["mode"]
            matches = ginfo["matches"]
            
            is_fixed = (mode == "고정페어")
            
            if is_fixed:
                stats = group_stats_fixed(matches)
                items = list(stats.keys())
                ranked = sorted(items, key=lambda t: (-stats[t]["승"], -stats[t]["득실"]))
            else:
                stats = group_stats_kdk(matches)
                items = list(stats.keys())
                ranked = sorted(items, key=lambda p: (-stats[p]["승"], -stats[p]["득실"]))
            
            for i, item in enumerate(ranked):
                pt = rank_pts(i+1, mode)
                if is_fixed:
                    grade = ["우승","준우승","3위"][i] if i<3 else "참가"
                    for p in list(item):
                        earn[p] = earn.get(p, 0) + pt
                        prev_rows.append({
                            "그룹": g,
                            "팀/선수": " & ".join(list(item)),
                            "등급": grade,
                            "이름": p,
                            "부과점": pt
                        })
                else:
                    grade = get_grade_kdk(i+1)
                    earn[item] = earn.get(item, 0) + pt
                    prev_rows.append({
                        "그룹": g,
                        "선수": item,
                        "등급": grade,
                        "부과점": pt
                    })

        if prev_rows:
            st.dataframe(pd.DataFrame(prev_rows), use_container_width=True, hide_index=True)

        c1, c2 = st.columns(2)
        with c1:
            if st.button("🏆 랭킹에 반영", type="primary", use_container_width=True):
                df_r = load_rank()
                if df_r.empty:
                    df_r = pd.DataFrame(columns=COLS_RANK)
                if "현재포인트" in df_r.columns:
                    df_r["3월 포인트"] = pd.to_numeric(df_r["현재포인트"], errors="coerce").fillna(0)
                for p, pt in earn.items():
                    if p in df_r["이름"].values:
                        cur = pd.to_numeric(df_r.loc[df_r["이름"] == p, "현재포인트"],
                                            errors="coerce").fillna(0).values[0]
                        df_r.loc[df_r["이름"] == p, "현재포인트"] = cur + pt
                        df_r.loc[df_r["이름"] == p, "부과점"] = pt
                    else:
                        nr = {c: "" for c in COLS_RANK}
                        nr.update({"이름": p, "현재포인트": pt, "3월 포인트": 0, "부과점": pt})
                        df_r = pd.concat([df_r, pd.DataFrame([nr])], ignore_index=True)
                save_rank(df_r)
                if "이름" in df_r.columns:
                    save_members(df_r["이름"].astype(str).str.strip().tolist())
                tours[sel_tid2]["status"] = "완료"
                save_tours(tours)
                st.success("✅ 랭킹 반영 완료!")
                st.rerun()
        with c2:
            if st.button("🗑 점수 초기화", use_container_width=True):
                for g in tour3["groups"]:
                    for m in tour3["groups"][g]["matches"]:
                        m["s1"] = 0
                        m["s2"] = 0
                tours[sel_tid2] = tour3
                save_tours(tours)
                st.success("✅ 점수 초기화")
                st.rerun()

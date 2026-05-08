import streamlit as st
import pandas as pd
import random, os, json
from datetime import date
from io import BytesIO

# ══════════════════════════════════════════════════════════════
# 앱 설정 (모바일 최적화)
# ══════════════════════════════════════════════════════════════
st.set_page_config(page_title="두류 랭킹 관리 시스템", page_icon="🎾",
                   layout="wide", initial_sidebar_state="collapsed")

# 모바일 최적화 CSS
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;600;700;900&display=swap');
* {
    font-family: 'Noto Sans KR', sans-serif !important;
    box-sizing: border-box;
}
.block-container { 
    padding: 0 0.5rem 1rem 0.5rem !important; 
    max-width: 100% !important;
}

/* 네비게이션 바 - 모바일 터치 최적화 */
section.main [data-testid="stHorizontalBlock"]:first-of-type .stButton > button {
    background: transparent !important;
    color: rgba(255,255,255,0.72) !important;
    border: none !important; 
    border-radius: 0 !important;
    font-size: clamp(0.7rem, 3vw, 0.9rem) !important;
    font-weight: 700 !important;
    padding: 14px 3px 10px !important;
    line-height: 1.3 !important;
    white-space: pre-line !important;
    box-shadow: none !important;
    min-height: 55px !important;
    border-bottom: 3px solid transparent !important;
}
section.main [data-testid="stHorizontalBlock"]:first-of-type .stButton > button:hover {
    background: rgba(255,255,255,0.12) !important;
    color: #fff !important;
}
section.main [data-testid="stHorizontalBlock"]:first-of-type .stButton > button[kind="primary"] {
    background: rgba(255,255,255,0.2) !important;
    color: #fff !important;
    font-weight: 900 !important;
    border-bottom: 3px solid #A5D6A7 !important;
}

/* 공통 헤더 - 모바일 */
.main-hdr {
    background: linear-gradient(135deg,#1D5B2E,#388E3C);
    color:#fff; 
    padding: 0.8rem 1rem; 
    border-radius: 12px;
    margin-bottom: 0.8rem; 
    font-size: clamp(1rem, 4.5vw, 1.5rem);
    font-weight: 900; 
    text-align: center;
    box-shadow: 0 3px 10px rgba(0,0,0,0.14);
}
.sec {
    font-size: 1rem; 
    font-weight: 900; 
    color:#1D5B2E;
    border-left: 4px solid #66BB6A; 
    padding-left: 10px; 
    margin: 12px 0 8px;
}

/* 탭 - 모바일 터치 최적화 */
button[data-baseweb="tab"] {
    font-size: 0.85rem !important;
    font-weight: 700 !important;
    padding: 8px 12px !important;
    border-radius: 10px 10px 0 0 !important;
}
button[data-baseweb="tab"][aria-selected="true"] {
    background: linear-gradient(135deg,#1D5B2E,#388E3C) !important;
    color: #fff !important;
}

/* ================================================================
   가운데 정렬
   ================================================================ */
div[data-testid="stDataFrame"] table,
div[data-testid="stDataEditor"] table,
.stDataFrame table,
table.dataframe {
    width: 100% !important;
}

div[data-testid="stDataFrame"] table th,
div[data-testid="stDataFrame"] table td,
.stDataFrame th, .stDataFrame td,
table th, table td {
    text-align: center !important;
    vertical-align: middle !important;
    padding: 6px 4px !important;
    font-size: 0.8rem !important;
}

/* 숫자 입력 필드 - 모바일 크기 */
input[type="number"] {
    text-align: center !important;
    font-size: 1rem !important;
    font-weight: 700 !important;
}
div[data-testid="stNumberInput"] input {
    text-align: center !important;
    font-weight: 700 !important;
    font-size: 1rem !important;
    padding: 6px !important;
}

/* 팀 도형 - 모바일 최적화 */
.team-box {
    border-radius: 12px;
    padding: 8px 10px !important;
    font-weight: 800 !important;
    font-size: 0.85rem !important;
    text-align: center;
    margin: 3px 0;
    box-shadow: 0 2px 6px rgba(0,0,0,.1);
    line-height: 1.3;
    min-height: 48px;
    display: flex;
    align-items: center;
    justify-content: center;
    width: 100%;
    word-break: keep-all;
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

/* VS 원 - 모바일 */
.vs-circle {
    background:#FFB74D;
    color:#fff;
    border-radius:50%;
    width: 40px !important;
    height: 40px !important;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 900;
    font-size: 0.85rem;
    margin: 0 auto;
    box-shadow: 0 2px 6px rgba(255,183,77,.4);
}

/* 라운드 카드 - 모바일 */
.round-card {
    background: linear-gradient(135deg, #ffffff, #f8f9fa);
    border: 1px solid #e0e0e0;
    border-radius: 14px;
    padding: 12px;
    margin: 10px 0;
    box-shadow: 0 2px 8px rgba(0,0,0,0.06);
}
.round-title {
    background: linear-gradient(90deg,#1D5B2E,#43A047);
    color: white;
    border-radius: 10px;
    padding: 6px 12px;
    font-weight: 800;
    text-align: center;
    margin-bottom: 12px;
    font-size: 0.9rem;
}

/* 구분선 */
hr {
    margin: 10px 0;
    border-color: #eee;
}

/* 참가자 태그 - 모바일 */
.p-tag {
    display: inline-block;
    background: #E8F5E9;
    border: 1px solid #66BB6A;
    border-radius: 20px;
    padding: 4px 10px;
    margin: 3px 4px;
    font-size: 0.8rem;
    font-weight: 700;
    color: #1D5B2E;
}

/* 카드 스타일 */
.tour-card, .rank-card {
    background: #fff;
    border: 1px solid #C8E6C9;
    border-radius: 12px;
    padding: 10px 12px;
    margin: 6px 0;
    box-shadow: 0 2px 8px rgba(0,0,0,0.05);
}
.rank-card-title {
    font-size: 0.95rem;
    font-weight: 900;
    color: #1D5B2E;
    border-bottom: 2px solid #A5D6A7;
    padding-bottom: 8px;
    margin-bottom: 12px;
    text-align: center;
}

/* 버튼 - 모바일 터치 영역 */
.stButton > button {
    border-radius: 10px !important;
    font-weight: 700 !important;
    font-size: 0.85rem !important;
    padding: 0.4rem 0.8rem !important;
    min-height: 40px !important;
}

/* 모바일 컬럼 간격 */
div[data-testid="column"] {
    gap: 8px;
}

/* 데이터프레임 모바일 스크롤 */
div[data-testid="stDataFrame"] {
    overflow-x: auto;
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

def tname(t):
    return " & ".join(t) if len(t)>1 else t[0]

def group_stats_fixed(matches):
    """고정페어 통계 계산 (팀 단위)"""
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
    """KDK 통계 계산 (개인 단위) - 페어 경기 결과를 개인에게 적용"""
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
# 대진 생성 함수
# ══════════════════════════════════════════════════════════════
def make_kdk(players, games_per_person):
    """KDK 대진 생성 - 페어 단위로 표시"""
    n = len(players)
    
    if games_per_person == 3:
        bp = KDK_3G.get(n)
    else:
        bp = KDK_4G.get(n)
    
    if not bp:
        return None
    
    shuffled = random.sample(players, n)
    player_by_number = {i+1: shuffled[i] for i in range(n)}
    
    matches = []
    for a, b, c, d in bp:
        matches.append({
            "t1": [player_by_number[a], player_by_number[b]],
            "t2": [player_by_number[c], player_by_number[d]],
            "s1": 0,
            "s2": 0
        })
    
    return matches

def make_fixed(players):
    n = len(players)
    pairs = [(players[i], players[n-1-i]) for i in range(n//2)]
    ms = []
    for i in range(len(pairs)):
        for j in range(i+1, len(pairs)):
            ms.append({"t1": list(pairs[i]), "t2": list(pairs[j]), "s1": 0, "s2": 0})
    random.shuffle(ms)
    return ms

def make_singles(players):
    pl = players[:]
    random.shuffle(pl)
    ms = [(pl[i], pl[j]) for i in range(len(pl)) for j in range(i+1, len(pl))]
    random.shuffle(ms)
    return [{"t1": [a], "t2": [b], "s1": 0, "s2": 0} for a, b in ms]

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
    ("ranking",  "🏆\n랭킹"),
    ("schedule", "📅\n대진/경기"),
    ("result",   "📊\n결과"),
    ("archive",  "📂\n기록"),
    ("admin",    "⚙️\n관리"),
]

st.markdown("""
<div style="background:#1D5B2E;padding:12px 12px 0 12px;margin:0 -0.5rem 0 -0.5rem;">
  <div style="text-align:center;color:rgba(255,255,255,0.55);
      font-size:0.7rem;letter-spacing:2px;font-weight:600;
      margin-bottom:4px">🎾 두류 테니스 클럽</div>
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
<div style="background:#1D5B2E;height:8px;margin:0 -0.5rem 12px -0.5rem;box-shadow:0 3px 10px rgba(0,0,0,0.15)"></div>
""", unsafe_allow_html=True)

M = st.session_state.menu

# ══════════════════════════════════════════════════════════════
# 1. 🏆 두류 랭킹
# ══════════════════════════════════════════════════════════════
if M == "ranking":
    st.markdown("<div class='main-hdr'>🏆 두류 랭킹</div>", unsafe_allow_html=True)
    df = load_rank()
    if df.empty:
        st.info("📋 등록된 랭킹이 없습니다.")
    else:
        icons = ["🥇","🥈","🥉"]
        disp = df.copy()
        disp.insert(0, "순위", [icons[i] if i<3 else str(i+1) for i in range(len(disp))])
        st.dataframe(disp, use_container_width=True, hide_index=True)
        st.download_button(
            "📥 엑셀 다운로드", data=to_excel(df),
            file_name=f"두류랭킹_{date.today()}.xlsx",
            use_container_width=True)

# ══════════════════════════════════════════════════════════════
# 2. 📅 대진 및 경기 현황
# ══════════════════════════════════════════════════════════════
elif M == "schedule":
    tours = load_tours()
    active = [k for k,v in tours.items() if v.get("status")=="진행중"]
    if not active:
        st.warning("⚠️ 진행 중인 대회가 없습니다.")
        st.stop()
    tid = active[-1]
    tour = tours[tid]
    st.markdown(f"<div class='main-hdr'>📅 {tour['title']}</div>", unsafe_allow_html=True)
    st.caption(f"📅 {tour.get('date','')} | 📍 {tour.get('place','')} | 코트 {tour.get('courts',2)}면")

    gnames = list(tour["groups"].keys())
    if not gnames:
        st.info("대진이 없습니다.")
        st.stop()

    tabs = st.tabs([f"{GLBL[i%len(GLBL)]} {g}" for i,g in enumerate(gnames)])
    for ti, g in enumerate(gnames):
        with tabs[ti]:
            ginfo = tour["groups"][g]
            matches = ginfo["matches"]
            mode = ginfo["mode"]
            cls = GCLS[ti % len(GCLS)]
            
            is_fixed = (mode == "고정페어")
            
            # 순위 계산
            if is_fixed:
                stats = group_stats_fixed(matches)
                items = list(stats.keys())
                ranked = sorted(items, key=lambda x: (-stats[x]["승"], -stats[x]["득실"]))
            else:
                stats = group_stats_kdk(matches)
                items = list(stats.keys())
                ranked = sorted(items, key=lambda x: (-stats[x]["승"], -stats[x]["득실"]))
            
            # 현재 순위 표시
            st.markdown("**🏅 현재 순위**")
            rows = []
            for i, item in enumerate(ranked):
                if is_fixed:
                    grade = ["우승","준우승","3위"][i] if i<3 else "참가"
                    rows.append({
                        "순위": ["🥇","🥈","🥉"][i] if i<3 else i+1,
                        "팀": " & ".join(list(item)),
                        "승": stats[item]["승"],
                        "패": stats[item]["패"],
                        "득실": f'{stats[item]["득실"]:+d}'
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
            st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
            
            st.divider()
            
            # 경기 입력
            st.markdown(f"**🎾 경기 입력**")
            
            changed = False
            for mi, m in enumerate(matches):
                t1 = " & ".join(m["t1"])
                t2 = " & ".join(m["t2"])
                
                color_idx = mi % 3
                color_class = ["match-color-0", "match-color-1", "match-color-2"][color_idx]
                
                # 모바일에서는 3컬럼 대신 2컬럼 + 중앙 VS
                col1, col2 = st.columns([5, 1])
                with col1:
                    st.markdown(f'<div class="team-box {color_class}">{t1}</div>', unsafe_allow_html=True)
                with col2:
                    st.markdown('<div class="vs-circle">VS</div>', unsafe_allow_html=True)
                
                # 점수 입력
                s_col1, s_col2 = st.columns(2)
                with s_col1:
                    s1 = st.number_input(f"{t1} 점수", 0, 50, int(m["s1"]),
                                         key=f"{tid}_{g}_{mi}_s1",
                                         label_visibility="collapsed")
                with s_col2:
                    s2 = st.number_input(f"{t2} 점수", 0, 50, int(m["s2"]),
                                         key=f"{tid}_{g}_{mi}_s2",
                                         label_visibility="collapsed")
                
                if s1 != int(m["s1"]) or s2 != int(m["s2"]):
                    tour["groups"][g]["matches"][mi]["s1"] = s1
                    tour["groups"][g]["matches"][mi]["s2"] = s2
                    changed = True
                
                st.markdown("<hr>", unsafe_allow_html=True)
            
            if changed:
                tours[tid] = tour
                save_tours(tours)
                st.toast("✅ 저장됨!", icon="✅")

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
    st.markdown(f"<div class='main-hdr'>📊 {tour['title']} 결과</div>", unsafe_allow_html=True)

    for g, ginfo in tour["groups"].items():
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
        
        st.markdown(f'<div class="sec">{g} 그룹 ({mode})</div>', unsafe_allow_html=True)
        
        # 최종 순위
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
                    "포인트": pt,
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
                    "포인트": pt,
                    "비고": grade
                })
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
        
        # 전체 경기 결과 (간략히)
        with st.expander("📋 전체 경기 결과"):
            mrows = []
            for m in matches:
                t1 = " & ".join(m["t1"])
                t2 = " & ".join(m["t2"])
                s1, s2 = int(m["s1"]), int(m["s2"])
                result = "🏆 " + t1 + " 승" if s1 > s2 else "🏆 " + t2 + " 승" if s2 > s1 else "무승부"
                mrows.append({"경기": f"{t1} vs {t2}", "결과": f"{s1}:{s2}", "승리": result})
            st.dataframe(pd.DataFrame(mrows), use_container_width=True, hide_index=True)

# ══════════════════════════════════════════════════════════════
# 4. 📂 지난 대회 아카이브
# ══════════════════════════════════════════════════════════════
elif M == "archive":
    st.markdown("<div class='main-hdr'>📂 지난 대회</div>", unsafe_allow_html=True)
    tours = load_tours()
    past = {k:v for k,v in tours.items() if v.get("status")!="진행중"}
    if not past:
        st.info("완료된 대회가 없습니다.")
        st.stop()

    sel = st.selectbox("대회 선택", list(past.keys()),
        format_func=lambda k: f"{past[k]['title']} ({past[k].get('date','')})")
    tour = past[sel]
    st.markdown(f"**🏆 {tour['title']}** | 📅 {tour.get('date','')} | 📍 {tour.get('place','')}")
    st.divider()
    
    if not tour.get("groups"):
        st.info("대진 정보가 없습니다.")
        st.stop()

    for g, ginfo in tour["groups"].items():
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
        
        st.markdown(f'<div class="sec">{g} ({mode})</div>', unsafe_allow_html=True)
        
        rows = []
        for i, item in enumerate(ranked):
            pt = rank_pts(i+1, mode)
            if is_fixed:
                grade = ["우승","준우승","3위"][i] if i<3 else "참가"
                rows.append({
                    "순위": i+1,
                    "팀": " & ".join(list(item)),
                    "승": stats[item]["승"],
                    "패": stats[item]["패"],
                    "득실": f'{stats[item]["득실"]:+d}',
                    "포인트": pt,
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
                    "포인트": pt,
                    "비고": grade
                })
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

# ══════════════════════════════════════════════════════════════
# 5. ⚙️ 관리자 (간소화)
# ══════════════════════════════════════════════════════════════
elif M == "admin":
    st.markdown("<div class='main-hdr'>⚙️ 관리자</div>", unsafe_allow_html=True)
    pw = st.text_input("🔒 비밀번호", type="password", placeholder="비밀번호 입력")
    if pw == ADMIN_PW:
        st.session_state.is_admin = True
    if not st.session_state.is_admin:
        if pw and pw != ADMIN_PW:
            st.error("❌ 비밀번호 오류")
        st.stop()
    st.success("✅ 관리자 모드")

    adm = st.tabs(["🏆 대회", "👥 참가자", "📋 랭킹", "💾 반영"])

    # 탭1: 대회 관리
    with adm[0]:
        st.markdown('<div class="sec">새 대회</div>', unsafe_allow_html=True)
        with st.form("f_new_tour"):
            c1, c2 = st.columns(2)
            tn = c1.text_input("대회명")
            td = c2.date_input("날짜", value=date.today())
            tp = st.text_input("장소")
            courts = st.selectbox("코트 수", [1,2,3], index=1)
            if st.form_submit_button("✅ 생성", use_container_width=True):
                if tn.strip():
                    tours = load_tours()
                    tid = f"{td}_{tn.strip()}"
                    if tid not in tours:
                        tours[tid] = {
                            "title": tn.strip(),
                            "date": str(td),
                            "place": tp,
                            "courts": courts,
                            "status": "진행중",
                            "groups": {}
                        }
                        save_tours(tours)
                        st.success(f"🎉 생성됨!")
                        st.rerun()
                    else:
                        st.warning("이미 존재함")
                else:
                    st.error("대회명 입력")
        st.divider()
        st.markdown('<div class="sec">대회 목록</div>', unsafe_allow_html=True)
        tours = load_tours()
        if tours:
            for tid2, tv in list(tours.items()):
                st.markdown(f"**{tv['title']}** ({tv.get('date','')}) - {tv.get('status','')}")
                c1, c2, c3 = st.columns(3)
                with c1:
                    new_st = st.selectbox("상태", ["진행중","완료","예정"], 
                        index=["진행중","완료","예정"].index(tv.get("status","진행중")),
                        key=f"st_{tid2}", label_visibility="collapsed")
                with c2:
                    if st.button("수정", key=f"edit_{tid2}"):
                        tours[tid2]["status"] = new_st
                        save_tours(tours)
                        st.rerun()
                with c3:
                    if st.button("삭제", key=f"del_{tid2}"):
                        del tours[tid2]
                        save_tours(tours)
                        st.rerun()
                st.divider()

    # 탭2: 참가자·대진
    with adm[1]:
        tours = load_tours()
        active = [k for k,v in tours.items() if v.get("status") == "진행중"]
        if not active:
            st.warning("진행 중인 대회가 없습니다.")
            st.stop()

        sel_tid = st.selectbox("대회 선택", active,
            format_func=lambda k: f"{tours[k]['title']}")
        tour = tours[sel_tid]
        st.info(f"**{tour['title']}** | 코트 {tour.get('courts',2)}면")

        st.markdown('<div class="sec">참가자</div>', unsafe_allow_html=True)
        member_roster = load_members()
        
        default_text = ", ".join(tour.get("players", st.session_state.participants))
        part_input = st.text_area("명단", value=default_text, height=100,
            placeholder="이름을 쉼표 또는 줄바꿈으로 구분")
        
        if st.button("✅ 저장", use_container_width=True, type="primary"):
            raw_names = part_input.replace("\n", ",").split(",")
            parsed = [n.strip() for n in raw_names if n.strip()]
            roster_order = {nm: i for i, nm in enumerate(member_roster)}
            parsed_sorted = sorted(set(parsed),
                key=lambda x: roster_order.get(x, len(member_roster)+1))
            st.session_state.participants = parsed_sorted
            tours[sel_tid]["players"] = parsed_sorted
            save_tours(tours)
            st.success(f"✅ {len(parsed_sorted)}명 저장")
            st.rerun()
        
        sel_names = tour.get("players", st.session_state.participants)
        if sel_names:
            tags = "".join([f'<span class="p-tag">{n}</span>' for n in sel_names])
            st.markdown(f"<div>{tags}</div>", unsafe_allow_html=True)
        
        st.divider()
        st.markdown('<div class="sec">대진 설정</div>', unsafe_allow_html=True)
        if not sel_names:
            st.warning("참가자 먼저 저장")
            st.stop()
        
        gcnt = st.number_input("그룹 수", 1, 6, value=4)
        gcfg = {}
        for i in range(gcnt):
            st.markdown(f"**그룹 {chr(65+i)}**")
            c1, c2, c3 = st.columns(3)
            with c1:
                sz = st.number_input("인원", 2, 30, value=8, key=f"sz{i}")
            with c2:
                md = st.selectbox("방식", ["고정페어","KDK","단식"], key=f"md{i}")
            with c3:
                gc = st.selectbox("게임수", [3,4,5], index=1, key=f"gc{i}")
            gcfg[f"그룹{chr(65+i)}"] = (sz, md, gc)
        
        total = sum(c[0] for c in gcfg.values())
        if total == len(sel_names):
            st.success(f"✅ {len(sel_names)}명 배정 완료")
        else:
            st.warning(f"⚠️ {len(sel_names)}명 / 배정 {total}명")
        
        if st.button("🎲 대진 생성", type="primary", use_container_width=True):
            players_sorted = sel_names
            ptr = 0
            new_groups = {}
            for gn, (sz, md, gc) in gcfg.items():
                gp = players_sorted[ptr:ptr+sz]
                ptr += sz
                if md == "고정페어":
                    ms = make_fixed(gp)
                elif md == "KDK":
                    ms = make_kdk(gp, gc)
                    if not ms:
                        ms = make_singles(gp)
                else:
                    ms = make_singles(gp)
                new_groups[gn] = {"players": gp, "mode": md, "games": gc, "matches": ms}
            tours[sel_tid]["groups"] = new_groups
            save_tours(tours)
            st.success("✅ 대진 생성 완료!")
            st.rerun()

    # 탭3: 랭킹 관리
    with adm[2]:
        st.markdown('<div class="sec">엑셀 업로드</div>', unsafe_allow_html=True)
        up = st.file_uploader("파일 선택", type=["xlsx","csv"])
        if up:
            try:
                df_up = (pd.read_excel(up) if up.name.endswith("xlsx")
                         else pd.read_csv(up, encoding_errors="replace"))
                if "현재포인트" in df_up.columns:
                    df_up["현재포인트"] = pd.to_numeric(df_up["현재포인트"], errors="coerce").fillna(0)
                    df_up = df_up.sort_values("현재포인트", ascending=False).reset_index(drop=True)
                    df_up["랭킹"] = df_up.index + 1
                st.dataframe(df_up, use_container_width=True)
                if st.button("💾 저장", type="primary"):
                    save_rank(df_up)
                    if "이름" in df_up.columns:
                        save_members(df_up["이름"].tolist())
                    st.success("저장 완료!")
                    st.rerun()
            except Exception as e:
                st.error(f"오류: {e}")
        
        st.divider()
        st.markdown('<div class="sec">현재 랭킹</div>', unsafe_allow_html=True)
        df_cur = load_rank()
        if not df_cur.empty:
            st.dataframe(df_cur, use_container_width=True)
            st.download_button("📥 다운로드", data=to_excel(df_cur), 
                file_name=f"랭킹_{date.today()}.xlsx")
        
        st.divider()
        st.markdown('<div class="sec">직접 수정</div>', unsafe_allow_html=True)
        df_edit = load_rank()
        if not df_edit.empty:
            edited = st.data_editor(df_edit, use_container_width=True, hide_index=True, num_rows="dynamic")
            if st.button("💾 수정 저장", type="primary"):
                save_rank(edited)
                save_members(edited["이름"].tolist())
                st.success("저장 완료!")
                st.rerun()

    # 탭4: 결과 반영
    with adm[3]:
        tours = load_tours()
        active = [k for k,v in tours.items() if v.get("status") == "진행중"]
        if not active:
            st.warning("진행 중인 대회 없음")
            st.stop()
        sel_tid2 = st.selectbox("대회", active, format_func=lambda k: tours[k]['title'])
        tour3 = tours[sel_tid2]
        
        if not tour3.get("groups"):
            st.warning("대진 없음")
            st.stop()
        
        earn = {}
        for g, ginfo in tour3["groups"].items():
            mode = ginfo["mode"]
            matches = ginfo["matches"]
            is_fixed = (mode == "고정페어")
            
            if is_fixed:
                stats = group_stats_fixed(matches)
                ranked = sorted(stats.keys(), key=lambda t: (-stats[t]["승"], -stats[t]["득실"]))
            else:
                stats = group_stats_kdk(matches)
                ranked = sorted(stats.keys(), key=lambda p: (-stats[p]["승"], -stats[p]["득실"]))
            
            for i, item in enumerate(ranked):
                pt = rank_pts(i+1, mode)
                if is_fixed:
                    for p in list(item):
                        earn[p] = earn.get(p, 0) + pt
                else:
                    earn[item] = earn.get(item, 0) + pt
        
        if earn:
            st.dataframe(pd.DataFrame(earn.items(), columns=["선수", "획득포인트"]))
        
        if st.button("🏆 랭킹 반영", type="primary"):
            df_r = load_rank()
            if df_r.empty:
                df_r = pd.DataFrame(columns=COLS_RANK)
            for p, pt in earn.items():
                if p in df_r["이름"].values:
                    cur = df_r.loc[df_r["이름"] == p, "현재포인트"].values[0]
                    df_r.loc[df_r["이름"] == p, "현재포인트"] = cur + pt
                else:
                    new_row = {c: "" for c in COLS_RANK}
                    new_row["이름"] = p
                    new_row["현재포인트"] = pt
                    df_r = pd.concat([df_r, pd.DataFrame([new_row])], ignore_index=True)
            save_rank(df_r)
            tours[sel_tid2]["status"] = "완료"
            save_tours(tours)
            st.success("반영 완료!")
            st.rerun()

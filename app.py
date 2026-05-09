import streamlit as st
import pandas as pd
import random, os, json
from datetime import date
from io import BytesIO

# ══════════════════════════════════════════════════════════════
# 앱 설정 (모바일 최적화)
# ══════════════════════════════════════════════════════════════
st.set_page_config(page_title="두류 랭킹", page_icon="🎾",
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
    padding: 0 0.5rem 0.8rem 0.5rem !important; 
    max-width: 100% !important;
}

/* 네비게이션 바 */
section.main [data-testid="stHorizontalBlock"]:first-of-type .stButton > button {
    background: transparent !important;
    color: rgba(255,255,255,0.8) !important;
    border: none !important; 
    border-radius: 0 !important;
    font-size: 0.7rem !important;
    font-weight: 600 !important;
    padding: 12px 2px 8px !important;
    line-height: 1.2 !important;
    white-space: pre-line !important;
    box-shadow: none !important;
    min-height: 48px !important;
    border-bottom: 2px solid transparent !important;
}
section.main [data-testid="stHorizontalBlock"]:first-of-type .stButton > button:hover {
    background: rgba(255,255,255,0.1) !important;
}
section.main [data-testid="stHorizontalBlock"]:first-of-type .stButton > button[kind="primary"] {
    background: rgba(255,255,255,0.15) !important;
    color: #fff !important;
    border-bottom: 2px solid #A5D6A7 !important;
}

.main-hdr {
    background: linear-gradient(135deg,#1D5B2E,#388E3C);
    color:#fff; 
    padding: 0.6rem 0.8rem; 
    border-radius: 10px;
    margin-bottom: 0.6rem; 
    font-size: 1.1rem;
    font-weight: 800; 
    text-align: center;
}
.sec {
    font-size: 0.95rem; 
    font-weight: 800; 
    color:#1D5B2E;
    border-left: 4px solid #66BB6A; 
    padding-left: 8px; 
    margin: 12px 0 6px;
}

button[data-baseweb="tab"] {
    font-size: 0.75rem !important;
    font-weight: 600 !important;
    padding: 8px 8px !important;
    border-radius: 8px 8px 0 0 !important;
}
button[data-baseweb="tab"][aria-selected="true"] {
    background: linear-gradient(135deg,#1D5B2E,#388E3C) !important;
}

div[data-testid="stDataFrame"] table,
div[data-testid="stDataEditor"] table {
    width: 100% !important;
    font-size: 0.75rem !important;
    text-align: center !important;
}
div[data-testid="stDataFrame"] table th,
div[data-testid="stDataFrame"] table td {
    text-align: center !important;
    vertical-align: middle !important;
    padding: 6px 3px !important;
    font-size: 0.75rem !important;
    white-space: nowrap;
}
div[data-testid="stDataFrame"] thead tr th {
    text-align: center !important;
    background: #f0f4f0 !important;
    font-weight: 700 !important;
}
div[data-testid="stDataFrame"] {
    overflow-x: auto !important;
}

input[type="number"] {
    text-align: center !important;
    font-size: 0.9rem !important;
    font-weight: 600 !important;
    min-height: 40px !important;
}
div[data-testid="stNumberInput"] input {
    text-align: center !important;
    font-weight: 600 !important;
    font-size: 0.9rem !important;
    padding: 6px !important;
    min-height: 40px !important;
}

.team-box {
    border-radius: 10px;
    padding: 8px 10px !important;
    font-weight: 700 !important;
    font-size: 0.8rem !important;
    text-align: center;
    margin: 4px 0;
    box-shadow: 0 1px 4px rgba(0,0,0,.08);
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

.match-color-0 { background: linear-gradient(135deg,#66BB6A,#43A047) !important; }
.match-color-1 { background: linear-gradient(135deg,#42A5F5,#1E88E5) !important; }
.match-color-2 { background: linear-gradient(135deg,#FFA726,#FB8C00) !important; }

.vs-circle {
    background:#FFB74D;
    color:#fff;
    border-radius:50%;
    width: 36px !important;
    height: 36px !important;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 800;
    font-size: 0.75rem;
    margin: 0 auto;
}

hr { margin: 10px 0; }

.p-tag {
    display: inline-block;
    background: #E8F5E9;
    border: 1px solid #66BB6A;
    border-radius: 20px;
    padding: 4px 10px;
    margin: 3px 4px;
    font-size: 0.75rem;
    font-weight: 600;
}

.stButton > button {
    border-radius: 10px !important;
    font-weight: 600 !important;
    font-size: 0.8rem !important;
    padding: 8px 12px !important;
    min-height: 44px !important;
}

.stTextInput > div > div > input,
.stTextArea > div > div > textarea,
.stSelectbox > div > div {
    min-height: 44px !important;
}

.matrix-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 0.7rem;
}
.matrix-table th, .matrix-table td {
    padding: 7px 5px;
    border: 1px solid #ddd;
    text-align: center;
    vertical-align: middle;
}
.matrix-table thead th {
    background: #f0f4f0;
    font-weight: 700;
    color: #1D5B2E;
}
.matrix-table tbody th {
    background: #f9f9f9;
    font-weight: 700;
    text-align: center;
}
.matrix-grey { background-color: #d0d0d0; color: #d0d0d0; }
.matrix-x { color: #bbb; }

.kdk-bracket {
    background: #f5f5f5;
    border-radius: 10px;
    padding: 10px;
    margin: 8px 0;
    font-size: 0.7rem;
    overflow-x: auto;
}
.kdk-bracket table {
    width: 100%;
    border-collapse: collapse;
}
.kdk-bracket th, .kdk-bracket td {
    padding: 6px 8px;
    font-size: 0.7rem;
    border: 1px solid #ddd;
    text-align: center;
}
.kdk-bracket thead th {
    background: #e8f5e9;
    font-weight: 700;
    color: #1D5B2E;
}
.kdk-bracket tbody tr:nth-child(even) {
    background: #fafafa;
}

.tour-card, .rank-card { padding: 8px 12px; margin: 6px 0; border-radius: 10px; }
.dataframe th { font-size: 0.7rem !important; padding: 6px 3px !important; }

/* 강력한 가운데 정렬 */
[data-testid="stDataFrame"] [data-testid="glideDataEditor"] {
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

# KDK 대진표
KDK_3G = {
    4: [(1,4,2,3), (1,3,2,4), (1,2,3,4)],
    8: [(1,2,3,4), (5,6,7,8), (1,8,2,7), (3,6,4,5), (1,4,5,8), (2,3,6,7)],
    12: [(1,2,3,4), (5,6,7,8), (9,10,11,12), (1,3,5,7), (2,4,6,8),
         (9,11,1,5), (4,8,9,12), (6,7,10,11), (10,12,2,3)]
}

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
        if rank <= 2: return 7
        elif rank <= 4: return 5
        elif rank <= 6: return 3
        else: return 1

def get_grade_kdk(rank):
    if rank <= 2: return "우승"
    elif rank <= 4: return "준우승"
    elif rank <= 6: return "3위"
    else: return "참가"

def make_kdk(players, games_per_person):
    n = len(players)
    bp = KDK_3G.get(n) if games_per_person == 3 else KDK_4G.get(n)
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
            "s1": 0, "s2": 0
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

def display_kdk_bracket(n, games_per_person, player_with_number):
    """KDK 대진표를 올바른 HTML로 출력 (깨진 문자 없음)"""
    if games_per_person == 3:
        bracket = KDK_3G.get(n)
        title = f"KDK 1인 3게임 - {n}명"
    else:
        bracket = KDK_4G.get(n)
        title = f"KDK 1인 4게임 - {n}명"
    if not bracket:
        return
    number_to_name = {v: k for k, v in player_with_number.items()}
    
    rows_html = ""
    for idx, (a, b, c, d) in enumerate(bracket):
        team1 = f"{number_to_name.get(a, str(a))}({a})&amp;{number_to_name.get(b, str(b))}({b})"
        team2 = f"{number_to_name.get(c, str(c))}({c})&amp;{number_to_name.get(d, str(d))}({d})"
        rows_html += f"<tr><td>{idx+1}</td><td>{team1} vs {team2}</td></tr>"
    
    html = f"""
<div class="kdk-bracket">
  <strong>📋 {title}</strong><br><br>
  <table>
    <thead><tr><th>순서</th><th>대진</th></tr></thead>
    <tbody>{rows_html}</tbody>
  </table>
</div>
"""
    st.markdown(html, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# 세션 초기화
# ══════════════════════════════════════════════════════════════
if "is_admin" not in st.session_state: st.session_state.is_admin = False
if "menu" not in st.session_state: st.session_state.menu = "ranking"
if "participants" not in st.session_state: st.session_state.participants = []

# ══════════════════════════════════════════════════════════════
# 네비게이션 바
# ══════════════════════════════════════════════════════════════
MENU_DEFS = [
    ("ranking", "🏆\n랭킹"),
    ("schedule", "📅\n대진"),
    ("result", "📊\n결과"),
    ("archive", "📂\n기록"),
    ("admin", "⚙️\n관리"),
]

st.markdown("""
<div style="background:#1D5B2E;padding:10px 12px 0 12px;margin:0 -0.5rem 0 -0.5rem;">
  <div style="text-align:center;color:rgba(255,255,255,0.55);font-size:0.65rem;letter-spacing:1px;margin-bottom:4px">🎾 두류 테니스</div>
</div>
""", unsafe_allow_html=True)

nav_cols = st.columns(len(MENU_DEFS))
for col, (key, label) in zip(nav_cols, MENU_DEFS):
    is_active = st.session_state.menu == key
    with col:
        btn_type = "primary" if is_active else "secondary"
        if st.button(label, key=f"nav_{key}", use_container_width=True, type=btn_type):
            st.session_state.menu = key
            st.rerun()

st.markdown("""
<div style="background:#1D5B2E;height:6px;margin:0 -0.5rem 10px -0.5rem;"></div>
""", unsafe_allow_html=True)

M = st.session_state.menu

# ══════════════════════════════════════════════════════════════
# 1. 랭킹
# ══════════════════════════════════════════════════════════════
if M == "ranking":
    st.markdown("<div class='main-hdr'>🏆 두류 랭킹</div>", unsafe_allow_html=True)
    df = load_rank()
    if df.empty:
        st.info("등록된 랭킹이 없습니다.")
    else:
        icons = ["🥇","🥈","🥉"]
        disp = df.copy()
        disp.insert(0, "순위", [icons[i] if i<3 else str(i+1) for i in range(len(disp))])
        # 가운데 정렬 column_config 적용
        col_cfg = {c: st.column_config.TextColumn(c, width="small") for c in disp.columns}
        st.dataframe(disp, use_container_width=True, hide_index=True, column_config=col_cfg)
        st.download_button("📥 엑셀 다운로드", data=to_excel(df), file_name=f"랭킹_{date.today()}.xlsx", use_container_width=True)

# ══════════════════════════════════════════════════════════════
# 2. 대진·경기현황
# ══════════════════════════════════════════════════════════════
elif M == "schedule":
    tours = load_tours()
    active = [k for k,v in tours.items() if v.get("status")=="진행중"]
    if not active:
        st.warning("진행 중인 대회가 없습니다.")
        st.stop()
    tid = active[-1]
    tour = tours[tid]
    st.markdown(f"<div class='main-hdr'>📅 {tour['title']}</div>", unsafe_allow_html=True)
    st.caption(f"{tour.get('date','')} | {tour.get('place','')} | 코트 {tour.get('courts',2)}면")

    gnames = list(tour["groups"].keys())
    if not gnames:
        st.info("대진이 없습니다.")
        st.stop()

    tabs = st.tabs([f"{GLBL[i%len(GLBL)]} {gn}" for i, gn in enumerate(gnames)])
    for ti, g in enumerate(gnames):
        with tabs[ti]:
            ginfo = tour["groups"][g]
            matches = ginfo["matches"]
            mode = ginfo["mode"]
            cls = GCLS[ti % len(GCLS)]
            player_with_number = ginfo.get("player_with_number", {})
            is_fixed = (mode == "고정페어")
            
            if is_fixed:
                stats = group_stats_fixed(matches)
                rank_items = list(stats.keys())
            else:
                stats = group_stats_kdk(matches)
                rank_items = list(stats.keys())
            
            st.markdown("**📋 전적 매트릭스**")
            if matches and rank_items:
                if is_fixed:
                    lab = {t: " & ".join(list(t)) for t in rank_items}
                else:
                    lab = {p: f"{p}({player_with_number.get(p, '?')})" for p in rank_items}
                mat = {lab[t]: {lab[o]: ("■" if t==o else "X") for o in lab.keys()} for t in lab.keys()}
                for m in matches:
                    if is_fixed:
                        t1, t2 = tuple(m["t1"]), tuple(m["t2"])
                    else:
                        p1, p2 = m["t1"], m["t2"]
                    s1, s2 = int(m["s1"]), int(m["s2"])
                    if s1 > 0 or s2 > 0:
                        if is_fixed:
                            mat[lab[t1]][lab[t2]] = f"{s1}:{s2}"
                            mat[lab[t2]][lab[t1]] = f"{s2}:{s1}"
                        else:
                            for a in p1:
                                for b in p2:
                                    mat[lab[a]][lab[b]] = f"{s1}:{s2}"
                                    mat[lab[b]][lab[a]] = f"{s2}:{s1}"
                mdf = pd.DataFrame(mat).T
                # 올바른 HTML 매트릭스 테이블 생성
                header_cells = "".join(f"<th>{col}</th>" for col in mdf.columns)
                html = f'<table class="matrix-table"><thead><tr><th></th>{header_cells}</tr></thead><tbody>'
                for idx, row in mdf.iterrows():
                    html += f"<tr><th>{idx}</th>"
                    for col in mdf.columns:
                        val = row[col]
                        if val == '■':
                            html += '<td class="matrix-grey">■</td>'
                        elif val == 'X':
                            html += '<td class="matrix-x">—</td>'
                        else:
                            html += f"<td>{val}</td>"
                    html += "</tr>"
                html += "</tbody></table>"
                st.markdown(html, unsafe_allow_html=True)
            
            if not is_fixed and player_with_number:
                st.divider()
                display_kdk_bracket(len(player_with_number), ginfo.get("games", 3), player_with_number)
            
            st.divider()
            st.markdown("**🏅 현재 순위**")
            if rank_items:
                ranked = sorted(rank_items, key=lambda x: (-stats[x]["승"], -stats[x]["득실"]))
                rows = []
                for i, item in enumerate(ranked):
                    if is_fixed:
                        rows.append({
                            "순위": i+1,
                            "팀": " & ".join(list(item)),
                            "승": stats[item]["승"],
                            "패": stats[item]["패"],
                            "득실": f'{stats[item]["득실"]:+d}'
                        })
                    else:
                        rows.append({
                            "순위": i+1,
                            "선수": item,
                            "승": stats[item]["승"],
                            "패": stats[item]["패"],
                            "득실": f'{stats[item]["득실"]:+d}',
                            "비고": get_grade_kdk(i+1)
                        })
                rank_df = pd.DataFrame(rows)
                rank_col_cfg = {c: st.column_config.TextColumn(c, width="small") for c in rank_df.columns}
                st.dataframe(rank_df, use_container_width=True, hide_index=True, column_config=rank_col_cfg)
            
            st.divider()
            st.markdown("**🎾 경기 입력**")
            changed = False
            for mi, m in enumerate(matches):
                t1 = " & ".join(m["t1"])
                t2 = " & ".join(m["t2"])
                color_class = ["match-color-0", "match-color-1", "match-color-2"][mi % 3]
                
                c1, c2, c3 = st.columns([4, 1, 4])
                with c1:
                    st.markdown(f'<div class="team-box {color_class}">{t1}</div>', unsafe_allow_html=True)
                    s1 = st.number_input("", 0, 50, int(m["s1"]), key=f"{tid}_{g}_{mi}_s1", label_visibility="collapsed")
                with c2:
                    st.markdown('<div class="vs-circle">VS</div>', unsafe_allow_html=True)
                with c3:
                    st.markdown(f'<div class="team-box {color_class}">{t2}</div>', unsafe_allow_html=True)
                    s2 = st.number_input("", 0, 50, int(m["s2"]), key=f"{tid}_{g}_{mi}_s2", label_visibility="collapsed")
                
                if s1 != int(m["s1"]) or s2 != int(m["s2"]):
                    tour["groups"][g]["matches"][mi]["s1"] = s1
                    tour["groups"][g]["matches"][mi]["s2"] = s2
                    changed = True
                if mi < len(matches)-1:
                    st.markdown("<hr>", unsafe_allow_html=True)
            
            if changed:
                tours[tid] = tour
                save_tours(tours)
                st.toast("✅ 저장됨", icon="✅")

# ══════════════════════════════════════════════════════════════
# 3. 경기 결과
# ══════════════════════════════════════════════════════════════
elif M == "result":
    tours = load_tours()
    active = [k for k,v in tours.items() if v.get("status")=="진행중"]
    if not active:
        st.warning("진행 중인 대회가 없습니다.")
        st.stop()
    tid = active[-1]
    tour = tours[tid]
    st.markdown(f"<div class='main-hdr'>📊 {tour['title']}</div>", unsafe_allow_html=True)

    for g, ginfo in tour["groups"].items():
        mode = ginfo["mode"]
        matches = ginfo["matches"]
        player_with_number = ginfo.get("player_with_number", {})
        is_fixed = (mode == "고정페어")
        
        if is_fixed:
            stats = group_stats_fixed(matches)
            ranked = sorted(stats.keys(), key=lambda t: (-stats[t]["승"], -stats[t]["득실"]))
        else:
            stats = group_stats_kdk(matches)
            ranked = sorted(stats.keys(), key=lambda p: (-stats[p]["승"], -stats[p]["득실"]))
        
        st.markdown(f'<div class="sec">{g} ({mode})</div>', unsafe_allow_html=True)
        
        if not is_fixed and player_with_number:
            display_kdk_bracket(len(player_with_number), ginfo.get("games", 3), player_with_number)
            st.divider()
        
        st.markdown("**🏆 최종 순위**")
        rows = []
        for i, item in enumerate(ranked):
            pt = rank_pts(i+1, mode)
            if is_fixed:
                rows.append({
                    "순위": i+1, "팀": " & ".join(list(item)),
                    "승": stats[item]["승"], "패": stats[item]["패"],
                    "득실": f'{stats[item]["득실"]:+d}', "포인트": pt,
                    "등급": ["우승","준우승","3위"][i] if i<3 else "참가"
                })
            else:
                rows.append({
                    "순위": i+1, "선수": item,
                    "승": stats[item]["승"], "패": stats[item]["패"],
                    "득실": f'{stats[item]["득실"]:+d}', "포인트": pt,
                    "비고": get_grade_kdk(i+1)
                })
        res_df = pd.DataFrame(rows)
        res_col_cfg = {c: st.column_config.TextColumn(c, width="small") for c in res_df.columns}
        st.dataframe(res_df, use_container_width=True, hide_index=True, column_config=res_col_cfg)
        
        with st.expander("📋 전체 경기 결과"):
            mrows = [{"경기": f"{' & '.join(m['t1'])} vs {' & '.join(m['t2'])}", 
                      "결과": f"{m['s1']}:{m['s2']}"} for m in matches]
            st.dataframe(pd.DataFrame(mrows), use_container_width=True, hide_index=True)

# ══════════════════════════════════════════════════════════════
# 4. 지난 대회
# ══════════════════════════════════════════════════════════════
elif M == "archive":
    st.markdown("<div class='main-hdr'>📂 지난 대회</div>", unsafe_allow_html=True)
    tours = load_tours()
    past = {k:v for k,v in tours.items() if v.get("status")!="진행중"}
    if not past:
        st.info("완료된 대회가 없습니다.")
        st.stop()
    sel = st.selectbox("대회 선택", list(past.keys()), format_func=lambda k: f"{past[k]['title']} ({past[k].get('date','')})")
    tour = past[sel]
    st.markdown(f"**🏆 {tour['title']}** | {tour.get('date','')} | {tour.get('place','')}")
    st.divider()
    if not tour.get("groups"):
        st.info("대진 정보 없음")
        st.stop()
    for g, ginfo in tour["groups"].items():
        mode = ginfo["mode"]
        matches = ginfo["matches"]
        player_with_number = ginfo.get("player_with_number", {})
        is_fixed = (mode == "고정페어")
        
        if is_fixed:
            stats = group_stats_fixed(matches)
            ranked = sorted(stats.keys(), key=lambda t: (-stats[t]["승"], -stats[t]["득실"]))
        else:
            stats = group_stats_kdk(matches)
            ranked = sorted(stats.keys(), key=lambda p: (-stats[p]["승"], -stats[p]["득실"]))
        
        st.markdown(f'<div class="sec">{g} ({mode})</div>', unsafe_allow_html=True)
        if not is_fixed and player_with_number:
            display_kdk_bracket(len(player_with_number), ginfo.get("games", 3), player_with_number)
            st.divider()
        
        rows = []
        for i, item in enumerate(ranked):
            pt = rank_pts(i+1, mode)
            if is_fixed:
                rows.append({
                    "순위": i+1, "팀/선수": " & ".join(list(item)),
                    "승": stats[item]["승"], "패": stats[item]["패"],
                    "득실": f'{stats[item]["득실"]:+d}', "포인트": pt,
                    "등급": ["우승","준우승","3위"][i] if i<3 else "참가"
                })
            else:
                rows.append({
                    "순위": i+1, "선수": item,
                    "승": stats[item]["승"], "패": stats[item]["패"],
                    "득실": f'{stats[item]["득실"]:+d}', "포인트": pt,
                    "비고": get_grade_kdk(i+1)
                })
        arc_df = pd.DataFrame(rows)
        arc_col_cfg = {c: st.column_config.TextColumn(c, width="small") for c in arc_df.columns}
        st.dataframe(arc_df, use_container_width=True, hide_index=True, column_config=arc_col_cfg)

# ══════════════════════════════════════════════════════════════
# 5. 관리자
# ══════════════════════════════════════════════════════════════
elif M == "admin":
    st.markdown("<div class='main-hdr'>⚙️ 관리자</div>", unsafe_allow_html=True)
    pw = st.text_input("🔒 비밀번호", type="password", placeholder="비밀번호 입력")
    if pw == ADMIN_PW:
        st.session_state.is_admin = True
    if not st.session_state.is_admin:
        if pw and pw != ADMIN_PW:
            st.error("비밀번호 오류")
        st.stop()
    st.success("관리자 모드")

    adm = st.tabs(["🏆 대회", "👥 참가자·대진", "📋 랭킹", "💾 반영"])

    # ── 대회 관리 ──────────────────────────────────────────────
    with adm[0]:
        st.markdown('<div class="sec">새 대회 생성</div>', unsafe_allow_html=True)
        with st.form("f_new_tour"):
            tn = st.text_input("대회명")
            td = st.date_input("날짜", value=date.today())
            tp = st.text_input("장소")
            courts = st.selectbox("코트 수", [1,2,3], index=1)
            if st.form_submit_button("✅ 생성", use_container_width=True):
                if tn.strip():
                    tours = load_tours()
                    tid = f"{td}_{tn.strip()}"
                    if tid not in tours:
                        tours[tid] = {"title": tn.strip(), "date": str(td), "place": tp,
                                      "courts": courts, "status": "진행중", "groups": {}}
                        save_tours(tours)
                        st.success("생성됨!")
                        st.rerun()
                    else:
                        st.warning("이미 존재")
        
        st.divider()
        st.markdown('<div class="sec">대회 목록</div>', unsafe_allow_html=True)
        tours = load_tours()
        if tours:
            for tid2, tv in list(tours.items()):
                col1, col2, col3 = st.columns([2, 1.5, 1.5])
                with col1:
                    st.markdown(f"**{tv['title']}** ({tv.get('date','')})")
                with col2:
                    cur_status = tv.get("status","진행중")
                    status_opts = ["진행중","완료","예정"]
                    # 고유 key 사용
                    new_st = st.selectbox(
                        "상태",
                        status_opts,
                        index=status_opts.index(cur_status) if cur_status in status_opts else 0,
                        key=f"status_sel_{tid2}",
                        label_visibility="collapsed"
                    )
                with col3:
                    if st.button("💾 상태 수정", key=f"edit_status_{tid2}", use_container_width=True):
                        tours[tid2]["status"] = new_st
                        save_tours(tours)
                        st.success("상태 수정됨!")
                        st.rerun()
                
                if st.button(f"✏️ 상세 수정", key=f"detail_edit_{tid2}", use_container_width=True):
                    st.session_state.edit_tour_id = tid2
                    st.rerun()
                
                if st.button(f"🗑 삭제", key=f"del_{tid2}", use_container_width=True):
                    del tours[tid2]
                    save_tours(tours)
                    st.rerun()
                st.divider()
        
        # 상세 수정 모드
        edit_id = st.session_state.get("edit_tour_id")
        if edit_id and edit_id in tours:
            edit_tour = tours[edit_id]
            st.markdown(f'<div class="sec">✏️ "{edit_tour["title"]}" 상세 수정</div>', unsafe_allow_html=True)
            
            new_title  = st.text_input("대회명", value=edit_tour["title"], key="edit_title")
            try:
                default_date = pd.to_datetime(edit_tour.get("date", str(date.today()))).date()
            except Exception:
                default_date = date.today()
            new_date   = st.date_input("날짜", value=default_date, key="edit_date")
            new_place  = st.text_input("장소", value=edit_tour.get("place", ""), key="edit_place")
            new_courts = st.selectbox("코트 수", [1,2,3], index=max(0, edit_tour.get("courts", 2)-1), key="edit_courts")
            
            col_save, col_cancel = st.columns(2)
            with col_save:
                if st.button("💾 기본 정보 저장", type="primary", use_container_width=True, key="save_basic_info"):
                    edit_tour["title"]  = new_title
                    edit_tour["date"]   = str(new_date)
                    edit_tour["place"]  = new_place
                    edit_tour["courts"] = new_courts
                    save_tours(tours)
                    st.success("저장 완료!")
                    st.session_state.edit_tour_id = None
                    st.rerun()
            with col_cancel:
                if st.button("취소", use_container_width=True, key="cancel_edit"):
                    st.session_state.edit_tour_id = None
                    st.rerun()
            st.divider()
            
            st.markdown('<div class="sec">🎲 그룹 설정 수정</div>', unsafe_allow_html=True)
            st.caption("※ 그룹 설정을 변경하면 기존 대진이 초기화됩니다.")
            
            current_groups     = edit_tour.get("groups", {})
            current_group_names = list(current_groups.keys())
            
            col_info1, col_info2 = st.columns(2)
            with col_info1:
                gcnt = st.number_input("그룹 수", 1, 6, value=max(1, len(current_group_names)), key="edit_gcnt")
            with col_info2:
                st.write(f"현재 {len(current_group_names)}개 그룹")
            
            gcfg = {}
            group_names = [f"{chr(65+i)}그룹" for i in range(int(gcnt))]
            for i, gn in enumerate(group_names):
                existing = current_groups.get(gn, {})
                st.markdown(f"**{gn}**")
                col_a, col_b, col_c, col_d = st.columns(4)
                with col_a:
                    default_sz = len(existing.get("players", [])) if existing else 8
                    sz = st.number_input("인원", 2, 30, value=default_sz, key=f"edit_sz_{edit_id}_{i}")
                with col_b:
                    default_md = existing.get("mode", "고정페어")
                    md_opts    = ["고정페어","KDK","단식"]
                    md = st.selectbox("방식", md_opts,
                                      index=md_opts.index(default_md) if default_md in md_opts else 0,
                                      key=f"edit_md_{edit_id}_{i}")
                with col_c:
                    default_gc = existing.get("games", 4)
                    gc_opts    = [3, 4, 5]
                    gc = st.selectbox("게임수", gc_opts,
                                      index=gc_opts.index(default_gc) if default_gc in gc_opts else 1,
                                      key=f"edit_gc_{edit_id}_{i}")
                with col_d:
                    current_count = len(existing.get("players", []))
                    st.write(f"현재 {current_count}명")
                gcfg[gn] = (sz, md, gc)
            
            total       = sum(c[0] for c in gcfg.values())
            all_players = edit_tour.get("players", [])
            if total == len(all_players):
                st.success(f"✅ 참가자 {len(all_players)}명 / 배정 {total}명")
            else:
                st.warning(f"⚠️ 참가자 {len(all_players)}명 / 배정 {total}명 (차이 {len(all_players)-total:+d}명)")
            
            if st.button("🎲 그룹 설정 적용 및 대진 재생성", type="primary", use_container_width=True, key="apply_group_config"):
                players_sorted = all_players
                ptr = 0
                new_groups = {}
                for gn, (sz, md, gc) in gcfg.items():
                    gp = players_sorted[ptr:ptr+sz]
                    ptr += sz
                    if md == "고정페어":
                        ms, pwn = make_fixed(gp), {}
                        ms = ms[0]
                    elif md == "KDK":
                        ms, pwn = make_kdk(gp, gc)
                        if not ms:
                            ms, pwn = make_singles(gp), {}
                            ms = ms[0]
                    else:
                        ms, pwn = make_singles(gp), {}
                        ms = ms[0]
                    new_groups[gn] = {"players": gp, "mode": md, "games": gc, "matches": ms, "player_with_number": pwn}
                edit_tour["groups"] = new_groups
                save_tours(tours)
                st.success("그룹 설정 적용 완료!")
                st.rerun()

    # ── 참가자·대진 (개별 수정) ─────────────────────────────────
    with adm[1]:
        tours = load_tours()
        active_t = [k for k,v in tours.items() if v.get("status") == "진행중"]
        if not active_t:
            st.warning("진행 중인 대회 없음")
            st.stop()
        sel_tid = st.selectbox("대회 선택", active_t,
                               format_func=lambda k: tours[k]['title'],
                               key="adm1_sel_tid")
        tour = tours[sel_tid]
        
        if tour.get("groups"):
            st.info(f"✅ 현재 {len(tour['groups'])}개 그룹")
            for gname, ginfo in tour["groups"].items():
                st.markdown(f"- **{gname}**: {ginfo['mode']} 방식, {len(ginfo['players'])}명")
        
        st.markdown('<div class="sec">📝 참가자 명단 (일괄 입력)</div>', unsafe_allow_html=True)
        member_roster = load_members()
        default_text  = ", ".join(tour.get("players", st.session_state.participants))
        part_input    = st.text_area("참가자 명단", value=default_text, height=100)
        
        if st.button("✅ 명단 저장 (기존 그룹 유지)", use_container_width=True, type="primary", key="save_roster"):
            raw_names    = part_input.replace("\n", ",").split(",")
            parsed       = [n.strip() for n in raw_names if n.strip()]
            roster_order = {nm: i for i, nm in enumerate(member_roster)}
            parsed_sorted = sorted(set(parsed), key=lambda x: roster_order.get(x, len(member_roster)+1))
            st.session_state.participants   = parsed_sorted
            tours[sel_tid]["players"]       = parsed_sorted
            save_tours(tours)
            st.success(f"{len(parsed_sorted)}명 저장됨")
            st.rerun()
        
        st.markdown('<div class="sec">✏️ 개별 참가자 수정 (대진 유지)</div>', unsafe_allow_html=True)
        if tour.get("groups"):
            groups = list(tour["groups"].keys())
            if groups:
                sel_group      = st.selectbox("그룹 선택", groups, key="adm1_edit_group")
                current_players = tour["groups"][sel_group]["players"].copy()
                st.markdown(f"**현재 {sel_group} 참가자:** {', '.join(current_players) if current_players else '없음'}")
                
                if current_players:
                    sel_player = st.selectbox("삭제할 참가자", current_players, key="adm1_del_player")
                    if st.button("🗑 삭제", use_container_width=True, key="adm1_del_btn"):
                        tour["groups"][sel_group]["players"].remove(sel_player)
                        new_matches = [m for m in tour["groups"][sel_group]["matches"]
                                       if sel_player not in m["t1"] and sel_player not in m["t2"]]
                        tour["groups"][sel_group]["matches"] = new_matches
                        all_group_players = [p for g in groups for p in tour["groups"][g]["players"]]
                        if sel_player not in all_group_players:
                            if sel_player in tour.get("players", []):
                                tour["players"].remove(sel_player)
                        save_tours(tours)
                        st.success(f"'{sel_player}' 삭제됨")
                        st.rerun()
                
                st.markdown("---")
                
                new_name = st.text_input("새 참가자 이름", placeholder="예: 홍길동", key="adm1_add_player")
                if st.button("➕ 추가", use_container_width=True, key="adm1_add_btn"):
                    if new_name and new_name.strip():
                        new_name = new_name.strip()
                        if new_name not in tour["groups"][sel_group]["players"]:
                            tour["groups"][sel_group]["players"].append(new_name)
                            if new_name not in tour.get("players", []):
                                if "players" not in tour:
                                    tour["players"] = []
                                tour["players"].append(new_name)
                            
                            mode = tour["groups"][sel_group]["mode"]
                            gc   = tour["groups"][sel_group].get("games", 3)
                            if mode == "고정페어":
                                new_ms, _ = make_fixed(tour["groups"][sel_group]["players"])
                            elif mode == "KDK":
                                new_ms, new_pwn = make_kdk(tour["groups"][sel_group]["players"], gc)
                                if new_ms:
                                    tour["groups"][sel_group]["player_with_number"] = new_pwn
                                else:
                                    new_ms, _ = make_singles(tour["groups"][sel_group]["players"])
                            else:
                                new_ms, _ = make_singles(tour["groups"][sel_group]["players"])
                            tour["groups"][sel_group]["matches"] = new_ms
                            save_tours(tours)
                            st.success(f"'{new_name}' 추가됨")
                            st.rerun()
                        else:
                            st.warning("이미 있는 참가자입니다.")
                
                st.markdown("---")
                
                all_players_with_group = [
                    (p, g) for g in groups for p in tour["groups"][g]["players"]
                ]
                if all_players_with_group:
                    move_player   = st.selectbox("이동할 참가자", [p for p,_ in all_players_with_group], key="adm1_move_player")
                    current_group = next((g for p, g in all_players_with_group if p == move_player), groups[0])
                    other_groups  = [g for g in groups if g != current_group]
                    if other_groups:
                        target_group = st.selectbox("이동할 그룹", other_groups, key="adm1_target_group")
                        if st.button("🔄 이동", use_container_width=True, key="adm1_move_btn"):
                            tour["groups"][current_group]["players"].remove(move_player)
                            tour["groups"][target_group]["players"].append(move_player)
                            
                            for grp in [current_group, target_group]:
                                mode = tour["groups"][grp]["mode"]
                                gc   = tour["groups"][grp].get("games", 3)
                                if mode == "고정페어":
                                    new_ms, _ = make_fixed(tour["groups"][grp]["players"])
                                elif mode == "KDK":
                                    new_ms, new_pwn = make_kdk(tour["groups"][grp]["players"], gc)
                                    if new_ms:
                                        tour["groups"][grp]["player_with_number"] = new_pwn
                                    else:
                                        new_ms, _ = make_singles(tour["groups"][grp]["players"])
                                else:
                                    new_ms, _ = make_singles(tour["groups"][grp]["players"])
                                tour["groups"][grp]["matches"] = new_ms
                            
                            save_tours(tours)
                            st.success(f"'{move_player}' {target_group}으로 이동됨")
                            st.rerun()
                    else:
                        st.info("이동할 다른 그룹이 없습니다.")
        else:
            st.info("아직 생성된 그룹이 없습니다. '대회 관리' 탭에서 그룹을 먼저 설정하세요.")

    # ── 랭킹 관리 ─────────────────────────────────────────────
    with adm[2]:
        st.markdown('<div class="sec">📁 엑셀 업로드</div>', unsafe_allow_html=True)
        up = st.file_uploader("파일 선택", type=["xlsx","csv"])
        if up:
            try:
                df_up = (pd.read_excel(up) if up.name.endswith("xlsx") else pd.read_csv(up, encoding_errors="replace"))
                if "현재포인트" in df_up.columns:
                    df_up["현재포인트"] = pd.to_numeric(df_up["현재포인트"], errors="coerce").fillna(0)
                    df_up = df_up.sort_values("현재포인트", ascending=False).reset_index(drop=True)
                    df_up["랭킹"] = df_up.index + 1
                st.dataframe(df_up, use_container_width=True)
                if st.button("💾 저장", type="primary", key="adm2_save_upload"):
                    save_rank(df_up)
                    if "이름" in df_up.columns:
                        save_members(df_up["이름"].tolist())
                    st.success("저장 완료!")
                    st.rerun()
            except Exception as e:
                st.error(f"오류: {e}")
        
        st.divider()
        st.markdown('<div class="sec">📊 현재 랭킹</div>', unsafe_allow_html=True)
        df_cur = load_rank()
        if not df_cur.empty:
            st.dataframe(df_cur, use_container_width=True)
            st.download_button("📥 다운로드", data=to_excel(df_cur),
                               file_name=f"랭킹_{date.today()}.xlsx",
                               key="adm2_download")
        
        st.divider()
        st.markdown('<div class="sec">✏️ 직접 수정</div>', unsafe_allow_html=True)
        df_edit = load_rank()
        if not df_edit.empty:
            edited = st.data_editor(df_edit, use_container_width=True, hide_index=True, num_rows="dynamic")
            if st.button("💾 수정 저장", type="primary", key="adm2_save_edit"):
                save_rank(edited)
                save_members(edited["이름"].tolist())
                st.success("저장 완료!")
                st.rerun()

    # ── 결과 반영 ─────────────────────────────────────────────
    with adm[3]:
        tours  = load_tours()
        active2 = [k for k,v in tours.items() if v.get("status") == "진행중"]
        if not active2:
            st.warning("진행 중인 대회 없음")
            st.stop()
        sel_tid2 = st.selectbox("대회 선택", active2,
                                format_func=lambda k: tours[k]['title'],
                                key="adm3_sel_tid")
        tour3 = tours[sel_tid2]
        
        if not tour3.get("groups"):
            st.warning("대진 없음")
            st.stop()
        
        earn = {}
        for g, ginfo in tour3["groups"].items():
            mode     = ginfo["mode"]
            matches  = ginfo["matches"]
            is_fixed = (mode == "고정페어")
            if is_fixed:
                stats  = group_stats_fixed(matches)
                ranked = sorted(stats.keys(), key=lambda t: (-stats[t]["승"], -stats[t]["득실"]))
            else:
                stats  = group_stats_kdk(matches)
                ranked = sorted(stats.keys(), key=lambda p: (-stats[p]["승"], -stats[p]["득실"]))
            for i, item in enumerate(ranked):
                pt = rank_pts(i+1, mode)
                if is_fixed:
                    for p in list(item):
                        earn[p] = earn.get(p, 0) + pt
                else:
                    earn[item] = earn.get(item, 0) + pt
        
        if earn:
            earn_df = pd.DataFrame(earn.items(), columns=["선수", "획득포인트"])
            earn_col_cfg = {c: st.column_config.TextColumn(c, width="small") for c in earn_df.columns}
            st.dataframe(earn_df, use_container_width=True, column_config=earn_col_cfg)
        
        c1, c2 = st.columns(2)
        with c1:
            if st.button("🏆 랭킹 반영", type="primary", use_container_width=True, key="adm3_apply"):
                df_r = load_rank()
                if df_r.empty:
                    df_r = pd.DataFrame(columns=COLS_RANK)
                for p, pt in earn.items():
                    if p in df_r["이름"].values:
                        cur = df_r.loc[df_r["이름"] == p, "현재포인트"].values[0]
                        df_r.loc[df_r["이름"] == p, "현재포인트"] = cur + pt
                    else:
                        nr = {c: "" for c in COLS_RANK}
                        nr["이름"] = p
                        nr["현재포인트"] = pt
                        df_r = pd.concat([df_r, pd.DataFrame([nr])], ignore_index=True)
                save_rank(df_r)
                tours[sel_tid2]["status"] = "완료"
                save_tours(tours)
                st.success("반영 완료!")
                st.rerun()
        with c2:
            if st.button("🗑 점수 초기화", use_container_width=True, key="adm3_reset"):
                for g in tour3["groups"]:
                    for m in tour3["groups"][g]["matches"]:
                        m["s1"] = 0
                        m["s2"] = 0
                save_tours(tours)
                st.success("초기화 완료!")
                st.rerun()

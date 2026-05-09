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
    font-size: 0.7rem !important;
}
div[data-testid="stDataFrame"] table th,
div[data-testid="stDataFrame"] table td {
    text-align: center !important;
    vertical-align: middle !important;
    padding: 6px 3px !important;
    font-size: 0.7rem !important;
    white-space: nowrap;
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
    font-size: 0.65rem;
}
.matrix-table th, .matrix-table td {
    padding: 6px 3px;
    border: 1px solid #ddd;
    text-align: center;
}
.matrix-grey { background-color: #d0d0d0; color: #d0d0d0; }
.matrix-x { color: #ccc; }

.kdk-bracket {
    background: #f5f5f5;
    border-radius: 10px;
    padding: 10px;
    margin: 8px 0;
    font-size: 0.7rem;
    overflow-x: auto;
}
.kdk-bracket th, .kdk-bracket td { padding: 6px; font-size: 0.7rem; }

.tour-card, .rank-card { padding: 8px 12px; margin: 6px 0; border-radius: 10px; }
.dataframe th { font-size: 0.7rem !important; padding: 6px 3px !important; }
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

# KDK 대진표 (1인 3게임)
KDK_3G = {
    4: [(1,4,2,3), (1,3,2,4), (1,2,3,4)],
    8: [(1,2,3,4), (5,6,7,8), (1,8,2,7), (3,6,4,5), (1,4,5,8), (2,3,6,7)],
    12: [(1,2,3,4), (5,6,7,8), (9,10,11,12), (1,3,5,7), (2,4,6,8),
         (9,11,1,5), (4,8,9,12), (6,7,10,11), (10,12,2,3)]
}

# KDK 대진표 (1인 4게임)
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
    if games_per_person == 3:
        bracket = KDK_3G.get(n)
        title = f"KDK 1인 3게임 기준 - {n}명"
    else:
        bracket = KDK_4G.get(n)
        title = f"KDK 1인 4게임 기준 - {n}명"
    if not bracket:
        return
    number_to_name = {v: k for k, v in player_with_number.items()}
    html = f'<div class="kdk-bracket"><strong>📋 {title}</strong><br><br>'
    html += '<table style="width:100%"><thead><tr><th>순서</th><th>대진 번호</th><th>대진 (참가자)</th></tr></thead><tbody>'
    for idx, (a, b, c, d) in enumerate(bracket):
        team1 = f"{number_to_name.get(a, a)}({a}) & {number_to_name.get(b, b)}({b})"
        team2 = f"{number_to_name.get(c, c)}({c}) & {number_to_name.get(d, d)}({d})"
        html += f'叉戟-th>{idx+1}叉戟-th>{a}{b} : {c}{d}叉戟-th>{team1} vs {team2}叉戟-th>'
    html += '</tbody></table></div>'
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
        st.info("📋 등록된 랭킹이 없습니다. 관리자에서 엑셀을 업로드하세요.")
    else:
        icons = ["🥇","🥈","🥉"]
        disp = df.copy()
        disp.insert(0, "순위", [icons[i] if i<3 else str(i+1) for i in range(len(disp))])
        st.dataframe(disp, use_container_width=True, hide_index=True)
        st.download_button("📥 엑셀 다운로드", data=to_excel(df), file_name=f"랭킹_{date.today()}.xlsx", use_container_width=True)

# ══════════════════════════════════════════════════════════════
# 2. 대진·경기현황
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
    st.caption(f"{tour.get('date','')} | {tour.get('place','')} | 코트 {tour.get('courts',2)}면")

    gnames = list(tour["groups"].keys())
    if not gnames:
        st.info("대진이 없습니다. 관리자에서 대진을 생성하세요.")
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
            
            # 상대별 전적 매트릭스
            st.markdown("**📋 상대별 전적 매트릭스**")
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
                html = '<table class="matrix-table"><thead><tr><th></th>'
                for col in mdf.columns:
                    html += f'<th>{col}</th>'
                html += '</table></thead><tbody>'
                for idx, row in mdf.iterrows():
                    html += f'叉戟-th>{idx}</th>'
                    for col in mdf.columns:
                        val = row[col]
                        if val == '■':
                            html += '<td class="matrix-grey">■</td>'
                        elif val == 'X':
                            html += '<td class="matrix-x">X</td>'
                        else:
                            html += f'<td>{val}</td>'
                    html += '</tr>'
                html += '</tbody></table>'
                st.markdown(html, unsafe_allow_html=True)
            else:
                st.info("경기 데이터가 없습니다.")
            
            # KDK 대진표 표시
            if not is_fixed and player_with_number:
                st.divider()
                n = len(player_with_number)
                gc = ginfo.get("games", 3)
                display_kdk_bracket(n, gc, player_with_number)
            
            # 현재 순위
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
                st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
            else:
                st.info("순위 정보가 없습니다.")
            
            # 경기 입력
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
                st.toast("✅ 점수가 저장되었습니다!", icon="✅")

# ══════════════════════════════════════════════════════════════
# 3. 경기 결과
# ══════════════════════════════════════════════════════════════
elif M == "result":
    tours = load_tours()
    active = [k for k,v in tours.items() if v.get("status")=="진행중"]
    if not active:
        st.warning("⚠️ 진행 중인 대회가 없습니다.")
        st.stop()
    tid = active[-1]
    tour = tours[tid]
    st.markdown(f"<div class='main-hdr'>📊 {tour['title']} 경기 결과</div>", unsafe_allow_html=True)

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
        
        # KDK 대진표 표시
        if not is_fixed and player_with_number:
            n = len(player_with_number)
            gc = ginfo.get("games", 3)
            display_kdk_bracket(n, gc, player_with_number)
            st.divider()
        
        # 최종 순위
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
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
        
        # 전체 경기 결과 상세
        with st.expander("📋 전체 경기 결과 상세보기"):
            mrows = []
            for m in matches:
                t1 = " & ".join(m["t1"])
                t2 = " & ".join(m["t2"])
                s1, s2 = int(m["s1"]), int(m["s2"])
                result = "🏆 " + t1 + " 승" if s1 > s2 else "🏆 " + t2 + " 승" if s2 > s1 else "무승부"
                mrows.append({
                    "페어1": t1,
                    "점수1": s1,
                    "점수2": s2,
                    "페어2": t2,
                    "결과": result
                })
            st.dataframe(pd.DataFrame(mrows), use_container_width=True, hide_index=True)

# ══════════════════════════════════════════════════════════════
# 4. 지난 대회
# ══════════════════════════════════════════════════════════════
elif M == "archive":
    st.markdown("<div class='main-hdr'>📂 지난 대회</div>", unsafe_allow_html=True)
    tours = load_tours()
    past = {k:v for k,v in tours.items() if v.get("status")!="진행중"}
    if not past:
        st.info("완료된 대회 기록이 없습니다.")
        st.stop()
    sel = st.selectbox("대회 선택", list(past.keys()), format_func=lambda k: f"{past[k]['title']} ({past[k].get('date','')})")
    tour = past[sel]
    st.markdown(f"**🏆 {tour['title']}** | {tour.get('date','')} | {tour.get('place','')}")
    st.divider()
    if not tour.get("groups"):
        st.info("대진 정보가 없습니다.")
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
        
        # KDK 대진표 표시
        if not is_fixed and player_with_number:
            n = len(player_with_number)
            gc = ginfo.get("games", 3)
            display_kdk_bracket(n, gc, player_with_number)
            st.divider()
        
        # 최종 순위
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
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
        
        # 전체 경기 결과
        with st.expander(f"📋 {g} 전체 경기 결과"):
            mrows = []
            for m in matches:
                t1 = " & ".join(m["t1"])
                t2 = " & ".join(m["t2"])
                s1, s2 = int(m["s1"]), int(m["s2"])
                result = "🏆 " + t1 + " 승" if s1 > s2 else "🏆 " + t2 + " 승" if s2 > s1 else "무승부"
                mrows.append({
                    "페어1": t1,
                    "점수1": s1,
                    "점수2": s2,
                    "페어2": t2,
                    "결과": result
                })
            st.dataframe(pd.DataFrame(mrows), use_container_width=True, hide_index=True)

# ══════════════════════════════════════════════════════════════
# 5. 관리자
# ══════════════════════════════════════════════════════════════
elif M == "admin":
    st.markdown("<div class='main-hdr'>⚙️ 관리자</div>", unsafe_allow_html=True)
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

        st.markdown('<div class="sec">📝 참가자 입력 (일괄)</div>', unsafe_allow_html=True)

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
        # 개별 참가자 수정 섹션 - 대진 유지
        # ============================================================
        st.markdown('<div class="sec">✏️ 개별 참가자 수정 (대진 유지)</div>', unsafe_allow_html=True)
        st.caption("대진이 이미 생성된 후에도 참가자를 개별적으로 수정할 수 있습니다.")
        
        if tour.get("groups"):
            groups = list(tour["groups"].keys())
            if groups:
                # 그룹 선택
                sel_group = st.selectbox("수정할 그룹 선택", groups, key="edit_group", format_func=lambda x: x)
                current_players = tour["groups"][sel_group]["players"].copy()
                st.markdown(f"**현재 {sel_group} 참가자:** {', '.join(current_players) if current_players else '없음'}")
                
                # 참가자 삭제
                if current_players:
                    sel_player = st.selectbox("삭제할 참가자 선택", current_players, key="del_player")
                    if st.button("🗑 선택한 참가자 삭제", use_container_width=True):
                        tour["groups"][sel_group]["players"].remove(sel_player)
                        new_matches = [m for m in tour["groups"][sel_group]["matches"] 
                                       if sel_player not in m["t1"] and sel_player not in m["t2"]]
                        tour["groups"][sel_group]["matches"] = new_matches
                        if sel_player not in [p for g in groups for p in tour["groups"][g]["players"]]:
                            if sel_player in tour.get("players", []):
                                tour["players"].remove(sel_player)
                        save_tours(tours)
                        st.success(f"✅ '{sel_player}' 님이 삭제되었습니다!")
                        st.rerun()
                
                st.markdown("---")
                
                # 새 참가자 추가
                new_name = st.text_input("새 참가자 이름", placeholder="예: 홍길동", key="add_player")
                if st.button("➕ 새 참가자 추가", use_container_width=True):
                    if new_name and new_name.strip():
                        new_name = new_name.strip()
                        if new_name not in tour["groups"][sel_group]["players"]:
                            tour["groups"][sel_group]["players"].append(new_name)
                            if "players" not in tour:
                                tour["players"] = []
                            if new_name not in tour["players"]:
                                tour["players"].append(new_name)
                            
                            mode = tour["groups"][sel_group]["mode"]
                            gc = tour["groups"][sel_group].get("games", 3)
                            if mode == "고정페어":
                                new_ms, _ = make_fixed(tour["groups"][sel_group]["players"])
                            elif mode == "KDK":
                                new_ms, new_pwn = make_kdk(tour["groups"][sel_group]["players"], gc)
                                tour["groups"][sel_group]["player_with_number"] = new_pwn
                            else:
                                new_ms, _ = make_singles(tour["groups"][sel_group]["players"])
                            tour["groups"][sel_group]["matches"] = new_ms
                            save_tours(tours)
                            st.success(f"✅ '{new_name}' 님이 추가되었습니다!")
                            st.rerun()
                        else:
                            st.warning("이미 있는 참가자입니다.")
                
                st.markdown("---")
                
                # 참가자 이동
                all_players_with_group = []
                for g in groups:
                    for p in tour["groups"][g]["players"]:
                        all_players_with_group.append((p, g))
                if all_players_with_group:
                    move_player = st.selectbox("이동할 참가자", [p[0] for p in all_players_with_group], key="move_player")
                    current_group = next((g for p, g in all_players_with_group if p == move_player), groups[0])
                    target_group = st.selectbox("이동할 그룹", [g for g in groups if g != current_group], key="target_group")
                    if st.button("🔄 참가자 그룹 이동", use_container_width=True):
                        # 현재 그룹에서 제거
                        tour["groups"][current_group]["players"].remove(move_player)
                        # 새 그룹에 추가
                        tour["groups"][target_group]["players"].append(move_player)
                        
                        # 두 그룹 모두 대진 재생성
                        for grp in [current_group, target_group]:
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
                        st.success(f"✅ '{move_player}' 님이 {target_group}으로 이동되었습니다!")
                        st.rerun()
        else:
            st.info("아직 생성된 그룹이 없습니다. 먼저 '대회 관리' 탭에서 대회를 생성하세요.")

        st.divider()

        # ============================================================
        # 그룹·대진 설정 (최초 생성 또는 재생성)
        # ============================================================
        st.markdown('<div class="sec">🎲 그룹·대진 설정 (새로 생성)</div>', unsafe_allow_html=True)
        st.caption("※ 주의: 새로 대진을 생성하면 기존 대진과 점수가 초기화됩니다.")
        
        if not sel_names:
            st.warning("먼저 참가자를 저장하세요.")
        else:
            # 기본값 설정
            default_gcnt = max(1, len(tour.get("groups", {}))) if tour.get("groups") else min(4, max(1, len(sel_names)//8))
            gcnt = st.number_input("그룹 수", 1, 6, value=default_gcnt, key="gcnt_input")
            gns = [f"{chr(65+i)}그룹" for i in range(gcnt)]
            gcfg = {}
            for i, gn in enumerate(gns):
                # 기존 그룹 설정 가져오기
                existing = tour.get("groups", {}).get(gn, {})
                hx = GHEX[i % len(GHEX)]
                st.markdown(f"<div style='background:{hx}18;border-left:4px solid {hx};"
                            f"border-radius:7px;padding:5px 12px;margin:6px 0;"
                            f"font-weight:800;color:{hx}'>{GLBL[i%len(GLBL)]} {gn}</div>",
                            unsafe_allow_html=True)
                cc = st.columns(4)
                dfsz = max(2, len(sel_names)//gcnt)
                with cc[0]:
                    nm2 = st.text_input("그룹명", gn, key=f"gn_{i}")
                with cc[1]:
                    default_sz = len(existing.get("players", [])) if existing else dfsz
                    sz = st.number_input("인원", 2, 30, value=default_sz, key=f"sz_{i}")
                with cc[2]:
                    default_md = existing.get("mode", "고정페어")
                    md = st.selectbox("방식", ["고정페어","KDK","단식"], index=["고정페어","KDK","단식"].index(default_md), key=f"md_{i}")
                with cc[3]:
                    default_gc = existing.get("games", 4)
                    gc = st.selectbox("1인 게임수", [3,4,5], index=[3,4,5].index(default_gc), key=f"gc_{i}")
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
                tours[sel_tid]["players"] = sel_names
                save_tours(tours)
                st.success("✅ 대진 생성 완료! (랭킹 높은 순 → A → B → C 그룹 순서로 배정됨)")
                st.rerun()

    # 탭3: 랭킹 관리
    with adm[2]:
        st.markdown('<div class="sec">📁 엑셀 업로드</div>', unsafe_allow_html=True)

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

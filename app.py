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

/* ── 네비게이션 바 ── */
.nav-wrap {
    display: flex; width: 100%; gap: 0;
    background: #1D5B2E; border-radius: 0 0 16px 16px;
    padding: 0; margin-bottom: 1rem;
    box-shadow: 0 4px 14px rgba(0,0,0,0.18);
}
.nav-btn {
    flex: 1; padding: 18px 6px; border: none; cursor: pointer;
    background: transparent; color: rgba(255,255,255,0.75);
    font-size: clamp(0.78rem, 2.2vw, 1rem); font-weight: 700;
    font-family: 'Noto Sans KR', sans-serif;
    transition: all 0.2s; border-radius: 0; line-height: 1.3;
}
.nav-btn:hover { background: rgba(255,255,255,0.12); color: #fff; }
.nav-btn.active {
    background: rgba(255,255,255,0.22); color: #fff;
    border-bottom: 4px solid #A5D6A7; font-weight: 900;
}
.nav-btn:first-child { border-radius: 0 0 0 16px; }
.nav-btn:last-child  { border-radius: 0 0 16px 0; }

/* ── 공통 헤더 ── */
.main-hdr {
    background: linear-gradient(135deg, #1D5B2E, #388E3C);
    color: #fff; padding: 1rem 1.4rem; border-radius: 14px;
    margin-bottom: 1rem; font-size: clamp(1.2rem,4vw,1.9rem);
    font-weight: 900; text-align: center;
    box-shadow: 0 6px 18px rgba(0,0,0,0.14);
}
.sec {
    font-size: 1.05rem; font-weight: 900; color: #1D5B2E;
    border-left: 5px solid #66BB6A; padding-left: 10px; margin: 14px 0 8px;
}

/* ── 탭 버튼 ── */
button[data-baseweb="tab"] {
    font-size: 0.97rem !important; font-weight: 700 !important;
    padding: 10px 16px !important; border-radius: 8px 8px 0 0 !important;
}
button[data-baseweb="tab"][aria-selected="true"] {
    background: linear-gradient(135deg,#1D5B2E,#388E3C) !important;
    color: #fff !important;
}

/* ── 일반 버튼 ── */
.stButton > button {
    border-radius: 9px !important; font-weight: 700 !important;
    transition: all 0.18s !important;
}
.stButton > button:hover { transform: translateY(-1px); }

/* ── 테이블 가운데 정렬 ── */
th, td { text-align: center !important; vertical-align: middle !important; }

/* ── 점수 입력 크게 ── */
input[type="number"] { text-align: center !important; font-weight: 700 !important; }
div[data-testid="stNumberInput"] input {
    font-size: 1.25rem !important; font-weight: 900 !important; text-align: center !important;
}

/* ── 팀 도형 카드 ── */
.team-box {
    border-radius: 12px; padding: 9px 13px; font-weight: 800;
    font-size: clamp(0.82rem,2.4vw,1rem); text-align: center;
    margin: 3px 0; box-shadow: 0 3px 8px rgba(0,0,0,0.13); line-height: 1.4;
}
.tg { background: linear-gradient(135deg,#2E7D32,#1B5E20); color:#fff; }
.tb { background: linear-gradient(135deg,#1565C0,#0D47A1); color:#fff; }
.to { background: linear-gradient(135deg,#E65100,#BF360C); color:#fff; }
.tp { background: linear-gradient(135deg,#6A1B9A,#4A148C); color:#fff; }
.tr { background: linear-gradient(135deg,#C62828,#B71C1C); color:#fff; }
.tt { background: linear-gradient(135deg,#00695C,#004D40); color:#fff; }

.vs-circle {
    background: #E53935; color: #fff; border-radius: 50%;
    width: 34px; height: 34px; display: flex; align-items: center;
    justify-content: center; font-weight: 900; font-size: 0.8rem;
    margin: 4px auto; box-shadow: 0 2px 8px rgba(229,57,53,0.4);
}
.rnd-hdr {
    background: linear-gradient(90deg,#1D5B2E,#43A047); color:#fff;
    border-radius: 8px; padding: 5px 14px; font-weight: 800;
    text-align: center; margin: 12px 0 6px;
}
.match-wrap {
    background: #fff; border-radius: 12px; padding: 8px;
    margin: 5px 0; box-shadow: 0 3px 10px rgba(0,0,0,0.08);
    border: 1px solid #E8F5E9;
}
/* ── 대회 카드 ── */
.tour-card {
    background: #F9FBF9; border: 1.5px solid #C8E6C9; border-radius: 12px;
    padding: 10px 14px; margin: 6px 0;
}
/* ── 반응형 ── */
@media (max-width: 640px) {
    .block-container { padding: 0 0.3rem 2rem !important; }
    .nav-btn { font-size: 0.72rem !important; padding: 14px 3px !important; }
}
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# 상수 / 데이터 함수
# ══════════════════════════════════════════════════════════════
RANK_FILE = "ranking_master.csv"
TOUR_FILE = "tournaments.json"
ADMIN_PW  = "0502"
COLS_RANK = ["랭킹","이름","현재포인트","3월 포인트","결과","부과점","그룹","비고"]

GCLS = ["tg","tb","to","tp","tr","tt"]
GHEX = ["#2E7D32","#1565C0","#E65100","#6A1B9A","#C62828","#00695C"]
GLBL = ["🟢","🔵","🟠","🟣","🔴","🩵"]

KDK_BP = {
    3: {
        4:  [(1,4,2,3),(1,3,2,4),(1,2,3,4)],
        8:  [(1,2,3,4),(5,6,7,8),(1,8,2,7),(3,6,4,5),(1,4,5,8),(2,3,6,7)],
        12: [(1,2,3,4),(5,6,7,8),(9,10,11,12),(1,3,5,7),(2,4,6,8),
             (9,11,1,5),(4,8,9,12),(6,7,10,11),(10,12,2,3)],
    },
    4: {
        5:  [(1,2,3,4),(1,3,2,5),(1,4,3,5),(1,5,2,4),(2,3,4,5)],
        6:  [(1,3,2,4),(1,5,4,6),(2,3,5,6),(1,4,3,5),(2,6,3,4),(1,6,2,5)],
        7:  [(1,2,3,4),(5,6,1,7),(2,3,5,7),(1,4,6,7),(3,5,2,4),(1,6,2,5),(4,6,3,7)],
        8:  [(1,2,3,4),(5,6,7,8),(1,3,5,7),(2,4,6,8),(1,5,2,6),(3,7,4,8),(1,6,3,8),(2,5,4,7)],
        9:  [(1,2,3,4),(5,6,7,8),(1,9,5,7),(2,3,6,8),(4,9,3,8),(1,5,2,6),(3,6,4,5),(1,7,8,9),(2,4,7,9)],
        10: [(1,2,3,5),(6,7,8,10),(2,3,4,6),(7,8,1,9),(3,4,5,7),(8,9,2,10),
             (4,5,6,8),(1,3,9,10),(5,6,7,9),(1,10,2,4)],
        11: [(1,2,3,5),(6,7,8,10),(4,9,1,11),(2,3,6,8),(4,5,7,10),(9,11,2,6),
             (1,3,7,11),(4,8,5,9),(1,10,2,8),(4,7,6,11),(3,9,5,10)],
    },
}

def load_rank():
    if not os.path.exists(RANK_FILE):
        return pd.DataFrame(columns=COLS_RANK)
    df = pd.read_csv(RANK_FILE)
    for c in ["현재포인트","3월 포인트","부과점"]:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0)
    # ★ 포인트 내림차순 정렬 (높을수록 1위)
    if "현재포인트" in df.columns:
        df = df.sort_values("현재포인트", ascending=False).reset_index(drop=True)
        df["랭킹"] = df.index + 1
    return df.fillna("")

def save_rank(df):
    if "현재포인트" in df.columns:
        df = df.sort_values("현재포인트", ascending=False).reset_index(drop=True)
        df["랭킹"] = df.index + 1
    df.to_csv(RANK_FILE, index=False)

def load_tours():
    if os.path.exists(TOUR_FILE):
        with open(TOUR_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_tours(d):
    with open(TOUR_FILE, "w", encoding="utf-8") as f:
        json.dump(d, f, ensure_ascii=False, indent=2)

def to_excel(df):
    buf = BytesIO()
    df.to_excel(buf, index=False)
    return buf.getvalue()

def tname(t):
    return " & ".join(t) if len(t) > 1 else t[0]

def group_stats(matches):
    stats = {}
    for m in matches:
        t1, t2 = tuple(m["t1"]), tuple(m["t2"])
        for t in [t1, t2]:
            if t not in stats: stats[t] = {"승":0,"패":0,"득실":0}
        s1, s2 = int(m["s1"]), int(m["s2"])
        if s1 > s2:   stats[t1]["승"]+=1; stats[t2]["패"]+=1
        elif s2 > s1: stats[t2]["승"]+=1; stats[t1]["패"]+=1
        stats[t1]["득실"] += (s1-s2)
        stats[t2]["득실"] += (s2-s1)
    return stats

def rank_pts(rank, mode):
    if mode == "고정페어":
        return {1:7, 2:5, 3:3}.get(rank, 1)
    else:  # KDK / 단식: 2명씩 묶음
        return {1:7, 2:7, 3:5, 4:5, 5:3, 6:3}.get(rank, 1)

def make_kdk(players, gc):
    bp = KDK_BP.get(gc, {}).get(len(players))
    if not bp: return None
    sh = random.sample(players, len(players))
    return [{"t1":[sh[a-1],sh[b-1]],"t2":[sh[c-1],sh[d-1]],"s1":0,"s2":0} for a,b,c,d in bp]

def make_fixed(players):
    n = len(players)
    pairs = [(players[i], players[n-1-i]) for i in range(n//2)]
    ms = []
    for i in range(len(pairs)):
        for j in range(i+1, len(pairs)):
            ms.append({"t1":list(pairs[i]),"t2":list(pairs[j]),"s1":0,"s2":0})
    random.shuffle(ms); return ms

def make_singles(players):
    pl = players[:]
    random.shuffle(pl)
    ms = [(pl[i], pl[j]) for i in range(len(pl)) for j in range(i+1, len(pl))]
    random.shuffle(ms)
    return [{"t1":[a],"t2":[b],"s1":0,"s2":0} for a,b in ms]

# ══════════════════════════════════════════════════════════════
# 세션 초기화
# ══════════════════════════════════════════════════════════════
if "is_admin" not in st.session_state: st.session_state.is_admin = False
if "menu"     not in st.session_state: st.session_state.menu     = "ranking"

MENU_DEFS = [
    ("ranking",  "🏆\n두류 랭킹"),
    ("schedule", "📅\n대진·경기현황"),
    ("result",   "📊\n경기 결과"),
    ("archive",  "📂\n지난 대회"),
    ("admin",    "⚙️\n관리자"),
]

# ══════════════════════════════════════════════════════════════
# 네비게이션 바 (HTML 버튼 → JS 대신 st.query_params 우회 불가,
#  Streamlit button으로 구성하되 CSS로 크고 진하게)
# ══════════════════════════════════════════════════════════════
st.markdown("<div style='background:#1D5B2E;border-radius:0 0 14px 14px;"
            "padding:4px 0 0 0;margin-bottom:12px;"
            "box-shadow:0 4px 14px rgba(0,0,0,0.2)'>", unsafe_allow_html=True)

nav_cols = st.columns(len(MENU_DEFS))
for col, (key, label) in zip(nav_cols, MENU_DEFS):
    active = st.session_state.menu == key
    # 활성 탭 스타일
    bg  = "rgba(255,255,255,0.22)" if active else "transparent"
    fw  = "900" if active else "700"
    col_txt = "#fff" if active else "rgba(255,255,255,0.7)"
    border  = "border-bottom:4px solid #A5D6A7;" if active else "border-bottom:4px solid transparent;"
    with col:
        if st.button(label, key=f"nav_{key}", use_container_width=True):
            st.session_state.menu = key
            st.rerun()
        # 버튼 위에 스타일 오버라이드
        st.markdown(f"""
        <style>
        div[data-testid="stButton"] button[kind="secondary"][key="nav_{key}"],
        button[data-testid="baseButton-secondary"]:has(p:contains("{label.split(chr(10))[1]}")) {{
            background:{bg}!important; color:{col_txt}!important;
            font-weight:{fw}!important; {border}
            border-radius:0!important; padding:14px 4px!important;
            font-size:clamp(.75rem,2vw,.95rem)!important; line-height:1.4!important;
        }}
        </style>""", unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)

# 버튼 공통 스타일 강제 (nav 전용)
st.markdown("""
<style>
/* nav 버튼들을 덮어쓰기 */
section.main div[data-testid="column"] .stButton > button {
    background: transparent !important;
    color: rgba(255,255,255,0.75) !important;
    border: none !important;
    border-radius: 0 !important;
    font-size: clamp(0.75rem,2.1vw,0.95rem) !important;
    font-weight: 700 !important;
    padding: 16px 4px !important;
    line-height: 1.4 !important;
    white-space: pre-line !important;
    box-shadow: none !important;
}
/* 활성 메뉴는 JS 미지원이므로 primary 타입으로 강조 */
section.main div[data-testid="column"] .stButton > button[kind="primary"] {
    background: rgba(255,255,255,0.22) !important;
    color: #fff !important;
    font-weight: 900 !important;
    border-bottom: 4px solid #A5D6A7 !important;
}
</style>
""", unsafe_allow_html=True)

M = st.session_state.menu

# ══════════════════════════════════════════════════════════════
# 1. 🏆 두류 랭킹
# ══════════════════════════════════════════════════════════════
if M == "ranking":
    st.markdown("<div class='main-hdr'>🏆 두류 랭킹 관리 시스템</div>", unsafe_allow_html=True)
    df = load_rank()

    if df.empty:
        st.info("📋 등록된 랭킹이 없습니다. 관리자에서 엑셀을 업로드하세요.")
    else:
        # 순위 아이콘
        def rank_icon(i):
            return ["🥇","🥈","🥉"][i] if i < 3 else str(i+1)
        disp = df.copy()
        disp.insert(0, "순위", [rank_icon(i) for i in range(len(disp))])
        st.dataframe(disp, use_container_width=True, hide_index=True)

    # 누구나 다운로드 가능
    if not df.empty:
        st.download_button(
            "📥 랭킹 엑셀 다운로드", data=to_excel(df),
            file_name=f"두류랭킹_{date.today()}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )

# ══════════════════════════════════════════════════════════════
# 2. 📅 대진 및 경기 현황  (일반 회원: 점수 입력 가능)
# ══════════════════════════════════════════════════════════════
elif M == "schedule":
    tours = load_tours()
    active = [k for k,v in tours.items() if v.get("status") == "진행중"]
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

    tabs = st.tabs([f"{GLBL[i%len(GLBL)]} {g}" for i, g in enumerate(gnames)])
    for ti, g in enumerate(gnames):
        with tabs[ti]:
            ginfo   = tour["groups"][g]
            matches = ginfo["matches"]
            mode    = ginfo["mode"]
            cls     = GCLS[ti % len(GCLS)]
            stats   = group_stats(matches)
            teams   = list(stats.keys())

            # ── 상단: 매트릭스 + 순위표 ──
            mc, rc = st.columns([3, 2])
            with mc:
                st.markdown("**📋 상대별 전적 매트릭스**")
                lab = {t: tname(list(t)) for t in teams}
                mat = {lab[t]: {lab[o]: ("■" if t==o else "–") for o in teams} for t in teams}
                for m in matches:
                    t1,t2 = tuple(m["t1"]),tuple(m["t2"])
                    s1,s2 = int(m["s1"]),int(m["s2"])
                    if s1>0 or s2>0:
                        mat[lab[t1]][lab[t2]] = f"{s1}:{s2}"
                        mat[lab[t2]][lab[t1]] = f"{s2}:{s1}"
                mdf = pd.DataFrame(mat).T
                # 자신 칸 배경 음영: Styler로 회색 처리
                def grey_diag(v): return "background-color:#e0e0e0;color:#e0e0e0" if v=="■" else ""
                st.dataframe(mdf.style.applymap(grey_diag), use_container_width=True)
            with rc:
                st.markdown("**🏅 현재 순위**")
                ranked = sorted(teams, key=lambda t: (-stats[t]["승"], -stats[t]["득실"]))
                rdf = pd.DataFrame([{
                    "순위": ["🥇","🥈","🥉"][i] if i<3 else i+1,
                    "팀/선수": tname(list(t)),
                    "승": stats[t]["승"], "패": stats[t]["패"],
                    "득실": f'{stats[t]["득실"]:+d}'
                } for i,t in enumerate(ranked)])
                st.dataframe(rdf, use_container_width=True, hide_index=True)

            st.divider()
            # ── 하단: 점수 입력 (일반 회원도 가능) ──
            changed = False
            for mi, m in enumerate(matches):
                t1,t2 = m["t1"],m["t2"]
                n1,n2 = tname(t1),tname(t2)
                st.markdown(f'<div class="rnd-hdr">경기 {mi+1}</div>', unsafe_allow_html=True)
                ca,cb,cc = st.columns([4,1,4])
                with ca:
                    st.markdown(f'<div class="team-box {cls}">{n1}</div>', unsafe_allow_html=True)
                    s1 = st.number_input(n1, 0, 50, int(m["s1"]),
                                         key=f"{tid}{g}{mi}s1", label_visibility="collapsed")
                with cb:
                    st.markdown('<div class="vs-circle">VS</div>', unsafe_allow_html=True)
                with cc:
                    st.markdown(f'<div class="team-box {cls}">{n2}</div>', unsafe_allow_html=True)
                    s2 = st.number_input(n2, 0, 50, int(m["s2"]),
                                         key=f"{tid}{g}{mi}s2", label_visibility="collapsed")
                if s1 != int(m["s1"]) or s2 != int(m["s2"]):
                    tour["groups"][g]["matches"][mi]["s1"] = s1
                    tour["groups"][g]["matches"][mi]["s2"] = s2
                    changed = True

            if changed:
                tours[tid] = tour
                save_tours(tours)
                st.toast("✅ 점수 저장됨!")

# ══════════════════════════════════════════════════════════════
# 3. 📊 경기 결과
# ══════════════════════════════════════════════════════════════
elif M == "result":
    tours  = load_tours()
    active = [k for k,v in tours.items() if v.get("status") == "진행중"]
    if not active:
        st.warning("⚠️ 진행 중인 대회가 없습니다.")
        st.stop()
    tid  = active[-1]; tour = tours[tid]
    st.markdown(f"<div class='main-hdr'>📊 {tour['title']} — 경기 결과</div>", unsafe_allow_html=True)

    for g, ginfo in tour["groups"].items():
        mode    = ginfo["mode"]
        matches = ginfo["matches"]
        stats   = group_stats(matches)
        ranked  = sorted(stats.keys(), key=lambda t: (-stats[t]["승"], -stats[t]["득실"]))
        st.markdown(f'<div class="sec">{g} 그룹 ({mode})</div>', unsafe_allow_html=True)

        rows = []
        if mode == "고정페어":
            for ri, t in enumerate(ranked):
                rank = ri + 1
                rows.append({
                    "순위":   ["🥇","🥈","🥉"][ri] if ri<3 else rank,
                    "팀":     tname(list(t)),
                    "승":     stats[t]["승"], "패": stats[t]["패"],
                    "득실":   f'{stats[t]["득실"]:+d}',
                    "부과점": rank_pts(rank, mode),
                    "등급":   ["우승","준우승","3위"][ri] if ri<3 else "참가",
                })
        else:
            GRADE = ["우승","우승","준우승","준우승","3위","3위"]
            for ri, t in enumerate(ranked):
                rank = ri + 1
                rows.append({
                    "순위":   rank,
                    "선수":   tname(list(t)),
                    "승":     stats[t]["승"], "패": stats[t]["패"],
                    "득실":   f'{stats[t]["득실"]:+d}',
                    "부과점": rank_pts(rank, mode),
                    "등급":   GRADE[ri] if ri < len(GRADE) else "참가",
                })
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

# ══════════════════════════════════════════════════════════════
# 4. 📂 지난 대회 아카이브
# ══════════════════════════════════════════════════════════════
elif M == "archive":
    st.markdown("<div class='main-hdr'>📂 지난 대회 아카이브</div>", unsafe_allow_html=True)
    tours = load_tours()
    past  = {k:v for k,v in tours.items() if v.get("status") != "진행중"}
    if not past:
        st.info("완료된 대회 기록이 없습니다.")
        st.stop()

    sel  = st.selectbox("대회 선택", list(past.keys()),
                        format_func=lambda k: f"{past[k]['title']}  ({past[k].get('date','날짜 없음')})")
    tour = past[sel]
    st.markdown(f"**🏆 {tour['title']}**&nbsp;&nbsp;📅 {tour.get('date','')}  |  📍 {tour.get('place','')}")
    st.divider()

    if not tour.get("groups"):
        st.info("이 대회는 대진 정보가 없습니다.")
        st.stop()

    for g, ginfo in tour["groups"].items():
        mode    = ginfo["mode"]
        matches = ginfo["matches"]
        stats   = group_stats(matches)
        ranked  = sorted(stats.keys(), key=lambda t: (-stats[t]["승"], -stats[t]["득실"]))
        st.markdown(f'<div class="sec">{g} 그룹 ({mode})</div>', unsafe_allow_html=True)
        GRADE = ["우승","우승","준우승","준우승","3위","3위"]
        rows = [{
            "순위":   ["🥇","🥈","🥉"][ri] if ri<3 else ri+1,
            "팀/선수": tname(list(t)),
            "승": stats[t]["승"], "패": stats[t]["패"],
            "득실":   f'{stats[t]["득실"]:+d}',
            "부과점": rank_pts(ri+1, mode),
            "등급":   (["우승","준우승","3위"][ri] if mode=="고정페어" and ri<3
                       else (GRADE[ri] if mode!="고정페어" and ri<len(GRADE) else "참가")),
        } for ri, t in enumerate(ranked)]
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

        # 전체 경기 결과
        with st.expander(f"📋 {g} 전체 경기 결과 보기"):
            mrows = []
            for m in matches:
                t1,t2 = m["t1"],m["t2"]; s1,s2=int(m["s1"]),int(m["s2"])
                res = ("🏆 "+tname(t1)+" 승" if s1>s2 else
                       "🏆 "+tname(t2)+" 승" if s2>s1 else "🤝 무승부")
                mrows.append({"팀1": tname(t1),"점수1":s1,"점수2":s2,"팀2":tname(t2),"결과":res})
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

    # ── 탭1: 대회 관리 (생성 + 수정/삭제) ──────────────────────
    with adm[0]:
        st.markdown('<div class="sec">새 대회 생성</div>', unsafe_allow_html=True)
        with st.form("f_new_tour"):
            c1,c2 = st.columns(2)
            tn = c1.text_input("대회명", placeholder="예: 5월 정기전")
            td = c2.date_input("날짜", value=date.today())
            c3,c4 = st.columns(2)
            tp     = c3.text_input("장소", placeholder="예: 두류공원 테니스장")
            courts = c4.selectbox("코트 수", [1,2,3], index=1)
            if st.form_submit_button("✅ 대회 생성", type="primary", use_container_width=True):
                if not tn.strip():
                    st.error("대회명을 입력하세요.")
                else:
                    tours = load_tours()
                    tid   = f"{td}_{tn.strip()}"
                    if tid in tours:
                        st.warning("같은 날짜·이름의 대회가 이미 있습니다.")
                    else:
                        tours[tid] = {"title":tn.strip(),"date":str(td),"place":tp,
                                      "courts":courts,"status":"진행중","groups":{}}
                        save_tours(tours)
                        st.success(f"🎉 '{tn}' 대회가 생성되었습니다!")
                        st.rerun()

        st.divider()
        st.markdown('<div class="sec">대회 목록 (수정 · 삭제)</div>', unsafe_allow_html=True)
        tours = load_tours()
        if not tours:
            st.info("생성된 대회가 없습니다.")
        else:
            STATUS_COLOR = {"진행중":"#FB8C00","완료":"#43A047","예정":"#1E88E5"}
            for tid2, tv in list(tours.items()):
                sc = STATUS_COLOR.get(tv.get("status",""), "#888")
                st.markdown(f"""
                <div class="tour-card">
                  <span style="font-weight:900;font-size:1rem">{tv['title']}</span>&nbsp;
                  <span style="font-size:.83rem;color:#555">📅{tv.get('date','')} &nbsp;📍{tv.get('place','')}&nbsp; 코트{tv.get('courts',2)}면</span>
                  <span style="color:{sc};font-weight:800;margin-left:8px">[{tv.get('status','')}]</span>
                </div>""", unsafe_allow_html=True)
                ca,cb,cc,cd = st.columns([2,3,2,2])
                with ca:
                    new_st = ca.selectbox("상태", ["진행중","완료","예정"],
                        index=["진행중","완료","예정"].index(tv.get("status","진행중")),
                        key=f"st_{tid2}", label_visibility="collapsed")
                with cb:
                    new_title = cb.text_input("대회명 수정", tv["title"],
                        key=f"tt_{tid2}", label_visibility="collapsed")
                with cc:
                    if st.button("💾 수정", key=f"edit_{tid2}", use_container_width=True):
                        tours[tid2]["title"]  = new_title
                        tours[tid2]["status"] = new_st
                        save_tours(tours); st.rerun()
                with cd:
                    if st.button("🗑 삭제", key=f"del_{tid2}", use_container_width=True):
                        del tours[tid2]; save_tours(tours); st.rerun()

    # ── 탭2: 참가자·대진 ────────────────────────────────────────
    with adm[1]:
        tours  = load_tours()
        active = [k for k,v in tours.items() if v.get("status") == "진행중"]
        if not active:
            st.warning("진행 중인 대회를 먼저 생성하세요.")
            st.stop()

        # 진행중 대회 선택
        sel_tid = st.selectbox("진행 중 대회",active,
            format_func=lambda k: f"{tours[k]['title']} ({tours[k].get('date','')})")
        tour = tours[sel_tid]
        st.info(f"현재 대회: **{tour['title']}** | 코트 {tour.get('courts',2)}면")

        # 참가자 등록
        st.markdown('<div class="sec">참가자 등록</div>', unsafe_allow_html=True)
        df_rank  = load_rank()
        all_names = df_rank["이름"].tolist() if not df_rank.empty else []

        raw   = st.text_area("카톡 명단 붙여넣기 (쉼표 또는 줄바꿈으로 구분)", height=55)
        typed = [n.strip() for n in raw.replace("\n",",").split(",") if n.strip()]

        sel_names = []
        chk_cols  = st.columns(5)
        for i, nm in enumerate(all_names):
            pre = nm in typed or nm in tour.get("players",[])
            if chk_cols[i%5].checkbox(nm, value=pre, key=f"att_{nm}"):
                sel_names.append(nm)

        rank_map = {str(r["이름"]): r["랭킹"] for _, r in df_rank.iterrows()} if not df_rank.empty else {}
        sel_names = sorted(set(sel_names), key=lambda x: float(rank_map.get(x,999)))
        st.success(f"선택 인원: **{len(sel_names)}명** — {', '.join(sel_names)}")

        st.divider()
        # 대진 설정
        st.markdown('<div class="sec">그룹 · 대진 설정 &nbsp;<small>(기본: 4그룹 × 8명 × 고정페어)</small></div>',
                    unsafe_allow_html=True)
        gcnt = st.number_input("그룹 수", 1, 6,
                               min(4, max(1, len(sel_names)//8)) if sel_names else 4)
        gns  = list("ABCDEF")[:gcnt]
        gcfg = {}
        for i, gn in enumerate(gns):
            hx = GHEX[i%len(GHEX)]
            st.markdown(
                f"<div style='background:{hx}18;border-left:4px solid {hx};"
                f"border-radius:7px;padding:5px 12px;margin:6px 0;"
                f"font-weight:800;color:{hx}'>{GLBL[i%len(GLBL)]} 그룹 {gn}</div>",
                unsafe_allow_html=True)
            cc = st.columns(4)
            dfsz = max(2, len(sel_names)//gcnt) if sel_names else 8
            with cc[0]: nm2 = st.text_input("그룹명", gn, key=f"gn{i}")
            with cc[1]: sz  = st.number_input("인원", 2, 30, dfsz, key=f"sz{i}")
            with cc[2]: md  = st.selectbox("방식", ["고정페어","KDK","단식"], key=f"md{i}")
            with cc[3]: gc  = st.selectbox("1인 게임수", [3,4,5], index=1, key=f"gc{i}")
            gcfg[nm2] = (sz, md, gc)

        total = sum(c[0] for c in gcfg.values())
        if sel_names:
            diff = len(sel_names) - total
            (st.success if diff==0 else st.warning)(
                f"{'✅' if diff==0 else '⚠️'} 참가자 {len(sel_names)}명 / 배정 {total}명"
                + (f" (차이 {diff:+d}명)" if diff else ""))

        if st.button("🎲 대진 생성", type="primary", use_container_width=True):
            if not sel_names:
                st.error("참가자를 선택하세요.")
            else:
                ptr = 0; new_groups = {}
                for gn, (sz, md, gc) in gcfg.items():
                    gp = sel_names[ptr:ptr+sz]; ptr += sz
                    if   md == "고정페어": ms = make_fixed(gp)
                    elif md == "KDK":
                        ms = make_kdk(gp, gc)
                        if not ms:
                            sh = random.sample(gp, len(gp))
                            pairs = [sh[i:i+2] for i in range(0,len(sh)-1,2)]
                            ms = [{"t1":list(a),"t2":list(b),"s1":0,"s2":0}
                                  for x,a in enumerate(pairs) for b in pairs[x+1:]]
                            st.warning(f"그룹 {gn}: 한울 KDK 데이터 없음 → 랜덤 리그 적용")
                    else: ms = make_singles(gp)
                    new_groups[gn] = {"players":gp,"mode":md,"games":gc,"matches":ms}
                tours[sel_tid]["groups"]  = new_groups
                tours[sel_tid]["players"] = sel_names
                save_tours(tours)
                st.success("✅ 대진 생성 완료! '대진 및 경기현황' 메뉴에서 확인하세요.")
                st.rerun()

    # ── 탭3: 랭킹 관리 (업로드 + 직접 수정) ────────────────────
    with adm[2]:
        st.markdown('<div class="sec">📥 엑셀 업로드</div>', unsafe_allow_html=True)
        st.caption("컬럼: 랭킹, 이름, 현재포인트, 3월 포인트, 결과, 부과점, 그룹, 비고")
        up = st.file_uploader("엑셀 / CSV 파일 선택", type=["xlsx","csv"])
        if up:
            try:
                df_up = (pd.read_excel(up) if up.name.endswith("xlsx")
                         else pd.read_csv(up, encoding_errors="replace"))
                df_up.columns = [str(c).strip() for c in df_up.columns]
                st.dataframe(df_up.head(15), use_container_width=True, hide_index=True)
                if st.button("💾 업로드 내용으로 랭킹 저장", type="primary", use_container_width=True):
                    save_rank(df_up)
                    st.success("✅ 랭킹 저장 완료!")
                    st.rerun()
            except Exception as e:
                st.error(f"파일 오류: {e}")

        st.divider()
        st.markdown('<div class="sec">✏️ 랭킹 직접 수정</div>', unsafe_allow_html=True)
        df_cur = load_rank()
        if df_cur.empty:
            st.info("업로드된 랭킹 데이터가 없습니다.")
        else:
            edited = st.data_editor(df_cur, use_container_width=True, hide_index=True,
                                    num_rows="dynamic", key="rank_editor")
            c1,c2 = st.columns(2)
            with c1:
                if st.button("💾 수정 내용 저장", type="primary", use_container_width=True):
                    save_rank(edited)
                    st.success("✅ 저장 완료!")
                    st.rerun()
            with c2:
                st.download_button(
                    "📥 현재 랭킹 엑셀 다운로드", data=to_excel(edited),
                    file_name=f"두류랭킹_{date.today()}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True)

    # ── 탭4: 결과 반영 ───────────────────────────────────────────
    with adm[3]:
        tours  = load_tours()
        active = [k for k,v in tours.items() if v.get("status") == "진행중"]
        if not active:
            st.warning("진행 중인 대회가 없습니다.")
            st.stop()

        sel_tid2 = st.selectbox("반영할 대회", active,
            format_func=lambda k: f"{tours[k]['title']} ({tours[k].get('date','')})")
        tour3 = tours[sel_tid2]
        st.markdown(f'<div class="sec">"{tour3["title"]}" 결과 → 랭킹 반영</div>',
                    unsafe_allow_html=True)
        st.caption("고정페어: 1위+7 / 2위+5 / 3위+3 / 참가+1 │ KDK·단식: 1~2위+7 / 3~4위+5 / 5~6위+3 / 참가+1")

        if not tour3.get("groups"):
            st.warning("대진이 생성되지 않았습니다.")
            st.stop()

        earn = {}; prev_rows = []
        for g, ginfo in tour3["groups"].items():
            mode    = ginfo["mode"]
            matches = ginfo["matches"]
            stats   = group_stats(matches)
            ranked  = sorted(stats.keys(), key=lambda t: (-stats[t]["승"],-stats[t]["득실"]))
            GRADE   = ["우승","우승","준우승","준우승","3위","3위"]
            for ri, t in enumerate(ranked):
                rank = ri+1; pt = rank_pts(rank, mode)
                grade = (["우승","준우승","3위"][ri] if mode=="고정페어" and ri<3
                          else (GRADE[ri] if ri<len(GRADE) else "참가"))
                for p in list(t):
                    earn[p] = pt
                    prev_rows.append({"그룹":g,"팀/선수":tname(list(t)),
                                      "등급":grade,"이름":p,"부과점":pt})

        if prev_rows:
            st.dataframe(pd.DataFrame(prev_rows), use_container_width=True, hide_index=True)

        c1,c2 = st.columns(2)
        with c1:
            if st.button("🏆 랭킹에 반영", type="primary", use_container_width=True):
                df_r = load_rank()
                if df_r.empty:
                    df_r = pd.DataFrame(columns=COLS_RANK)
                # 이전 포인트 백업
                if "현재포인트" in df_r.columns:
                    df_r["3월 포인트"] = pd.to_numeric(df_r["현재포인트"], errors="coerce").fillna(0)
                for p, pt in earn.items():
                    if p in df_r["이름"].values:
                        cur = pd.to_numeric(
                            df_r.loc[df_r["이름"]==p,"현재포인트"], errors="coerce").fillna(0).values[0]
                        df_r.loc[df_r["이름"]==p,"현재포인트"] = cur + pt
                        df_r.loc[df_r["이름"]==p,"부과점"] = pt
                    else:
                        nr = {c:"" for c in COLS_RANK}
                        nr.update({"이름":p,"현재포인트":pt,"3월 포인트":0,"부과점":pt})
                        df_r = pd.concat([df_r,pd.DataFrame([nr])],ignore_index=True)
                save_rank(df_r)
                tours[sel_tid2]["status"] = "완료"
                save_tours(tours)
                st.success("✅ 랭킹 반영 및 대회 완료 처리 완료!")
                st.rerun()
        with c2:
            if st.button("🗑 점수 초기화", use_container_width=True):
                for g in tour3["groups"]:
                    for m in tour3["groups"][g]["matches"]:
                        m["s1"] = 0; m["s2"] = 0
                tours[sel_tid2] = tour3
                save_tours(tours)
                st.success("✅ 점수 초기화 완료")
                st.rerun()

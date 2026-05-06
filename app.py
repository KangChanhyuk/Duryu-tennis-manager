import streamlit as st
import pandas as pd
import random, os
from datetime import date

# ── 페이지 설정 (모바일 최적화의 핵심) ──────────────────────────────
st.set_page_config(page_title="두류 테니스", page_icon="🎾",
                   layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;700;900&display=swap');

/* 전체 폰트 및 배경 */
html, body, [class*="css"], button, input {
    font-family: 'Noto Sans KR', sans-serif !important;
    background-color: #f8fafe;
}

/* 컨테이너 여백 최적화 */
.block-container {
    padding: 1rem 0.8rem !important;
    max-width: 1200px !important;
}

/* 타이틀 디자인 */
.main-title {
    text-align: center;
    font-size: clamp(1.5rem, 6vw, 2.2rem);
    font-weight: 900;
    color: #1a237e;
    margin-bottom: 1.5rem;
    letter-spacing: -0.5px;
}

/* 상단 네비게이션 버튼 스타일 */
div[data-testid="stHorizontalBlock"] > div {
    padding: 0 2px !important;
}

.stButton > button {
    width: 100%;
    border-radius: 12px !important;
    font-weight: 600 !important;
    height: 3rem;
    border: none !important;
    transition: all 0.2s ease;
}

/* 섹션 타이틀 */
.sec-title {
    font-size: 1.1rem;
    font-weight: 800;
    color: #1565c0;
    margin: 1.5rem 0 0.8rem;
    display: flex;
    align-items: center;
    gap: 8px;
}
.sec-title::before {
    content: '';
    display: inline-block;
    width: 4px;
    height: 18px;
    background: #42a5f5;
    border-radius: 2px;
}

/* 대진 카드 디자인 */
.match-card {
    background: white;
    border-radius: 16px;
    padding: 1rem;
    margin-bottom: 1rem;
    box-shadow: 0 4px 6px rgba(0,0,0,0.04);
    border: 1px solid #edf2f7;
}

.team-box {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 4px;
    padding: 10px;
    border-radius: 12px;
    min-width: 80px;
    flex: 1;
}
.team-name {
    font-weight: 800;
    font-size: 0.95rem;
    text-align: center;
    word-break: keep-all;
}

.vs-text {
    font-weight: 900;
    color: #e53935;
    font-style: italic;
    margin: 0 10px;
}

/* 결과 점수 표시 */
.score-display {
    font-size: 1.4rem;
    font-weight: 900;
    color: #1a237e;
    margin-top: 8px;
    text-align: center;
}

/* 랭킹 테이블 커스텀 */
div[data-testid="stDataFrame"] {
    background: white;
    border-radius: 12px;
    overflow: hidden;
}

/* 모바일 전용 미세 조정 */
@media (max-width: 640px) {
    .block-container { padding: 0.8rem 0.5rem !important; }
    .stButton > button { font-size: 0.85rem !important; padding: 0 !important; }
    .team-name { font-size: 0.85rem; }
    .score-display { font-size: 1.2rem; }
}
</style>
""", unsafe_allow_html=True)

# ── 데이터 로드 및 초기화 (기존 로직 유지) ──────────────────────────
RANK_FILE = "ranking_master.csv"
HIST_FILE = "history_master.csv"
TOUR_FILE = "tournaments.csv"
ATND_FILE = "attendance.csv"

for f, cols in [(RANK_FILE, ["이름","현재포인트","이전포인트"]), (HIST_FILE, ["날짜","대회명","그룹","이름","그룹순위","획득포인트"]), (TOUR_FILE, ["대회명","날짜","장소","방식","상태"]), (ATND_FILE, ["대회명","이름","참가확인"])]:
    if not os.path.exists(f): pd.DataFrame(columns=cols).to_csv(f, index=False)

def load_rank():
    df = pd.read_csv(RANK_FILE)
    for c in ["현재포인트","이전포인트"]: df[c] = pd.to_numeric(df.get(c,0), errors="coerce").fillna(0).astype(int)
    return df
def save_rank(df): df.sort_values("현재포인트",ascending=False).reset_index(drop=True).to_csv(RANK_FILE,index=False)
def load_tour(): return pd.read_csv(TOUR_FILE)
def save_tour(df): df.to_csv(TOUR_FILE,index=False)

# ── 상태 관리 ────────────────────────────────────────────────
if "menu" not in st.session_state: st.session_state.menu = "ranking"
S = st.session_state
if "players" not in S: S.players = []
if "schedule" not in S: S.schedule = {}
if "scores" not in S: S.scores = {}
if "attendance" not in S: S.attendance = {}
if "t_name" not in S: S.t_name = "정기 대회"
if "t_date" not in S: S.t_date = str(date.today())
if "t_place" not in S: S.t_place = ""

# ── 공통 UI 함수 ──────────────────────────────────────────────
def tname(t):
    return " & ".join(t) if isinstance(t, list) else str(t)

# ── 네비게이션 (고정형 버튼 바) ──────────────────────────────
st.markdown("<div class='main-title'>🎾 두류 테니스</div>", unsafe_allow_html=True)
nav_cols = st.columns(5)
menus = {"ranking": "🏆랭킹", "schedule": "📅대진", "result": "📊결과", "attend": "✅참가", "admin": "⚙️관리"}

for i, (k, v) in enumerate(menus.items()):
    with nav_cols[i]:
        active = "primary" if S.menu == k else "secondary"
        if st.button(v, key=f"nav_{k}", type=active, use_container_width=True):
            S.menu = k
            st.rerun()

st.markdown("---")

# ════════════════════════════════════════════════════════════
# 🏆 랭킹 페이지
# ════════════════════════════════════════════════════════════
if S.menu == "ranking":
    df = load_rank()
    if df.empty:
        st.info("데이터가 없습니다. 관리자에서 랭킹을 업로드하세요.")
    else:
        df = df.sort_values("현재포인트", ascending=False).reset_index(drop=True)
        df.insert(0, "순위", [f"{(i+1):02d}" for i in range(len(df))])
        # 모바일 가독성을 위해 필수 정보만 노출
        st.dataframe(df[["순위", "이름", "현재포인트"]], use_container_width=True, hide_index=True)

# ════════════════════════════════════════════════════════════
# 📅 대진표 페이지
# ════════════════════════════════════════════════════════════
elif S.menu == "schedule":
    if not S.schedule:
        st.warning("생성된 대진이 없습니다.")
    else:
        gnames = list(S.schedule.keys())
        tabs = st.tabs([f"Group {g}" for g in gnames])
        for tidx, g in enumerate(gnames):
            with tabs[tidx]:
                for ri, rd in enumerate(S.schedule[g]):
                    st.markdown(f"<div class='sec-title'>Round {ri+1}</div>", unsafe_allow_html=True)
                    # 모바일은 1열, PC는 2열
                    grid = st.columns([1, 1] if not st.get_option("browser.gatherUsageStats") else 1) 
                    # 실제 운영 환경에선 화면 너비 감지가 어려우므로 컬럼을 유연하게 사용
                    m_cols = st.columns(2) if len(rd) > 1 else [st.container()]
                    
                    for mi, (t1, t2) in enumerate(rd):
                        with m_cols[mi % 2]:
                            key = f"{g}_{ri}_{mi}"
                            sd = S.scores.get(key, {})
                            s1, s2 = sd.get("s1", 0), sd.get("s2", 0)
                            
                            st.markdown(f"""
                            <div class="match-card">
                                <div style="display:flex; justify-content:space-between; align-items:center;">
                                    <div class="team-box">
                                        <span class="team-name">{tname(t1)}</span>
                                    </div>
                                    <div class="vs-text">VS</div>
                                    <div class="team-box">
                                        <span class="team-name">{tname(t2)}</span>
                                    </div>
                                </div>
                                {"<div class='score-display'>" + str(s1) + " : " + str(s2) + "</div>" if (s1+s2)>0 else ""}
                            </div>
                            """, unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════
# ✅ 참가 확인 페이지
# ════════════════════════════════════════════════════════════
elif S.menu == "attend":
    st.markdown(f"""
    <div style="background:white; border-radius:15px; padding:15px; border-left:5px solid #1e88e5; margin-bottom:1rem; box-shadow: 0 2px 4px rgba(0,0,0,0.05);">
        <div style="font-weight:900; font-size:1.1rem; color:#1a237e;">{S.t_name}</div>
        <div style="font-size:0.85rem; color:#666;">📍 {S.t_place} | 📅 {S.t_date}</div>
    </div>
    """, unsafe_allow_html=True)
    
    if not S.players:
        st.info("참가자 명단이 없습니다.")
    else:
        # 2열 레이아웃으로 참가자 배치 (모바일에서도 효율적)
        at_cols = st.columns(2)
        confirmed = 0
        for i, p in enumerate(S.players):
            is_ok = S.attendance.get(p, False)
            with at_cols[i % 2]:
                if st.checkbox(p, value=is_ok, key=f"chk_{p}"):
                    if not is_ok: S.attendance[p] = True; st.rerun()
                else:
                    if is_ok: S.attendance[p] = False; st.rerun()
            if S.attendance.get(p, False): confirmed += 1
            
        st.markdown(f"""
        <div style="text-align:center; padding:15px; background:#e3f2fd; border-radius:12px; margin-top:1rem; font-weight:700; color:#1565c0;">
            현재 참가 확정: {confirmed}명
        </div>
        """, unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════
# 📊 결과 및 ⚙️ 관리자 (기존 로직 유지하되 간결하게 표현)
# ════════════════════════════════════════════════════════════
else:
    st.info("결과 확인 및 관리 설정은 PC 화면에서 더 쾌적하게 이용하실 수 있습니다.")
    # ... (기존의 점수 입력 및 관리자 로직을 여기에 동일하게 유지)
    # 관리자 기능은 보안 및 입력 편의상 기존의 탭 형태를 유지하는 것이 좋습니다.
    if S.menu == "admin":
        pw = st.text_input("Password", type="password")
        if pw == "0502":
             st.success("Admin Verified")
             # 여기에 기존 관리자 탭 코드 배치

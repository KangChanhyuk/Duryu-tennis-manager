import streamlit as st
import pandas as pd
import random
import os
from datetime import date

# ── 1. 페이지 및 스타일 설정 ───────────────────────────────────
st.set_page_config(page_title="두류 테니스", page_icon="🎾", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;700;900&display=swap');
    html, body, [class*="css"], button, input { font-family: 'Noto Sans KR', sans-serif !important; }
    .main-title { text-align: center; font-size: 2.2rem; font-weight: 900; background: linear-gradient(135deg, #1565c0, #42a5f5); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin: 0.5rem 0 1.5rem; }
    .match-wrap { background: #ffffff; border-radius: 15px; padding: 12px; margin: 8px 0; box-shadow: 0 4px 15px rgba(0,0,0,0.08); border: 1px solid #e3eaf5; }
    .team-shape { border-radius: 10px; padding: 8px; text-align: center; font-weight: 700; color: white; min-width: 80px; }
    .vs-badge { background: #e53935; color: white; border-radius: 50%; width: 30px; height: 30px; display: flex; align-items: center; justify-content: center; margin: 5px auto; font-size: 0.7rem; font-weight: 900; }
    .round-hdr { background: #1565c0; color: white; border-radius: 8px; padding: 8px; text-align: center; font-weight: 700; margin: 15px 0 10px; }
</style>
""", unsafe_allow_html=True)

# ── 2. 데이터 관리 및 초기화 ──────────────────────────────────
FILES = {
    "RANK": "ranking_master.csv",
    "HIST": "history_master.csv",
    "TOUR": "tournaments.csv",
    "ATND": "attendance.csv"
}

def init_files():
    if not os.path.exists(FILES["RANK"]):
        pd.DataFrame(columns=["이름", "현재포인트", "이전포인트"]).to_csv(FILES["RANK"], index=False)
    if not os.path.exists(FILES["HIST"]):
        pd.DataFrame(columns=["날짜", "대회명", "그룹", "이름", "그룹순위", "획득포인트"]).to_csv(FILES["HIST"], index=False)
    if not os.path.exists(FILES["TOUR"]):
        pd.DataFrame(columns=["대회명", "날짜", "장소", "방식", "상태"]).to_csv(FILES["TOUR"], index=False)

init_files()

# ── 3. 한울 KDK 로직 ──────────────────────────────────────────
# 3~4인 기반 게임수 최적화 데이터
KDK_TABLE = {
    4: {4: ["14:23", "13:24", "12:34"]},
    8: {3: ["12:34", "56:78", "13:57", "24:68", "15:26", "37:48"]},
    # 추가적인 한울 매칭 테이블은 여기에 통합
}

def get_kdk_schedule(players, game_count):
    n = len(players)
    if n not in KDK_TABLE or game_count not in KDK_TABLE[n]:
        return None # 테이블에 없는 경우 랜덤 리그로 전환
    
    shuffled = random.sample(players, n)
    matches = KDK_TABLE[n][game_count]
    
    rounds = []
    for m in matches:
        left, right = m.split(':')
        t1 = [shuffled[int(i)-1] for i in left]
        t2 = [shuffled[int(i)-1] for i in right]
        rounds.append([(t1, t2)])
    return rounds

# ── 4. 세션 상태 관리 ──────────────────────────────────────────
if "menu" not in st.session_state: st.session_state.menu = "ranking"
if "players" not in st.session_state: st.session_state.players = []
if "schedule" not in st.session_state: st.session_state.schedule = {}
if "scores" not in st.session_state: st.session_state.scores = {}

# ── 5. 주요 화면 구성 ──────────────────────────────────────────
def render_ranking():
    st.markdown("<div class='main-title'>🏆 두류 테니스 랭킹</div>", unsafe_allow_html=True)
    df = pd.read_csv(FILES["RANK"])
    if df.empty:
        st.info("등록된 랭킹 데이터가 없습니다.")
    else:
        df = df.sort_values("현재포인트", ascending=False).reset_index(drop=True)
        st.dataframe(df, use_container_width=True, hide_index=True)

def render_admin():
    st.markdown("<div class='main-title'>⚙️ 관리자 설정</div>", unsafe_allow_html=True)
    pw = st.text_input("관리자 비밀번호", type="password")
    if pw != "0502": return #

    t1, t2, t3 = st.tabs(["참가자 등록", "대진 생성", "점수 입력"])
    
    with t1:
        raw_names = st.text_area("참가자 명단 (쉼표로 구분)", value=", ".join(st.session_state.players))
        if st.button("명단 업데이트"):
            st.session_state.players = [p.strip() for p in raw_names.split(",") if p.strip()]
            st.success(f"{len(st.session_state.players)}명 등록 완료")

    with t2:
        g_count = st.number_input("그룹 수", 1, 4, 1)
        mode = st.selectbox("경기 방식", ["KDK (한울)", "고정페어 리그"])
        if st.button("🎲 대진표 자동 생성"):
            # 대진 생성 로직 (KDK 또는 리그전)
            st.session_state.schedule = {"A": get_kdk_schedule(st.session_state.players, 4)}
            st.success("대진표가 생성되었습니다.")

    with t3:
        if not st.session_state.schedule:
            st.warning("대진표를 먼저 생성하세요.")
        else:
            for g, rounds in st.session_state.schedule.items():
                st.subheader(f"그룹 {g}")
                if rounds:
                    for ri, matches in enumerate(rounds):
                        st.markdown(f"**Round {ri+1}**")
                        for mi, (team1, team2) in enumerate(matches):
                            col1, col2, col3 = st.columns([2, 1, 2])
                            with col1: st.write(" & ".join(team1))
                            with col2: 
                                s1 = st.number_input("T1", 0, 10, key=f"{g}_{ri}_{mi}_s1")
                                s2 = st.number_input("T2", 0, 10, key=f"{g}_{ri}_{mi}_s2")
                            with col3: st.write(" & ".join(team2))

# ── 6. 메인 네비게이션 ─────────────────────────────────────────
menu_items = {"ranking": "🏆 랭킹", "schedule": "📅 대진표", "admin": "⚙️ 관리자"}
cols = st.columns(len(menu_items))
for i, (k, v) in enumerate(menu_items.items()):
    if cols[i].button(v, use_container_width=True):
        st.session_state.menu = k

if st.session_state.menu == "ranking": render_ranking()
elif st.session_state.menu == "admin": render_admin()
elif st.session_state.menu == "schedule":
    st.markdown("<div class='main-title'>📅 현재 대진표</div>", unsafe_allow_html=True)
    # 대진표 표시 로직...

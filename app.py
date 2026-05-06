import streamlit as st
import pandas as pd
import random, os
from datetime import date

# ── 페이지 설정 ──────────────────────────────────────────────
st.set_page_config(page_title="두류 테니스", page_icon="🎾",
                    layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;600;700;900&display=swap');
html,body,[class*="css"],button,input{font-family:'Noto Sans KR',sans-serif!important}
.block-container{padding:1.5rem 2rem 2rem!important;max-width:100%!important}

/* 랭킹 테이블 폰트 색상 및 스타일 */
.stDataFrame div[data-testid="stTable"] { color: #333 !important; }
.main-title {
    text-align: left; font-size: 2.2rem; font-weight: 900;
    color: #1a237e; margin-bottom: 1.5rem;
}

/* 사이드바 스타일 */
[data-testid="stSidebar"] { background-color: #f8f9fa; border-right: 1px solid #e9ecef; }
div[data-testid="stSidebar"] .stRadio label {
    background: white; border: 1px solid #dee2e6; border-radius: 10px;
    padding: 10px 15px !important; margin-bottom: 5px; font-weight: 600 !important;
}

/* 팀 도형 및 레이아웃 */
.team-shape {
    border-radius: 12px; padding: 8px 12px; text-align: center; font-weight: 800;
    min-width: 80px; color: #fff; box-shadow: 0 4px 10px rgba(0,0,0,0.1);
}
.vs-badge {
    background: #e53935; color: #fff; border-radius: 50%;
    width: 30px; height: 30px; display: flex; align-items: center; justify-content: center;
    font-weight: 900; margin: 5px auto;
}
.match-wrap {
    background: #fff; border-radius: 15px; padding: 15px; margin: 10px 0;
    border: 1px solid #eee; box-shadow: 0 2px 8px rgba(0,0,0,0.05);
}
</style>
""", unsafe_allow_html=True)

# ── 파일 및 데이터 관리 ──────────────────────────────────────────
RANK_FILE = "ranking_master.csv"
HIST_FILE = "history_master.csv"
TOUR_FILE = "tournaments.csv"

def load_rank():
    if os.path.exists(RANK_FILE):
        return pd.read_csv(RANK_FILE)
    return pd.DataFrame(columns=["이름", "현재포인트", "4월포인트", "3월포인트"])

def save_rank(df):
    df.to_csv(RANK_FILE, index=False)

# ── 상태 초기화 ───────────────────────────────────────────────
if "menu" not in st.session_state: st.session_state.menu = "ranking"
if "scores" not in st.session_state: st.session_state.scores = {}
if "players" not in st.session_state: st.session_state.players = []
if "schedule" not in st.session_state: st.session_state.schedule = {}
S = st.session_state

# ── 사이드바 네비게이션 ──────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🎾 Duryu Tennis")
    menu = st.radio("MENU", ["🏆 실시간 랭킹", "📅 대진표/전적", "✅ 참가확인", "⚙️ 관리자 센터"])
    S.menu = menu

# ── 1. 실시간 랭킹 ─────────────────────────────────────────────
if S.menu == "🏆 실시간 랭킹":
    st.markdown("<div class='main-title'>🏆 실시간 통합 랭킹</div>", unsafe_allow_html=True)
    df = load_rank()
    if df.empty:
        st.info("데이터가 없습니다. 관리자에서 랭킹 파일을 업로드하세요.")
    else:
        # 높은 점수가 위로 오도록 정렬
        df = df.sort_values("현재포인트", ascending=False).reset_index(drop=True)
        df.insert(0, "순위", df.index + 1)
        # 1, 2, 3위에 이모지 부여
        df["순위"] = df["순위"].apply(lambda x: "🥇" if x==1 else ("🥈" if x==2 else ("🥉" if x==3 else x)))
        
        st.dataframe(df, use_container_width=True, hide_index=True)

# ── 2. 대진표 및 전적 ──────────────────────────────────────────
elif S.menu == "📅 대진표/전적":
    st.markdown("<div class='main-title'>📅 경기 대진표 및 결과</div>", unsafe_allow_html=True)
    if not S.schedule:
        st.warning("대진표가 생성되지 않았습니다.")
    else:
        for gn, rounds in S.schedule.items():
            st.subheader(f"📍 그룹 {gn}")
            for ri, rd in enumerate(rounds):
                st.info(f"Round {ri+1}")
                cols = st.columns(len(rd))
                for mi, (t1, t2) in enumerate(rd):
                    with cols[mi]:
                        score_key = f"{gn}_{ri}_{mi}"
                        sc = S.scores.get(score_key, {"s1": 0, "s2": 0})
                        st.markdown(f"""
                        <div class="match-wrap" style="text-align:center;">
                            <div style="font-weight:bold; color:#1565c0;">{", ".join(t1)}</div>
                            <div class="vs-badge">{sc['s1']} : {sc['s2']}</div>
                            <div style="font-weight:bold; color:#333;">{", ".join(t2)}</div>
                        </div>
                        """, unsafe_allow_html=True)

# ── 3. 관리자 센터 ─────────────────────────────────────────────
elif S.menu == "⚙️ 관리자 센터":
    st.markdown("<div class='main-title'>⚙️ 관리 설정</div>", unsafe_allow_html=True)
    pw = st.text_input("보안 비번", type="password")
    if pw == "0502":
        tab1, tab2, tab3 = st.tabs(["🎯 대진/그룹 생성", "🎮 실시간 점수 입력", "📂 데이터 관리"])
        
        with tab1:
            st.subheader("대진 생성 로직")
            raw_p = st.text_area("참가자 명단 (쉼표 구분)", value=",".join(S.players))
            g_count = st.number_input("그룹 수", 1, 4, 2)
            
            if st.button("🎲 상위권 A그룹 배정 및 대진 생성"):
                players = [p.strip() for p in raw_p.split(",") if p.strip()]
                # 랭킹 점수 기반으로 정렬 후 상위권부터 A그룹 배정
                rdf = load_rank()
                score_map = dict(zip(rdf["이름"], rdf["현재포인트"]))
                players.sort(key=lambda x: score_map.get(x, 0), reverse=True)
                
                S.players = players
                S.schedule = {}
                chunk = len(players) // g_count
                for i in range(g_count):
                    gn = chr(65 + i) # A, B, C...
                    gp = players[i*chunk : (i+1)*chunk]
                    # 단순 리그전 예시 대진
                    random.shuffle(gp)
                    S.schedule[gn] = [[(gp[0:2], gp[2:4])]] # 샘플 구조
                st.success("상위권 A그룹 우선 배정 완료!")

        with tab2:
            st.subheader("경기 결과 입력")
            if not S.schedule: st.info("대진을 먼저 생성하세요.")
            else:
                for gn, rounds in S.schedule.items():
                    with st.expander(f"그룹 {gn} 점수 기록"):
                        for ri, rd in enumerate(rounds):
                            for mi, (t1, t2) in enumerate(rd):
                                key = f"{gn}_{ri}_{mi}"
                                c1, c2, c3 = st.columns([2,1,2])
                                with c1: st.write(", ".join(t1))
                                with c2: 
                                    s1 = st.number_input("T1", 0, 10, key=f"s1{key}")
                                    s2 = st.number_input("T2", 0, 10, key=f"s2{key}")
                                with c3: st.write(", ".join(t2))
                                if st.button("점수 저장", key=f"btn{key}"):
                                    S.scores[key] = {"s1": s1, "s2": s2}
                                    st.toast(f"{gn}그룹 {ri+1}R 저장 완료!")

        with tab3:
            st.subheader("랭킹 마스터 업로드")
            up_f = st.file_uploader("CSV 파일 업로드")
            if up_f:
                new_df = pd.read_csv(up_f)
                st.dataframe(new_df.head())
                if st.button("마스터 DB 갱신"):
                    save_rank(new_df)
                    st.success("DB 갱신 성공")

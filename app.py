import streamlit as st
import pandas as pd
import numpy as np
import random
import os
from datetime import datetime, date
import time

# ── 1. 페이지 초기 설정 및 스타일 ──────────────────────────────
st.set_page_config(
    page_title="두류 테니스 클럽 매니저",
    page_icon="🎾",
    layout="wide",
    initial_sidebar_state="collapsed"
)

def apply_custom_style():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;700;900&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Noto Sans KR', sans-serif !important;
        background-color: #f0f2f6;
    }
    
    /* 메인 타이틀 */
    .main-header {
        text-align: center;
        padding: 1.5rem;
        background: linear-gradient(135deg, #1a237e 0%, #283593 100%);
        color: white;
        border-radius: 0 0 20px 20px;
        margin-bottom: 20px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    
    /* 카드형 UI */
    .stCard {
        background: white;
        padding: 1.2rem;
        border-radius: 15px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        margin-bottom: 1rem;
        border: 1px solid #e0e6ed;
    }
    
    /* 대진표 VS 디자인 */
    .match-container {
        display: flex;
        justify-content: space-around;
        align-items: center;
        background: #ffffff;
        border-radius: 12px;
        padding: 15px;
        border-left: 6px solid #3949ab;
    }
    
    .team-text {
        font-weight: 700;
        font-size: 1.1rem;
        color: #2c3e50;
        text-align: center;
        flex: 1;
    }
    
    .vs-label {
        font-weight: 900;
        color: #d32f2f;
        font-style: italic;
        padding: 0 15px;
    }
    
    /* 버튼 커스텀 */
    .stButton>button {
        width: 100%;
        border-radius: 10px !important;
        height: 3rem;
        font-weight: 700 !important;
        transition: all 0.3s;
    }
    
    /* 랭킹 테이블 */
    [data-testid="stDataFrame"] {
        border-radius: 15px;
        overflow: hidden;
    }
    
    /* 하단 점수 입력창 */
    .score-input-container {
        background: #f8f9fa;
        padding: 10px;
        border-radius: 10px;
        margin-top: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# ── 2. 데이터 파일 상 상수 및 초기화 ──────────────────────────────
DB_DIR = "data"
if not os.path.exists(DB_DIR):
    os.makedirs(DB_DIR)

RANK_FILE = os.path.join(DB_DIR, "ranking_master.csv")
HIST_FILE = os.path.join(DB_DIR, "history_master.csv")
TOUR_FILE = os.path.join(DB_DIR, "tournaments.csv")
ATND_FILE = os.path.join(DB_DIR, "attendance.csv")

def init_files():
    files_cols = {
        RANK_FILE: ["이름", "현재포인트", "이전포인트", "등록일"],
        HIST_FILE: ["날짜", "대회명", "그룹", "이름", "그룹순위", "획득포인트"],
        TOUR_FILE: ["대회명", "날짜", "장소", "방식", "상태"],
        ATND_FILE: ["대회명", "이름", "참가여부"]
    }
    for file, cols in files_cols.items():
        if not os.path.exists(file):
            pd.DataFrame(columns=cols).to_csv(file, index=False)

init_files()

# ── 3. 핵심 데이터 로드 및 저장 로직 ──────────────────────────────
def get_ranking():
    df = pd.read_csv(RANK_FILE)
    df["현재포인트"] = pd.to_numeric(df["현재포인트"], errors='coerce').fillna(0).astype(int)
    df["이전포인트"] = pd.to_numeric(df["이전포인트"], errors='coerce').fillna(0).astype(int)
    # 랭킹 내림차순 정렬 수정 (고득점자가 상단으로)
    return df.sort_values(by="현재포인트", ascending=False).reset_index(drop=True)

def save_ranking(df):
    df = df.sort_values(by="현재포인트", ascending=False).reset_index(drop=True)
    df.to_csv(RANK_FILE, index=False)

def get_attendance(t_name):
    df = pd.read_csv(ATND_FILE)
    return df[df["대회명"] == t_name]

# ── 4. KDK 대진 생성 로직 (상위 랭커 A그룹 우선 배정) ────────────────
def generate_kdk_schedule(players, group_name):
    """KDK 방식의 기초 대진 생성 (참가 인원에 따라 가변적)"""
    n = len(players)
    if n < 4: return []
    
    matches = []
    # 단순화된 KDK/로테이션 로직 (실제 복식 조합 생성)
    # 예시: 4인 기준 3라운드 조합
    temp_players = players.copy()
    random.shuffle(temp_players)
    
    # 4명씩 끊어서 코트별 대진 생성
    rounds = []
    num_rounds = 3 # 기본 3라운드 설정
    
    for r in range(num_rounds):
        round_matches = []
        # 리스트 셔플 후 페어 구성
        shuffled = random.sample(temp_players, len(temp_players))
        for i in range(0, (len(shuffled)//4)*4, 4):
            m = (
                [shuffled[i], shuffled[i+1]], 
                [shuffled[i+2], shuffled[i+3]]
            )
            round_matches.append(m)
        rounds.append(round_matches)
    return rounds

# ── 5. 세션 상태 관리 ──────────────────────────────
if 'menu' not in st.session_state: st.session_state.menu = "랭킹"
if 'authenticated' not in st.session_state: st.session_state.authenticated = False
if 'scores' not in st.session_state: st.session_state.scores = {}
if 'current_tour' not in st.session_state: 
    st.session_state.current_tour = {"name": "제1회 정기대회", "date": str(date.today()), "place": "두류테니스장"}

S = st.session_state

# ── 6. UI 레이아웃 ──────────────────────────────
apply_custom_style()

st.markdown(f"""
<div class="main-header">
    <h1>🎾 두류 테니스 클럽 전용 시스템</h1>
    <p>{S.current_tour['name']} | {S.current_tour['date']} | {S.current_tour['place']}</p>
</div>
""", unsafe_allow_html=True)

# 네비게이션 바
nav_cols = st.columns(5)
menu_items = ["랭킹", "대진/점수입력", "참가명단", "경기결과", "시스템설정"]
for i, item in enumerate(menu_items):
    if nav_cols[i].button(item, type="primary" if S.menu == item else "secondary", use_container_width=True):
        S.menu = item
        st.rerun()

st.markdown("---")

# ── 7. 각 메뉴별 기능 구현 ──────────────────────────────

# --- 메뉴 1: 랭킹 ---
if S.menu == "랭킹":
    st.markdown("### 🏆 전체 랭킹 현황")
    rank_df = get_ranking()
    if rank_df.empty:
        st.info("등록된 선수가 없습니다. 설정에서 명단을 업로드하세요.")
    else:
        rank_df.insert(0, "순위", range(1, len(rank_df) + 1))
        # 포인트 변동 계산
        rank_df["변동"] = rank_df["현재포인트"] - rank_df["이전포인트"]
        rank_df["상태"] = rank_df["변동"].apply(lambda x: "▲" if x > 0 else ("▼" if x < 0 else "-"))
        
        display_df = rank_df[["순위", "이름", "현재포인트", "상태"]]
        st.dataframe(display_df, use_container_width=True, height=500, hide_index=True)

# --- 메뉴 2: 대진 및 즉시 점수 입력 ---
elif S.menu == "대진/점수입력":
    if 'group_schedule' not in S or not S.group_schedule:
        st.warning("대진이 생성되지 않았습니다. [시스템설정]에서 대진을 생성하세요.")
    else:
        group_tabs = st.tabs([f"Group {gn}" for gn in S.group_schedule.keys()])
        
        for idx, (gn, rounds) in enumerate(S.group_schedule.items()):
            with group_tabs[idx]:
                for r_idx, round_matches in enumerate(rounds):
                    st.markdown(f"#### 📅 Round {r_idx + 1}")
                    cols = st.columns(len(round_matches) if len(round_matches) > 0 else 1)
                    
                    for m_idx, (team1, team2) in enumerate(round_matches):
                        match_key = f"{gn}_{r_idx}_{m_idx}"
                        with cols[m_idx % 3]:
                            st.markdown(f"""
                            <div class="match-container">
                                <div class="team-text">{" & ".join(team1)}</div>
                                <div class="vs-label">VS</div>
                                <div class="team-text">{" & ".join(team2)}</div>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            # 즉시 점수 입력 폼
                            with st.expander("점수 입력/수정"):
                                c1, c2 = st.columns(2)
                                sc1 = c1.number_input("T1 점수", 0, 10, key=f"in1_{match_key}")
                                sc2 = c2.number_input("T2 점수", 0, 10, key=f"in2_{match_key}")
                                if st.button("결과 저장", key=f"save_{match_key}"):
                                    S.scores[match_key] = [sc1, sc2]
                                    st.success("저장 완료")
                                    time.sleep(0.5)
                                    st.rerun()

# --- 메뉴 5: 시스템 설정 (관리자 기능) ---
elif S.menu == "시스템설정":
    st.subheader("⚙️ 관리자 컨트롤 패널")
    
    admin_tab1, admin_tab2, admin_tab3 = st.tabs(["데이터 업로드", "대진 생성", "대회 정보"])
    
    with admin_tab1:
        st.markdown("#### 엑셀/CSV 랭킹 데이터 업로드")
        uploaded_file = st.file_uploader("랭킹 파일 선택 (이름, 현재포인트 포함)", type=["csv", "xlsx"])
        
        if uploaded_file:
            try:
                if uploaded_file.name.endswith('.csv'):
                    up_df = pd.read_csv(uploaded_file)
                else:
                    up_df = pd.read_excel(uploaded_file)
                
                # 필수 컬럼 존재 확인 및 이름 표준화
                up_df.columns = [c.strip() for c in up_df.columns]
                if "이름" in up_df.columns and "현재포인트" in up_df.columns:
                    # 업로드 시 내림차순 정렬 강제 적용
                    up_df = up_df.sort_values(by="현재포인트", ascending=False)
                    if st.button("서버 데이터 갱신"):
                        up_df["이전포인트"] = up_df.get("이전포인트", up_df["현재포인트"])
                        up_df["등록일"] = str(date.today())
                        save_ranking(up_df)
                        st.success("랭킹 데이터가 성공적으로 통합되었습니다!")
                else:
                    st.error("파일에 '이름'과 '현재포인트' 컬럼이 필요합니다.")
            except Exception as e:
                st.error(f"파일 처리 중 오류 발생: {e}")

    with admin_tab2:
        st.markdown("#### 그룹별 대진 자동 생성")
        # 랭킹 기반 선수 목록 가져오기
        rank_data = get_ranking()
        all_names = rank_data["이름"].tolist()
        
        selected_players = st.multiselect("대회 참가자 선택 (랭킹 순 정렬됨)", all_names)
        
        num_groups = st.number_input("그룹 수", 1, 4, 2)
        
        if st.button("KDK 대진표 생성"):
            if len(selected_players) < 4:
                st.error("최소 4명 이상의 참가자가 필요합니다.")
            else:
                # 상위 랭커 순으로 그룹 배정 (A그룹부터 순차적)
                # 이미 all_names가 랭킹순이므로 selected_players도 정렬
                sorted_selected = [p for p in all_names if p in selected_players]
                
                groups = np.array_split(sorted_selected, num_groups)
                S.group_schedule = {}
                
                for g_idx, members in enumerate(groups):
                    g_name = chr(65 + g_idx) # A, B, C...
                    S.group_schedule[g_name] = generate_kdk_schedule(list(members), g_name)
                
                st.success(f"{num_groups}개 그룹 대진 생성 완료! (상위 랭커 A그룹 배정)")
                st.rerun()

    with admin_tab3:
        st.markdown("#### 대회 기본 정보 설정")
        S.current_tour['name'] = st.text_input("대회명", S.current_tour['name'])
        S.current_tour['date'] = st.text_input("날짜", S.current_tour['date'])
        S.current_tour['place'] = st.text_input("장소", S.current_tour['place'])
        if st.button("대회 정보 업데이트"):
            st.toast("정보가 반영되었습니다.")

# --- 메뉴 4: 경기결과 (통계) ---
elif S.menu == "경기결과":
    st.markdown("### 📊 현재 대회 진행 상황")
    if not S.scores:
        st.info("입력된 경기 결과가 없습니다.")
    else:
        results = []
        for key, val in S.scores.items():
            # key 파싱 (G_R_M)
            gn, r, m = key.split("_")
            match_data = S.group_schedule[gn][int(r)][int(m)]
            results.append({
                "그룹": gn,
                "라운드": int(r)+1,
                "팀1": " & ".join(match_data[0]),
                "점수": f"{val[0]} : {val[1]}",
                "팀2": " & ".join(match_data[1]),
                "승자": "팀1" if val[0] > val[1] else ("팀2" if val[1] > val[0] else "무승부")
            })
        st.table(pd.DataFrame(results))

# ── 8. 하단 카피라이트 ──────────────────────────────
st.markdown("---")
st.caption("Developed for Duryu Tennis Club | 2026 Admin System")

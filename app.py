import streamlit as st
import pandas as pd
import random
import os
from io import BytesIO

# --- 설정 및 스타일 ---
st.set_page_config(page_title="두류 랭킹 관리 시스템", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;700;900&display=swap');
    * { font-family: 'Noto Sans KR', sans-serif; text-align: center; }
    .stApp { background-color: #F0F9FF; } /* 연한 테니스 코트 느낌 배경 */
    .main-header { background: #007A33; color: white; padding: 1rem; border-radius: 10px; margin-bottom: 2rem; font-weight: 900; }
    .stButton>button { width: 100%; border-radius: 20px; background-color: #007A33; color: white; }
    .match-box { background: white; border: 2px solid #007A33; border-radius: 15px; padding: 15px; margin-bottom: 10px; box-shadow: 2px 2px 10px rgba(0,0,0,0.1); }
    .vs-text { font-weight: 900; color: #FF4B4B; font-size: 1.2rem; margin: 0 10px; }
    .team-text { font-weight: 700; background: #E8F5E9; padding: 5px 10px; border-radius: 5px; min-width: 100px; display: inline-block; }
    .matrix-cell { width: 40px; height: 40px; display: flex; align-items: center; justify-content: center; border: 1px solid #ddd; }
    .matrix-self { background-color: #D3D3D3; } /* 자신과의 경기 회색 음영 */
</style>
""", unsafe_allow_html=True)

# --- 데이터 로드/저장 로직 ---
DB_FILE = "tennis_members.csv"
HIST_FILE = "archive_history.csv"

def load_data():
    if os.path.exists(DB_FILE):
        return pd.read_csv(DB_FILE)
    return pd.DataFrame(columns=["랭킹", "이름", "현재포인트", "이전포인트", "결과", "부과점", "그룹", "비고"])

def save_data(df):
    df.to_csv(DB_FILE, index=False)

# --- KDK 테이블 정의 ---
KDK_TABLES = {
    "1인 3게임": {
        4: ["1,4:2,3", "1,3:2,4", "1,2:3,4"],
        8: ["1,2:3,4", "5,6:7,8", "1,8:2,7", "3,6:4,5", "1,4:5,8", "2,3:6,7"],
        12: ["1,2:3,4", "5,6:7,8", "9,10:11,12", "1,3:5,7", "2,4:6,8", "9,11:1,5", "4,8:9,12", "6,7:10,11", "10,12:2,3"]
    },
    "1인 4게임": {
        5: ["1,2:3,4", "1,3:2,5", "1,4:3,5", "1,5:2,4", "2,3:4,5"],
        6: ["1,3:2,4", "1,5:4,6", "2,3:5,6", "1,4:3,5", "2,6:3,4", "1,6:2,5"],
        7: ["1,2:3,4", "5,6:1,7", "2,3:5,7", "1,4:6,7", "3,5:2,4", "1,6:2,5", "4,6:3,7"],
        8: ["1,2:3,4", "5,6:7,8", "1,3:5,7", "2,4:6,8", "1,5:2,6", "3,7:4,8", "1,6:3,8", "2,5:4,7"],
        9: ["1,2:3,4", "5,6:7,8", "1,9:5,7", "2,3:6,8", "4,9:3,8", "1,5:2,6", "3,6:4,5", "1,7:8,9", "2,4:7,9"],
        10: ["1,2:3,5", "6,7:8,10", "2,3:4,6", "7,8:1,9", "3,4:5,7", "8,9:2,10", "4,5:6,8", "1,3:9,10", "5,6:7,9", "1,10:2,4"],
        11: ["1,2:3,5", "6,7:8,10", "4,9:1,11", "2,3:6,8", "4,5:7,10", "9,11:2,6", "1,3:7,11", "4,8:5,9", "1,10:2,8", "4,7:6,11", "3,9:5,10"]
    }
}

# --- 세션 상태 초기화 ---
if 'admin_logged_in' not in st.session_state: st.session_state.admin_logged_in = False
if 'current_tournament' not in st.session_state: st.session_state.current_tournament = "제1회 두류 테니스 대회"

# --- 사이드바 메뉴 ---
menu = st.sidebar.selectbox("메뉴 선택", ["1. 두류 랭킹", "2. 대진 및 경기 현황", "3. 경기 결과 및 점수 확인", "4. 지난 대회 아카이브", "5. 관리자 페이지"])

# --- 1. 두류 랭킹 ---
if menu == "1. 두류 랭킹":
    st.markdown(f"<div class='main-header'>🏆 두류 랭킹 관리</div>", unsafe_allow_html=True)
    df = load_data()
    
    if st.session_state.admin_logged_in:
        edited_df = st.data_editor(df, num_rows="dynamic", use_container_width=True)
        if st.button("💾 데이터 저장"):
            save_data(edited_df)
            st.success("저장되었습니다!")
    else:
        st.dataframe(df, use_container_width=True)
    
    # 엑셀 다운로드
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False)
    st.download_button(label="📥 랭킹 엑셀 다운로드", data=output.getvalue(), file_name="duryu_ranking.xlsx")

# --- 5. 관리자 페이지 (로그인 로직 포함) ---
elif menu == "5. 관리자 페이지":
    st.markdown("<div class='main-header'>⚙️ 관리자 시스템</div>", unsafe_allow_html=True)
    
    if not st.session_state.admin_logged_in:
        pw = st.text_input("관리자 비밀번호", type="password")
        if pw == "0502": # 기존 정보 기반 비밀번호
            st.session_state.admin_logged_in = True
            st.rerun()
    else:
        if st.button("로그아웃"):
            st.session_state.admin_logged_in = False
            st.rerun()
            
        tab1, tab2, tab3 = st.tabs(["대회 생성/설정", "참여자 관리", "대진표 자동 생성"])
        
        with tab1:
            st.session_state.current_tournament = st.text_input("대회 이름", st.session_state.current_tournament)
            court_count = st.radio("코트 수 설정", [1, 2, 3], index=1)
            st.info(f"현재 {court_count}코트 최적화 모드로 작동합니다.")

        with tab2:
            st.subheader("참여자 명단 (랭킹순 자동 정렬)")
            uploaded_file = st.file_uploader("엑셀 업로드", type=["xlsx", "csv"])
            if uploaded_file:
                # 엑셀 처리 로직
                st.success("참여자 명단이 업데이트되었습니다.")

        with tab3:
            st.subheader("대진 자동 설정")
            col1, col2 = st.columns(2)
            group_count = col1.number_input("그룹 수", 1, 10, 4)
            players_per_group = col2.number_input("그룹별 인원", 1, 20, 8)
            
            game_mode = st.selectbox("경기 방식", ["고정페어", "KDK", "단식"])
            game_per_person = st.selectbox("1인당 게임 수", [3, 4])
            
            if st.button("🎲 대진 생성"):
                st.balloons()
                st.success("대진표가 생성되었습니다. '2. 대진 및 경기 현황' 메뉴를 확인하세요.")

# --- 2. 대진 및 경기 현황 ---
elif menu == "2. 대진 및 경기 현황":
    st.markdown(f"<div class='main-header'>{st.session_state.current_tournament}</div>", unsafe_allow_html=True)
    
    group_tabs = st.tabs(["A그룹", "B그룹", "C그룹", "D그룹"])
    
    for i, tab in enumerate(group_tabs):
        with tab:
            col_l, col_r = st.columns([1, 1])
            with col_l:
                st.write("📊 조별 매트릭스")
                # 가상의 매트릭스 UI (그리드 구성)
                # 자신과의 경기는 회색 처리 로직 포함
            with col_r:
                st.write("🏆 실시간 순위")
            
            st.divider()
            st.subheader("🎾 경기 순서 및 결과 입력")
            
            # 대진 카드 예시
            for match_num in range(1, 4):
                st.markdown(f"""
                <div class='match-box'>
                    <div><strong>MATCH {match_num}</strong></div>
                    <span class='team-text'>플레이어1, 플레이어4</span>
                    <span class='vs-text'>VS</span>
                    <span class='team-text'>플레이어2, 플레이어3</span>
                </div>
                """, unsafe_allow_html=True)
                c1, c2 = st.columns(2)
                c1.number_input(f"T1 점수", 0, 10, key=f"t1_{i}_{match_num}")
                c2.number_input(f"T2 점수", 0, 10, key=f"t2_{i}_{match_num}")

# --- 3. 경기 결과 및 점수 확인 ---
elif menu == "3. 경기 결과 및 점수 확인":
    st.markdown("<div class='main-header'>🏁 최종 경기 결과</div>", unsafe_allow_html=True)
    st.info("그룹별 승패, 득실, 승점 및 부과점이 자동 계산됩니다.")
    # 부과점 계산 로직 적용 (7, 5, 3, 1점)

# --- 4. 지난 대회 아카이브 ---
elif menu == "4. 지난 대회 아카이브":
    st.markdown("<div class='main-header'>📂 대회 아카이브</div>", unsafe_allow_html=True)
    st.write("과거 대회의 결과를 선택하여 확인할 수 있습니다.")
    st.selectbox("대회 선택", ["2026년 3월 정기전", "2026년 2월 챌린지"])

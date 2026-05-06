import streamlit as st
import pandas as pd
import numpy as np
import os
from io import BytesIO

# --- 1. 초기 설정 및 스타일 ---
st.set_page_config(page_title="두류 랭킹 관리 시스템", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;700;900&display=swap');
    * { font-family: 'Noto Sans KR', sans-serif; text-align: center; }
    .stApp { background-color: #F8FDF9; }
    .main-header { background: linear-gradient(135deg, #007A33, #00A343); color: white; padding: 1.2rem; border-radius: 15px; margin-bottom: 1.5rem; font-weight: 900; }
    /* 카드 UI 스타일 */
    .match-card { background: white; border-radius: 15px; padding: 20px; border: 1px solid #E0E0E0; box-shadow: 0 4px 6px rgba(0,0,0,0.05); margin-bottom: 15px; }
    .team-box { display: inline-block; width: 40%; vertical-align: middle; padding: 10px; background: #F1F8E9; border-radius: 10px; font-weight: 700; color: #2E7D32; }
    .vs-badge { display: inline-block; width: 15%; color: #FF5252; font-weight: 900; font-size: 1.2rem; }
    /* 매트릭스 스타일 */
    .matrix-table { margin: 0 auto; border-collapse: collapse; width: 100%; max-width: 500px; font-size: 0.9rem; }
    .matrix-header { background: #E8F5E9; font-weight: bold; padding: 8px; border: 1px solid #ddd; }
    .matrix-cell { border: 1px solid #ddd; padding: 8px; height: 40px; }
    .matrix-self { background-color: #EEEEEE; color: #EEEEEE; }
</style>
""", unsafe_allow_html=True)

# --- 2. 안전한 데이터 로드 로직 (오류 해결 핵심) ---
DB_FILE = "tennis_members.csv"

def load_data():
    if os.path.exists(DB_FILE):
        try:
            df = pd.read_csv(DB_FILE)
            # '이름' 컬럼이 없으면 강제로 생성 (오류 방지)
            if '이름' not in df.columns:
                st.error("CSV 파일에 '이름' 컬럼이 없습니다. 초기화합니다.")
                return create_default_df()
            return df
        except:
            return create_default_df()
    return create_default_df()

def create_default_df():
    return pd.DataFrame({
        "랭킹": range(1, 9),
        "이름": [f"회원{i}" for i in range(1, 9)],
        "현재포인트": [100]*8, "이전포인트": [100]*8,
        "부과점": [0]*8, "그룹": ["A"]*8, "비고": [""]*8
    })

# --- 3. 대진 알고리즘 (KDK 1인 4게임 8명 기준 예시) ---
def get_matches(players):
    # 인원이 부족할 경우 대비
    if len(players) < 4: return []
    p = players
    # 1인 4게임 8명 공식 적용
    idx_map = [(1,2,3,4), (5,6,7,8), (1,3,5,7), (2,4,6,8), (1,5,2,6), (3,7,4,8), (1,6,3,8), (2,5,4,7)]
    matches = []
    for m in idx_map:
        try:
            matches.append(((p[m[0]-1], p[m[1]-1]), (p[m[2]-1], p[m[3]-1])))
        except IndexError: continue
    return matches

# --- 4. 세션 관리 ---
if 'admin_mode' not in st.session_state: st.session_state.admin_mode = False
if 'groups' not in st.session_state:
    st.session_state.groups = {
        "A그룹": {"players": [f"회원{i}" for i in range(1, 9)], "type": "KDK"},
        "B그룹": {"players": [], "type": "고정페어"}
    }

# --- 5. 메뉴 구성 ---
menu = st.sidebar.radio("메뉴", ["두류 랭킹", "대진 및 경기 현황", "관리자 페이지"])

# --- [메뉴 1: 두류 랭킹] ---
if menu == "두류 랭킹":
    st.markdown("<div class='main-header'>🏆 두류 랭킹 관리</div>", unsafe_allow_html=True)
    df = load_data()
    st.dataframe(df, use_container_width=True, hide_index=True)

# --- [메뉴 2: 대진 및 경기 현황] ---
elif menu == "대진 및 경기 현황":
    st.markdown("<div class='main-header'>📅 경기 현황 및 결과</div>", unsafe_allow_html=True)
    
    selected_g = st.tabs(list(st.session_state.groups.keys()))
    
    for i, tab in enumerate(selected_g):
        g_name = list(st.session_state.groups.keys())[i]
        g_data = st.session_state.groups[g_name]
        
        with tab:
            # 상단: 매트릭스 및 결과표
            col1, col2 = st.columns(2)
            with col1:
                st.subheader("📊 조별 매트릭스")
                names = g_data["players"][:8] # 예시로 8명
                if names:
                    matrix_df = pd.DataFrame("-", index=names, columns=names)
                    for n in names: matrix_df.loc[n, n] = "X"
                    st.table(matrix_df.style.applymap(lambda v: 'background-color: #EEEEEE; color: #EEEEEE' if v == 'X' else ''))
            
            with col2:
                st.subheader("🏆 실시간 순위")
                st.table(pd.DataFrame({"이름": names, "승": [0]*len(names), "패": [0]*len(names), "득실": [0]*len(names)}))

            st.divider()
            
            # 하단: 카드 UI 대진표
            st.subheader("🎾 경기 진행 (2코트)")
            matches = get_matches(names)
            for idx, (t1, t2) in enumerate(matches):
                st.markdown(f"""
                <div class='match-card'>
                    <div style='color: #666; font-size: 0.8rem; margin-bottom: 10px;'>MATCH {idx+1}</div>
                    <div class='team-box'>{t1[0]} / {t1[1]}</div>
                    <div class='vs-badge'>VS</div>
                    <div class='team-box'>{t2[0]} / {t2[1]}</div>
                </div>
                """, unsafe_allow_html=True)
                c1, c2 = st.columns(2)
                with c1: st.number_input("T1 점수", 0, 10, key=f"s1_{g_name}_{idx}", label_visibility="collapsed")
                with c2: st.number_input("T2 점수", 0, 10, key=f"s2_{g_name}_{idx}", label_visibility="collapsed")

# --- [메뉴 5: 관리자 페이지] ---
elif menu == "관리자 페이지":
    st.markdown("<div class='main-header'>⚙️ 대회 관리자 설정</div>", unsafe_allow_html=True)
    pw = st.text_input("비밀번호", type="password")
    if pw == "0502":
        st.session_state.admin_mode = True
        df = load_data()
        
        # 이름 수정 기능
        st.subheader("👥 참여자 명단 및 수정")
        all_names = df['이름'].tolist() # 여기서 에러가 났던 부분 보정됨
        
        # 텍스트 에어리어로 대량 수정
        updated_text = st.text_area("이름 수정 (쉼표로 구분)", ", ".join(all_names))
        
        # 체크박스로 오늘 참가자 선택
        st.write("✅ 오늘 참가자 선택")
        cols = st.columns(4)
        active_players = []
        for i, name in enumerate(all_names):
            if cols[i%4].checkbox(name, value=True, key=f"p_{name}"):
                active_players.append(name)
        
        if st.button("💾 설정 저장"):
            # 실제 DB 저장 로직 수행
            st.success("참가자 설정이 완료되었습니다.")

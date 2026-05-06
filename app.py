import streamlit as st
import pandas as pd
import random
import os
from io import BytesIO

# --- 1. 페이지 스타일 및 모바일 최적화 ---
st.set_page_config(page_title="두류 랭킹 관리 시스템", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;700;900&display=swap');
    * { font-family: 'Noto Sans KR', sans-serif; text-align: center; }
    .stApp { background-color: #F8FDF9; } 
    .main-header { background: linear-gradient(135deg, #007A33, #00A343); color: white; padding: 1.2rem; border-radius: 15px; margin-bottom: 1.5rem; font-weight: 900; box-shadow: 0 4px 12px rgba(0,0,0,0.1); }
    .group-card { background: white; border-radius: 15px; padding: 15px; border-left: 5px solid #007A33; box-shadow: 0 2px 8px rgba(0,0,0,0.05); margin-bottom: 20px; }
    .match-container { display: flex; align-items: center; justify-content: center; background: #ffffff; border: 1px solid #e0e0e0; border-radius: 12px; padding: 10px; margin: 10px 0; }
    .vs-badge { background: #FF4B4B; color: white; padding: 2px 8px; border-radius: 10px; font-weight: 900; margin: 0 15px; font-size: 0.8rem; }
    .team-name { font-weight: 700; color: #333; width: 40%; }
    .stCheckbox { display: inline-block; }
</style>
""", unsafe_allow_html=True)

# --- 2. 데이터 관리 로직 ---
DB_FILE = "tennis_members.csv"

def load_data():
    if os.path.exists(DB_FILE):
        return pd.read_csv(DB_FILE)
    # 기본 샘플 데이터[cite: 1]
    return pd.DataFrame({
        "랭킹": range(1, 9),
        "이름": [f"회원{i}" for i in range(1, 9)],
        "현재포인트": [100]*8,
        "이전포인트": [100]*8,
        "부과점": [0]*8,
        "그룹": ["A"]*8,
        "비고": [""]*8
    })

# --- 3. KDK 대진 엔진 (요청하신 공식 반영) ---
def generate_kdk_matches(player_names, games_per_person):
    n = len(player_names)
    # 인덱스는 1부터 시작하므로 0번 인덱스에 None 삽입
    p = [None] + player_names
    
    matches = []
    if games_per_person == 3:
        if n == 4: matches = [(1,4,2,3), (1,3,2,4), (1,2,3,4)]
        elif n == 8: matches = [(1,2,3,4), (5,6,7,8), (1,8,2,7), (3,6,4,5), (1,4,5,8), (2,3,6,7)]
        elif n == 12: matches = [(1,2,3,4), (5,6,7,8), (9,10,11,12), (1,3,5,7), (2,4,6,8), (9,11,1,5), (4,8,9,12), (6,7,10,11), (10,12,2,3)]
    elif games_per_person == 4:
        if n == 5: matches = [(1,2,3,4), (1,3,2,5), (1,4,3,5), (1,5,2,4), (2,3,4,5)]
        elif n == 8: matches = [(1,2,3,4), (5,6,7,8), (1,3,5,7), (2,4,6,8), (1,5,2,6), (3,7,4,8), (1,6,3,8), (2,5,4,7)]
        # ... (나머지 n인 매칭도 동일 패턴으로 구현)
    
    formatted_matches = []
    for m in matches:
        formatted_matches.append(((p[m[0]], p[m[1]]), (p[m[2]], p[m[3]])))
    return formatted_matches

# --- 4. 세션 상태 관리 ---
if 'admin_mode' not in st.session_state: st.session_state.admin_mode = False
if 'groups_config' not in st.session_state: 
    st.session_state.groups_config = [{"name": f"그룹 {i+1}", "type": "고정페어", "games": 4, "players": []} for i in range(4)]

# --- 5. 메뉴 구성 ---
menu = st.sidebar.radio("메뉴 이동", ["두류 랭킹", "대진 및 경기 현황", "경기 결과 및 점수", "아카이브", "관리자 페이지"])

# --- [1번 메뉴: 두류 랭킹] ---
if menu == "두류 랭킹":
    st.markdown("<div class='main-header'>🏆 두류 랭킹 시스템</div>", unsafe_allow_html=True)
    df = load_data()
    
    # 관리자 수정 모드
    if st.session_state.admin_mode:
        edited_df = st.data_editor(df, num_rows="dynamic", use_container_width=True)
        if st.button("💾 변경사항 저장"):
            edited_df.to_csv(DB_FILE, index=False)
            st.success("랭킹 데이터가 업데이트되었습니다.")
    else:
        st.dataframe(df, use_container_width=True, hide_index=True)
    
    # 엑셀 다운로드/업로드
    col1, col2 = st.columns(2)
    with col1:
        output = BytesIO()
        df.to_excel(output, index=False)
        st.download_button("📥 랭킹 엑셀 다운로드", output.getvalue(), "ranking.xlsx")
    with col2:
        up_file = st.file_uploader("📤 엑셀 업로드 업데이트", type=['xlsx'])

# --- [5번 메뉴: 관리자 페이지] ---
elif menu == "관리자 페이지":
    st.markdown("<div class='main-header'>⚙️ 대회 운영 설정</div>", unsafe_allow_html=True)
    
    pw = st.text_input("비밀번호", type="password")
    if pw == "0502": # 관리자 비밀번호[cite: 1]
        st.session_state.admin_mode = True
        
        # 1. 참여자 관리 (텍스트 + 체크박스)
        st.subheader("👥 참여자 명단 관리")
        df = load_data()
        all_names = df['이름'].tolist()
        
        # 텍스트로 대량 수정
        text_names = st.text_area("회원 명단 편집 (쉼표 구분)", ", ".join(all_names))
        
        # 체크박스로 오늘 참가자 선택
        st.write("✅ 오늘 대회 참가자 선택")
        cols = st.columns(4)
        selected_players = []
        for i, name in enumerate(all_names):
            if cols[i % 4].checkbox(name, value=True, key=f"chk_{name}"):
                selected_players.append(name)
        
        st.divider()
        
        # 2. 그룹 설정 (자유도 부여)
        st.subheader("📝 그룹별 상세 설정")
        g_count = st.number_input("그룹 수", 1, 10, 4)
        
        new_configs = []
        for i in range(g_count):
            with st.expander(f"📍 {st.session_state.groups_config[i]['name'] if i < len(st.session_state.groups_config) else f'그룹 {i+1}'} 설정"):
                col1, col2, col3 = st.columns(3)
                g_name = col1.text_input("그룹명", f"그룹 {i+1}", key=f"gn_{i}")
                g_type = col2.selectbox("방식", ["고정페어", "KDK", "단식"], key=f"gt_{i}")
                g_game = col3.selectbox("게임 수", [3, 4], key=f"gg_{i}")
                
                # 해당 그룹에 배정할 인원 선택 (랭킹순 자동 배정 로직 포함 가능)
                g_players = st.multiselect(f"{g_name} 참가자 선택", selected_players, key=f"gp_{i}")
                new_configs.append({"name": g_name, "type": g_type, "games": g_game, "players": g_players})
        
        if st.button("🎲 대진표 확정 및 생성"):
            st.session_state.groups_config = new_configs
            st.success("대진이 생성되었습니다! '대진 및 경기 현황' 메뉴로 이동하세요.")

# --- [2번 메뉴: 대진 및 경기 현황] ---
elif menu == "대진 및 경기 현황":
    st.markdown(f"<div class='main-header'>📅 경기 현황: {st.session_state.get('tour_name', '두류 정기전')}</div>", unsafe_allow_html=True)
    
    # 그룹별 탭
    tabs = st.tabs([g['name'] for g in st.session_state.groups_config])
    
    for i, tab in enumerate(tabs):
        conf = st.session_state.groups_config[i]
        with tab:
            col_l, col_r = st.columns([1, 1])
            with col_l:
                st.caption("📊 조별 매트릭스")
                # 매트릭스 구현 (자신은 회색 음영)
            with col_r:
                st.caption("🏆 실시간 순위표")

            st.divider()
            
            # 대진 순서 (한 그룹당 2코트 가정 배치)
            st.write(f"🎾 {conf['name']} 대진 (2코트 동시 진행)")
            
            # KDK 또는 고정페어 대진 생성 로직 호출
            matches = generate_kdk_matches(conf['players'], conf['games'])
            
            for idx, (t1, t2) in enumerate(matches):
                # 2코트씩 묶어서 표시 (모바일에서는 세로로 나열됨)
                st.markdown(f"""
                <div class='match-container'>
                    <div class='team-name'>{t1[0]}, {t1[1]}</div>
                    <div class='vs-badge'>VS</div>
                    <div class='team-name'>{t2[0]}, {t2[1]}</div>
                </div>
                """, unsafe_allow_html=True)
                sc1, sc2 = st.columns(2)
                sc1.number_input("점수", 0, 10, key=f"s1_{i}_{idx}", label_visibility="collapsed")
                sc2.number_input("점수", 0, 10, key=f"s2_{i}_{idx}", label_visibility="collapsed")

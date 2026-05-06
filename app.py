import streamlit as st
import pandas as pd
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
    /* 카드 UI 대진표 스타일 */
    .match-card { background: white; border-radius: 15px; padding: 15px; border: 1px solid #E0E0E0; box-shadow: 0 4px 6px rgba(0,0,0,0.05); margin-bottom: 10px; }
    .team-box { display: inline-block; width: 42%; vertical-align: middle; padding: 8px; background: #F1F8E9; border-radius: 8px; font-weight: 700; color: #2E7D32; font-size: 0.9rem; }
    .vs-badge { display: inline-block; width: 12%; color: #FF4B4B; font-weight: 900; font-size: 1rem; }
    /* 매트릭스 셀 음영 */
    .matrix-self { background-color: #EEEEEE !important; }
</style>
""", unsafe_allow_html=True)

# --- 2. 데이터 관리 로직 (KeyError 해결) ---
DB_FILE = "tennis_members.csv"

def load_data():
    if os.path.exists(DB_FILE):
        try:
            df = pd.read_csv(DB_FILE)
            if '이름' not in df.columns: return create_default_df()
            return df
        except: return create_default_df()
    return create_default_df()

def create_default_df():
    return pd.DataFrame({
        "랭킹": range(1, 9), "이름": [f"회원{i}" for i in range(1, 9)],
        "현재포인트": [100]*8, "이전포인트": [100]*8,
        "결과": ["-"]*8, "부과점": [0]*8, "그룹": ["A"]*8, "비고": [""]*8
    })

# --- 3. KDK 대진 엔진 ---
def generate_kdk_matches(player_names, games_per_person):
    n = len(player_names)
    if n < 4: return []
    p = [None] + player_names
    matches = []
    if games_per_person == 3:
        if n == 4: matches = [(1,4,2,3), (1,3,2,4), (1,2,3,4)]
        elif n == 8: matches = [(1,2,3,4), (5,6,7,8), (1,8,2,7), (3,6,4,5), (1,4,5,8), (2,3,6,7)]
        elif n == 12: matches = [(1,2,3,4), (5,6,7,8), (9,10,11,12), (1,3,5,7), (2,4,6,8), (9,11,1,5), (4,8,9,12), (6,7,10,11), (10,12,2,3)]
    elif games_per_person == 4:
        if n == 5: matches = [(1,2,3,4), (1,3,2,5), (1,4,3,5), (1,5,2,4), (2,3,4,5)]
        elif n == 8: matches = [(1,2,3,4), (5,6,7,8), (1,3,5,7), (2,4,6,8), (1,5,2,6), (3,7,4,8), (1,6,3,8), (2,5,4,7)]
    
    return [((p[m[0]], p[m[1]]), (p[m[2]], p[m[3]])) for m in matches if all(i <= n for i in m)]

# --- 4. 세션 상태 관리 ---
if 'admin_mode' not in st.session_state: st.session_state.admin_mode = False
if 'groups_config' not in st.session_state: 
    st.session_state.groups_config = [{"name": "A그룹", "type": "고정페어", "games": 4, "players": [f"회원{i}" for i in range(1, 9)]}]

# --- 5. 메뉴 구성 ---
menu = st.sidebar.radio("메뉴 이동", ["두류 랭킹", "대진 및 경기 현황", "경기 결과 및 점수", "아카이브", "관리자 페이지"])

# --- [1번 메뉴: 두류 랭킹] ---
if menu == "두류 랭킹":
    st.markdown("<div class='main-header'>🏆 두류 랭킹 시스템</div>", unsafe_allow_html=True)
    df = load_data()
    if st.session_state.admin_mode:
        edited_df = st.data_editor(df, num_rows="dynamic", use_container_width=True)
        if st.button("💾 변경사항 저장"):
            edited_df.to_csv(DB_FILE, index=False)
            st.success("랭킹 데이터가 업데이트되었습니다.")
    else:
        st.dataframe(df, use_container_width=True, hide_index=True)
    
    col1, col2 = st.columns(2)
    with col1:
        output = BytesIO()
        df.to_excel(output, index=False)
        st.download_button("📥 랭킹 엑셀 다운로드", output.getvalue(), "ranking.xlsx")

# --- [2번 메뉴: 대진 및 경기 현황] ---
elif menu == "대진 및 경기 현황":
    st.markdown(f"<div class='main-header'>📅 {st.session_state.get('tour_name', '두류 정기전')}</div>", unsafe_allow_html=True)
    tabs = st.tabs([g['name'] for g in st.session_state.groups_config])
    
    for i, tab in enumerate(tabs):
        conf = st.session_state.groups_config[i]
        with tab:
            # 상단: 매트릭스 & 순위표 배치
            m1, m2 = st.columns([1, 1])
            with m1:
                st.caption("📊 조별 매트릭스")
                names = conf['players']
                if names:
                    m_df = pd.DataFrame("-", index=names, columns=names)
                    for n in names: m_df.loc[n, n] = "X"
                    st.table(m_df.style.applymap(lambda v: 'background-color: #EEEEEE; color: #EEEEEE' if v == 'X' else ''))
            with m2:
                st.caption("🏆 실시간 순위표")
                st.table(pd.DataFrame({"이름": names, "승점": [0]*len(names)}))

            st.divider()
            
            # 하단: 카드 UI 대진표 (2코트 가정)
            st.write(f"🎾 {conf['name']} 경기 대진")
            matches = generate_kdk_matches(conf['players'], conf['games'])
            for idx, (t1, t2) in enumerate(matches):
                st.markdown(f"""
                <div class='match-card'>
                    <div style='color: #888; font-size: 0.7rem;'>MATCH {idx+1}</div>
                    <div class='team-box'>{t1[0]} / {t1[1]}</div>
                    <div class='vs-badge'>VS</div>
                    <div class='team-box'>{t2[0]} / {t2[1]}</div>
                </div>
                """, unsafe_allow_html=True)
                sc1, sc2 = st.columns(2)
                sc1.number_input("점수", 0, 10, key=f"s1_{i}_{idx}", label_visibility="collapsed")
                sc2.number_input("점수", 0, 10, key=f"s2_{i}_{idx}", label_visibility="collapsed")

# --- [3번 메뉴: 경기 결과 및 점수] ---
elif menu == "경기 결과 및 점수":
    st.markdown("<div class='main-header'>🏁 경기 결과 및 부과점</div>", unsafe_allow_html=True)
    st.info("그룹별 순위에 따라 우승(7점), 준우승(5점), 3위(3점), 참가(1점)가 부여됩니다.")

# --- [4번 메뉴: 아카이브] ---
elif menu == "아카이브":
    st.markdown("<div class='main-header'>📂 지난 대회 아카이브</div>", unsafe_allow_html=True)
    st.selectbox("대회 선택", ["2026-04 정기전", "2026-03 챌린지"])

# --- [5번 메뉴: 관리자 페이지] ---
elif menu == "관리자 페이지":
    st.markdown("<div class='main-header'>⚙️ 대회 운영 설정</div>", unsafe_allow_html=True)
    pw = st.text_input("비밀번호", type="password")
    if pw == "0502":
        st.session_state.admin_mode = True
        df = load_data()
        all_names = df['이름'].tolist()
        
        st.subheader("👥 참여자 명단 관리")
        st.text_area("회원 명단 수정 (쉼표 구분)", ", ".join(all_names))
        
        st.write("✅ 오늘 참가자 선택")
        cols = st.columns(4)
        selected_players = [n for i, n in enumerate(all_names) if cols[i%4].checkbox(n, value=True, key=f"chk_{n}")]
        
        st.divider()
        st.subheader("📝 그룹별 상세 설정")
        g_count = st.number_input("그룹 수", 1, 10, 1)
        new_configs = []
        for i in range(int(g_count)):
            with st.expander(f"📍 {chr(65+i)}그룹 설정"):
                col1, col2, col3 = st.columns(3)
                g_name = col1.text_input("그룹명", f"{chr(65+i)}그룹", key=f"gn_{i}")
                g_type = col2.selectbox("방식", ["고정페어", "KDK", "단식"], key=f"gt_{i}")
                g_game = col3.selectbox("게임 수", [3, 4], key=f"gg_{i}")
                g_players = st.multiselect("참가자 선택", selected_players, key=f"gp_{i}")
                new_configs.append({"name": g_name, "type": g_type, "games": g_game, "players": g_players})
        
        if st.button("🎲 대진표 확정 및 생성"):
            st.session_state.groups_config = new_groups
            st.success("대진이 생성되었습니다!")

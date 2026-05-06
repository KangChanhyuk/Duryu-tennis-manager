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
    .match-card { background: white; border-radius: 15px; padding: 15px; border: 1px solid #E0E0E0; box-shadow: 0 4px 6px rgba(0,0,0,0.05); margin-bottom: 10px; }
    .team-box { display: inline-block; width: 42%; vertical-align: middle; padding: 8px; background: #F1F8E9; border-radius: 8px; font-weight: 700; color: #2E7D32; font-size: 0.9rem; }
    .vs-badge { display: inline-block; width: 12%; color: #FF4B4B; font-weight: 900; font-size: 1rem; }
</style>
""", unsafe_allow_html=True)

# --- 2. 데이터 관리 로직 (엑셀 업로드 반영 로직 추가) ---
DB_FILE = "tennis_members.csv"

def load_data():
    if os.path.exists(DB_FILE):
        try:
            return pd.read_csv(DB_FILE)
        except:
            return create_default_df()
    return create_default_df()

def create_default_df():
    return pd.DataFrame({
        "랭킹": range(1, 9), "이름": [f"회원{i}" for i in range(1, 9)],
        "현재포인트": [100]*8, "이전포인트": [100]*8,
        "부과점": [0]*8, "그룹": ["A"]*8, "비고": [""]*8
    })

# --- 3. 대진 알고리즘 (KDK) ---
def generate_kdk_matches(player_names, games_per_person):
    n = len(player_names)
    if n < 4: return []
    p = [None] + player_names
    matches = []
    if games_per_person == 3:
        if n == 4: matches = [(1,4,2,3), (1,3,2,4), (1,2,3,4)]
        elif n == 8: matches = [(1,2,3,4), (5,6,7,8), (1,8,2,7), (3,6,4,5), (1,4,5,8), (2,3,6,7)]
    elif games_per_person == 4:
        if n == 5: matches = [(1,2,3,4), (1,3,2,5), (1,4,3,5), (1,5,2,4), (2,3,4,5)]
        elif n == 8: matches = [(1,2,3,4), (5,6,7,8), (1,3,5,7), (2,4,6,8), (1,5,2,6), (3,7,4,8), (1,6,3,8), (2,5,4,7)]
    return [((p[m[0]], p[m[1]]), (p[m[2]], p[m[3]])) for m in matches if all(i <= n for i in m)]

# --- 4. 세션 상태 관리 ---
if 'admin_mode' not in st.session_state: st.session_state.admin_mode = False
if 'tour_name' not in st.session_state: st.session_state.tour_name = "제1회 두류 테니스 대회"
if 'groups_config' not in st.session_state: 
    st.session_state.groups_config = [{"name": "A그룹", "type": "KDK", "games": 4, "players": []}]

# --- 5. 메뉴 구성 ---
menu = st.sidebar.radio("메뉴 이동", ["두류 랭킹", "대진 및 경기 현황", "경기 결과 및 점수", "아카이브", "관리자 페이지"])

# --- [1. 두류 랭킹] ---
if menu == "두류 랭킹":
    st.markdown("<div class='main-header'>🏆 두류 랭킹 시스템</div>", unsafe_allow_html=True)
    df = load_data()
    st.dataframe(df, use_container_width=True, hide_index=True)
    
    output = BytesIO()
    df.to_excel(output, index=False)
    st.download_button("📥 현재 랭킹 엑셀 다운로드", output.getvalue(), "ranking.xlsx")

# --- [2. 대진 및 경기 현황] ---
elif menu == "대진 및 경기 현황":
    st.markdown(f"<div class='main-header'>📅 {st.session_state.tour_name}</div>", unsafe_allow_html=True)
    tabs = st.tabs([g['name'] for g in st.session_state.groups_config])
    
    for i, tab in enumerate(tabs):
        conf = st.session_state.groups_config[i]
        with tab:
            m1, m2 = st.columns(2)
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
            matches = generate_kdk_matches(conf['players'], conf['games'])
            for idx, (t1, t2) in enumerate(matches):
                st.markdown(f"""<div class='match-card'><div class='team-box'>{t1[0]}/{t1[1]}</div><div class='vs-badge'>VS</div><div class='team-box'>{t2[0]}/{t2[1]}</div></div>""", unsafe_allow_html=True)

# --- [5. 관리자 페이지] ---
elif menu == "관리자 페이지":
    st.markdown("<div class='main-header'>⚙️ 대회 운영 설정</div>", unsafe_allow_html=True)
    pw = st.text_input("관리자 비밀번호", type="password")
    if pw == "0502":
        st.session_state.admin_mode = True
        df = load_data()
        
        # 1. 대회 생성 및 기본 설정
        st.subheader("🏁 대회 기본 설정")
        st.session_state.tour_name = st.text_input("대회 이름", st.session_state.tour_name)
        
        # 2. 엑셀 업로드 (기능 보강)
        st.subheader("📥 랭킹 데이터 업데이트")
        up_file = st.file_uploader("엑셀 파일을 업로드하면 회원 명단이 자동 갱신됩니다.", type=['xlsx'])
        if up_file:
            try:
                new_df = pd.read_excel(up_file)
                if '이름' in new_df.columns:
                    new_df.to_csv(DB_FILE, index=False)
                    st.success("엑셀 데이터가 성공적으로 반영되었습니다. 페이지를 새로고침 하세요.")
                    st.rerun()
                else:
                    st.error("엑셀 파일에 '이름' 컬럼이 반드시 포함되어야 합니다.")
            except Exception as e:
                st.error(f"오류 발생: {e}")

        # 3. 참여자 텍스트 직접 입력 및 체크박스
        st.subheader("👥 참여자 명단 관리")
        current_names = df['이름'].tolist()
        text_names = st.text_area("회원 명단 (쉼표로 구분하여 직접 수정 가능)", ", ".join(current_names))
        
        if st.button("텍스트 명단 반영"):
            updated_list = [n.strip() for n in text_names.split(",") if n.strip()]
            new_df = pd.DataFrame({"이름": updated_list})
            # 기존 랭킹 정보가 있다면 유지하는 로직 추가 가능
            new_df.to_csv(DB_FILE, index=False)
            st.success("명단이 수정되었습니다.")
            st.rerun()

        st.write("✅ 오늘 대회 참가자 선택")
        cols = st.columns(4)
        active_p = [n for i, n in enumerate(current_names) if cols[i%4].checkbox(n, value=True, key=f"chk_{n}")]

        # 4. 그룹 상세 설정
        st.subheader("📝 그룹별 상세 설정")
        g_count = st.number_input("그룹 수", 1, 10, len(st.session_state.groups_config))
        new_configs = []
        for i in range(int(g_count)):
            with st.expander(f"📍 {chr(65+i)}그룹 설정"):
                gn = st.text_input("그룹명", f"{chr(65+i)}그룹", key=f"gn_{i}")
                gt = st.selectbox("방식", ["고정페어", "KDK", "단식"], key=f"gt_{i}")
                gg = st.selectbox("게임 수", [3, 4], key=f"gg_{i}")
                gp = st.multiselect("참가자 배정", active_p, key=f"gp_{i}")
                new_configs.append({"name": gn, "type": gt, "games": gg, "players": gp})
        
        if st.button("🎲 대진 확정"):
            st.session_state.groups_config = new_configs
            st.success("대진 설정이 저장되었습니다.")

# --- 나머지 메뉴(3, 4)는 기존 코드 유지 ---
elif menu == "경기 결과 및 점수":
    st.markdown("<div class='main-header'>🏁 경기 결과</div>", unsafe_allow_html=True)
elif menu == "아카이브":
    st.markdown("<div class='main-header'>📂 아카이브</div>", unsafe_allow_html=True)

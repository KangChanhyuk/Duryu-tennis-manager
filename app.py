import streamlit as st
import pandas as pd
import os
import random
from io import BytesIO

# --- 1. 페이지 설정 및 디자인 ---
st.set_page_config(page_title="두류 랭킹 관리 시스템", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;700;900&display=swap');
    * { font-family: 'Noto Sans KR', sans-serif; text-align: center; }
    .stApp { background-color: #F0F9F1; }
    .main-header { background: linear-gradient(135deg, #2E7D32, #4CAF50); color: white; padding: 1.5rem; border-radius: 20px; margin-bottom: 2rem; box-shadow: 0 4px 15px rgba(0,0,0,0.1); font-weight: 900; }
    .match-card { background: white; border-radius: 15px; padding: 20px; border: 2px solid #E8F5E9; box-shadow: 0 4px 6px rgba(0,0,0,0.05); margin-bottom: 15px; display: flex; align-items: center; justify-content: center; }
    .team-box { width: 40%; background: #E8F5E9; padding: 10px; border-radius: 10px; font-weight: 700; color: #1B5E20; font-size: 1.1rem; border: 1px solid #C8E6C9; }
    .vs-badge { width: 10%; color: #D32F2F; font-weight: 900; font-size: 1.2rem; }
    .player-edit { cursor: pointer; color: #2E7D32; text-decoration: underline; }
    .stButton>button { border-radius: 10px; width: 100%; }
</style>
""", unsafe_allow_html=True)

# --- 2. 데이터 로직 ---
DB_FILE = "tennis_members.csv"
ARCHIVE_FILE = "tournament_archive.csv"

def load_data():
    if os.path.exists(DB_FILE): return pd.read_csv(DB_FILE)
    return pd.DataFrame({"랭킹": range(1, 33), "이름": [f"회원{i}" for i in range(1, 33)], "포인트": [100]*32})

def save_archive(data):
    df = pd.DataFrame([data])
    if os.path.exists(ARCHIVE_FILE): df.to_csv(ARCHIVE_FILE, mode='a', header=False, index=False)
    else: df.to_csv(ARCHIVE_FILE, index=False)

# --- 3. 대진 알고리즘 엔진 ---
def get_kdk_logic(n, games):
    # 1인 3게임 로직
    if games == 3:
        if n == 4: return [(1,4,2,3), (1,3,2,4), (1,2,3,4)]
        if n == 8: return [(1,2,3,4), (5,6,7,8), (1,8,2,7), (3,6,4,5), (1,4,5,8), (2,3,6,7)]
        if n == 12: return [(1,2,3,4), (5,6,7,8), (9,10,11,12), (1,3,5,7), (2,4,6,8), (9,11,1,5), (4,8,9,12), (6,7,10,11), (10,12,2,3)]
    # 1인 4게임 로직
    elif games == 4:
        if n == 5: return [(1,2,3,4), (1,3,2,5), (1,4,3,5), (1,5,2,4), (2,3,4,5)]
        if n == 6: return [(1,3,2,4), (1,5,4,6), (2,3,5,6), (1,4,3,5), (2,6,3,4), (1,6,2,5)]
        if n == 7: return [(1,2,3,4), (5,6,1,7), (2,3,5,7), (1,4,6,7), (3,5,2,4), (1,6,2,5), (4,6,3,7)]
        if n == 8: return [(1,2,3,4), (5,6,7,8), (1,3,5,7), (2,4,6,8), (1,5,2,6), (3,7,4,8), (1,6,3,8), (2,5,4,7)]
        if n == 9: return [(1,2,3,4), (5,6,7,8), (1,9,5,7), (2,3,6,8), (4,9,3,8), (1,5,2,6), (3,6,4,5), (1,7,8,9), (2,4,7,9)]
        if n == 10: return [(1,2,3,5), (6,7,8,10), (2,3,4,6), (7,8,1,9), (3,4,5,7), (8,9,2,10), (4,5,6,8), (1,3,9,10), (5,6,7,9), (1,10,2,4)]
        if n == 11: return [(1,2,3,5), (6,7,8,10), (4,9,1,11), (2,3,6,8), (4,5,7,10), (9,11,2,6), (1,3,7,11), (4,8,5,9), (1,10,2,8), (4,7,6,11), (3,9,5,10)]
    return []

def generate_matches(players, mode, games):
    n = len(players)
    if mode == "고정페어": # 1위-최하위 매칭
        pairs = []
        for i in range(n // 2):
            pairs.append((players[i], players[n-1-i]))
        matches = []
        # 페어들끼리 1인당 게임수(games)만큼 대진 생성
        for i in range(games):
            random.shuffle(pairs)
            for j in range(0, len(pairs)-1, 2):
                matches.append((pairs[j], pairs[j+1]))
        return matches
    elif mode == "KDK":
        indices = get_kdk_logic(n, games)
        return [((players[idx[0]-1], players[idx[1]-1]), (players[idx[2]-1], players[idx[3]-1])) for idx in indices]
    elif mode == "단식":
        matches = []
        for i in range(games):
            pool = list(players)
            random.shuffle(pool)
            for j in range(0, len(pool)-1, 2):
                matches.append(((pool[j], ""), (pool[j+1], "")))
        return matches
    return []

# --- 4. 세션 초기화 ---
if 'admin_mode' not in st.session_state: st.session_state.admin_mode = False
if 'groups' not in st.session_state: 
    st.session_state.groups = [{"name": f"그룹 {chr(65+i)}", "num": 8, "mode": "고정페어", "games": 4} for i in range(4)]
if 'participants' not in st.session_state: st.session_state.participants = []

# --- 5. 메뉴 구성 ---
menu = st.sidebar.radio("메뉴 이동", ["두류 랭킹", "대진 및 경기 현황", "지난 대회 아카이브", "관리자 페이지"])

# --- [1. 두류 랭킹] ---
if menu == "두류 랭킹":
    st.markdown("<div class='main-header'>🏆 두류 랭킹 시스템</div>", unsafe_allow_html=True)
    df = load_data()
    st.dataframe(df, use_container_width=True, hide_index=True)
    col1, col2 = st.columns(2)
    with col1:
        output = BytesIO()
        df.to_excel(output, index=False)
        st.download_button("📥 랭킹 엑셀 다운로드", output.getvalue(), "ranking.xlsx")
    with col2:
        up_file = st.file_uploader("📤 랭킹 엑셀 업로드", type=['xlsx'])
        if up_file:
            pd.read_excel(up_file).to_csv(DB_FILE, index=False)
            st.rerun()

# --- [2. 대진 및 경기 현황] ---
elif menu == "대진 및 경기 현황":
    st.markdown(f"<div class='main-header'>📅 현재 대회 경기 현황</div>", unsafe_allow_html=True)
    if not st.session_state.get('matches'):
        st.warning("관리자 페이지에서 대진표를 먼저 생성해주세요.")
    else:
        for g_idx, g_data in enumerate(st.session_state.matches):
            with st.expander(f"🎾 {g_data['name']} 경기 현황", expanded=True):
                for m in g_data['matches']:
                    st.markdown(f"""
                    <div class='match-card'>
                        <div class='team-box'>{m[0][0]} {f'& {m[0][1]}' if m[0][1] else ''}</div>
                        <div class='vs-badge'>VS</div>
                        <div class='team-box'>{m[1][0]} {f'& {m[1][1]}' if m[1][1] else ''}</div>
                    </div>
                    """, unsafe_allow_html=True)

# --- [4. 관리자 페이지] ---
elif menu == "관리자 페이지":
    st.markdown("<div class='main-header'>⚙️ 대회 통합 관리</div>", unsafe_allow_html=True)
    pw = st.text_input("관리자 비밀번호", type="password")
    if pw == "0502":
        st.session_state.admin_mode = True
        
        # 1. 참여자 명단 및 랭킹 관리
        st.subheader("👥 참여자 명단 (랭킹순)")
        df = load_data()
        current_players = df['이름'].tolist()
        
        # 텍스트로 확인 및 수정
        p_text = st.text_area("회원 명단 (쉼표 구분)", ", ".join(current_players))
        if st.button("명단 업데이트"):
            new_list = [n.strip() for n in p_text.split(",") if n.strip()]
            pd.DataFrame({"랭킹": range(1, len(new_list)+1), "이름": new_list}).to_csv(DB_FILE, index=False)
            st.rerun()

        st.write("✅ 오늘 대회 참가자 선택 (체크박스)")
        cols = st.columns(4)
        active_p = []
        for i, name in enumerate(current_players):
            if cols[i%4].checkbox(name, value=True, key=f"p_{i}"):
                active_p.append(name)
        
        st.divider()

        # 2. 그룹 설정
        st.subheader("📝 그룹 및 대진 방식 설정")
        col_g1, col_g2 = st.columns(2)
        g_count = col_g1.number_input("그룹 수", 1, 10, len(st.session_state.groups))
        court_count = col_g2.selectbox("코트 수 설정", [1, 2, 3], index=1)
        
        new_groups = []
        last_idx = 0
        for i in range(int(g_count)):
            with st.expander(f"📍 그룹 {i+1} 설정", expanded=True):
                c1, c2, c3, c4 = st.columns([2,1,1,1])
                gn = c1.text_input("그룹 이름", f"{chr(65+i)}그룹", key=f"gn_{i}")
                gn_num = c2.number_input("인원수", 4, 32, 8, key=f"gnum_{i}")
                gn_mode = c3.selectbox("방식", ["고정페어", "KDK", "단식"], key=f"gmode_{i}")
                gn_games = c4.selectbox("인당 게임수", [3, 4], key=f"ggames_{i}")
                
                # 랭킹순 자동 배정 로직
                g_players = active_p[last_idx : last_idx + int(gn_num)]
                new_groups.append({"name": gn, "num": gn_num, "mode": gn_mode, "games": gn_games, "players": g_players})
                last_idx += int(gn_num)
                st.caption(f"배정된 인원: {', '.join(g_players) if g_players else '인원 부족'}")

        if st.button("🎲 대진표 생성 및 대회 시작"):
            all_matches = []
            for g in new_groups:
                if len(g['players']) >= 4:
                    matches = generate_matches(g['players'], g['mode'], g['games'])
                    all_matches.append({"name": g['name'], "matches": matches})
            st.session_state.matches = all_matches
            st.success("대진표가 생성되었습니다!")

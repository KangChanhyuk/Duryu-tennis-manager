import streamlit as st
import pandas as pd
import os
import json
import random
from datetime import datetime
from io import BytesIO

# --- [1. 스타일 및 시각화 설정] ---
st.set_page_config(page_title="두류 테니스 운영 시스템", layout="wide", initial_sidebar_state="expanded")

def apply_design():
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;700;900&display=swap');
        * { font-family: 'Noto Sans KR', sans-serif; text-align: center; }
        .stApp { background-color: #F7FAF7; }
        
        /* 메인 헤더 */
        .main-header { 
            background: linear-gradient(135deg, #1D5B2E 0%, #388E3C 100%); 
            color: white; padding: 2.5rem; border-radius: 25px; 
            margin-bottom: 35px; box-shadow: 0 12px 24px rgba(0,0,0,0.15);
        }
        
        /* 매치 카드 */
        .match-card { 
            background: white; border-radius: 18px; padding: 25px; 
            border: 1px solid #E0E0E0; margin-bottom: 20px; 
            box-shadow: 0 6px 15px rgba(0,0,0,0.06);
        }
        .team-unit { 
            background: #F1F8E9; padding: 15px; 
            border-radius: 12px; border: 1px solid #C8E6C9;
            margin: 5px 0;
        }
        .player-text { font-weight: 700; color: #2E7D32; font-size: 1.1rem; }
        .score-input { width: 60px !important; text-align: center; font-weight: bold; }
        
        /* 그룹 구분선 */
        .group-header {
            background: #FFD600; color: #333; padding: 8px 20px;
            border-radius: 50px; font-weight: 800; font-size: 1rem;
            margin: 20px 0; display: inline-block;
        }
    </style>
    """, unsafe_allow_html=True)

# --- [2. 데이터 매니지먼트 클래스] ---
class DuryuDataHandler:
    MEMBER_FILE = "duryu_members.csv"
    HISTORY_FILE = "tournament_history.json"

    @staticmethod
    def load_members():
        if os.path.exists(DuryuDataHandler.MEMBER_FILE):
            df = pd.read_csv(DuryuDataHandler.MEMBER_FILE)
            df.columns = [c.strip() for c in df.columns]
            return df.sort_values(by="랭킹").reset_index(drop=True)
        return pd.DataFrame({"랭킹": range(1, 21), "이름": [f"회원{i}" for i in range(1, 21)], "급수": ["A"]*20})

    @staticmethod
    def save_members(df):
        df.to_csv(DuryuDataHandler.MEMBER_FILE, index=False)

    @staticmethod
    def load_history():
        if os.path.exists(DuryuDataHandler.HISTORY_FILE):
            try:
                with open(DuryuDataHandler.HISTORY_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except: return {}
        return {}

    @staticmethod
    def save_history(history):
        with open(DuryuDataHandler.HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(history, f, ensure_ascii=False, indent=4)

# --- [3. 대진 생성 엔진] ---
class TournamentEngine:
    @staticmethod
    def get_kdk_blueprint(n, games):
        if games == 3:
            if n == 4: return [(1,4,2,3), (1,3,2,4), (1,2,3,4)]
            if n == 8: return [(1,2,3,4), (5,6,7,8), (1,8,2,7), (3,6,4,5), (1,4,5,8), (2,3,6,7)]
            if n == 12: return [(1,2,3,4), (5,6,7,8), (9,10,11,12), (1,3,5,7), (2,4,6,8), (9,11,1,5), (4,8,9,12), (6,7,10,11), (10,12,2,3)]
        elif games == 4:
            if n == 5: return [(1,2,3,4), (1,3,2,5), (1,4,3,5), (1,5,2,4), (2,3,4,5)]
            if n == 6: return [(1,3,2,4), (1,5,4,6), (2,3,5,6), (1,4,3,5), (2,6,3,4), (1,6,2,5)]
            if n == 8: return [(1,2,3,4), (5,6,7,8), (1,3,5,7), (2,4,6,8), (1,5,2,6), (3,7,4,8), (1,6,3,8), (2,5,4,7)]
        return []

    @staticmethod
    def build_matches(players, mode, games):
        n = len(players)
        if mode == "고정페어":
            pairs = [(players[i], players[n-1-i]) for i in range(n // 2)]
            matches = []
            for _ in range(games):
                random.shuffle(pairs)
                for j in range(0, len(pairs)-1, 2):
                    matches.append({"team1": pairs[j], "team2": pairs[j+1], "score1": 0, "score2": 0})
            return matches
        elif mode == "KDK":
            blueprint = TournamentEngine.get_kdk_blueprint(n, games)
            return [{"team1": (players[i[0]-1], players[i[1]-1]), "team2": (players[i[2]-1], players[i[3]-1]), "score1": 0, "score2": 0} for i in blueprint]
        return []

# --- [4. 메인 어플리케이션] ---
def main():
    apply_design()
    handler = DuryuDataHandler()
    engine = TournamentEngine()
    
    # 세션 상태 초기화
    if 'select_all' not in st.session_state: st.session_state.select_all = False
    if 'temp_attendees' not in st.session_state: st.session_state.temp_attendees = []

    st.sidebar.title("🎾 두류 테니스 관리")
    menu = st.sidebar.radio("메뉴 이동", ["🏆 클럽 랭킹", "📊 경기 현황 및 점수입력", "⚙️ 관리자 설정"])

    # --- 메뉴 1: 클럽 랭킹 (조회 전용) ---
    if menu == "🏆 클럽 랭킹":
        st.markdown("<div class='main-header'>🏆 두류 테니스 클럽 회원 랭킹</div>", unsafe_allow_html=True)
        df_members = handler.load_members()
        st.dataframe(df_members, use_container_width=True, hide_index=True)

    # --- 메뉴 2: 경기 현황 및 점수입력 (모든 유저 가능) ---
    elif menu == "📊 경기 현황 및 점수입력":
        history = handler.load_history()
        if not history:
            st.info("현재 진행 중인 대회가 없습니다.")
        else:
            latest_id = list(history.keys())[-1]
            data = history[latest_id]
            st.markdown(f"<div class='main-header'>📅 {data['title']}</div>", unsafe_allow_html=True)
            
            # 점수 수정을 위한 세션 상태 업데이트 로직
            updated = False
            
            for g_name, g_info in data['groups'].items():
                st.markdown(f"<div class='group-header'>{g_name} - {g_info['mode']} ({g_info['games']}게임)</div>", unsafe_allow_html=True)
                
                # 2열 배치
                cols = st.columns(2)
                for idx, m in enumerate(g_info['matches']):
                    with cols[idx % 2]:
                        with st.container():
                            st.markdown("<div class='match-card'>", unsafe_allow_html=True)
                            c1, c_vs, c2 = st.columns([4, 1, 4])
                            
                            with c1:
                                st.markdown(f"<div class='team-unit'><span class='player-text'>{m['team1'][0]} & {m['team1'][1]}</span></div>", unsafe_allow_html=True)
                                s1 = st.number_input("점수", 0, 10, m['score1'], key=f"s1_{g_name}_{idx}")
                            
                            with c_vs:
                                st.markdown("<h3 style='margin-top:40px;'>VS</h3>", unsafe_allow_html=True)
                                
                            with c2:
                                st.markdown(f"<div class='team-unit'><span class='player-text'>{m['team2'][0]} & {m['team2'][1]}</span></div>", unsafe_allow_html=True)
                                s2 = st.number_input("점수", 0, 10, m['score2'], key=f"s2_{g_name}_{idx}")
                            
                            # 점수가 바뀌면 저장 준비
                            if s1 != m['score1'] or s2 != m['score2']:
                                m['score1'], m['score2'] = s1, s2
                                updated = True
                            st.markdown("</div>", unsafe_allow_html=True)
                st.divider()
            
            if updated:
                handler.save_history(history)
                st.toast("점수가 실시간으로 반영되었습니다!")

    # --- 메뉴 3: 관리자 설정 (암호 보호) ---
    elif menu == "⚙️ 관리자 설정":
        st.markdown("<div class='main-header'>⚙️ 관리자 전용 대회 설정</div>", unsafe_allow_html=True)
        admin_pw = st.text_input("관리자 암호를 입력하세요", type="password")
        
        if admin_pw == "0502":
            tab1, tab2, tab3 = st.tabs(["👥 회원/참여자 관리", "🚀 대회 생성", "📂 기록 삭제"])
            
            with tab1:
                st.subheader("회원 명단 업데이트 및 참여자 접수")
                df_all = handler.load_members()
                
                # 엑셀 업로드
                up_file = st.file_uploader("랭킹 엑셀 업로드", type=['xlsx'])
                if up_file:
                    handler.save_members(pd.read_excel(up_file))
                    st.success("회원 명단 갱신 완료!")
                    st.rerun()

                st.divider()
                st.write("### 당일 참가자 선택")
                
                # 텍스트 일괄 입력
                input_text = st.text_area("카톡 명단 붙여넣기 (이름 사이 쉼표나 줄바꿈)", help="입력 시 아래 체크박스가 자동으로 체크됩니다.")
                text_names = [n.strip() for n in input_text.replace('\n', ',').split(',') if n.strip()]
                
                # 전체 선택
                if st.checkbox("전체 선택/해제", value=st.session_state.select_all):
                    st.session_state.select_all = True
                else:
                    st.session_state.select_all = False
                
                selected_names = []
                chk_cols = st.columns(4)
                for i, row in df_all.iterrows():
                    is_checked = st.session_state.select_all or (row['이름'] in text_names)
                    if chk_cols[i%4].checkbox(f"{row['이름']} ({row['랭킹']}위)", value=is_checked, key=f"admin_att_{row['이름']}"):
                        selected_names.append(row['이름'])
                
                # 최종 참여자 세션 저장 (랭킹순 정렬)
                final_list = sorted(list(set(selected_names)), key=lambda x: df_all[df_all['이름'] == x]['랭킹'].values[0] if x in df_all['이름'].values else 999)
                st.session_state.temp_attendees = final_list
                st.success(f"현재 선택된 인원: {len(final_list)}명")

            with tab2:
                st.subheader("그룹 슬라이싱 및 대진표 생성")
                attendees = st.session_state.temp_attendees
                if not attendees:
                    st.warning("먼저 '참여자 관리' 탭에서 인원을 선택해주세요.")
                else:
                    g_count = st.number_input("그룹 수", 1, 6, 2)
                    final_tournament = {}
                    ptr = 0
                    
                    for i in range(g_count):
                        with st.expander(f"📍 {i+1}번 그룹 설정", expanded=True):
                            c1, c2, c3, c4 = st.columns([2, 1, 1, 1])
                            g_name = c1.text_input("그룹명", f"{chr(65+i)}그룹", key=f"set_gn_{i}")
                            g_size = c2.number_input("인원수", 4, 30, 8, key=f"set_gs_{i}")
                            g_mode = c3.selectbox("방식", ["고정페어", "KDK"], index=1, key=f"set_gm_{i}")
                            g_games = c4.selectbox("게임수", [3, 4], index=1, key=f"set_gg_{i}")
                            
                            # 랭킹순 슬라이싱
                            assigned = attendees[ptr : ptr + int(g_size)]
                            st.info(f"배정 인원: {', '.join(assigned)}")
                            
                            if assigned:
                                final_tournament[g_name] = {
                                    "mode": g_mode, "games": g_games, "players": assigned,
                                    "matches": engine.build_matches(assigned, g_mode, g_games)
                                }
                                ptr += int(g_size)

                    if st.button("🚀 대진표 생성 및 공식 등록"):
                        history = handler.load_history()
                        tid = datetime.now().strftime("%Y%m%d_%H%M")
                        history[tid] = {
                            "title": f"{datetime.now().strftime('%m월 %d일')} 정기전",
                            "groups": final_tournament
                        }
                        handler.save_history(history)
                        st.balloons()
                        st.success("대회가 공식 등록되었습니다!")

            with tab3:
                st.subheader("과거 기록 관리")
                history = handler.load_history()
                for tid in reversed(list(history.keys())):
                    if st.button(f"🗑 {history[tid]['title']} ({tid}) 삭제"):
                        del history[tid]
                        handler.save_history(history)
                        st.rerun()
        elif admin_pw != "":
            st.error("암호가 올바르지 않습니다.")

if __name__ == "__main__":
    main()

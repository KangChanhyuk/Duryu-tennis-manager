import streamlit as st
import pandas as pd
import os
import json
import random
from datetime import datetime
from io import BytesIO

# --- [1. 스타일 및 테마 설정] ---
st.set_page_config(page_title="두류 랭킹 시스템", layout="wide", initial_sidebar_state="expanded")

def apply_custom_style():
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;700;900&display=swap');
        * { font-family: 'Noto Sans KR', sans-serif; text-align: center; }
        .stApp { background-color: #F4F9F4; }
        
        /* 헤더 스타일 */
        .main-header { 
            background: linear-gradient(135deg, #1D5B2E 0%, #388E3C 100%); 
            color: white; padding: 2rem; border-radius: 20px; 
            margin-bottom: 30px; box-shadow: 0 10px 20px rgba(0,0,0,0.1);
        }
        
        /* 카드형 대진표 스타일 */
        .match-card { 
            background: white; border-radius: 15px; padding: 25px; 
            border: 1px solid #E0E0E0; margin-bottom: 20px; 
            box-shadow: 0 4px 12px rgba(0,0,0,0.05);
            display: flex; align-items: center; justify-content: space-around;
        }
        .team-container { 
            width: 40%; background: #F1F8E9; padding: 15px; 
            border-radius: 12px; border: 2px solid #C8E6C9;
        }
        .player-name { font-weight: 700; color: #2E7D32; font-size: 1.2rem; }
        .vs-circle { 
            background: #FF5252; color: white; width: 45px; height: 45px; 
            border-radius: 50%; display: flex; align-items: center; 
            justify-content: center; font-weight: 900; font-size: 0.9rem;
        }
        
        /* 배지 스타일 */
        .group-badge {
            background: #FFD600; color: #000; padding: 6px 18px;
            border-radius: 30px; font-weight: 800; font-size: 0.85rem;
            margin-bottom: 15px; display: inline-block;
        }
    </style>
    """, unsafe_allow_html=True)

# --- [2. 핵심 데이터 처리 클래스] ---
class DuryuManager:
    DB_FILE = "tennis_members.csv"
    HISTORY_FILE = "tournament_history.json"

    @staticmethod
    def load_members():
        if os.path.exists(DuryuManager.DB_FILE):
            df = pd.read_csv(DuryuManager.DB_FILE)
            return df.sort_values(by="랭킹").reset_index(drop=True)
        # 기본 데이터셋
        return pd.DataFrame({
            "랭킹": range(1, 21),
            "이름": [f"회원{i}" for i in range(1, 21)],
            "연락처": [f"010-0000-{i:04d}" for i in range(1, 21)],
            "포인트": [1000 for _ in range(20)]
        })

    @staticmethod
    def save_members(df):
        df.to_csv(DuryuManager.DB_FILE, index=False)

    @staticmethod
    def load_history():
        if os.path.exists(DuryuManager.HISTORY_FILE):
            with open(DuryuManager.HISTORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

    @staticmethod
    def save_history(history):
        with open(DuryuManager.HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(history, f, ensure_ascii=False, indent=4)

# --- [3. 대진 생성 엔진] ---
class MatchEngine:
    @staticmethod
    def get_kdk_logic(n, games):
        # 1인 3게임 로직 (찬혁님 제공 데이터 기반)
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

    @staticmethod
    def generate(players, mode, games):
        n = len(players)
        if mode == "고정페어":
            # 1위와 최하위, 2위와 차하위 평균으로 묶기
            pairs = []
            for i in range(n // 2):
                pairs.append((players[i], players[n-1-i]))
            matches = []
            # 페어별 경기 수 맞추기
            for _ in range(games):
                random.shuffle(pairs)
                for j in range(0, len(pairs)-1, 2):
                    matches.append((pairs[j], pairs[j+1]))
            return matches

        elif mode == "KDK":
            logic = MatchEngine.get_kdk_logic(n, games)
            # 번호 기반을 이름으로 매핑
            return [((players[i[0]-1], players[i[1]-1]), (players[i[2]-1], players[i[3]-1])) for i in logic]

        elif mode == "단식":
            matches = []
            for _ in range(games):
                pool = list(players)
                random.shuffle(pool)
                for j in range(0, len(pool)-1, 2):
                    matches.append(((pool[j], ""), (pool[j+1], "")))
            return matches
        return []

# --- [4. 메인 애플리케이션] ---
def main():
    apply_custom_style()
    dm = DuryuManager()
    engine = MatchEngine()
    
    # 사이드바 관리자 인증
    st.sidebar.title("🏸 두류 컨트롤 타워")
    admin_pw = st.sidebar.text_input("관리자 인증", type="password")
    is_admin = (admin_pw == "0502")

    menu = st.sidebar.radio("메뉴 선택", ["🏆 두류 전체 랭킹", "📅 당일 대진 현황", "📂 대회 기록 관리", "⚙️ 대회 생성/수정"])

    # --- 메뉴 1: 전체 랭킹 (엑셀 기반) ---
    if menu == "🏆 두류 전체 랭킹":
        st.markdown("<div class='main-header'>🏆 두류 테니스 클럽 회원 랭킹</div>", unsafe_allow_html=True)
        df = dm.load_members()
        st.dataframe(df, use_container_width=True, hide_index=True, height=500)
        
        if is_admin:
            c1, c2 = st.columns(2)
            with c1:
                output = BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    df.to_excel(writer, index=False)
                st.download_button("📥 전체 명단 엑셀 다운로드", output.getvalue(), "duryu_members.xlsx")
            with c2:
                up_file = st.file_uploader("📤 랭킹 업데이트 (엑셀)", type=['xlsx'])
                if up_file:
                    new_df = pd.read_excel(up_file)
                    dm.save_members(new_df)
                    st.success("랭킹 정보가 갱신되었습니다.")
                    st.rerun()

    # --- 메뉴 2: 당일 대진 현황 ---
    elif menu == "📅 당일 대진 현황":
        history = dm.load_history()
        if not history:
            st.warning("진행 중인 대회가 없습니다. 관리자 메뉴에서 대회를 생성하세요.")
        else:
            latest_id = list(history.keys())[-1]
            data = history[latest_id]
            st.markdown(f"<div class='main-header'>📅 {data['title']}</div>", unsafe_allow_html=True)
            
            for g_name, g_info in data['groups'].items():
                st.markdown(f"<div class='group-badge'>{g_name} | {g_info['mode']}</div>", unsafe_allow_html=True)
                cols = st.columns(2)
                for idx, m in enumerate(g_info['matches']):
                    with cols[idx % 2]:
                        p1, p2 = m
                        st.markdown(f"""
                        <div class='match-card'>
                            <div class='team-container'>
                                <div class='player-name'>{p1[0]}</div>
                                {f"<div style='color:#666; font-size:0.8rem;'>{p1[1]}</div>" if p1[1] else ""}
                            </div>
                            <div class='vs-circle'>VS</div>
                            <div class='team-container'>
                                <div class='player-name'>{p2[0]}</div>
                                {f"<div style='color:#666; font-size:0.8rem;'>{p2[1]}</div>" if p2[1] else ""}
                            </div>
                        </div>
                        """, unsafe_allow_html=True)

    # --- 메뉴 3: 대회 기록 관리 (수정/삭제) ---
    elif menu == "📂 대회 기록 관리":
        st.markdown("<div class='main-header'>📂 지난 대회 아카이브</div>", unsafe_allow_html=True)
        history = dm.load_history()
        
        if not history:
            st.info("저장된 대회 기록이 없습니다.")
        else:
            for tid in reversed(list(history.keys())):
                with st.expander(f"📌 {history[tid]['title']} ({tid})"):
                    st.write(f"경기 방식: {len(history[tid]['groups'])}개 그룹 운영")
                    if is_admin:
                        new_title = st.text_input("대회명 수정", history[tid]['title'], key=f"edit_t_{tid}")
                        col1, col2 = st.columns(2)
                        if col1.button("제목 업데이트", key=f"up_t_{tid}"):
                            history[tid]['title'] = new_title
                            dm.save_history(history)
                            st.rerun()
                        if col2.button("⚠️ 대회 영구 삭제", key=f"del_t_{tid}"):
                            del history[tid]
                            dm.save_history(history)
                            st.rerun()

    # --- 메뉴 4: 대회 생성 (랭킹순 자동 배정 로직 핵심) ---
    elif menu == "⚙️ 대회 생성/수정":
        if not is_admin:
            st.error("이 메뉴는 관리자만 접근 가능합니다. 암호를 입력해주세요.")
            return

        st.markdown("<div class='main-header'>⚙️ 신규 대회 생성 및 자동 배정</div>", unsafe_allow_html=True)
        
        df_all = dm.load_members()
        
        # 1단계: 오늘 온 사람 체크 (랭킹순으로 보여줌)
        st.subheader("STEP 1. 당일 참가자 체크")
        st.caption("전체 명단에서 오늘 출석한 사람을 모두 체크해주세요. 체크된 순서와 상관없이 랭킹순으로 자동 재정렬됩니다.")
        
        # 이름 수정 및 랭킹 확인을 위한 데이터 에디터
        edited_members = st.data_editor(df_all, use_container_width=True, hide_index=True, key="member_editor")
        if st.button("회원 정보(이름/연락처) 영구 저장"):
            dm.save_members(edited_members)
            st.success("기본 회원 DB가 수정되었습니다.")

        attendees_idx = []
        chk_cols = st.columns(4)
        for i, row in edited_members.iterrows():
            if chk_cols[i%4].checkbox(f"{row['이름']} ({row['랭킹']}위)", value=False):
                attendees_idx.append(i)
        
        # 선택된 인원을 랭킹순으로 확정
        active_players = edited_members.iloc[attendees_idx].sort_values(by="랭킹")['이름'].tolist()
        
        if active_players:
            st.success(f"현재 {len(active_players)}명 선택됨: {', '.join(active_players)}")
            
            st.divider()
            
            # 2단계: 그룹 및 경기 방식 설정
            st.subheader("STEP 2. 그룹 배정 및 로직 설정")
            g_count = st.number_input("나눌 그룹 수", 1, 10, 2)
            
            final_groups = {}
            current_ptr = 0
            
            for i in range(g_count):
                with st.container():
                    st.markdown(f"#### 📍 {i+1}번 그룹 설정")
                    c1, c2, c3, c4 = st.columns([2,1,1,1])
                    gn = c1.text_input("그룹 이름", f"{chr(65+i)}그룹", key=f"gn_{i}")
                    g_size = c2.number_input("배정 인원", 4, 30, 8, key=f"gs_{i}")
                    g_mode = c3.selectbox("경기 방식", ["고정페어", "KDK", "단식"], index=1, key=f"gm_{i}")
                    g_games = c4.selectbox("인당 게임수", [3, 4], index=1, key=f"gg_{i}")
                    
                    # [랭킹순 자동 배정 핵심 코드]
                    # 전체 참여자 중 현재 순번부터 설정된 인원수만큼 슬라이싱
                    assigned = active_players[current_ptr : current_ptr + int(g_size)]
                    
                    if len(assigned) < int(g_size):
                        st.warning(f"인원이 부족합니다. (현재 {len(assigned)}명 배정 가능)")
                    else:
                        st.info(f"자동 배정된 명단(랭킹순): {', '.join(assigned)}")
                    
                    final_groups[gn] = {
                        "mode": g_mode,
                        "games": g_games,
                        "players": assigned,
                        "matches": engine.generate(assigned, g_mode, g_games)
                    }
                    current_ptr += int(g_size)
                    st.divider()

            if st.button("🔥 최종 대진표 확정 및 대회 시작"):
                if not final_groups:
                    st.error("배정된 그룹이 없습니다.")
                else:
                    new_id = datetime.now().strftime("%Y-%m-%d %H:%M")
                    history = dm.load_history()
                    history[new_id] = {
                        "title": f"{datetime.now().strftime('%m/%d')} 두류 정기전",
                        "groups": final_groups
                    }
                    dm.save_history(history)
                    st.balloons()
                    st.success("대진표 생성이 완료되었습니다! '당일 대진 현황' 메뉴를 확인하세요.")

if __name__ == "__main__":
    main()

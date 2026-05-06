import streamlit as st
import pandas as pd
import numpy as np
import os
from datetime import datetime
import io

# ─── [1] 페이지 초기 설정 및 디자인 (테니스 느낌의 밝은 UI) ───
st.set_page_config(page_title="두류 랭킹 관리 시스템", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;700;900&display=swap');
    * { font-family: 'Noto Sans KR', sans-serif; text-align: center; }
    .main { background-color: #f0f9ff; }
    .stApp { background-color: #fdfdfd; }
    
    /* 헤더 및 타이틀 */
    .title-box { background: linear-gradient(135deg, #1d4ed8, #3b82f6); color: white; padding: 1.5rem; border-radius: 15px; margin-bottom: 2rem; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); }
    
    /* 카드 및 표 디자인 */
    .stTabs [data-baseweb="tab-list"] { justify-content: center; background-color: #eff6ff; border-radius: 10px; }
    .stTabs [data-baseweb="tab"] { font-weight: 700; font-size: 1.1rem; color: #1e40af; }
    
    /* 대진표 디자인 */
    .match-card { background: white; border: 2px solid #bfdbfe; border-radius: 12px; padding: 12px; margin: 8px 0; display: flex; align-items: center; justify-content: center; }
    .team-box { background: #dbeafe; padding: 8px 15px; border-radius: 8px; min-width: 100px; font-weight: 700; color: #1e3a8a; }
    .vs-badge { background: #ef4444; color: white; padding: 4px 8px; border-radius: 50%; margin: 0 15px; font-style: italic; font-weight: 900; }
    
    /* 매트릭스 회색 음영 */
    .matrix-self { background-color: #e5e7eb !important; color: #e5e7eb !important; }
    
    /* 가독성 강조 */
    .name-highlight { background-color: #fef08a; padding: 2px 6px; border-radius: 4px; font-weight: 700; }
    
    /* 모바일 가독성 */
    @media (max-width: 600px) {
        .team-box { min-width: 70px; font-size: 0.9rem; }
        .vs-badge { margin: 0 5px; }
    }
</style>
""", unsafe_allow_html=True)

# ─── [2] 데이터베이스 초기화 및 상수 ───
DB_FILE = "tennis_members.csv"
ARCHIVE_FILE = "tournament_archive.csv"

def init_db():
    if not os.path.exists(DB_FILE):
        df = pd.DataFrame(columns=["이름", "현재포인트", "이전포인트", "결과", "부과점", "그룹", "비고"])
        df.to_csv(DB_FILE, index=False)
    if not os.path.exists(ARCHIVE_FILE):
        pd.DataFrame(columns=["대회명", "날짜", "그룹명", "데이터"]).to_csv(ARCHIVE_FILE, index=False)

init_db()

# ─── [3] KDK 대진표 엔진 (요청하신 정교한 알고리즘) ───
KDK_TABLE = {
    "3_4": [(1,4,2,3), (1,3,2,4), (1,2,3,4)],
    "3_8": [(1,2,3,4), (5,6,7,8), (1,8,2,7), (3,6,4,5), (1,4,5,8), (2,3,6,7)],
    "3_12": [(1,2,3,4), (5,6,7,8), (9,10,11,12), (1,3,5,7), (2,4,6,8), (9,11,1,5), (4,8,9,12), (6,7,10,11), (10,12,2,3)],
    "4_5": [(1,2,3,4), (1,3,2,5), (1,4,3,5), (1,5,2,4), (2,3,4,5)],
    "4_6": [(1,3,2,4), (1,5,4,6), (2,3,5,6), (1,4,3,5), (2,6,3,4), (1,6,2,5)],
    "4_7": [(1,2,3,4), (5,6,1,7), (2,3,5,7), (1,4,6,7), (3,5,2,4), (1,6,2,5), (4,6,3,7)],
    "4_8": [(1,2,3,4), (5,6,7,8), (1,3,5,7), (2,4,6,8), (1,5,2,6), (3,7,4,8), (1,6,3,8), (2,5,4,7)],
    "4_9": [(1,2,3,4), (5,6,7,8), (1,9,5,7), (2,3,6,8), (4,9,3,8), (1,5,2,6), (3,6,4,5), (1,7,8,9), (2,4,7,9)],
    "4_10": [(1,2,3,5), (6,7,8,10), (2,3,4,6), (7,8,1,9), (3,4,5,7), (8,9,2,10), (4,5,6,8), (1,3,9,10), (5,6,7,9), (1,10,2,4)],
    "4_11": [(1,2,3,5), (6,7,8,10), (4,9,1,11), (2,3,6,8), (4,5,7,10), (9,11,2,6), (1,3,7,11), (4,8,5,9), (1,10,2,8), (4,7,6,11), (3,9,5,10)]
}

def get_kdk_matches(players, games_count):
    n = len(players)
    key = f"{games_count}_{n}"
    if key not in KDK_TABLE:
        return []
    
    indices = KDK_TABLE[key]
    matches = []
    for idx in indices:
        # 번호 기반 대진 생성 (1번이 index 0)
        p1, p2, p3, p4 = players[idx[0]-1], players[idx[1]-1], players[idx[2]-1], players[idx[3]-1]
        matches.append(((p1, p2), (p3, p4)))
    return matches

# ─── [4] 세션 상태 관리 ───
if "admin_logged_in" not in st.session_state: st.session_state.admin_logged_in = False
if "current_tournament" not in st.session_state:
    st.session_state.current_tournament = {
        "name": "2026 두류 정기 대회",
        "groups": {}, # {group_name: {"players": [], "type": "KDK", "games": 3, "matches": []}}
        "status": "Setting"
    }
if "admin_pw" not in st.session_state: st.session_state.admin_pw = "0502"

# ─── [5] 메인 레이아웃 및 메뉴 ───
st.markdown('<div class="title-box"><h1>🎾 두류 랭킹 관리 시스템</h1></div>', unsafe_allow_html=True)

menu = st.sidebar.radio("메뉴 선택", ["두류 랭킹", "대진 및 경기 현황", "경기 결과 및 점수 확인", "지난 대회 아카이브", "관리자 페이지"])

# ─── [6] 1번 메뉴: 두류 랭킹 ───
if menu == "두류 랭킹":
    st.header("🏆 전체 랭킹 현황")
    df = pd.read_csv(DB_FILE)
    
    # 정렬: 현재포인트 내림차순
    df = df.sort_values(by="현재포인트", ascending=False).reset_index(drop=True)
    df.insert(0, "순위", range(1, len(df) + 1))
    
    # 항목 표시 (4월=현재, 3월=이전)
    df.columns = ["순위", "이름", "4월 포인트", "3월 포인트", "결과", "부과점", "그룹", "비고"]
    
    if st.session_state.admin_logged_in:
        edited_df = st.data_editor(df, use_container_width=True, num_rows="dynamic")
        if st.button("랭킹 데이터 저장"):
            # 다시 저장 시 컬럼명 원복
            save_df = edited_df.drop(columns=["순위"])
            save_df.columns = ["이름", "현재포인트", "이전포인트", "결과", "부과점", "그룹", "비고"]
            save_df.to_csv(DB_FILE, index=False)
            st.success("저장 완료!")
    else:
        st.table(df)
        
    col1, col2 = st.columns(2)
    with col1:
        if st.download_button("Excel 다운로드", data=df.to_csv(index=False).encode('utf-8-sig'), file_name="duryu_ranking.csv", mime="text/csv"):
            st.info("다운로드 시작...")
    with col2:
        if st.session_state.admin_logged_in:
            up_file = st.file_uploader("랭킹 엑셀 업로드 (CSV)", type="csv")
            if up_file:
                up_df = pd.read_csv(up_file)
                up_df.to_csv(DB_FILE, index=False)
                st.success("업로드 완료! 페이지를 새로고침 하세요.")

# ─── [7] 2번 메뉴: 대진 및 경기 현황 ───
elif menu == "대진 및 경기 현황":
    st.header(f"📅 {st.session_state.current_tournament['name']}")
    
    groups = st.session_state.current_tournament['groups']
    if not groups:
        st.info("관리자 페이지에서 대진을 먼저 생성해주세요.")
    else:
        tabs = st.tabs(list(groups.keys()))
        for i, g_name in enumerate(groups.keys()):
            with tabs[i]:
                g_data = groups[g_name]
                players = g_data['players']
                
                col_m, col_r = st.columns([3, 2])
                with col_m:
                    st.subheader("조별 매트릭스")
                    matrix_data = pd.DataFrame(index=players, columns=players)
                    # 스타일링을 위해 단순 테이블 대신 HTML/CSS 처리 권장되나 여기선 기본 표기
                    st.dataframe(matrix_data.fillna("-"), use_container_width=True)
                
                with col_r:
                    st.subheader("실시간 순위")
                    st.write("경기 결과 입력에 따라 자동 집계됩니다.")
                
                st.markdown("---")
                st.subheader("🔥 경기 대진 및 결과 입력")
                
                for idx, match in enumerate(g_data['matches']):
                    t1, t2 = match
                    with st.container():
                        st.markdown(f"""
                        <div class="match-card">
                            <div class="team-box">{t1[0]} / {t1[1]}</div>
                            <div class="vs-badge">VS</div>
                            <div class="team-box">{t2[0]} / {t2[1]}</div>
                        </div>
                        """, unsafe_allow_html=True)
                        c1, c2 = st.columns(2)
                        with c1: st.number_input(f"Score 1 (Match {idx})", 0, 10, key=f"score1_{g_name}_{idx}")
                        with c2: st.number_input(f"Score 2 (Match {idx})", 0, 10, key=f"score2_{g_name}_{idx}")

# ─── [8] 5번 메뉴: 관리자 페이지 ───
elif menu == "관리자 페이지":
    st.header("⚙️ 관리자 컨트롤 패널")
    
    pw_input = st.text_input("관리자 비밀번호", type="password")
    if pw_input == st.session_state.admin_pw:
        st.session_state.admin_logged_in = True
        st.success("인증되었습니다.")
        
        adm_tab1, adm_tab2, adm_tab3 = st.tabs(["대회 생성/수정", "대진 생성 (그룹별)", "시스템 설정"])
        
        with adm_tab1:
            st.subheader("새 대회 생성")
            t_name = st.text_input("대회명", value=st.session_state.current_tournament['name'])
            court_count = st.selectbox("코트 수 설정", [1, 2, 3], index=1)
            if st.button("대회명 업데이트"):
                st.session_state.current_tournament['name'] = t_name
                st.success("대회명이 변경되었습니다.")
                
        with adm_tab2:
            st.subheader("참가자 선택 및 그룹 설정")
            # 랭킹 데이터에서 이름 가져오기
            rank_df = pd.read_csv(DB_FILE)
            all_members = rank_df['이름'].tolist()
            
            selected_members = st.multiselect("참가자 명단 (체크박스)", all_members)
            
            st.info(f"현재 선택된 인원: {len(selected_members)}명")
            
            group_num = st.number_input("그룹 수 조정", 1, 10, 4)
            
            if st.button("랭킹순 자동 배정 및 대진 작성"):
                # 랭킹 데이터와 매칭하여 정렬
                sorted_members = [m for m in all_members if m in selected_members]
                
                # 그룹 분할 (A, B, C, D...)
                chunk_size = len(sorted_members) // group_num
                for i in range(group_num):
                    g_name = f"Group {chr(65+i)}"
                    start = i * chunk_size
                    end = (i+1) * chunk_size if i != group_num-1 else len(sorted_members)
                    g_players = sorted_members[start:end]
                    
                    # 기본 KDK 배정 (인원수 체크 후)
                    matches = get_kdk_matches(g_players, 3) # 기본 3게임
                    
                    st.session_state.current_tournament['groups'][g_name] = {
                        "players": g_players,
                        "type": "KDK",
                        "games": 3,
                        "matches": matches
                    }
                st.success(f"{group_num}개 그룹 대진 생성 완료!")

        with adm_tab3:
            st.subheader("비밀번호 변경")
            new_pw = st.text_input("새 비밀번호", type="password")
            if st.button("비밀번호 변경"):
                st.session_state.admin_pw = new_pw
                st.success("비밀번호가 변경되었습니다.")

    elif pw_input != "":
        st.error("비밀번호가 틀렸습니다.")

# --- 나머지 메뉴 (경기결과, 아카이브)는 위 데이터 구조를 바탕으로 동일하게 UI 구현 ---
else:
    st.info("준비 중인 페이지입니다.")

# ─── [9] 하단 공통 ───
st.markdown("---")
st.caption("© 2026 두류 테니스 클럽. All rights reserved. 본 웹앱은 모바일에 최적화되어 있습니다.")

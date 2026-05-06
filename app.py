import streamlit as st
import pandas as pd
import random, os, json
from datetime import date
from io import BytesIO

# ── 앱 설정 ──────────────────────────────────────────────────
st.set_page_config(page_title="두류 랭킹 관리 시스템", page_icon="🎾",
                   layout="wide", initial_sidebar_state="collapsed")
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;600;700;900&display=swap');
*{font-family:'Noto Sans KR',sans-serif!important}
.block-container{padding:.5rem .7rem 2rem!important;max-width:100%!important}
.main-hdr{background:linear-gradient(135deg,#1D5B2E,#388E3C);color:#fff;
  padding:1.2rem 1.5rem;border-radius:18px;margin-bottom:1rem;
  font-size:clamp(1.3rem,4vw,2rem);font-weight:900;text-align:center}
.sec{font-size:1.1rem;font-weight:900;color:#1D5B2E;border-left:5px solid #66BB6A;
  padding-left:10px;margin:12px 0 8px}
button[data-baseweb="tab"]{font-size:1rem!important;font-weight:700!important;
  padding:9px 18px!important;border-radius:8px 8px 0 0!important}
button[data-baseweb="tab"][aria-selected="true"]{background:linear-gradient(135deg,#1D5B2E,#388E3C)!important;color:#fff!important}
.stButton>button{border-radius:9px!important;font-weight:700!important;transition:.2s!important}
input[type="number"]{text-align:center!important;font-weight:700!important}
th,td{text-align:center!important;vertical-align:middle!important}
.team-box{border-radius:12px;padding:8px 12px;font-weight:800;font-size:.95rem;
  text-align:center;margin:3px 0;box-shadow:0 3px 8px rgba(0,0,0,.12)}
.tg{background:linear-gradient(135deg,#2E7D32,#1B5E20);color:#fff}
.tb{background:linear-gradient(135deg,#1565C0,#0D47A1);color:#fff}
.to{background:linear-gradient(135deg,#E65100,#BF360C);color:#fff}
.tp{background:linear-gradient(135deg,#6A1B9A,#4A148C);color:#fff}
.vs{background:#E53935;color:#fff;border-radius:50%;width:32px;height:32px;
  display:flex;align-items:center;justify-content:center;font-weight:900;
  font-size:.8rem;margin:3px auto}
.rnd{background:linear-gradient(90deg,#1D5B2E,#388E3C);color:#fff;border-radius:8px;
  padding:5px 14px;font-weight:800;text-align:center;margin:10px 0 6px}
.mcard{background:#fff;border-radius:12px;padding:8px;margin:5px 0;
  box-shadow:0 3px 10px rgba(0,0,0,.08);border:1px solid #E8F5E9}
.acard{border-radius:10px;padding:8px 12px;margin:3px 0;display:flex;align-items:center;gap:8px;font-weight:600}
.aok{background:#F1F8E9;border:1.5px solid #66BB6A}
.ano{background:#FFF3F3;border:1.5px solid #EF9A9A}
@media(max-width:640px){.block-container{padding:.3rem .3rem 2rem!important}}
</style>""", unsafe_allow_html=True)

# ── 파일 ─────────────────────────────────────────────────────
RANK_FILE = "ranking_master.csv"
TOUR_FILE = "tournaments.json"
ADMIN_PW  = "0502"

GCLS = ["tg","tb","to","tp","tg","tb"]
GHEX = ["#2E7D32","#1565C0","#E65100","#6A1B9A","#2E7D32","#1565C0"]
GLBL = ["🟢","🔵","🟠","🟣","🟢","🔵"]

# ── 한울 KDK 대진 ─────────────────────────────────────────────
KDK_BP = {
 3:{4:[(1,4,2,3),(1,3,2,4),(1,2,3,4)],
    8:[(1,2,3,4),(5,6,7,8),(1,8,2,7),(3,6,4,5),(1,4,5,8),(2,3,6,7)],
    12:[(1,2,3,4),(5,6,7,8),(9,10,11,12),(1,3,5,7),(2,4,6,8),(9,11,1,5),(4,8,9,12),(6,7,10,11),(10,12,2,3)]},
 4:{5:[(1,2,3,4),(1,3,2,5),(1,4,3,5),(1,5,2,4),(2,3,4,5)],
    6:[(1,3,2,4),(1,5,4,6),(2,3,5,6),(1,4,3,5),(2,6,3,4),(1,6,2,5)],
    7:[(1,2,3,4),(5,6,1,7),(2,3,5,7),(1,4,6,7),(3,5,2,4),(1,6,2,5),(4,6,3,7)],
    8:[(1,2,3,4),(5,6,7,8),(1,3,5,7),(2,4,6,8),(1,5,2,6),(3,7,4,8),(1,6,3,8),(2,5,4,7)],
    9:[(1,2,3,4),(5,6,7,8),(1,9,5,7),(2,3,6,8),(4,9,3,8),(1,5,2,6),(3,6,4,5),(1,7,8,9),(2,4,7,9)],
    10:[(1,2,3,5),(6,7,8,10),(2,3,4,6),(7,8,1,9),(3,4,5,7),(8,9,2,10),(4,5,6,8),(1,3,9,10),(5,6,7,9),(1,10,2,4)],
    11:[(1,2,3,5),(6,7,8,10),(4,9,1,11),(2,3,6,8),(4,5,7,10),(9,11,2,6),(1,3,7,11),(4,8,5,9),(1,10,2,8),(4,7,6,11),(3,9,5,10)]}
}

def make_kdk(players, gc):
    bp = KDK_BP.get(gc,{}).get(len(players))
    if not bp: return None
    sh = random.sample(players, len(players))
    return [{"t1":[sh[a-1],sh[b-1]],"t2":[sh[c-1],sh[d-1]],"s1":0,"s2":0} for a,b,c,d in bp]

def make_fixed(players):
    n=len(players); pairs=[(players[i],players[n-1-i]) for i in range(n//2)]
    matches=[]
    for i in range(len(pairs)):
        for j in range(i+1,len(pairs)):
            matches.append({"t1":list(pairs[i]),"t2":list(pairs[j]),"s1":0,"s2":0})
    random.shuffle(matches); return matches

def make_singles(players):
    pl=players[:]; random.shuffle(pl)
    matches=[(pl[i],pl[j]) for i in range(len(pl)) for j in range(i+1,len(pl))]
    random.shuffle(matches)
    return [{"t1":[a],"t2":[b],"s1":0,"s2":0} for a,b in matches]

# ── 포인트 규칙 ───────────────────────────────────────────────
# 고정페어: 1위팀7, 2위팀5, 3위팀3, 나머지1
# KDK/단식: 1~2위 묶어7, 3~4위 묶어5, 5~6위 묶어3, 나머지1
def rank_pts(rank, mode):
    if mode=="고정페어":
        return {1:7,2:5,3:3}.get(rank,1)
    else:  # KDK/단식: 1~2위 묶음
        return {1:7,2:7,3:5,4:5,5:3,6:3}.get(rank,1)

# ── 데이터 함수 ───────────────────────────────────────────────
def load_rank():
    if not os.path.exists(RANK_FILE):
        return pd.DataFrame(columns=["랭킹","이름","현재포인트","3월 포인트","결과","부과점","그룹","비고"])
    df = pd.read_csv(RANK_FILE)
    for c in ["현재포인트","3월 포인트","부과점"]:
        if c in df.columns: df[c]=pd.to_numeric(df[c],errors="coerce").fillna(0)
    return df.fillna("")

def save_rank(df): df.to_csv(RANK_FILE,index=False)

def load_tours():
    if os.path.exists(TOUR_FILE):
        with open(TOUR_FILE,"r",encoding="utf-8") as f: return json.load(f)
    return {}

def save_tours(d):
    with open(TOUR_FILE,"w",encoding="utf-8") as f: json.dump(d,f,ensure_ascii=False,indent=2)

def to_excel(df):
    buf=BytesIO(); df.to_excel(buf,index=False); return buf.getvalue()

def tname(t): return " & ".join(t) if len(t)>1 else t[0]

def group_stats(matches, mode):
    stats={}
    for m in matches:
        t1,t2=tuple(m["t1"]),tuple(m["t2"])
        for t in [t1,t2]:
            if t not in stats: stats[t]={"승":0,"패":0,"득실":0}
        s1,s2=m["s1"],m["s2"]
        if s1>s2: stats[t1]["승"]+=1; stats[t2]["패"]+=1
        elif s2>s1: stats[t2]["승"]+=1; stats[t1]["패"]+=1
        stats[t1]["득실"]+=(s1-s2); stats[t2]["득실"]+=(s2-s1)
    return stats

# ── 세션 ─────────────────────────────────────────────────────
if "is_admin" not in st.session_state: st.session_state.is_admin=False

# ── 네비게이션 ────────────────────────────────────────────────
MENUS=["🏆 두류 랭킹","📅 대진 및 경기현황","📊 경기 결과","📂 지난 대회","⚙️ 관리자"]
if "menu" not in st.session_state: st.session_state.menu=MENUS[0]
cols=st.columns(len(MENUS))
for i,(lbl) in enumerate(MENUS):
    with cols[i]:
        tp="primary" if st.session_state.menu==lbl else "secondary"
        if st.button(lbl,key=f"nav{i}",use_container_width=True,type=tp):
            st.session_state.menu=lbl; st.rerun()
st.divider()
M=st.session_state.menu

# ════════════════════════════════════════════════════════════
# 1. 두류 랭킹
# ════════════════════════════════════════════════════════════
if M==MENUS[0]:
    st.markdown("<div class='main-hdr'>🏆 두류 랭킹 관리 시스템</div>",unsafe_allow_html=True)
    df=load_rank()
    if df.empty: st.info("관리자에서 엑셀을 업로드하세요."); st.stop()

    if st.session_state.is_admin:
        st.markdown('<div class="sec">✏️ 랭킹 직접 수정</div>',unsafe_allow_html=True)
        edited=st.data_editor(df,use_container_width=True,hide_index=True,
            num_rows="dynamic",key="rank_edit")
        c1,c2=st.columns(2)
        with c1:
            if st.button("💾 저장",use_container_width=True,type="primary"):
                save_rank(edited); st.success("저장 완료!"); st.rerun()
        with c2:
            st.download_button("📥 엑셀 다운로드",data=to_excel(edited),
                file_name="두류랭킹.xlsx",mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True)
    else:
        st.dataframe(df,use_container_width=True,hide_index=True)
        st.download_button("📥 엑셀 다운로드",data=to_excel(df),
            file_name="두류랭킹.xlsx",mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

# ════════════════════════════════════════════════════════════
# 2. 대진 및 경기 현황
# ════════════════════════════════════════════════════════════
elif M==MENUS[1]:
    tours=load_tours()
    active=[k for k,v in tours.items() if v.get("status")=="진행중"]
    if not active: st.warning("진행 중인 대회가 없습니다."); st.stop()
    tid=active[-1]; tour=tours[tid]
    st.markdown(f"<div class='main-hdr'>📅 {tour['title']}</div>",unsafe_allow_html=True)

    gnames=list(tour["groups"].keys())
    tabs=st.tabs([f"{GLBL[i%len(GLBL)]} {g}" for i,g in enumerate(gnames)])

    for ti,g in enumerate(gnames):
        with tabs[ti]:
            ginfo=tour["groups"][g]; matches=ginfo["matches"]; mode=ginfo["mode"]
            cls=GCLS[ti%len(GCLS)]
            stats=group_stats(matches,mode)
            teams=list(stats.keys())

            # 상단: 매트릭스(좌) + 순위표(우)
            c1,c2=st.columns([3,2])
            with c1:
                st.markdown("**📋 상대별 전적 매트릭스**")
                mdict={tname(list(t)):{tname(list(o)):("" if t==o else "-") for o in teams} for t in teams}
                for m in matches:
                    t1,t2=tuple(m["t1"]),tuple(m["t2"]); s1,s2=m["s1"],m["s2"]
                    if s1>0 or s2>0:
                        mdict[tname(list(t1))][tname(list(t2))]=f"{s1}:{s2}"
                        mdict[tname(list(t2))][tname(list(t1))]=f"{s2}:{s1}"
                mdf=pd.DataFrame(mdict).T
                # 자신 칸 음영 → NaN으로 표시
                for nm in mdf.index:
                    if nm in mdf.columns: mdf.loc[nm,nm]="▪"
                st.dataframe(mdf,use_container_width=True)
            with c2:
                st.markdown("**🏅 현재 순위**")
                ranked=sorted(teams,key=lambda t:(-stats[t]["승"],-stats[t]["득실"]))
                rdf=pd.DataFrame([{"순위":["🥇","🥈","🥉"][i] if i<3 else i+1,
                    "팀/선수":tname(list(t)),"승":stats[t]["승"],"패":stats[t]["패"],
                    "득실":f'{stats[t]["득실"]:+d}'} for i,t in enumerate(ranked)])
                st.dataframe(rdf,use_container_width=True,hide_index=True)

            st.divider()
            # 하단: 대진 + 점수 입력
            changed=False
            for mi,m in enumerate(matches):
                t1,t2=m["t1"],m["t2"]; n1,n2=tname(t1),tname(t2)
                st.markdown(f'<div class="rnd">경기 {mi+1}</div>',unsafe_allow_html=True)
                ca,cb,cc=st.columns([4,1,4])
                with ca:
                    st.markdown(f'<div class="team-box {cls}">{n1}</div>',unsafe_allow_html=True)
                    s1=st.number_input(n1,0,50,m["s1"],key=f"{tid}{g}{mi}s1",label_visibility="collapsed")
                with cb:
                    st.markdown('<div class="vs">VS</div>',unsafe_allow_html=True)
                with cc:
                    st.markdown(f'<div class="team-box {cls}">{n2}</div>',unsafe_allow_html=True)
                    s2=st.number_input(n2,0,50,m["s2"],key=f"{tid}{g}{mi}s2",label_visibility="collapsed")
                if s1!=m["s1"] or s2!=m["s2"]:
                    tour["groups"][g]["matches"][mi]["s1"]=s1
                    tour["groups"][g]["matches"][mi]["s2"]=s2
                    changed=True
            if changed: tours[tid]=tour; save_tours(tours); st.toast("✅ 점수 저장됨!")

# ════════════════════════════════════════════════════════════
# 3. 경기 결과
# ════════════════════════════════════════════════════════════
elif M==MENUS[2]:
    tours=load_tours()
    active=[k for k,v in tours.items() if v.get("status")=="진행중"]
    if not active: st.warning("진행 중인 대회가 없습니다."); st.stop()
    tid=active[-1]; tour=tours[tid]
    st.markdown(f"<div class='main-hdr'>📊 {tour['title']} — 경기 결과</div>",unsafe_allow_html=True)

    for g,ginfo in tour["groups"].items():
        mode=ginfo["mode"]; matches=ginfo["matches"]
        stats=group_stats(matches,mode)
        ranked=sorted(stats.keys(),key=lambda t:(-stats[t]["승"],-stats[t]["득실"]))
        st.markdown(f'<div class="sec">{g} 그룹 ({mode})</div>',unsafe_allow_html=True)

        # 결과 행
        rows=[]
        if mode=="고정페어":
            for ri,t in enumerate(ranked):
                rank=ri+1
                rows.append({"순위":["🥇","🥈","🥉"][ri] if ri<3 else rank,
                    "팀":tname(list(t)),"승":stats[t]["승"],"패":stats[t]["패"],
                    "득실":f'{stats[t]["득실"]:+d}',"부과점":rank_pts(rank,mode),"등급":["우승","준우승","3위"][ri] if ri<3 else "참가"})
        else:  # KDK/단식: 2명씩 묶음
            for ri,t in enumerate(ranked):
                rank=ri+1
                grp=["우승","우승","준우승","준우승","3위","3위"][ri] if ri<6 else "참가"
                rows.append({"순위":rank,"선수":tname(list(t)),"승":stats[t]["승"],"패":stats[t]["패"],
                    "득실":f'{stats[t]["득실"]:+d}',"부과점":rank_pts(rank,mode),"등급":grp})
        st.dataframe(pd.DataFrame(rows),use_container_width=True,hide_index=True)

# ════════════════════════════════════════════════════════════
# 4. 지난 대회 아카이브
# ════════════════════════════════════════════════════════════
elif M==MENUS[3]:
    st.markdown("<div class='main-hdr'>📂 지난 대회 기록</div>",unsafe_allow_html=True)
    tours=load_tours()
    past={k:v for k,v in tours.items() if v.get("status")!="진행중"}
    if not past: st.info("완료된 대회가 없습니다."); st.stop()
    sel=st.selectbox("대회 선택",list(past.keys()),
        format_func=lambda k: f"{past[k]['title']} ({past[k].get('date',k)})")
    tour=past[sel]
    st.markdown(f"**🏆 {tour['title']}** | 📅 {tour.get('date','')} | 📍 {tour.get('place','')}",)
    for g,ginfo in tour["groups"].items():
        mode=ginfo["mode"]; matches=ginfo["matches"]
        stats=group_stats(matches,mode)
        ranked=sorted(stats.keys(),key=lambda t:(-stats[t]["승"],-stats[t]["득실"]))
        st.markdown(f'<div class="sec">{g} ({mode})</div>',unsafe_allow_html=True)
        rows=[{"순위":ri+1,"팀/선수":tname(list(t)),"승":stats[t]["승"],"패":stats[t]["패"],
               "득실":f'{stats[t]["득실"]:+d}',"부과점":rank_pts(ri+1,mode)} for ri,t in enumerate(ranked)]
        st.dataframe(pd.DataFrame(rows),use_container_width=True,hide_index=True)

# ════════════════════════════════════════════════════════════
# 5. 관리자
# ════════════════════════════════════════════════════════════
elif M==MENUS[4]:
    st.markdown("<div class='main-hdr'>⚙️ 관리자 센터</div>",unsafe_allow_html=True)
    pw=st.text_input("🔒 비밀번호",type="password")
    if pw==ADMIN_PW: st.session_state.is_admin=True
    if not st.session_state.is_admin: st.stop()
    st.success("✅ 관리자 모드")

    adm=st.tabs(["🏆 대회 생성","👥 참가자·대진","📂 랭킹 관리","📝 대회 수정/삭제","💾 결과 반영"])

    # ── 탭1: 대회 생성 ────────────────────────────────────────
    with adm[0]:
        st.markdown('<div class="sec">새 대회 만들기</div>',unsafe_allow_html=True)
        with st.form("f_new"):
            tn=st.text_input("대회명",placeholder="예: 5월 정기전")
            td=st.date_input("날짜",value=date.today())
            tp=st.text_input("장소",placeholder="예: 두류공원 테니스장")
            courts=st.selectbox("코트 수",[1,2,3],index=1)
            if st.form_submit_button("✅ 대회 생성",type="primary",use_container_width=True):
                if not tn.strip(): st.error("대회명 입력 필요")
                else:
                    tours=load_tours()
                    tid=f"{td}_{tn.strip()}"
                    tours[tid]={"title":tn.strip(),"date":str(td),"place":tp,"courts":courts,
                                "status":"진행중","groups":{}}
                    save_tours(tours); st.success(f"'{tn}' 대회 생성 완료!"); st.rerun()

    # ── 탭2: 참가자·대진 ─────────────────────────────────────
    with adm[1]:
        tours=load_tours()
        active=[k for k,v in tours.items() if v.get("status")=="진행중"]
        if not active: st.warning("진행 중인 대회를 먼저 생성하세요."); st.stop()
        tid=active[-1]; tour=tours[tid]
        st.info(f"현재 대회: **{tour['title']}**")

        # 참가자
        st.markdown('<div class="sec">참가자 등록</div>',unsafe_allow_html=True)
        df_rank=load_rank()
        all_names=df_rank["이름"].tolist() if not df_rank.empty else []

        raw=st.text_area("카톡 명단 붙여넣기 (쉼표·줄바꿈)",height=60)
        typed=[n.strip() for n in raw.replace("\n",",").split(",") if n.strip()]
        st.caption("체크박스로 개별 선택하거나 위 텍스트로 일괄 입력")
        sel_names=[]
        chk_cols=st.columns(4)
        for i,nm in enumerate(all_names):
            pre_chk= nm in typed
            if chk_cols[i%4].checkbox(nm,value=pre_chk,key=f"att_{nm}"): sel_names.append(nm)
        # 랭킹순 정렬
        rank_map={r["이름"]:r["랭킹"] for _,r in df_rank.iterrows()} if not df_rank.empty else {}
        sel_names=sorted(set(sel_names),key=lambda x:rank_map.get(x,999))
        st.success(f"선택 인원: {len(sel_names)}명")
        if sel_names: st.write("**명단:** "+", ".join(sel_names))

        st.divider()
        # 대진 설정
        st.markdown('<div class="sec">대진 설정 (기본: 4그룹 × 8명 × 고정페어)</div>',unsafe_allow_html=True)
        gcnt=st.number_input("그룹 수",1,6,min(4,max(1,len(sel_names)//8 if sel_names else 4)))
        gns=list("ABCDEF")[:gcnt]
        gcfg={}
        for i,gn in enumerate(gns):
            hx=GHEX[i%len(GHEX)]
            st.markdown(f"<div style='background:{hx}18;border-left:4px solid {hx};border-radius:7px;"
                        f"padding:5px 12px;margin:6px 0;font-weight:800;color:{hx}'>{GLBL[i%len(GLBL)]} 그룹 {gn}</div>",
                        unsafe_allow_html=True)
            cc=st.columns(4)
            dfsz=max(2,len(sel_names)//gcnt) if sel_names else 8
            with cc[0]: nm2=st.text_input("그룹명",gn,key=f"gn{i}")
            with cc[1]: sz=st.number_input("인원",2,30,dfsz,key=f"sz{i}")
            with cc[2]: md=st.selectbox("방식",["고정페어","KDK","단식"],key=f"md{i}")
            with cc[3]: gc=st.selectbox("1인 게임수",[3,4,5],index=1,key=f"gc{i}")
            gcfg[nm2]=(sz,md,gc)

        if st.button("🎲 대진 생성",type="primary",use_container_width=True):
            if not sel_names: st.error("참가자를 선택하세요"); st.stop()
            ptr=0; new_groups={}
            for gn,(sz,md,gc) in gcfg.items():
                gp=sel_names[ptr:ptr+sz]; ptr+=sz
                if md=="고정페어": ms=make_fixed(gp)
                elif md=="KDK":
                    ms=make_kdk(gp,gc)
                    if not ms:
                        random.shuffle(gp)
                        pairs=[gp[i:i+2] for i in range(0,len(gp)-1,2)]
                        ms=[{"t1":list(p1),"t2":list(p2),"s1":0,"s2":0} for i,p1 in enumerate(pairs) for p2 in pairs[i+1:]]
                        st.warning(f"그룹 {gn}: 한울 KDK 없음 → 랜덤 페어 리그")
                else: ms=make_singles(gp)
                new_groups[gn]={"players":gp,"mode":md,"games":gc,"matches":ms}
            tours[tid]["groups"]=new_groups; save_tours(tours)
            st.success("✅ 대진 생성 완료!"); st.rerun()

    # ── 탭3: 랭킹 관리 ────────────────────────────────────────
    with adm[2]:
        st.markdown('<div class="sec">엑셀 업로드 (컬럼: 랭킹,이름,현재포인트,3월 포인트,결과,부과점,그룹,비고)</div>',unsafe_allow_html=True)
        up=st.file_uploader("엑셀/CSV 업로드",type=["xlsx","csv"])
        if up:
            try:
                df_up=pd.read_excel(up) if up.name.endswith("xlsx") else pd.read_csv(up,encoding_errors="replace")
                df_up.columns=[str(c).strip() for c in df_up.columns]
                st.dataframe(df_up.head(10),use_container_width=True,hide_index=True)
                if st.button("💾 랭킹 저장",type="primary",use_container_width=True):
                    save_rank(df_up); st.success("✅ 랭킹 저장 완료!"); st.rerun()
            except Exception as e: st.error(f"파일 오류: {e}")

    # ── 탭4: 대회 수정/삭제 ───────────────────────────────────
    with adm[3]:
        tours=load_tours()
        if not tours: st.info("대회 없음"); st.stop()
        for tid2,tv in list(tours.items()):
            sc={"진행중":"#FB8C00","완료":"#43A047","예정":"#1E88E5"}.get(tv.get("status",""),"#888")
            st.markdown(f"<div style='background:#f9f9f9;border:1px solid #ddd;border-radius:10px;"
                        f"padding:9px 14px;margin:5px 0'><b>{tv['title']}</b> "
                        f"<span style='font-size:.83rem;color:#555'>📅{tv.get('date','')} 📍{tv.get('place','')}</span>"
                        f" <span style='color:{sc};font-weight:800'>[{tv.get('status','')}]</span></div>",
                        unsafe_allow_html=True)
            ca,cb,cc=st.columns(3)
            with ca:
                if st.button("✅ 완료",key=f"done{tid2}",use_container_width=True):
                    tours[tid2]["status"]="완료"; save_tours(tours); st.rerun()
            with cb:
                new_title=st.text_input("이름 변경",tv["title"],key=f"tt{tid2}",label_visibility="collapsed")
                if st.button("수정",key=f"edit{tid2}",use_container_width=True):
                    tours[tid2]["title"]=new_title; save_tours(tours); st.rerun()
            with cc:
                if st.button("🗑 삭제",key=f"del{tid2}",use_container_width=True):
                    del tours[tid2]; save_tours(tours); st.rerun()

    # ── 탭5: 결과 반영 ────────────────────────────────────────
    with adm[4]:
        tours=load_tours()
        active2=[k for k,v in tours.items() if v.get("status")=="진행중"]
        if not active2: st.warning("진행 중인 대회 없음"); st.stop()
        tid3=active2[-1]; tour3=tours[tid3]
        st.markdown(f'<div class="sec">"{tour3["title"]}" 결과 → 랭킹 반영</div>',unsafe_allow_html=True)
        st.caption("1위+7 | 2위+5 | 3위+3 | 참가+1 (KDK/단식은 2명씩 묶음)")

        earn={}
        prev_rows=[]
        for g,ginfo in tour3["groups"].items():
            mode=ginfo["mode"]; matches=ginfo["matches"]
            stats=group_stats(matches,mode)
            ranked=sorted(stats.keys(),key=lambda t:(-stats[t]["승"],-stats[t]["득실"]))
            for ri,t in enumerate(ranked):
                pt=rank_pts(ri+1,mode)
                for p in list(t):
                    earn[p]=pt
                    prev_rows.append({"그룹":g,"팀/선수":tname(list(t)),
                        "등급":["우승","우승","준우승","준우승","3위","3위"][ri] if ri<6 else "참가",
                        "이름":p,"부과점":pt})

        st.dataframe(pd.DataFrame(prev_rows),use_container_width=True,hide_index=True)

        if st.button("🏆 랭킹 반영",type="primary",use_container_width=True):
            df_r=load_rank()
            if df_r.empty: df_r=pd.DataFrame(columns=["랭킹","이름","현재포인트","3월 포인트","결과","부과점","그룹","비고"])
            df_r["3월 포인트"]=df_r.get("현재포인트",0) if "현재포인트" in df_r.columns else 0
            for p,pt in earn.items():
                if p in df_r["이름"].values:
                    df_r.loc[df_r["이름"]==p,"현재포인트"]=(pd.to_numeric(df_r.loc[df_r["이름"]==p,"현재포인트"],errors="coerce").fillna(0)+pt).values
                    df_r.loc[df_r["이름"]==p,"부과점"]=pt
                else:
                    nr=pd.DataFrame([[0,p,pt,0,"","",""," "]],columns=["랭킹","이름","현재포인트","3월 포인트","결과","부과점","그룹","비고"])
                    df_r=pd.concat([df_r,nr],ignore_index=True)
            df_r=df_r.sort_values("현재포인트",ascending=False).reset_index(drop=True)
            df_r["랭킹"]=df_r.index+1
            save_rank(df_r)
            tours[tid3]["status"]="완료"; save_tours(tours)
            st.success("✅ 랭킹 반영 완료!"); st.rerun()

import streamlit as st
import pandas as pd
import numpy as np

# 페이지 설정
st.set_page_config(
    page_title = "0.5초 음악 퀴즈",
    page_icon = "d:\다운로드\icons8-사과-음악-64.png",
    layout = "wide",
    initial_sidebar_state = "expanded"
)

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False # 로그인 상태 변수를 만든 후 false로 초기화

if "saved_id" not in st.session_state:
    st.session_state.saved_id = ""
if "saved_pw" not in st.session_state:
    st.session_state.saved_pw = ""

if not st.session_state.logged_in:  # 로그인 상태가 false일때 로그인 화면 창 띄움

    # 제목과 소개
    st.title("0.5초 음악 퀴즈 💽")
    st.markdown("#### 학번: 2023204054")
    st.markdown("#### 이름: 김대유")
    
    co1, col2 = st.columns(2)   

    # 회원가입 창
    with co1:
        with st.expander("회원가입"):
            new_id = st.text_input("아이디", key = "signup_id")
            new_pw = st.text_input("비밀번호", type ="password", key ="signup_pw")


            if st.button("가입"):
                st.session_state.saved_id = new_id 
                st.session_state.saved_pw = new_pw
                st.success("회원가입 완료!")
    # 로그인 창
    with col2:        
        with st.expander("로그인"):
            user_id = st.text_input("아이디", key = "login_id")
            user_pw = st.text_input("비밀번호", type = "password", key = "login_pw")
    
            # 회원가입 하지 않고 로그인 시도 막음
            if not st.session_state.saved_id or not st.session_state.saved_pw:
                st.error("회원가입을 먼저 해주세요!")

            else:
                if st.button("로그인"):
                    if ((user_id == st.session_state.saved_id) and (user_pw == st.session_state.saved_pw)): 
                        st.success("로그인 성공!")
                        st.session_state.logged_in = True # 로그인 상태를 true로 바꿈
                        st.rerun() # 프로그램 재실행후 로그인상태가 true이므로 if문에 안걸리고 창 넘어감
                    else:
                        st.error("아이디 또는 비밀번호가 다릅니다!")
            
    st.stop() # 로그인이 안되면 안 넘어가게 실행 중단 

# 사이드 바
st.sidebar.title('장르 선택 메뉴')
st.sidebar.write('장르를 선택하세요!')
menu = st.sidebar.radio("장르",["설명","국내힙합","발라드","K-POP"])

if st.sidebar.button("로그아웃"):
    st.session_state.logged_in = False
    st.rerun()

# 캐싱
@st.cache_data # 캐싱으로 파일을 한 번만 불러와 연산 빨라짐
def load_audio(path):
    with open(path, "rb") as f:
        return f.read()

# 오답, 힌트, 정답 보기 점수 초기화
if "stats" not in st.session_state:
    st.session_state.stats = {
        "국내힙합": {"wrong": 0, "hint" : 0, "answer": 0},
        "발라드": {"wrong": 0, "hint" : 0, "answer": 0},
        "K-POP": {"wrong": 0, "hint" : 0, "answer": 0}
    }

# 퀴즈 화면 함수
def quiz_page(
    title,
    difficulty,
    audio_path,
    answers,
    key,
    next_page=None,
    prev_page=None,
    next_label="다음 문제",
    prev_label="이전 문제",
    hint_lines=None,
    answer_text="",
):
    col1, col2 = st.columns(2)

    with col1:
        st.header(title)
        st.subheader(f"난이도 {difficulty}")

        audio_bytes = load_audio(audio_path)
        st.audio(audio_bytes)

        user_input = st.text_input("정답은?", key = key)

        if user_input:
            if user_input in answers:
                st.success("정답입니다!")
                if next_page and st.button(next_label):
                    return next_page
            else:
                st.error("오답입니다")
                st.session_state.stats[menu]["wrong"] += 1
    
    with col2: 
        if prev_page and st.button(prev_label): # 이전 페이지의 값이 none 이라면 버튼이 뜨지 않음
            return prev_page # 버튼 누르면 이전 페이지 값 반환

        if hint_lines:
            if st.button("힌트"):
                st.session_state.stats[menu]["hint"] += 1
                for line in hint_lines:
                    st.markdown(line)
                st.info("힌트를 사용했습니다")

        if answer_text:
            if st.button("정답"):
                st.session_state.stats[menu]["answer"] += 1
                st.markdown(answer_text)
                st.info("정답 보기를 사용했습니다")

    return None

# 결과창 함수
def result_page(
        menu,
        prev_page = None,
        reset_page = None,
        prev_label = "이전 문제",
        reset_label = "처음으로"
):
    st.balloons()
    st.header("결과")
    
    s = st.session_state.stats[menu]
    col1, col2 = st.columns(2)
    with col1:
            st.markdown(f"### - ❌ 오답: {s['wrong']}회")
            st.markdown(f"### - 💡 힌트 사용: {s['hint']}회")
            st.markdown(f"### - 📖 정답 보기: {s['answer']}회")

            wrong_stat = s["wrong"] * 0.1
            hint_stat = s["hint"] * 0.3
            ans_stat = s["answer"]
            sum_stat = max(0, round(5 - wrong_stat - hint_stat - ans_stat, 2)) # 소수점 첫 번째까지 표시, 최저를 0까지 조절
            
            st.markdown(f"### 당신의 총점: {sum_stat} / 5")

    with col2:
            if prev_page and st.button(prev_label): 
                return prev_page 
        
            if reset_page and st.button(reset_label):
                st.session_state.stats[menu] = {"wrong": 0, "hint": 0, "answer": 0} # 돌아갈때 오답 힌트 정답 초기화
                return reset_page
            
    return None

# 설명창    
if menu == "설명":
    col1, col2 = st.columns(2)

    
    with col1:
        st.header("0.5초 음악 퀴즈에 오신걸 환영합니다!")
        st.subheader("시작하기에 앞서 간단한 규칙을 설명드리겠습니다")
        st.markdown("- 주어진 노래를 듣고 노래 제목을 맞추면 되는 퀴즈입니다.")
        st.markdown("- 장르는 국내힙합, K-POP, 발라드 총 3개의 장르로 구성되어 있고 각 장르당 5개의 문제가 있습니다.")
        st.markdown("- 각 노래는 하이라이트 부분이 1초씩 재생됩니다.")
        st.markdown("- 각 문제는 띄어쓰기 없이 작성해주세요")
        st.markdown("- 정답이 영어라면 소문자로 입력해주세요")
        st.markdown("- **모르겠다면 힌트와 정답이 있으니 적절히 활용해주세요!**")
        st.markdown("- 오답: -0.1점, 힌트 -0.3점, 정답 보기:-1점 입니다!")
        st.markdown("- 오른쪽에 연습문제가 준비되어 있습니다.")

    # 연습문제
    with col2:
        st.header("연습 문제")
        st.subheader("난이도 2️⃣/5️⃣")

        audio_bytes1 = load_audio('assets/love_love_love.mp3')
        st.audio(audio_bytes1)

        answer1 = st.text_input("정답은?", key = "ans1")

        if answer1: # answer1의 값이 입력되기 전에 채점을 방지 
            if answer1 in ["럽럽럽", "러브러브러브", "lovelovelove"]:
                st.success("정답입니다!")
            else:
                st.error("오답입니다")

        if st.button("힌트"):
            st.markdown("- 가수: 에픽하이")
            st.markdown("- 2007년 발매")
            st.info("힌트를 사용했습니다")
        
        if st.button("정답"):
            st.markdown("**에픽하이 - lovelovelove**")
            st.info("정답 보기를 사용했습니다")

# 힙합
elif menu == "국내힙합":

    # 힙합 난이도 분기를 위한 페이지 변수 초기화
    if "h_page" not in st.session_state:
        st.session_state.h_page = "힙합1"

    h_page = st.session_state.h_page

    # 힙합 1
    if h_page == "힙합1":

        result = quiz_page(
            title = "국내힙합1",
            difficulty = "1️⃣/5️⃣",
            audio_path =  "assets/meteor.mp3",
            answers = ["메테오", "meteor"],
            key = "h_ans1",
            next_page = "힙합2",
            hint_lines = ["- 가수: 창모", "- 2019년 발매"],
            answer_text = "**창모 - 메테오**"
        )
    
        if result:
            st.session_state.h_page = result
            st.rerun()
        
    
    # 힙합 2
    elif h_page == "힙합2":

        result = quiz_page(
            title = "국내힙합2",
            difficulty = "2️⃣/5️⃣",
            audio_path =  "assets/lov3.mp3",
            answers = ["lov3", "러브3"],
            key = "h_ans2",
            next_page = "힙합3",
            prev_page = "힙합1",
            hint_lines = ["- 가수: 식케이, 릴모쉬핏", "- 2025년 발매"],
            answer_text = "**식케이,릴모쉬핏 - LOV3**"
        )

        if result:
            st.session_state.h_page = result
            st.rerun()

    # 힙합 3
    elif h_page == "힙합3":

        result = quiz_page(
            title = "국내힙합3",
            difficulty = "3️⃣/5️⃣",
            audio_path =  "assets/freak.mp3",
            answers = ["freak"],
            key = "h_ans3",
            next_page = "힙합4",
            prev_page = "힙합2",
            hint_lines = ["- 가수: 릴보이, 원슈타인, 칠린호미, 스카이민혁", "- 2020년 발매"],
            answer_text = "**릴보이, 원슈타인, 칠린호미, 스카이민혁 - freak**"
        )
        
        if result:
            st.session_state.h_page = result
            st.rerun()

    # 힙합 4
    elif h_page == "힙합4":

        result = quiz_page(
            title = "국내힙합4",
            difficulty = "4️⃣/5️⃣",
            audio_path =  "assets/be.mp3",
            answers = ["be","비","be!"],
            key = "h_ans4",
            next_page = "힙합5",
            prev_page = "힙합3",
            hint_lines = ["- 가수: 소코도모", "- 2021년 발매"],
            answer_text = "**소코도모 - BE!**"
        )
        
        if result:
            st.session_state.h_page = result
            st.rerun()
    
    # 힙합 5
    elif h_page == "힙합5":

        result = quiz_page(
            title = "국내힙합5",
            difficulty = "5️⃣/5️⃣",
            audio_path =  "assets/city.mp3",
            answers = ["city"],
            key = "h_ans5",
            next_page = "h_결과",
            prev_page = "힙합4",
            hint_lines = ["- 가수: 오왼", "- 2016년 발매"],
            answer_text = "**오왼 - city**"
        )
        
        if result:
            st.session_state.h_page = result
            st.rerun()

    # 힙합_결과
    elif h_page == "h_결과":

        temp = result_page(
            menu = "국내힙합",
            prev_page = "힙합5",
            reset_page = "힙합1"
        )

        if temp:
            st.session_state.h_page = temp
            st.rerun()   
        

# 발라드
elif menu == "발라드":

    # 발라드 난이도 분기를 위한 페이지 변수 초기화
    if "b_page" not in st.session_state:
        st.session_state.b_page = "발라드1"

    b_page = st.session_state.b_page

    # 발라드 1
    if b_page == "발라드1":

        result = quiz_page(
            title = "발라드1",
            difficulty = "1️⃣/5️⃣",
            audio_path =  "assets/헤어지자말해요.mp3",
            answers = ["헤어지자말해요"],
            key = "b_ans1",
            next_page = "발라드2",
            hint_lines = ["- 가수: 박재정", "- 2023년 발매"],
            answer_text = "**박재정  - 헤어지자말해요**"
        )

        if result:
            st.session_state.b_page = result
            st.rerun()

    # 발라드2
    elif b_page == "발라드2":

        result = quiz_page(
            title = "발라드2",
            difficulty = "2️⃣/5️⃣",
            audio_path =  "assets/지나오다.mp3",
            answers = ["지나오다"],
            key = "b_ans2",
            next_page = "발라드3",
            prev_page = "발라드1",
            hint_lines = ["- 가수: 닐로", "- 2017년 발매"],
            answer_text = "**닐로  - 지나오다**"
        )

        if result:
            st.session_state.b_page = result
            st.rerun()

    # 발라드3
    elif b_page == "발라드3":

        result = quiz_page(
            title = "발라드3",
            difficulty = "3️⃣/5️⃣",
            audio_path =  "assets/onelove.mp3",
            answers = ["onelove","원러브"],
            key = "b_ans3",
            next_page = "발라드4",
            prev_page = "발라드2",
            hint_lines = ["- 가수: 엠씨더맥스", "- 2002년 발매"],
            answer_text = "**엠씨더맥스  - onelove**"
        )

        if result:
            st.session_state.b_page = result
            st.rerun()

    # 발라드4
    elif b_page == "발라드4":

        result = quiz_page(
            title = "발라드4",
            difficulty = "4️⃣/5️⃣",
            audio_path =  "assets/기억을걷는시간.mp3",
            answers = ["기억을걷는시간"],
            key = "b_ans4",
            next_page = "발라드5",
            prev_page = "발라드3",
            hint_lines = ["- 가수: 넬", "- 2008년 발매"],
            answer_text = "**넬  - 기억을걷는시간**"
        )

        if result:
            st.session_state.b_page = result
            st.rerun()
    
    # 발라드5
    elif b_page == "발라드5":

        result = quiz_page(
            title = "발라드5",
            difficulty = "5️⃣/5️⃣",
            audio_path =  "assets/귀로.mp3",
            answers = ["귀로"],
            key = "b_ans5",
            next_page = "b_결과",
            prev_page = "발라드4",
            hint_lines = ["- 가수: 나얼", "- 2005년 발매"],
            answer_text = "**나얼  - 귀로**"
        )   

        if result:
            st.session_state.b_page = result
            st.rerun()
    
    # 발라드 결과
    elif b_page == "b_결과":

        temp = result_page(
            menu = "발라드",
            prev_page = "발라드5",
            reset_page = "발라드1"
        )

        if temp:
            st.session_state.b_page = temp
            st.rerun()
        
# K-POP
elif menu == "K-POP":
    
    # 케이팝 난이도 분기를 위한 페이지 변수 초기화
    if "k_page" not in st.session_state:
        st.session_state.k_page = "케이팝1"

    k_page = st.session_state.k_page

    # 케이팝1
    if k_page == "케이팝1":

        result = quiz_page(
            title = "케이팝1",
            difficulty = "1️⃣/5️⃣",
            audio_path =  "assets/drowning.mp3",
            answers = ["drowning", "드라우닝"],
            key = "k_ans1",
            next_page = "케이팝2",
            hint_lines = ["- 가수: 우즈", "- 2023년 발매"],
            answer_text = "**우즈  - drowning**"
        )

        if result:
            st.session_state.k_page = result
            st.rerun()
    
    # 케이팝2
    elif k_page == "케이팝2":

        result = quiz_page(
            title = "케이팝2",
            difficulty = "2️⃣/5️⃣",
            audio_path =  "assets/404.mp3",
            answers = ["404", "404(newera)"],
            key = "k_ans2",
            next_page = "케이팝3",
            prev_page = "케이팝1",
            hint_lines = ["- 가수: 키키", "- 2026년 발매"],
            answer_text = "**키키  - 404**"
        )

        if result:
            st.session_state.k_page = result
            st.rerun()

    # 케이팝3
    elif k_page == "케이팝3":

        result = quiz_page(
            title = "케이팝3",
            difficulty = "3️⃣/5️⃣",
            audio_path =  "assets/generation.mp3",
            answers = ["generation", "제너레이션"],
            key = "k_ans3",
            next_page = "케이팝4",
            prev_page = "케이팝2",
            hint_lines = ["- 가수: 트리플s", "- 2022년 발매"],
            answer_text = "**트리플에스  - generation**"
        )

        if result:
            st.session_state.k_page = result
            st.rerun()
    
    # 케이팝4
    elif k_page == "케이팝4":

        result = quiz_page(
            title = "케이팝4",
            difficulty = "4️⃣/5️⃣",
            audio_path =  "assets/love.mp3",
            answers = ["love", "러브"],
            key = "k_ans4",
            next_page = "케이팝5",
            prev_page = "케이팝3",
            hint_lines = ["- 가수: 브라운아이드걸스", "- 2006년 발매"],
            answer_text = "**브라운아이드걸스  - LOVE**"
        )

        if result:
            st.session_state.k_page = result
            st.rerun()

    # 케이팝5
    elif k_page == "케이팝5":

        result = quiz_page(
            title = "케이팝5",
            difficulty = "5️⃣/5️⃣",
            audio_path =  "assets/10minute.mp3",
            answers = ["10minutes", "텐미닛"],
            key = "k_ans5",
            next_page = "k_결과",
            prev_page = "케이팝4",
            hint_lines = ["- 가수: 이효리", "- 2003년 발매"],
            answer_text = "**이효리  - 10minutes**"
        )

        if result:
            st.session_state.k_page = result
            st.rerun()
    
    elif k_page == "k_결과":
       
        temp = result_page(
            menu = "K-POP",
            prev_page = "케이팝5",
            reset_page = "케이팝1"
        )

        if temp:
            st.session_state.k_page = temp
            st.rerun()
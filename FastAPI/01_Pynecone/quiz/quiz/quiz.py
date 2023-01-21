"""Welcome to Pynecone! This file outlines the steps to create a basic app."""
import pynecone as pc
from .results import results

question_style = {
    "bg": "white",
    "padding": "2em",
    "border_radius": "25px",
    "w": "100%",
    "align_items": "left",
}


class State(pc.State):
    """The app state."""

    enneagram2 = [False, False, False, False]
    answer_key = ["False", "[10, 20, 30, 40]", [False, False, True, True, True]]
    score: int
    selected: str = "INTJ"
    enneagram1: str = "No Selection"

    def set_enneagram2(self, answer, sub_index=None):
        if sub_index is None:
            self.enneagram2 = answer
        else:
            self.enneagram2[sub_index] = answer
        print(self.enneagram2)

    def submit(self):
        self.score = 100
        return pc.redirect("/result")


def header():
    return pc.vstack(
        pc.heading("MBTI 기반 추천"),
        style=question_style,
    )


def question1():
    """Choose MBTI Question"""
    mbtis = [
        "INTJ",
        "INTP",
        "INFJ",
        "INFP",
        "ISTJ",
        "ISTP",
        "ISFJ",
        "ISFP",
        "ENTJ",
        "ENTP",
        "ENFJ",
        "ENFP",
        "ESTJ",
        "ESTP",
        "ESFJ",
        "ESFP",
    ]
    return pc.vstack(
        pc.heading("Question #1"),
        pc.text("MBTI를 골라주세요."),
        pc.divider(),
        pc.select(
            mbtis,
            on_change=State.set_selected,
        ),
        style=question_style,
    )


def question2():
    return pc.vstack(
        pc.heading("Question #2"),
        pc.text("주의! 희망사항이 아니라 실제 어떻게 행동할건가에 대해 답변입니다."),
        pc.code_block(
            """처음보는 사람들이 20명 이상 모여있는 방에 들어가려고 한다. 이때의 나는?
ex) 학교 교실, 예비군훈련""",
            language="markdown",
        ),
        pc.radio_group(
            ["나는 여기서 중요한 인물이다.", "여기서 내 역할은 뭘까?", "여기서 일어나는 일에 엮이고 싶지 않아.", "모르겠다."],
            on_change=State.set_enneagram1,
        ),
        style=question_style,
    )


def question3():
    return pc.vstack(
        pc.heading("Question #3"),
        pc.code_block(
            """나에게 어떤 문제가 생겼다. 남들에 비해 **상대적으로 나는 어떤 편**인가?
여기서의 문제는 **누구에게나 생길 수 있는 사소한(?) 문제**이다.""",
            language="markdown",
        ),
        pc.vstack(
            pc.checkbox(
                pc.text("잘 되겠지 뭐..."),
                on_change=lambda answer: State.set_enneagram2(answer, 0),
            ),
            pc.checkbox(
                pc.text("해결할 방법을 생각해보자."),
                on_change=lambda answer: State.set_enneagram2(answer, 1),
            ),
            pc.checkbox(
                pc.text("어휴~ 속상해..(짜증나 등등)"),
                on_change=lambda answer: State.set_enneagram2(answer, 2),
            ),
            pc.checkbox(
                pc.text("모르겠다."),
                on_change=lambda answer: State.set_enneagram2(answer, 3),
            ),
            align_items="left",
        ),
        style=question_style,
    )


def index():
    """The main view."""
    return pc.center(
        pc.vstack(
            header(),
            question1(),
            question2(),
            question3(),
            pc.button(
                "Submit",
                bg="black",
                color="white",
                width="6em",
                padding="1em",
                on_click=State.submit,
            ),
            spacing="1em",
        ),
        padding_y="2em",
        height="100vh",
        align_items="top",
        bg="#ededed",
        overflow="auto",
    )


def result():
    return results(State)


# Add state and page to the app.
app = pc.App(state=State)
app.add_page(index, title="Pynecone Quiz")
app.add_page(result, title="Quiz Results")
app.compile()

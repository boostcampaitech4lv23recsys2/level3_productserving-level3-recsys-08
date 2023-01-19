import pynecone as pc

answer_style = {
    "border_radius": "10px",
    "border": "1px solid #ededed",
    "padding": "0.5em",
    "align_items": "left",
    "shadow": "0px 0px 5px 0px #ededed",
}


def render_answer(State, index):
    # print(int(index))
    return pc.tr(
        pc.td(index + 1),
        pc.td(
            pc.cond(
                True,
                pc.icon(tag="CheckIcon", color="green"),
                pc.icon(tag="CloseIcon", color="red"),
            ),
        ),
        pc.td(
            pc.circular_progress(
                pc.circular_progress_label(100),
                value=100,
                size="3em",
            )
        ),
        pc.td(State.enneagram2[index].to_string()),
    )


def results(State):
    """The results view."""
    return pc.center(
        pc.vstack(
            pc.heading("추천 결과"),
            pc.text("Below are the results of the quiz."),
            pc.divider(),
            pc.table(
                pc.thead(pc.tr(pc.th("#"), pc.th("Result"), pc.th("유사도"), pc.th("하하"))),
                pc.foreach(State.enneagram2, lambda answer, i: render_answer(State, i)),
            ),
            pc.link(pc.button("Take Quiz Again"), href="/"),
            bg="white",
            padding_x="5em",
            padding_y="2em",
            border_radius="25px",
            align_items="left",
            overflow="auto",
        ),
        padding="1em",
        height="100vh",
        align_items="top",
        bg="#ededed",
        overflow="auto",
    )

from fractions import Fraction

import streamlit as st


OPERATORS = {"+", "-", "*", "/"}
BUTTON_ROWS = [
    ["7", "8", "9", "/"],
    ["4", "5", "6", "*"],
    ["1", "2", "3", "-"],
    ["0", "C", "=", "+"],
]

BUTTON_LABELS = {
    "+": "+",
    "-": "−",
    "*": "×",
    "/": "÷",
}


def _tokenize(expression: str) -> list[str]:
    tokens: list[str] = []
    current = []

    for char in expression.replace(" ", ""):
        if char.isdigit():
            current.append(char)
            continue

        if char in OPERATORS:
            if current:
                tokens.append("".join(current))
                current = []
            tokens.append(char)

    if current:
        tokens.append("".join(current))

    return tokens


def _apply_operator(left: Fraction, operator: str, right: Fraction) -> Fraction:
    if operator == "+":
        return left + right
    if operator == "-":
        return left - right
    if operator == "*":
        return left * right
    if operator == "/":
        if right == 0:
            raise ZeroDivisionError("Division by zero is not allowed")
        return left / right
    raise ValueError(f"Unsupported operator: {operator}")


def _evaluate_expression(expression: str) -> Fraction:
    tokens = _tokenize(expression)
    if not tokens:
        return Fraction(0, 1)

    values: list[Fraction] = []
    operators: list[str] = []
    precedence = {"+": 1, "-": 1, "*": 2, "/": 2}

    def reduce_once() -> None:
        right = values.pop()
        left = values.pop()
        operator = operators.pop()
        values.append(_apply_operator(left, operator, right))

    for token in tokens:
        if token in OPERATORS:
            while operators and precedence[operators[-1]] >= precedence[token]:
                reduce_once()
            operators.append(token)
        else:
            values.append(Fraction(int(token), 1))

    while operators:
        reduce_once()

    if len(values) != 1:
        raise ValueError("Invalid calculator expression")

    return values[0]


def _format_fraction(value: Fraction) -> str:
    if value.denominator == 1:
        return str(value.numerator)
    return f"{value.numerator}/{value.denominator}"


def _append_input(symbol: str) -> None:
    if st.session_state.just_evaluated and symbol.isdigit():
        st.session_state.expression = symbol
        st.session_state.just_evaluated = False
        return

    st.session_state.expression += symbol
    st.session_state.just_evaluated = False


def _clear() -> None:
    st.session_state.expression = ""
    st.session_state.result = ""
    st.session_state.error = ""
    st.session_state.just_evaluated = False


def _calculate() -> None:
    expression = st.session_state.expression.strip()
    if not expression:
        st.session_state.result = "0"
        st.session_state.error = ""
        st.session_state.just_evaluated = True
        return

    try:
        result = _evaluate_expression(expression)
        st.session_state.result = _format_fraction(result)
        st.session_state.error = ""
        st.session_state.just_evaluated = True
    except Exception as exc:
        st.session_state.result = ""
        st.session_state.error = str(exc)
        st.session_state.just_evaluated = False


def main() -> None:
    st.set_page_config(page_title="Rational Calculator", page_icon="🧮", layout="centered")
    st.title("Rational Number Calculator")
    st.caption("Exact arithmetic with fractions using Streamlit buttons.")

    st.session_state.setdefault("expression", "")
    st.session_state.setdefault("result", "")
    st.session_state.setdefault("error", "")
    st.session_state.setdefault("just_evaluated", False)

    display_value = st.session_state.expression or st.session_state.result or "0"
    st.text_input("Display", value=display_value, disabled=True, label_visibility="collapsed")

    if st.session_state.error:
        st.error(st.session_state.error)
    elif st.session_state.result:
        st.success(st.session_state.result)

    for row in BUTTON_ROWS:
        columns = st.columns(len(row))
        for column, label in zip(columns, row):
            with column:
                button_label = BUTTON_LABELS.get(label, label)
                if st.button(button_label, key=f"button_{label}_{row.index(label)}", use_container_width=True):
                    if label == "C":
                        _clear()
                    elif label == "=":
                        _calculate()
                    else:
                        _append_input(label)
                    st.rerun()


if __name__ == "__main__":
    main()
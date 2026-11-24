"""Build the two Burden & Faires exercise collections from a local 9th-ed. PDF.

Usage: python scripts/build_burden_phase1.py [--pdf PATH] [--check | --dry-run]
Requires pymupdf and numpy. PDF page numbers below are one-based.
"""

import argparse
import json
import math
import re
import unicodedata
from decimal import Decimal as D, ROUND_DOWN, ROUND_HALF_UP, getcontext
from fractions import Fraction
from pathlib import Path

import numpy as np
import pymupdf


ROOT = Path(__file__).resolve().parents[1]
LETTERS = "abcdefgh"
PI = D("3.141592653589793238462643383279502884197169399375105821")
ERROR = (r"$E=|v-v^*|$ và $\varepsilon_t=E/|v|$ (sai số tương đối dạng tỉ số, "
         r"không nhân $100$).")
FP = (r"Đưa toán hạng về $k$ chữ số có nghĩa; áp dụng $\operatorname{fl}_k$ sau từng phép toán. "
      "Làm tròn lấy chữ số kế tiếp từ 5 trở lên; chặt cụt bỏ các chữ số dư về phía 0. ")
TAGS = ("Round-off Error", "Floating-Point Arithmetic", "Horner's Method",
        "Lagrange Interpolation")
GLOSSARY = (
    {"absolute error": "sai số tuyệt đối", "relative error": "sai số tương đối",
     "cancellation": "triệt tiêu chữ số có nghĩa"},
    {"significant digit": "chữ số có nghĩa", "rounding": "làm tròn", "chopping": "chặt cụt",
     "floating-point arithmetic": "số học dấu phẩy động"},
    {"nested arithmetic": "số học dạng lồng", "expanded form": "dạng khai triển",
     "round-off error": "sai số làm tròn"},
    {"interpolation node": "nút nội suy", "Lagrange basis": "cơ sở Lagrange",
     "interpolating polynomial": "đa thức nội suy", "error bound": "chặn sai số"},
)


def page_text(pdf, page):
    return unicodedata.normalize("NFKC", pdf[page - 1].get_text()).split("Copyright 2010")[0].strip()


def extract(pdf):
    """Extract exercise blocks and selected answers, excluding headers and footers."""
    p = {i: page_text(pdf, i) for i in (*range(44, 50), 132, 133, 134, 793, 794, 800)}
    sec12 = [p[46].split("E X E R C I S E S E T 1.2\n", 1)[1],
             *("\n".join(p[i].splitlines()[3:]) for i in (47, 48, 49))]
    sec31 = [p[132].split("E X E R C I S E S E T 3.1\n", 1)[1],
             *("\n".join(p[i].splitlines()[3:]) for i in (133, 134))]

    def blocks(pages):
        parts = re.split(r"(?m)^(\d+)\.\n", "\n".join(pages))
        return {int(parts[i]): parts[i + 1].strip() for i in range(1, len(parts), 2)}

    example = p[44].split("Example 6\n", 1)[1].split("\nSolution", 1)[0]
    a12 = (p[793].split("Exercise Set 1.2 (Page 28)", 1)[1] + "\n"
           + p[794].split("Exercise Set 1.3", 1)[0].split("\n", 2)[2])
    a31 = p[800].split("Exercise Set 3.1 (Page 114)", 1)[1]

    def answers(text):
        parts = re.split(r"(?m)^(\d+)\.(?: |\n)", text.replace("−", "-"))
        return {int(parts[i]): parts[i + 1].strip() for i in range(1, len(parts), 2)}

    return blocks(sec12), blocks(sec31), example, answers(a12), answers(a31)


def intro(block):
    return " ".join(re.split(r"\n(?=a\.\n)", block, maxsplit=1)[0].split())


def fmt(value, digits=6):
    if value is None:
        return "\\text{—}"
    if not value:
        return "0"
    s = format(value, f".{digits}g").lower()
    if "e" in s:
        coefficient, exponent = s.split("e")
        return rf"{coefficient}\times 10^{{{int(exponent)}}}"
    return s


def m(value, digits=6):
    return f"${fmt(value, digits)}$"


def final_num(value):
    # Don't erase small but nonzero answers with decimal-place rounding.
    if 0 < abs(value) < 0.01:
        return fmt(value, 5)
    return format(value, ".4f")


def gather(lines):
    # final_answer is bare TeX: ExerciseCard supplies the surrounding math delimiters.
    return r"\begin{gathered}" + r"\\[3pt]".join(lines) + r"\end{gathered}"


def table(headers, rows):
    return "\n".join("| " + " | ".join(row) + " |" for row in
                     [headers, ["---"] * len(headers), *rows])


def card(section, number, tag, statement, hint, formula, tables, conclusion, final, target,
         label, *, focus=True, source_name=None):
    chapter = "01" if section == "1.2" else "04"
    return {
        "id": f"ch{chapter}-burden-sec{section}-{number}",
        "source_problem": (source_name or f"Exercise {section} - Problem {number[1:]}") +
                          " (Burden & Faires 9th)",
        "method_tag": TAGS[tag],
        "exam_focus": focus,
        "problem_en": statement,
        "glossary": GLOSSARY[tag],
        "hint": hint,
        "steps": [
            "**Bước 1: Công thức**\n\n" + formula,
            "**Bước 2: Bảng tính toán kiểm chứng**\n\n" + tables,
            "**Bước 3: Kết luận & sai số**\n\n" + conclusion,
        ],
        "final_answer": final,
        "expected_numeric_value": float(target),
        "numeric_target_label": label,
    }


def rel(value, reference):
    return abs(value - reference) / abs(reference) if reference else None


class FloatModel:
    def __init__(self, digits, rounding):
        self.digits = digits
        self.mode = ROUND_HALF_UP if rounding else ROUND_DOWN
        self.trace = []

    def fl(self, value):
        value = D(value)
        return value.quantize(D(1).scaleb(value.adjusted() - self.digits + 1),
                              rounding=self.mode) if value else D(0)

    def op(self, sign, a, b=None):
        v = self.fl(calc(sign, a, b))
        symbol = {"+": "+", "-": "-", "*": r"\cdot", "/": "/"}.get(sign)
        expr = (rf"({fmt(a)}){symbol}({fmt(b)})" if symbol
                else rf"\sqrt{{{fmt(a)}}}")
        self.trace.append(f"{expr}={fmt(v)}")
        return v


def calc(sign, a, b=None):
    if sign == "+":
        return a + b
    if sign == "-":
        return a - b
    if sign == "*":
        return a * b
    if sign == "/":
        return a / b
    if sign == "sqrt":
        return a.sqrt()
    raise ValueError(sign)


def evaluate(expr, model=None):
    if not isinstance(expr, tuple):
        return model.fl(expr) if model else D(expr)
    sign, a, b = expr
    return (model.op if model else calc)(sign, evaluate(a, model), evaluate(b, model))


def suite(expressions, digits, rounding):
    numbers, traces = [], []
    for expr in expressions:
        model = FloatModel(digits, rounding) if digits else None
        numbers.append(evaluate(expr, model))
        traces.append(model.trace if model else [])
    return numbers, traces


def trail(trace):
    return "; ".join(f"${s}$" for s in trace)


def frac(a, b):
    return "/", str(a), str(b)


def listed(math_items):
    return "\n".join(f"{letter}. ${tex}$" for letter, tex in zip(LETTERS, math_items))


ARITH4 = (
    ("+", frac(4, 5), frac(1, 3)), ("*", frac(4, 5), frac(1, 3)),
    ("+", ("-", frac(1, 3), frac(3, 11)), frac(3, 20)),
    ("-", ("+", frac(1, 3), frac(3, 11)), frac(3, 20)),
)
TEX4 = (
    r"\frac45+\frac13", r"\frac45\cdot\frac13",
    r"\left(\frac13-\frac3{11}\right)+\frac3{20}", r"\left(\frac13+\frac3{11}\right)-\frac3{20}",
)


def arithmetic5(e):
    return (
        ("+", "133", "0.921"), ("-", "133", "0.499"),
        ("-", ("-", "121", "0.327"), "119"), ("-", ("-", "121", "119"), "0.327"),
        ("/", ("-", frac(13, 14), frac(6, 7)), ("-", ("*", "2", e), "5.4")),
        ("-", ("+", ("*", "-10", PI), ("*", "6", e)), frac(3, 62)),
        ("*", frac(2, 9), frac(9, 7)), ("/", ("-", PI, frac(22, 7)), frac(1, 17)),
    )


TEX5 = (
    "133+0.921", "133-0.499", "(121-0.327)-119", "(121-119)-0.327",
    r"\frac{\frac{13}{14}-\frac67}{2e-5.4}", r"-10\pi+6e-\frac3{62}",
    r"\left(\frac29\right)\cdot\left(\frac97\right)", r"\frac{\pi-\frac{22}{7}}{\frac1{17}}",
)


def poly_model(coefficients, x, digits, rounding, nested):
    f = FloatModel(digits, rounding)
    x, c = f.fl(x), list(map(f.fl, coefficients))
    if nested:
        v = c[0]
        for a in c[1:]:
            v = f.op("+" if a >= 0 else "-", f.op("*", v, x), abs(a))
    else:
        powers = [f.fl(1), x]
        for _ in range(2, len(c)):
            powers.append(f.op("*", powers[-1], x))
        terms = [p if a == 1 else f.op("*", a, p)
                 for a, p in zip(c[:-1], reversed(powers[1:]))] + [c[-1]]
        v = terms[0]
        for a in terms[1:]:
            v = f.op("+" if a >= 0 else "-", v, abs(a))
    return v, f.trace


def horner(c, x):
    value = c[0]
    for coefficient in c[1:]:
        value = value * x + coefficient
    return value


QUADRATICS = (
    (frac(1, 3), frac(-123, 4), frac(1, 6)),
    (frac(1, 3), frac(123, 4), frac(-1, 6)),
    ("1.002", "-11.01", "0.01265"), ("1.002", "11.01", "0.01265"),
)
SYSTEMS = (("1.130", "-6.990", "1.013", "-6.099", "14.20", "14.22"),
           ("8.110", "12.20", "-18.11", "112.2", "-0.1370", "-0.1376"))


def quadratic(coefficients, f=None):
    a, b, c = (evaluate(x, f) for x in coefficients)
    op = f.op if f else calc
    s = op("sqrt", op("-", op("*", b, b), op("*", op("*", D(4), a), c)))
    denom = op("*", D(2), a)
    numer = op("*", D(-2), c)

    def quotient(x, y):
        return op("/", x, y) if y else None

    direct = (quotient(op("+", -b, s), denom), quotient(op("-", -b, s), denom))
    stable = (quotient(numer, op("+", b, s)), quotient(numer, op("-", b, s)))
    best = (direct[0], stable[1]) if b < 0 else (stable[0], direct[1])
    return direct, stable, best


def system(coefficients, f=None):
    a, b, c, d, e, g = map(f.fl if f else D, coefficients)
    op = f.op if f else calc
    multiplier = op("/", c, a)
    d1 = op("-", d, op("*", multiplier, b))
    f1 = op("-", g, op("*", multiplier, e))
    y = op("/", f1, d1)
    x = op("/", op("-", e, op("*", b, y)), a)
    return (x, y), (multiplier, d1, f1)


def series18():
    f = FloatModel(3, False)
    power = factorial = D(1)
    a = b = prev_a = prev_b = D(0)
    true = D(-5).exp()
    rows = []
    for i in range(10):
        if i:
            power = f.op("*", power, D(5))
            factorial = f.op("*", factorial, D(i))
        term = f.op("/", power, factorial)
        a = f.op("-" if i % 2 else "+", a, term)
        b = f.op("+", b, term)
        reciprocal = f.op("/", D(1), b)
        rows.append([str(i), m(term), m(a), m(reciprocal),
                     m(rel(prev_a, a) if i else None), m(rel(prev_b, reciprocal) if i else None),
                     m(rel(a, true)), m(rel(reciprocal, true))])
        prev_a, prev_b = a, reciprocal
    return a, reciprocal, rows


def chapter1(source, example):
    def make(n, tag, *args, **kwargs):
        return card("1.2", f"p{n}" if isinstance(n, int) else n, tag, *args, **kwargs)

    e = D(1).exp()
    pairs = [(PI, D(22)/7), (PI, D("3.1416")), (e, D("2.718")), (D(2).sqrt(), D("1.414")),
             (e**10, D(22000)), (D(10)**PI, D(1400)), (D(math.factorial(8)), D(39900)),
             (D(math.factorial(9)), (18*PI).sqrt()*(9/e)**9)]
    tex = [r"p=\pi,\ p^*=22/7", r"p=\pi,\ p^*=3.1416", "p=e,\ p^*=2.718",
           r"p=\sqrt{2},\ p^*=1.414", "p=e^{10},\ p^*=22000", r"p=10^\pi,\ p^*=1400",
           "p=8!,\ p^*=39900", r"p=9!,\ p^*=\sqrt{18\pi}(9/e)^9"]
    rounded = [abs(p-q) for p, q in pairs]
    rows = [[letter, m(p), m(q), m(a), m(rel(q,p))]
            for letter, (p,q), a in zip(LETTERS, pairs, rounded)]
    statement = re.sub(r"p∗|(?<!\w)p(?!\w)", lambda match: "$p^*$" if "∗" in match[0] else "$p$",
                       intro(source[1]))
    yield make(1, 0, statement + "\n\n" + listed(tex), ERROR, ERROR,
               table(["Ý", "$p$", "$p^*$", "$E$", r"$\varepsilon_t$"], rows),
               "So sánh sai số tương đối để biết sai lệch so với độ lớn của giá trị đúng.",
               gather([rf"\text{{{l})}}\ E={fmt(a)},\quad\varepsilon_t={fmt(rel(q,p))}"
                       for l, (p,q), a in zip(LETTERS, pairs, rounded)]),
               rounded[0], "sai số tuyệt đối $E$ ở câu (a).")

    for n, values, symbols, delta in (
        (2, [PI, e, D(2).sqrt(), (D(7).ln()/3).exp()], [r"\pi", "e", r"\sqrt{2}", r"\sqrt[3]{7}"], D(".0001")),
        (3, list(map(D, [150, 900, 1500, 90])), ["150", "900", "1500", "90"], D(".001")),
    ):
        text = re.sub(r"p∗|(?<!\w)p(?!\w)|10−[34]",
                      lambda s: {"p∗": "$p^*$", "p": "$p$"}.get(s[0], "$10^{-" + s[0][-1] + "}$"),
                      intro(source[n]))
        ends = [(v-delta*abs(v), v+delta*abs(v)) for v in values]
        rows = [[l, f"${s}$", m(v*delta), m(a), m(b)]
                for l, s, v, (a,b) in zip(LETTERS, symbols, values, ends)]
        yield make(n, 0, text + "\n\n" + listed(symbols), "Giải bất phương trình sai số tương đối.",
                   r"$|p-p^*|/|p|\le\delta$ tương đương "
                   r"$p^*\in[p-\delta|p|,\ p+\delta|p|]$.",
                   table(["Ý", "$p$", r"$\delta|p|$", "Cận dưới", "Cận trên"], rows),
                   "Cả hai đầu mút đều được nhận vì đề dùng “at most”."
                   + (" Sách in khoảng mở cho bài này; hai đầu mút vẫn thỏa bất đẳng thức."
                      if n == 3 else ""),
                   gather([rf"\text{{{l})}}\ [{a:.6f},\,{b:.6f}]"
                           for l, (a,b) in zip(LETTERS, ends)]),
                   ends[0][0], "cận dưới ở câu (a).")

    exact, _ = suite(ARITH4, None, False)
    chop, ct = suite(ARITH4, 3, False)
    rnd, rt = suite(ARITH4, 3, True)
    frac_tex = [rf"\frac{{{f.numerator}}}{{{f.denominator}}}"
                for f in [Fraction(str(v)).limit_denominator() for v in exact]]
    rows = [[l, f"${r}$", m(a), m(rel(a,v)), m(b), m(rel(b,v))]
            for l, r, v, a, b in zip(LETTERS, frac_tex, exact, chop, rnd)]
    yield make(4, 1, intro(source[4]) + "\n\n" + listed(TEX4), FP,
               "Tính với phân số trước; sau đó mô phỏng riêng hai chế độ 3 chữ số. " + FP + ERROR,
               table(["Ý", "Đúng", "Chặt cụt", r"$\varepsilon_t$",
                      "Làm tròn", r"$\varepsilon_t$"], rows) + "\n\n" +
               table(["Ý", "Phép tính chặt cụt", "Phép tính làm tròn"],
                     [[l, trail(a), trail(b)] for l,a,b in zip(LETTERS,ct,rt)]),
               "Chỉ làm tròn ở cuối không tương đương với làm tròn sau mỗi phép.",
               gather([rf"\text{{{l})}}\ \bigl({r},\,{fmt(a)},\,{fmt(b)}\bigr)"
                       for l, r, a, b in zip(LETTERS, frac_tex, chop, rnd)]),
               rnd[0], "kết quả làm tròn 3 chữ số ở câu (a).")

    expressions = arithmetic5(e)
    exact, _ = suite(expressions, None, False)
    for n, digits, rounding in ((5,3,True), (6,4,True), (7,3,False), (8,4,False)):
        approx, traces = suite(expressions, digits, rounding)
        rows = [[l, m(x), m(y), m(abs(x-y)), m(rel(y,x))]
                for l,x,y in zip(LETTERS, exact, approx)]
        yield make(n, 1, intro(source[n]) + "\n\n" + listed(TEX5), FP,
                   f"Dùng {digits} chữ số có nghĩa ở mọi phép toán. " + ERROR,
                   table(["Ý", "Đúng (hiển thị 6 chữ số)", "Xấp xỉ", "$E$", r"$\varepsilon_t$"], rows)
                   + "\n\n" + table(["Ý", "Chuỗi phép tính"],
                                     [[l, trail(t)] for l,t in zip(LETTERS,traces)]),
                   "Hai biểu thức (c), (d) bằng nhau trong số học chính xác, nhưng việc nhóm phép "
                   "tính có thể làm chúng khác nhau trong số học hữu hạn; (h) dễ mất chữ số khi trừ.",
                   gather([rf"\text{{{l})}}\ {fmt(a)}" for l,a in zip(LETTERS,approx)]),
                   approx[0], "giá trị xấp xỉ ở câu (a).")

    yield cancellation_card(source[11])
    yield quadratic_card(source[13])
    yield intercept_card(source[17])
    yield series_card(source[18])
    yield system_card(source[19])
    yield nested_card("p21", source[21])
    yield nested_card("ex6", example)


def cancellation_card(block):
    f = FloatModel(4, True)
    x = D("0.1")
    sin = f.fl(str(math.sin(float(x))))
    cos = f.fl(str(math.cos(float(x))))
    product = f.op("*", x, cos)
    numerator = f.op("-", product, sin)
    denominator = f.op("-", x, sin)
    direct = f.op("/", numerator, denominator)
    polynomial = D(-2)
    reference = D(str((0.1*math.cos(0.1)-math.sin(0.1))/(0.1-math.sin(0.1))))
    formula = (r"$\sin x\approx x-x^3/6$, $\cos x\approx1-x^2/2$. "
               r"Thế và rút gọn trên giấy trước khi làm tròn: "
               r"$\frac{-x^3/3}{x^3/6}=-2$. "
               r"Khi $x\to0$, phần dư là bậc cao hơn $x^3$, nên giới hạn cũng bằng $-2$.")
    title = intro(block).split("f (x)", 1)[0].strip()
    statement = (title + r" $f(x)=\frac{x\cos x-\sin x}{x-\sin x}$." + "\n\n"
                 r"a. Find $\lim_{x\to0}f(x)$." + "\n"
                 r"b. Use four-digit rounding arithmetic to evaluate $f(0.1)$." + "\n"
                 "c. Replace each trigonometric function with its third Maclaurin polynomial, "
                 "and repeat part (b).\n"
                 r"d. The actual value is $f(0.1)=-1.99899998$. Find the relative error "
                 "for the values obtained in parts (b) and (c).")
    rows = [["Trực tiếp", m(cos), m(sin), m(numerator), m(denominator), m(direct), m(rel(direct, reference))],
            ["Maclaurin, đã rút gọn", "—", "—", r"$-x^3/3$", r"$x^3/6$", m(polynomial),
             m(rel(polynomial, reference))]]
    return card("1.2", "p11", 0, statement, "Khai triển trước, rút gọn rồi mới thay số.",
                FP + formula + "\n\n" + ERROR,
                table(["Cách", r"$\cos x$", r"$\sin x$", "Tử", "Mẫu", "$f^*$", r"$\varepsilon_t$"], rows),
                "Cách trực tiếp mất chữ số qua cả hai phép trừ; cách Maclaurin rút gọn tránh "
                f"hai phép trừ đó. Giá trị tham chiếu $f(0.1)\\approx {reference:.8f}$.",
                rf"\lim_{{x\to0}}f(x)=-2,\quad f_b^*={fmt(direct)},\quad f_c^*=-2",
                direct, "giá trị trực tiếp ở câu (b).")


def quadratic_card(block):
    text = [r"\frac13x^2-\frac{123}{4}x+\frac16=0",
            r"\frac13x^2+\frac{123}{4}x-\frac16=0",
            "1.002x^2-11.01x+0.01265=0", "1.002x^2+11.01x+0.01265=0"]
    rows, stages, final = [], [], []
    for l, coefficients in zip(LETTERS, QUADRATICS):
        f = FloatModel(4, True)
        direct, rational, best = quadratic(coefficients, f)
        truth = quadratic(coefficients)[2]
        stages.append([l, trail(f.trace)])
        for j, (d, r, b, v) in enumerate(zip(direct, rational, best, truth), 1):
            rows.append([l, f"${j}$", m(d), m(r), m(b), m(v), m(abs(b-v)), m(rel(b,v))])
        final.append(rf"\text{{{l})}}\ (x_1,x_2)\approx({fmt(best[0])},\,{fmt(best[1])})")
    return card("1.2", "p13", 0, intro(block) + "\n\n" + listed(text),
                r"Khi tử số $-b\pm\sqrt{D}$ bị triệt tiêu, dùng công thức hữu tỉ hóa.",
                FP + r"Với $s=\sqrt{b^2-4ac}$, công thức (1.1) cho $x_{1,2}=(-b\pm s)/(2a)$. "
                r"Hữu tỉ hóa cho $x_1=-2c/(b+s)$ (1.2), $x_2=-2c/(b-s)$ (1.3). "
                r"Nếu $b<0$, dùng (1.1) cho $x_1$ và (1.3) cho $x_2$; nếu $b>0$, dùng (1.2) "
                r"cho $x_1$ và (1.1) cho $x_2$. " + ERROR,
                table(["Ý", "$j$", "(1.1)", "(1.2)/(1.3)", "Chọn", "Nghiệm đúng", "$E$",
                       r"$\varepsilon_t$"], rows) + "\n\n"
                + "Dấu — biểu thị phép chia cho 0 sau làm tròn.\n\n"
                + table(["Ý", "Chuỗi phép tính"], stages),
                "Chọn công thức theo dấu của hệ số để tránh trừ hai số gần bằng nhau.",
                gather(final), quadratic(QUADRATICS[0], FloatModel(4, True))[2][1],
                "nghiệm nhỏ $x_2$ ở câu (a).")


def intercept_card(block):
    x0, y0, x1, y1 = map(D, ("1.31", "3.24", "1.93", "4.76"))
    first = ("/", ("-", ("*", x0, y1), ("*", x1, y0)), ("-", y1, y0))
    second = ("-", x0, ("/", ("*", ("-", x1, x0), y0), ("-", y1, y0)))
    truth = evaluate(first)
    (a,b), traces = suite([first, second], 3, True)
    prefix = " ".join(block.split("x = x0y1", 1)[0].split())
    for original, tex in (("(x0, y0)", "$(x_0,y_0)$"), ("(x1, y1)", "$(x_1,y_1)$"),
                          ("y1̸ = y0", r"$y_1\ne y_0$"), ("x-intercept", "$x$-intercept")):
        prefix = prefix.replace(original, tex)
    formulas = r"$$x=\frac{x_0y_1-x_1y_0}{y_1-y_0},\qquad x=x_0-\frac{(x_1-x_0)y_0}{y_1-y_0}.$$"
    return card("1.2", "p17", 0, prefix + "\n\n" + formulas + "\n\n"
                "a. Show that both formulas are algebraically correct.\n"
                r"b. Use the data $(x_0,y_0)=(1.31,3.24)$ and $(x_1,y_1)=(1.93,4.76)$ and "
                "three-digit rounding arithmetic to compute the $x$-intercept both ways. "
                "Which method is better and why?",
                "Đặt tung độ bằng 0 trong phương trình đường thẳng.",
                r"Đặt $0-y_0=(y_1-y_0)(x-x_0)/(x_1-x_0)$, rồi giải theo $x$. "
                r"Quy đồng dạng thứ hai để được dạng thứ nhất. Dạng tham số "
                r"$x=x_0+t(x_1-x_0),\ y=y_0+t(y_1-y_0)$ cũng xử lý được $x_1=x_0$. "
                + FP + ERROR,
                table(["Dạng", "Phép tính", "$x^*$", "$E$", r"$\varepsilon_t$"],
                      [[str(i), trail(t), m(v), m(abs(v-truth)), m(rel(v,truth))]
                       for i, (v,t) in enumerate(zip((a,b), traces), 1)]),
                f"Giá trị đúng $x\\approx {fmt(truth)}$. Dạng 2 tốt hơn trên bộ dữ liệu này: "
                "không tạo tử số bằng hiệu của hai tích gần bằng nhau.",
                rf"x_{{(1)}}={fmt(a)},\qquad x_{{(2)}}={fmt(b)}", b, "giao điểm tính theo công thức thứ hai.")


def series_card(block):
    a, b, rows = series18()
    statement = (r"The Taylor polynomial of degree $n$ for $f(x)=e^x$ is $\sum_{i=0}^n x^i/i!$. "
                 "Use the Taylor polynomial of degree nine and three-digit chopping arithmetic "
                 r"to find an approximation to $e^{-5}$ by each of the following methods." "\n\n"
                 r"a. $e^{-5}\approx\sum_{i=0}^9(-5)^i/i!=\sum_{i=0}^9(-1)^i5^i/i!$." "\n"
                 r"b. $e^{-5}=1/e^5\approx1/\sum_{i=0}^9 5^i/i!$." "\n"
                 r"c. An approximate value of $e^{-5}$ correct to three digits is $6.74\times10^{-3}$. "
                 "Which formula, (a) or (b), gives the most accuracy, and why?")
    assert "degree\nnine" in block
    return card("1.2", "p18", 1, statement, "Cộng theo thứ tự từ bậc 0 đến bậc 9.",
                FP + r"Tạo $p_i=\operatorname{fl}_3(5p_{i-1})$ và "
                r"$q_i=\operatorname{fl}_3(iq_{i-1})$ từ $p_0=q_0=1$. "
                r"Dùng $\operatorname{fl}_3(p_i/q_i)$ cho hai tổng lũy kế, sau đó nghịch đảo tổng dương. "
                r"$\varepsilon_a=|v_i-v_{i-1}|/|v_i|$; — nếu chưa có bước trước hoặc mẫu bằng 0. " + ERROR,
                table(["$i$", "$t_i$", "$S_i^-$", "$1/S_i^+$", r"$\varepsilon_{a,A}$",
                       r"$\varepsilon_{a,B}$", r"$\varepsilon_{t,A}$", r"$\varepsilon_{t,B}$"], rows),
                f"Giá trị đúng là {m(D(-5).exp())}. Dạng (b) tránh cộng các số hạng trái dấu; "
                "dạng (a) còn chịu sai số cắt chuỗi lớn tại bậc 9. "
                "Các cách tạo số hạng khác có thể cho kết quả khác dưới số học chặt cụt.",
                rf"A={fmt(a)},\qquad B={fmt(b)}", b, "xấp xỉ $e^{-5}$ bằng nghịch đảo ở câu (b).")


def system_card(block):
    text = [r"\begin{cases}1.130x-6.990y=14.20\\1.013x-6.099y=14.22\end{cases}",
            r"\begin{cases}8.110x+12.20y=-0.1370\\-18.11x+112.2y=-0.1376\end{cases}"]
    assert "four-digit rounding" in " ".join(block.split())
    statement = ("The two-by-two linear system $ax+by=e$, $cx+dy=f$, where "
                 "$a,b,c,d,e,f$ are given, can be solved for $x$ and $y$ as follows:\n\n"
                 r"$$m=c/a\ (a\ne0),\qquad d_1=d-mb,\qquad f_1=f-me,\qquad "
                 r"y=f_1/d_1,\qquad x=(e-by)/a.$$" "\n\n"
                 "Solve the following linear systems using four-digit rounding arithmetic.\n\n" + listed(text))
    rows, trace_rows, final = [], [], []
    for l, coefficients in zip(LETTERS, SYSTEMS):
        f = FloatModel(4, True)
        (x,y), (mult,d1,f1) = system(coefficients, f)
        (x_ref,y_ref), _ = system(coefficients)
        rows.append([l, *map(m, (mult,d1,f1,x,y,x_ref,y_ref,rel(x,x_ref),rel(y,y_ref)))])
        trace_rows.append([l, trail(f.trace)])
        final.append(rf"\text{{{l})}}\ (x,y)\approx({fmt(x)},\,{fmt(y)})")
    return card("1.2", "p19", 1, statement,
                r"Khử $x$ khỏi phương trình thứ hai rồi thế ngược; làm tròn cả các tích trung gian.",
                FP + r"Lấy phương trình thứ hai trừ $m=c/a$ lần phương trình thứ nhất, "
                r"thu được $d_1y=f_1$. Thế $y$ vào phương trình đầu để lấy $x$. " + ERROR,
                table(["Ý", "$m$", "$d_1$", "$f_1$", "$x^*$", "$y^*$", "$x$ đúng", "$y$ đúng",
                       r"$\varepsilon_{t,x}$", r"$\varepsilon_{t,y}$"], rows) + "\n\n"
                + table(["Ý", "Phép tính"], trace_rows),
                "Ở (a), việc tính hệ số $d_1$ bằng hiệu hai số gần nhau khuếch đại sai số. "
                "Đáp số in ở PDF 794 không khớp với các hệ in ở PDF 48; "
                "bảng dùng đúng hệ số đề bài và công thức khử được chỉ định.",
                gather(final), system(SYSTEMS[0], FloatModel(4,True))[0][0], "nghiệm $x$ ở câu (a).")


def nested_card(number, block):
    if number == "p21":
        c = list(map(D, ["1.01","-4.62","-3.11","12.2","-1.99"]))
        statement = ("a. Show that the polynomial nesting technique described in Example 6 can also be "
                     "applied to the evaluation of\n\n"
                     r"$$f(x)=1.01e^{4x}-4.62e^{3x}-3.11e^{2x}+12.2e^x-1.99.$$" "\n\n"
                     r"b. Use three-digit rounding arithmetic, the assumption that $e^{1.53}=4.62$, "
                     r"and the fact that $e^{nx}=(e^x)^n$ to evaluate $f(1.53)$ as given in part (a)." "\n"
                     "c. Redo the calculation in part (b) by first nesting the calculations.\n"
                     r"d. Compare the approximations in parts (b) and (c) to the true three-digit result "
                     r"$f(1.53)=-7.61$.")
        assert "polynomial nesting technique" in intro(block)
        x, reference = D("4.62"), horner(c, D("1.53").exp())
        formula = r"Đặt $z=e^x$: $f(x)=(((1.01z-4.62)z-3.11)z+12.2)z-1.99$."
        modes = [(3, True)]
        label = "giá trị dạng lồng ở câu (c)."
    else:
        c, x = list(map(D, ["1","-6.1","3.2","1.5"])), D("4.71")
        assert "Evaluate" in block and "4.71" in block
        statement = (r"Evaluate $f(x)=x^3-6.1x^2+3.2x+1.5$ at $x=4.71$ using three-digit arithmetic."
                     "\n\nPractice extension: compare the expanded and nested forms using both rounding "
                     "and chopping with three and four significant digits.")
        reference = horner(c, x)
        formula = r"$f(x)=((x-6.1)x+3.2)x+1.5$."
        modes = [(3,True), (4,True), (3,False), (4,False)]
        label = "giá trị Horner làm tròn 3 chữ số."
    rows, trace_rows, final = [], [], []
    for digits, rounding in modes:
        mode = f"{digits} " + ("làm tròn" if rounding else "chặt cụt")
        direct, dt = poly_model(c, x, digits, rounding, False)
        nested, nt = poly_model(c, x, digits, rounding, True)
        rows.append([mode, m(direct), m(rel(direct,reference)), m(nested), m(rel(nested,reference))])
        trace_rows.extend([[mode + " — khai triển", trail(dt)], [mode + " — Horner", trail(nt)]])
        final.append(rf"\text{{{mode}:}}\ ({fmt(direct)},\,{fmt(nested)})")
    conclusion = (f"Giá trị tham chiếu chưa làm tròn: {m(reference)}. "
                  "Dạng lồng giảm số phép nhân; mức cải thiện phụ thuộc vào dữ liệu và độ chính xác.")
    if number == "p21":
        conclusion += f" Nếu coi $e^{{1.53}}=4.62$ là chính xác, đa thức cho {m(horner(c,x))}; "
        conclusion += "sai số vì thay $e^{1.53}$ bằng $4.62$ tồn tại ngay cả khi chưa làm tròn phép tính."
    return card("1.2", number, 2, statement, "Nhân và cộng từ hệ số bậc cao nhất xuống.",
                FP + formula + " Dạng khai triển tính lũy thừa bằng nhân liên tiếp và cộng từ trái qua phải. "
                + ERROR,
                table(["Chế độ", "Khai triển", r"$\varepsilon_t$", "Horner", r"$\varepsilon_t$"], rows)
                + "\n\n" + table(["Chế độ và dạng", "Chuỗi phép tính"], trace_rows),
                conclusion, gather(final), poly_model(c,x,3,True,True)[0], label,
                source_name="Section 1.2 - Example 6 (practice extension)" if number == "ex6" else None)


LAGRANGE = (r"$P_n(x)=\sum_{j=0}^n y_jL_j(x)$, "
            r"$L_j(x)=\prod_{i\ne j}(x-x_i)/(x_j-x_i)$.")
REMAINDER = (r"Trên khoảng $I$ chứa điểm cần tính và các nút, đặt "
             r"$M_{n+1}\ge\max_{\xi\in I}\lvert f^{(n+1)}(\xi)\rvert$. "
             r"Khi đủ khả vi, $|f(t)-P_n(t)|\le B_n=M_{n+1}|\omega_n(t)|/(n+1)!$, "
             r"$\omega_n(t)=\prod_{j=0}^n(t-x_j)$.")
DATA_ERROR = (r"Nếu dùng số liệu đã làm tròn $y_j$, cộng thêm "
              r"$B_{\mathrm{data}}=\sum_j|L_j(t)|\,|y_j-f(x_j)|$. "
              r"Chặn tổng là $B_n+B_{\mathrm{data}}$.")


class Function:
    def __init__(self, tex, evaluate, bound_tex, bounds):
        self.tex, self.evaluate = tex, evaluate
        self.bound_tex, self.bounds = bound_tex, bounds

    def limit(self, n, a, b):
        return self.bounds[n-1](a,b) if self.bounds[n-1] else None


def form(tex, function, bounds_tex, *bounds):
    return Function(tex, function, bounds_tex, bounds)


FUNCTIONS = {
    1: (
        form(r"\cos x", math.cos, r"$M_2=1$, $M_3=\sin b$.",
             lambda a,b: 1, lambda a,b: math.sin(b)),
        form(r"\sqrt{1+x}", lambda x: math.sqrt(1+x),
             r"$M_2=1/[4(1+a)^{3/2}]$, $M_3=3/[8(1+a)^{5/2}]$.",
             lambda a,b: .25/(1+a)**1.5, lambda a,b: .375/(1+a)**2.5),
        form(r"\ln(x+1)", math.log1p, r"$M_2=(1+a)^{-2}$, $M_3=2(1+a)^{-3}$.",
             lambda a,b: 1/(1+a)**2, lambda a,b: 2/(1+a)**3),
        form(r"\tan x", math.tan,
             r"Với $u=\tan b$, $M_2=2u(1+u^2)$, $M_3=2(1+u^2)(1+3u^2)$.",
             lambda a,b: 2*math.tan(b)*(1+math.tan(b)**2),
             lambda a,b: 2*(1+math.tan(b)**2)*(1+3*math.tan(b)**2)),
    ),
    2: (
        form(r"\sin(\pi x)", lambda x: 0.0 if x == 1 else math.sin(math.pi*x),
             r"$M_2=\pi^2$, $M_3=\pi^3$.",
             lambda a,b: math.pi**2, lambda a,b: math.pi**3),
        form(r"\sqrt[3]{x-1}", lambda x: math.cbrt(x-1),
             r"$M_2=2/[9(a-1)^{5/3}]$ với $a>1$. "
             r"Ở bậc 2, $|f'''(x)|=10/[27(x-1)^{8/3}]$ không bị chặn khi $x\to1^+$.",
             lambda a,b: 2/(9*(a-1)**(5/3)), None),
        form(r"\log_{10}(3x-1)", lambda x: math.log10(3*x-1),
             r"$M_2=9/[(3a-1)^2\ln 10]$, $M_3=54/[(3a-1)^3\ln 10]$.",
             lambda a,b: 9/((3*a-1)**2*math.log(10)), lambda a,b: 54/((3*a-1)**3*math.log(10))),
        form(r"e^{2x}-x", lambda x: math.exp(2*x)-x, r"$M_2=4e^{2b}$, $M_3=8e^{2b}$.",
             lambda a,b: 4*math.exp(2*b), lambda a,b: 8*math.exp(2*b)),
    ),
    5: (
        form(r"x\ln x", lambda x: x*math.log(x), r"$M_2=1/a$, $M_3=1/a^2$, $M_4=2/a^3$.",
             lambda a,b: 1/a, lambda a,b: 1/a**2, lambda a,b: 2/a**3),
        form(r"x^3+4.001x^2+4.002x+1.101", lambda x: horner([1,4.001,4.002,1.101],x),
             r"$M_2=\max(|6a+8.002|,|6b+8.002|)$, $M_3=6$, $M_4=0$.",
             lambda a,b: max(abs(6*a+8.002),abs(6*b+8.002)), lambda a,b: 6, lambda a,b: 0),
        form(r"x\cos x-2x^2+3x-1", lambda x: x*math.cos(x)-2*x*x+3*x-1,
             r"$M_2=4+2\sin b+b$, $M_3=3+b\sin b$, $M_4=4\sin b+b$ "
             r"theo bất đẳng thức tam giác trên khoảng nút.",
             lambda a,b: 4+2*math.sin(b)+b, lambda a,b: 3+b*math.sin(b),
             lambda a,b: 4*math.sin(b)+b),
        form(r"\sin(e^x-2)", lambda x: math.sin(math.exp(x)-2),
             r"Với $u=e^b$, chặn đạo hàm bằng các tổng hệ số: "
             r"$M_2=u+u^2$, $M_3=u+3u^2+u^3$, $M_4=u+7u^2+6u^3+u^4$.",
             lambda a,b: (u:=math.exp(b))+u*u, lambda a,b: (u:=math.exp(b))+3*u*u+u**3,
             lambda a,b: (u:=math.exp(b))+7*u*u+6*u**3+u**4),
    ),
    6: (
        form(r"e^{2x}", lambda x: math.exp(2*x), r"$M_r=2^r e^{2b}$.",
             *[lambda a,b,r=r: 2**r*math.exp(2*b) for r in (2,3,4)]),
        form(r"x^4-x^3+x^2-x+1", lambda x: horner([1,-1,1,-1,1],x),
             r"$M_2=\max(12a^2-6a+2,12b^2-6b+2)$ theo tính lồi; "
             r"$M_3=\max(|24a-6|,|24b-6|)$, $M_4=24$.",
             lambda a,b: max(12*a*a-6*a+2,12*b*b-6*b+2),
             lambda a,b: max(abs(24*a-6),abs(24*b-6)), lambda a,b: 24),
        form(r"x^2\cos x-3x", lambda x: x*x*math.cos(x)-3*x,
             r"$M_2=2+4b\sin b$, $M_3=6\sin b+6b$, $M_4=12+8b\sin b$ "
             r"theo bất đẳng thức tam giác trên khoảng nút.",
             lambda a,b: 2+4*b*math.sin(b), lambda a,b: 6*math.sin(b)+6*b,
             lambda a,b: 12+8*b*math.sin(b)),
        form(r"\ln(e^x+2)", lambda x: math.log(math.exp(x)+2),
             r"Đặt $u=e^x/(e^x+2)$. Ba đạo hàm bậc 2–4 lần lượt là "
             r"$u(1-u)$, $u(1-u)(1-2u)$ và $u(1-u)(1-6u+6u^2)$; "
             r"do $0<u<1$, có thể lấy $M_2=M_3=M_4=1/4$.",
             *[lambda a,b: .25]*3),
    ),
}

# The first two nodes bracket the target. For tied extra nodes, use the
# published selections for #5; use the right node for the tie in #6(b).
ORDER = ((1,2,3,0), (1,2,3,0), (1,2,3,0), (2,3,1,0),
         (1,2,3,0), (1,2,3,0), (0,1,2,3), (2,3,1,0))
TARGETS = (.45, 1.4, 8.4, -1/3, .25, .9, .43, 0, .18, .25)
TARGET_TEX = ("0.45", "1.4", "8.4", r"-\frac13", "0.25", "0.9", "0.43", "0", "0.18", "0.25")


def subparts(block):
    return re.split(r"(?m)^[a-d]\.\n", block)[1:5]


def interpolation_data(source, number, j):
    if number in (1,2):
        nodes = (0,.6,.9) if number == 1 else (1,1.25,1.6)
        values = [FUNCTIONS[number][j].evaluate(x) for x in nodes]
        return [(x,y) for x,y in zip(nodes,values)] if number == 1 else [
            (nodes[i], values[i]) for i in (1,2,0)]
    index = (number-5)*4+j
    # The original equations use a dotted italic f and minus U+2212. TeX
    # uses the same decimal precision as the given data.
    pairs = re.findall(r"f\s*\((-?[\d.]+)\)\s*=\s*(-?[\d.]+)",
                       subparts(source[number])[j].replace("−","-"))
    if len(pairs) != 4:
        raise ValueError(f"Expected 4 tabulated values for {number}{LETTERS[j]}")
    return [tuple(map(float, pairs[i])) for i in ORDER[index]]


def lagrange(nodes, t):
    polynomial = np.polynomial.Polynomial([0.0])
    weights = []
    for j, (x,y) in enumerate(nodes):
        other = [k for i,(k,_) in enumerate(nodes) if i != j]
        denom = math.prod(x-k for k in other)
        weights.append(math.prod(t-k for k in other)/denom)
        polynomial += np.polynomial.Polynomial.fromroots(other)*(y/denom)
    value = math.fsum(w*y for w, (_,y) in zip(weights,nodes))
    return polynomial, weights, value


def polynomial_tex(poly):
    parts = []
    for i,v in reversed(list(enumerate(poly.coef))):
        if abs(v) < 1e-13:
            continue
        parts.append(("-" if v < 0 else ("+" if parts else "")) +
                     fmt(abs(v)) + (f"x^{{{i}}}" if i > 1 else "x" if i else ""))
    return "".join(parts) or "0"


def interp_runs(nodes, function, t, tabular=False):
    reference = function.evaluate(t)
    for n in range(1,len(nodes)):
        subset = nodes[:n+1]
        poly, weights, result = lagrange(subset, t)
        a,b = min(t,*(x for x,_ in subset)), max(t,*(x for x,_ in subset))
        M = function.limit(n,a,b)
        omega = abs(math.prod(t-x for x,_ in subset))
        data_bound = math.fsum(abs(w)*abs(y-function.evaluate(x))
                               for w,(x,y) in zip(weights,subset)) if tabular else 0.0
        error = abs(result-reference)
        # For decimals representing an exact cubic, discard binary round-off noise.
        if tabular and M == 0 and max(error, data_bound) < 1e-13:
            error = data_bound = 0.0
        yield (n, subset, poly, weights, result, a, b, M, omega, error,
               None if M is None else M*omega/math.factorial(n+1), data_bound)


def chapter4(source):
    for number in range(1,7):
        base = number-2 if number in (3,4) else number
        for j, letter in enumerate(LETTERS[:4]):
            index = base-1 if base in (1,2) else 2+(base-5)*4+j
            t, tt = TARGETS[index], TARGET_TEX[index]
            f = FUNCTIONS[base][j]
            is_bound, is_table = number in (3,4), number in (5,6)
            reference = f.evaluate(t)
            nodes = interpolation_data(source, base, j)
            runs = list(interp_runs(nodes,f,t,is_table))
            node_note = ("Chọn hai nút kẹp điểm cần tính để lập đa thức bậc 1, "
                         "rồi thêm các nút gần đó cho bậc cao hơn.")
            if is_table:
                pairs = re.findall(r"f\s*\((-?[\d.]+)\)\s*=\s*(-?[\d.]+)",
                                   subparts(source[number])[j].replace("−","-"))
                statement = intro(source[number]) + "\n\n" + f"{letter}. $f({tt})$ if " + ", ".join(
                    f"$f({x})={y}$" for x,y in pairs) + "."
                statement += (f"\n\nError comparison ({base+2}{letter}): "
                              f"use $f(x)={f.tex}$ to compare the actual errors with the bounds.")
            else:
                orig = intro(source[base])
                orig = re.sub(r"(?<!\w)x([0-2]) = ([\d.]+)", r"$x_\1=\2$", orig)
                orig = orig.replace("f (x)", "$f(x)$").replace(f"f ({tt})", f"$f({tt})$")
                orig += f"\n\n{letter}. $f(x)={f.tex}$."
                statement = (intro(source[number]) + f"\n\nData from Exercise {base}({letter}):\n\n" + orig
                             if is_bound else orig)

            def b_fmt(bound):
                return fmt(bound) if bound is not None else r"\text{không áp dụng}"

            values, basis, bounds = [], [], []
            for n, subset, poly, weights, result, a, b, M, omega, err, bound, db in runs:
                result_rel = err/abs(reference) if reference != 0 else None
                values.append([m(n), f"${polynomial_tex(poly)}$", m(result), m(err), m(result_rel)])
                basis.extend([[m(n), m(x), m(y), m(w), m(y*w)] for (x,y),w in zip(subset,weights)])
                row = [m(n), f"$[{fmt(a)},{fmt(b)}]$", m(M), m(omega), m(err), m(bound)]
                if is_table:
                    row += [m(db), m(bound+db)]
                bounds.append(row)
            checks = table(["$n$", "$P_n(x)$ (hệ số hiển thị)", "$P_n(t)$", "$E$",
                            r"$\varepsilon_t$"], values)
            checks += "\n\n" + table(["$n$", "$x_j$", "$y_j$", "$L_j(t)$", "$y_j L_j(t)$"], basis)
            if is_bound or is_table:
                headers = ["$n$", "$I=[a,b]$", "$M_{n+1}$", r"$|\omega_n(t)|$".replace("|", r"\vert "),
                           "$E$", "$B_n$"]
                if is_table:
                    headers += [r"$B_{\mathrm{data}}$", "Chặn tổng"]
                checks += "\n\n" + table(headers,bounds)
            conclusion = (f"Giá trị tham chiếu $f({tt})={fmt(reference)}$ (hiển thị 6 chữ số); "
                          "các sai số được tính trước khi làm tròn để hiển thị.")
            if is_bound or is_table:
                conclusion += " Các chặn trong bảng được hiển thị gần đúng; dùng công thức để giữ đủ độ chính xác."
            if number == 4 and j == 1:
                conclusion += (" Định lý 3.3 không cho chặn bậc 2 vì nút $x=1$ là điểm kỳ dị "
                               "của đạo hàm; sai số thực tế vẫn tính được.")
            if number in (1,3) and j == 3:
                conclusion += " Với bộ nút này, đa thức bậc 2 có sai số lớn hơn đa thức bậc 1."
            if is_table:
                conclusion += " So sánh sai số của bảng với chặn tổng, không chỉ với sai số nội suy lý tưởng."
            if is_bound:
                final = gather([rf"B_{{{r[0]}}}\approx {b_fmt(r[-2])}" if r[-2] is not None
                                else rf"B_{{{r[0]}}}:\ \text{{Định lý 3.3 không áp dụng}}"
                                for r in runs])
                target = runs[-1][-2] if runs[-1][-2] is not None else runs[0][-2]
                label = f"chặn lý thuyết $B_{2 if runs[-1][-2] is not None else 1}$."
            else:
                final = gather([rf"P_{{{r[0]}}}({tt})\approx {final_num(r[4])},"
                                rf"\quad E_{{{r[0]}}}\approx {fmt(r[-3])}" for r in runs])
                target = runs[-1][4]
                label = f"giá trị $P_{runs[-1][0]}({tt})$."
            formula = LAGRANGE + " " + node_note + " " + ERROR
            if is_bound or is_table:
                formula += "\n\n" + REMAINDER + " " + f.bound_tex
                if is_table:
                    formula += " " + DATA_ERROR
            yield card("3.1", f"p{number}{letter}", 3, statement,
                       "Lập các cơ sở Lagrange trên từng bộ nút; "
                       + ("dùng đoạn chứa cả nút lẫn điểm cần tính để chặn đạo hàm."
                          if is_bound else "thay điểm cần tính vào từng cơ sở và cộng đóng góp."),
                       formula, checks, conclusion, final, target, label,
                       source_name=f"Exercise 3.1 - Problem {number}({letter})")



def main():
    import json
    from pathlib import Path
    import fitz

    doc = fitz.open("D:/pps/numerical_analysis_9th.pdf")
    sec12_blocks, sec31_blocks, example, ans12, ans31 = extract(doc)

    ch01_new = list(chapter1(sec12_blocks, example))
    ch04_new = list(chapter4(sec31_blocks))

    print(f"Generated {len(ch01_new)} cards for Chapter 1 (Error Analysis).")
    print(f"Generated {len(ch04_new)} cards for Chapter 4 (Lagrange Interpolation).")

    # Update data/ch01_errors.json
    p1 = Path("data/ch01_errors.json")
    ch01_data = json.loads(p1.read_text(encoding="utf-8")) if p1.exists() else []
    existing_ids_1 = {x["id"] for x in ch01_data}
    added_1 = 0
    for c in ch01_new:
        if c["id"] not in existing_ids_1:
            ch01_data.append(c)
            existing_ids_1.add(c["id"])
            added_1 += 1
    p1.write_text(json.dumps(ch01_data, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Updated data/ch01_errors.json: added {added_1}, total {len(ch01_data)}.")

    # Update data/ch04_interpolation.json
    p4 = Path("data/ch04_interpolation.json")
    ch04_data = json.loads(p4.read_text(encoding="utf-8")) if p4.exists() else []
    existing_ids_4 = {x["id"] for x in ch04_data}
    added_4 = 0
    for c in ch04_new:
        if c["id"] not in existing_ids_4:
            ch04_data.append(c)
            existing_ids_4.add(c["id"])
            added_4 += 1
    p4.write_text(json.dumps(ch04_data, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Updated data/ch04_interpolation.json: added {added_4}, total {len(ch04_data)}.")


if __name__ == "__main__":
    main()

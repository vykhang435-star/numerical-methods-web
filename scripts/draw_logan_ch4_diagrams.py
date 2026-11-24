"""Draw shear and moment diagrams directly from equilibrium fields."""

from html import escape

import numpy as np

from logan_ch4_beam import numeric_models, symbolic_model


def diagram(number, sol):
    origins = np.r_[0, np.cumsum([s.length for s in sol.model.spans])]
    x_right = origins[-1]
    imperial = number == 10
    symbolic = number in (12, 13, 14, 15)
    x_unit = "x/L" if symbolic else ("x (in)" if imperial else "x (m)")
    force = "kip" if imperial else "kN"
    length = "in" if imperial else "m"
    labels = (("V/(wL)", "M/(wL²)") if symbolic
              else (f"V ({force})", f"M ({force}·{length})"))
    width, left, right = 710, 75, 660
    content = [
        '<rect width="710" height="422" fill="#fff" rx="12"/>',
        f'<text x="20" y="27" font-size="15" font-weight="bold">P4–{number} · Lực cắt và mô men uốn</text>',
    ]

    def xpx(x):
        return left + (right-left)*x/x_right

    for kind, (label, color, top) in enumerate(zip(labels, ("#126c83", "#923521"), (59, 236))):
        series = []
        for e, span in enumerate(sol.model.spans):
            bounds = [0, *sorted(t*span.length for t, _ in span.points), span.length]
            for a, b in zip(bounds, bounds[1:]):
                poly = sol.fields(e, (a+b)/2)[kind+1]
                x = np.linspace(a, b, 51)
                series.append((x + origins[e], poly(x)))
        peak = max(max(abs(y)) for _, y in series)
        axis = top + 65

        def ypx(y):
            return axis - 52*y/peak

        content += [f'<line x1="{left-5}" y1="{axis}" x2="{right+5}" y2="{axis}" stroke="#64748b"/>',
                    f'<text x="{right+5}" y="{axis+16}" font-size="11">{escape(x_unit)}</text>',
                    f'<text x="20" y="{top-8}" fill="{color}" font-weight="bold">{escape(label)}</text>']
        for val in (-peak, 0, peak):
            y = ypx(val)
            content.append(f'<text x="{left-8}" y="{y+4:.2f}" text-anchor="end" font-size="11">{val:.4g}</text>')
        for x in origins:
            x_pixel = xpx(x)
            content += [f'<line x1="{x_pixel:.2f}" x2="{x_pixel:.2f}" y1="{top+7}" y2="{top+124}" '
                        'stroke="#cbd5e1" stroke-dasharray="3 4"/>',
                        f'<text x="{x_pixel:.2f}" y="{top+145}" text-anchor="middle" font-size="11">{x:.4g}</text>']
        path = [(left, axis)]
        for xs, ys in series:
            path.extend((xpx(x), ypx(y)) for x, y in zip(xs, ys))
        path.append((right, axis))
        coordinates = " ".join(f"{x:.2f},{y:.2f}" for x, y in path)
        content.append(f'<polyline points="{coordinates}" fill="none" stroke="{color}" stroke-width="2.4"/>')
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} 422" '
            'font-family="system-ui,sans-serif" font-size="13" fill="#172033" role="img">'
            f'<title>P4–{number}: shear force and bending moment diagrams</title>'
            + "\n".join(content) + "</svg>\n")


def draw_diagrams(output_dir, numbers):
    output_dir.mkdir(parents=True, exist_ok=True)
    models = numeric_models()
    for n in sorted(numbers):
        model = models[n] if n in models else symbolic_model(n)
        path = output_dir / f"logan_p4_{n}_shear_moment.svg"
        path.write_text(diagram(n, model.solve()), encoding="utf-8")

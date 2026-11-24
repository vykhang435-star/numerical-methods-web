"""Check the FEM results against independent integration and Logan 5e."""

import numpy as np
from numpy.polynomial.legendre import leggauss

from logan_ch4_beam import Span, numeric_models, symbolic_model

SYMBOLIC_NUMBERS = (12, 13, 14, 15, 18, 37, 38, 39)


def exact_by_equilibrium(model):
    """Solve by integrating V', M', θ', v' and enforcing support conditions.

    Unknowns are initial v, θ and the restrained DOF reactions, not the
    assembled stiffness DOFs. Reactions enter as jumps in V or M.
    """
    fixed = tuple(model.fixed)
    nodal = dict(model.nodal)
    springs = dict(model.springs)
    n = len(model.spans) + 1

    def march(z, load_scale):
        v, theta = z[:2]
        shear = moment = 0
        r = np.zeros(2*n)
        r[list(fixed)] = z[2:]
        d = []
        for i in range(n):
            di = 2*i
            d.extend((v, theta))
            if di in springs:
                r[di] = -springs[di]*v
            shear += r[di] + load_scale*nodal.get(di, 0)
            moment -= r[di+1] + load_scale*nodal.get(di+1, 0)
            if i == n-1:
                break
            span = model.spans[i]
            l, ei = span.length, span.ei
            a = load_scale*span.q_left
            slope = load_scale*(span.q_right-span.q_left)/l
            v += theta*l + (moment*l*l/2 + shear*l**3/6 + a*l**4/24 + slope*l**5/120)/ei
            theta += (moment*l + shear*l*l/2 + a*l**3/6 + slope*l**4/24)/ei
            moment += shear*l + a*l*l/2 + slope*l**3/6
            shear += a*l + slope*l*l/2
            for t, p in span.points:
                dx, p = (1-t)*l, p*load_scale
                v += p*dx**3/(6*ei)
                theta += p*dx*dx/(2*ei)
                moment += p*dx
                shear += p
        d = np.array(d)
        return np.r_[d[list(fixed)], shear, moment], d, r

    basis = np.eye(len(fixed)+2)
    a = np.column_stack([march(z, 0)[0] for z in basis])
    b = march(np.zeros(len(basis)), 1)[0]
    return march(np.linalg.solve(a, -b), 1)[1:]


def verify_solution(sol):
    d_exact, r_exact = exact_by_equilibrium(sol.model)
    # Direct solves; no successive iterates, so epsilon_a is not defined.
    np.testing.assert_allclose(sol.d, d_exact, rtol=1e-9, atol=1e-10)
    np.testing.assert_allclose(sol.reactions, r_exact, rtol=1e-9, atol=1e-8)
    np.testing.assert_allclose(sol.residual[sol.free], 0, atol=1e-8)
    for e, (span, end) in enumerate(zip(sol.model.spans, sol.end_actions, strict=True)):
        l = span.length
        v, shear, moment = sol.fields(e, l)
        np.testing.assert_allclose([v(l), v.deriv()(l)], sol.d[2*e+2:2*e+4], atol=1e-10)
        np.testing.assert_allclose([-shear(l), moment(l)], end[2:], atol=1e-8)
    nonzero = np.abs(d_exact) > 1e-10
    return (100*np.max(np.abs((sol.d[nonzero]-d_exact[nonzero])/d_exact[nonzero]))
            if np.any(nonzero) else 0)


def verify_all():
    numeric = {n: model.solve() for n, model in numeric_models().items()}
    for n, sol in numeric.items():
        error = verify_solution(sol)
        print(f"4.{n}: max displacement or rotation epsilon_t = {error:.2e}% (exact beam theory)")
    for n in SYMBOLIC_NUMBERS:
        errors = [verify_solution(symbolic_model(n, *args).solve())
                  for args in [(1, 1, 1, 0), (1, 1, 0, 1), (2.3, 7.2, 2.1, 4.7)]]
        print(f"4.{n}: max displacement or rotation epsilon_t = {max(errors):.2e}% (exact beam theory)")

    # P4–16: independent Gaussian integration of the virtual-work expression.
    span = Span(1, 1, 0, -1)
    x, weights = leggauss(3)
    gauss_load = sum(-w*(1+t)/4 * span.shape((1+t)/2) for t, w in zip(x, weights))
    np.testing.assert_allclose(span.load(), gauss_load, atol=1e-14)
    np.testing.assert_allclose(span.load(), [-3/20, -1/30, -7/20, 1/20], atol=1e-14)
    print("4.16: consistent load vector checked by independent quadrature")

    # PDF pp. 799–800. Discrepant book entries are tested as discrepancies,
    # not treated as analytic truth; full explanations appear with each result.
    for n, dofs, d_ref in (
        (9, [4, 3, 1], [-7.619e-4, -3.809e-4, 1.904e-4]),
        (10, [2, 3], [-.886, -.00554]),
        (11, [2, 1], [-7.934e-3, -2.975e-3]),
        (19, [4, 5, 3], [-.0244, -.0071, -.00305]),
        (20, [1, 2, 5], [-.0032, -.0115, .0032]),
        (21, [2, 3, 5], [-2.514, -.00698, .0279]),
        (22, [4, 5, 3], [-3.277, -.0323, -.0130]),
        (23, [2], [-2.34]),
    ):
        np.testing.assert_allclose(numeric[n].d[dofs], d_ref, rtol=.003)
    for n, dofs, ref in (
        (9, [0, 2], [-.889, 4.889]), (10, [0], [1.115]),
        (11, [0, 4, 2], [5.208, 5.208, 1.587]),
        (19, [0, 1, 2], [-24, -32, 56]),
        (20, [0, 2, 4], [29.94, .1152, 29.94]),
        (21, [0, 4], [37.5, 22.5]), (22, [0, 1, 2], [-20.5, -71.67*12, 60.5]),
        (23, [0, 1, 4, 5], [5.325, 19.9*12, 5.325, -19.9*12]),
    ):
        np.testing.assert_allclose(numeric[n].reactions[dofs], ref, rtol=.001)
    np.testing.assert_allclose(numeric[19].end_actions, [[-24, -32, 24, -64], [32, 64, 0, 0]], atol=1e-10)
    np.testing.assert_allclose(numeric[20].end_actions[0], [29.94, 0, .058, 59.65], atol=.005)
    np.testing.assert_allclose(numeric[10].reactions[1], 267, atol=.5)  # book has opposite sign
    np.testing.assert_allclose(numeric[21].reactions[1]/12, 225)  # book labels kip·in, not kip·ft

    for n, dofs, ref_d, rdofs, ref_r in (
        (12, [2, 4, 6, 3, 7], [-2/1215, -613/311040, -2/1215, -1/270, 1/270],
         [0, 1], [1/2, 41/540]),
        (13, [2], [-1/384], [0, 1], [1/2, 1/12]),
        (14, [2, 1, 5], [-5/384, -1/24, 1/24], [0], [1/2]),
        (15, [4, 3, 5], [-1/4, -1/8, -7/24], [0, 1, 2], [-3/4, -1/4, 7/4]),
        (18, [3], [1/80], [0, 1, 2], [9/40, 7/120, 11/40]),
        (37, [2], [-1/192-1/384], [0, 1], [1, 1/8+1/12]),
        (38, [2], [-5/648], [], []),
        (39, [2, 3], [-(25+22)/240, -2/8], [0, 1], [1+1/2, 1/2+1/3]),
    ):
        sol = symbolic_model(n).solve()
        np.testing.assert_allclose(sol.d[dofs], ref_d, atol=1e-13)
        np.testing.assert_allclose(sol.reactions[rdofs], ref_r, atol=1e-12)
    s12 = symbolic_model(12).solve()
    np.testing.assert_allclose(s12.d[4], -1/507, rtol=.001)
    assert not np.isclose(s12.reactions[1], 1/12)

    v26, top26 = numeric[26].extrema((.25, .25))
    v27, top27 = numeric[27].extrema((10, 10, 10))
    np.testing.assert_allclose(numeric[26].fields(1, 10)[0](10), -.1953, atol=.00005)
    np.testing.assert_allclose(numeric[27].d[2], -1.028, atol=.0005)
    np.testing.assert_allclose(max(x[1] for x in top26)*200e3, 469, atol=.5)
    np.testing.assert_allclose(np.array([min(x[1] for x in top27), max(x[1] for x in top27)])*30e6,
                               [-34000, 65800], atol=50)
    np.testing.assert_allclose(min(v26, key=lambda x: x[1])[:2], [20.74691689, -.196777515], rtol=1e-7)
    np.testing.assert_allclose(min(v27, key=lambda x: x[1])[:2], [170.05589747, -1.033089577], rtol=1e-7)
    print("All 19 cases checked; see solution notes for printed discrepancies.")


if __name__ == "__main__":
    verify_all()

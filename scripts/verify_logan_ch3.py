"""Cross-check Chapter 3 models against a mixed solve and the printed answer key."""

from math import sqrt

import numpy as np

from logan_ch3_axial import SELECTED, solve

# Observables: d=node displacement, q=free-coordinate displacement, N=axial
# force (positive in tension), s=stress, R=reaction. Node numbers are 1-based.
# Convert the printed local end forces to N=-f_i. Displacement references are
# converted to the model units (mm, in, or ft·lb coefficients for 3.24).
BOOK = {
    "2": (794, {"d2x": -.0595, "d3x": -.119, "R1x": 5, "N1": -5, "N2": -5}),
    "3": (794, {"d2x": .00191, "R1x": -5715, "R3x": -2286, "N1": 5715, "N2": -2286}),
    "4": (794, {"d2x": -.000166, "d3x": -.00133, "R1x": 667, "R4x": 5333,
                "N1": -667, "N2": -4667, "N3": 5333}),
    "5": (794, {"d2x": .003, "d3x": .009, "R1x": -15000, "N1": 15000, "N2": 15000}),
    "7": (794, {"d2x": .0000221, "d3x": .00665, "R1x": -33.15, "R4x": -9975,
                "N1": 33.15, "N2": 33.15, "N3": -9975}),
    "8": (795, {"d2x": -.250, "d3x": -1.678, "R1x": 20}),
    "9": (795, {"d2x": 12.38, "R1x": -520, "R3x": 530, "N1": 520, "N2": 530}),
    "10": (795, {"d2x": .935, "d3x": .727, "R1x": -6.546, "R4x": -1.455,
                 "N1": 6.546, "N2": -1.455, "N3": -1.455}),
    "20": (796, {"d2x": 0, "d2y": .142, "s1": 707, "s2": 707}),
    "22": (796, {"d1x": .00422, "d1y": .01570, "s1": -574, "s2": 422, "s3": 996}),
    "23": (796, {"d1x": .24, "d1y": 0, "s1": 12000}),
    "24": (796, {"d2x": 26675, "d2y": 105021, "d3x": -26675, "d3y": 105021,
                 "N1": 1333, "N2": 1667, "N3": -1667, "N4": 0, "N5": -1333, "N6": 0}),
    "27": (796, {"d3x": .0463, "d3y": -.0176, "N1": 2055, "N2": -6279, "N3": 6600}),
    "29": (796, {"d1x": -.0893, "d1y": -.446, "s1": 31.2, "s2": 26.5, "s3": 6.25}),
    "30": (797, {"d1x": .171, "d1y": -.755, "s1": 79.28, "s2": 11.97, "s3": -23.87}),
    "33a": (797, {"d1x": -3.448, "d1y": -6.896, "s1": 102.4, "s2": -72.4}),
    "33b": (797, {}),
    "49": (798, {"q1": 0, "d2y": -.00283, "R2x": 2000, "s1": 0, "s2": 1414, "s3": 0}),
    "50": (798, {"d2y": -.00283}),
    "51": (798, {"q1": .002, "f1t": -2800, "f2t_abs": 2000, "R2n": -2828}),
}
DISCREPANCIES = {
    "20": {"d2y", "s1", "s2"},
    "51": {"f1t", "R2n"},
}


def verify_mixed(model, result):
    """Solve for member forces and displacements simultaneously, without K."""
    xy = np.asarray(model.nodes, dtype=float)
    g = np.zeros((len(model.elements), xy.size))
    flex = []
    for row, e in zip(g, model.elements):
        dx = xy[e.j - 1] - xy[e.i - 1]
        L = sqrt(dx @ dx)
        row.reshape(xy.shape)[[e.i - 1, e.j - 1]] = [-dx / L, dx / L]
        flex.append(1 / e.spring if e.spring is not None else L / (e.E * e.A))

    scale = 1 / min(flex)
    T = result.T
    b = g @ T
    matrix = np.block([[np.diag(np.array(flex) * scale), -b],
                       [b.T, np.zeros((T.shape[1], T.shape[1]))]])
    rhs = np.r_[scale * g @ result.d0, T.T @ result.P]
    exact = np.linalg.solve(matrix, rhs)
    n = len(flex)
    np.testing.assert_allclose(result.axial, exact[:n], atol=1e-8, rtol=1e-11)
    np.testing.assert_allclose(result.q, exact[n:] / scale, atol=1e-10, rtol=1e-11)
    np.testing.assert_allclose(result.reactions.ravel(), g.T @ exact[:n] - result.P,
                               atol=1e-8, rtol=1e-11)
    external = result.reactions + result.P.reshape(xy.shape)
    np.testing.assert_allclose(T.T @ result.reactions.ravel(), 0, atol=1e-8)
    np.testing.assert_allclose(external.sum(axis=0), 0, atol=1e-8)
    if model.dim == 2:
        moment = (xy[:, 0] * external[:, 1] - xy[:, 1] * external[:, 0]).sum()
        np.testing.assert_allclose(moment, 0, atol=1e-7)


def reference_value(result, label):
    if label in {"f1t", "f2t_abs", "R2n"}:
        applied = result.P.reshape(result.d.shape)
        if label == "f1t":
            return result.reactions[0] @ (np.array([1., -1.]) / sqrt(2))
        if label == "f2t_abs":
            return abs((applied[1] + result.reactions[1]) @ (np.ones(2) / sqrt(2)))
        return result.reactions[1] @ (np.array([-1., 1.]) / sqrt(2))
    category = label[0]
    if category in "dR":
        node, axis = int(label[1:-1]) - 1, "xy".index(label[-1])
        return (result.d if category == "d" else result.reactions)[node, axis]
    return {"N": result.axial, "q": result.q, "s": result.stress}[category][int(label[1:]) - 1]


def verify_all(*, verbose=False):
    results = {}
    for key, model in SELECTED.items():
        result = results[key] = solve(model)
        verify_mixed(model, result)
        page, printed = BOOK[key]
        errors = []
        for label, reference in printed.items():
            actual = reference_value(result, label)
            if reference == 0:
                np.testing.assert_allclose(actual, 0, atol=1e-8)
                continue
            error_pct = 100 * abs(actual - reference) / abs(reference)
            if label in DISCREPANCIES.get(key, set()):
                assert error_pct > 1, (key, label, actual, reference)
                errors.append(f"{label}: {error_pct:.4g}% (discrepancy)")
            elif key == "51" and label == "q1":
                assert round(float(actual), 3) == reference
                errors.append(f"{label}: {error_pct:.4g}% (matches at 0.001 in)")
            else:
                assert error_pct < 1, (key, label, actual, reference, error_pct)
                errors.append(f"{label}: {error_pct:.4g}%")
        if key == "33b":
            # Symmetric two-bar closed form plus vertical spring.
            e = model.elements[0]
            vertical_k = 2 * e.E * e.A / 5000 * (3 / 4) + model.elements[2].spring
            np.testing.assert_allclose(result.q, (0, -100 / vertical_k), atol=1e-12)
        if verbose:
            print(f"P3-{key}: mixed solve + equilibrium OK; PDF p. {page}: "
                  + (", ".join(errors) if printed else "not listed; symmetric closed form OK"))
    if verbose:
        print(f"Verified {len(results)} direct solves. No iterations (epsilon_a not applicable).")
    return results


if __name__ == "__main__":
    verify_all(verbose=True)

"""Euler–Bernoulli beam models, using upward forces and CCW couples."""

from dataclasses import dataclass
from fractions import Fraction as Q

import numpy as np
from numpy.polynomial import Polynomial


@dataclass(frozen=True)
class Span:
    length: float
    ei: float
    q_left: float = 0
    q_right: float = 0
    points: tuple = ()  # (x / length, signed transverse force)

    def stiffness(self):
        l = self.length
        return self.ei / l**3 * np.array([
            [12, 6*l, -12, 6*l],
            [6*l, 4*l*l, -6*l, 2*l*l],
            [-12, -6*l, 12, -6*l],
            [6*l, 2*l*l, -6*l, 4*l*l],
        ], dtype=float)

    def shape(self, t):
        l = self.length
        return np.array([1-3*t*t+2*t**3, l*(t-2*t*t+t**3),
                         3*t*t-2*t**3, l*(-t*t+t**3)], dtype=float)

    def load(self):
        l, a, b = self.length, self.q_left, self.q_right
        vector = np.array([l*(7*a+3*b)/20, l*l*(3*a+2*b)/60,
                           l*(3*a+7*b)/20, -l*l*(2*a+3*b)/60], dtype=float)
        for t, p in self.points:
            vector += self.shape(t) * p
        return vector


@dataclass(frozen=True)
class Beam:
    spans: tuple
    fixed: tuple
    nodal: tuple = ()    # (global DOF, signed load)
    springs: tuple = ()  # (vertical DOF, stiffness to immovable ground)

    def solve(self):
        n = 2 * (len(self.spans) + 1)
        k, f = np.zeros((n, n)), np.zeros(n)
        for e, span in enumerate(self.spans):
            s = slice(2*e, 2*e+4)
            k[s, s] += span.stiffness()
            f[s] += span.load()
        for i, p in self.nodal:
            f[i] += p
        for i, ks in self.springs:
            k[i, i] += ks
        free = sorted(set(range(n)) - set(self.fixed))
        d = np.zeros(n)
        d[free] = np.linalg.solve(k[np.ix_(free, free)], f[free])
        residual = k @ d - f
        reactions = np.zeros(n)
        reactions[list(self.fixed)] = residual[list(self.fixed)]
        for i, ks in self.springs:
            reactions[i] -= ks*d[i]
        end_actions = tuple(span.stiffness() @ d[2*e:2*e+4] - span.load()
                            for e, span in enumerate(self.spans))
        return Solution(self, k, f, free, d, residual, reactions, end_actions)


@dataclass
class Solution:
    model: Beam
    k: np.ndarray
    f: np.ndarray
    free: list
    d: np.ndarray
    residual: np.ndarray
    reactions: np.ndarray
    end_actions: tuple

    def fields(self, e, x):
        """Exact within each load interval: v, V, M as polynomials in local x."""
        span = self.model.spans[e]
        v0, theta0 = self.d[2*e:2*e+2]
        shear0, couple0 = self.end_actions[e][:2]
        moment = Polynomial([-couple0, shear0, span.q_left/2,
                             (span.q_right-span.q_left)/(6*span.length)])
        displacement = Polynomial([v0, theta0]) + moment.integ(2) / span.ei
        for t, p in span.points:
            a = t*span.length
            if a < x:
                moment += Polynomial([-p*a, p])
                displacement += p/(6*span.ei)*Polynomial([-a, 1])**3
        return displacement, moment.deriv(), moment

    def extrema(self, depths):
        """Return candidates (x, value, element) for deflection and top stress."""
        origin = 0
        v_values, stress_values = [], []
        for e, (span, c) in enumerate(zip(self.model.spans, depths, strict=True)):
            l = span.length
            breaks = [0, *sorted(t*l for t, _ in span.points), l]
            for a, b in zip(breaks, breaks[1:]):
                v, shear, moment = self.fields(e, (a+b)/2)
                for slope, field, scale, results in (
                    (v.deriv(), v, 1, v_values),
                    (shear, moment, -c/span.ei, stress_values),
                ):
                    roots = [r.real for r in slope.roots() if abs(r.imag) < 1e-9 and a < r.real < b]
                    results.extend((origin+x, scale*field(x), e) for x in [a, *roots, b])
            origin += l
        # Stress values must still be multiplied by E, since span.ei is EI.
        return v_values, stress_values


def numeric_models():
    """SI models use kN/m; US customary models use kip/in."""
    return {
        9: Beam(tuple(Span(l, 70e6*1e-4) for l in (3, 2, 2, 3)),
                (0, 2, 6, 8), ((4, -8),)),
        10: Beam((Span(240, 29e3*200),), (0, 1), ((2, -2),), ((2, 1),)),
        11: Beam((Span(4, 70e6*2e-4),)*2, (0, 4), ((2, -12),), ((2, 200),)),
        19: Beam((Span(4, 70e6*3e-4), Span(4, 70e6*3e-4, -8, -8)), (0, 1, 2)),
        20: Beam((Span(6, 210e6*4e-4, -10, 0), Span(6, 210e6*4e-4, 0, -10)),
                 (0, 4), springs=((2, 10),)),
        21: Beam((Span(180, 29e3*200, -2/12, -2/12),)*2, (0, 1, 4)),
        22: Beam((Span(120, 29e3*150, 0, -2/12), Span(120, 29e3*150, -2/12, -4/12)),
                 (0, 1, 2)),
        23: Beam((Span(240, 1.6e3*100, -.5/12, -.5/12),)*2,
                 (0, 1, 4, 5), springs=((2, 4),)),
        26: Beam((Span(10, 200e6*500e-6, -30, -30),
                  Span(20, 200e6*1000e-6, -30, -30)), (0, 2, 4)),
        27: Beam((Span(180, 30e3*1500), Span(180, 30e3*1500),
                  Span(360, 30e3*500, -2/12, -2/12)), (0, 4, 6), ((2, -75),)),
    }


def symbolic_model(number, length=1, ei=1, w=1, p=1):
    """Physical model for arbitrary base L, EI, w and P; L is one bay in 4.15."""
    def span(l, a=0, b=0, ratio=1, points=()):
        return Span(length*float(l), ei*ratio, -w*a, -w*b,
                    tuple((float(t), -p) for t in points))

    if number == 12:
        return Beam((span(Q(1, 3), 1, 1), span(Q(1, 6), 1, 1, 2),
                     span(Q(1, 6), 1, 1, 2), span(Q(1, 3), 1, 1)), (0, 1, 8, 9))
    if number == 13:
        return Beam((span(.5, 1, 1),)*2, (0, 1, 4, 5))
    if number == 14:
        return Beam((span(.5, 1, 1),)*2, (0, 4))
    if number == 15:
        return Beam((span(1), span(1, 1, 1)), (0, 1, 2))
    if number == 18:
        return Beam((span(1, 0, 1),), (0, 1, 2))
    if number == 37:
        return Beam((span(.5, 1, 1),)*2, (0, 1, 4, 5), ((2, -p),))
    if number == 38:
        return Beam((span(.5, points=(Q(2, 3),)), span(.5, points=(Q(1, 3),))),
                    (0, 1, 4, 5))
    if number == 39:
        return Beam((span(1, 0, 1, points=(.5,)),), (0, 1))
    raise ValueError(f"No symbolic model for problem 4.{number}")


def unit_responses(number):
    """Separate unit responses to w and P before recovering dimensional formulas."""
    model = symbolic_model(number)
    uniform = symbolic_model(number, p=0).solve()
    point = symbolic_model(number, w=0).solve()
    return model, uniform, point

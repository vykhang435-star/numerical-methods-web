"""Input models and direct-stiffness solver for the selected Logan 5e exercises."""

from dataclasses import dataclass
from math import sqrt

import numpy as np


@dataclass(frozen=True)
class Element:
    i: int
    j: int
    E: float = 0.
    A: float = 0.
    spring: float | None = None


@dataclass(frozen=True)
class Freedom:
    node: int
    label: str
    direction: tuple


@dataclass(frozen=True)
class Model:
    nodes: tuple
    elements: tuple
    loads: dict
    free: tuple
    length_unit: str
    force_unit: str
    prescribed: tuple = ()
    symbolic: bool = False

    @property
    def dim(self):
        return len(self.nodes[0])

    @property
    def stress_unit(self):
        return "MPa" if self.length_unit == "mm" else "psi"


@dataclass(frozen=True)
class Result:
    K: np.ndarray
    P: np.ndarray
    d0: np.ndarray
    T: np.ndarray
    lengths: np.ndarray
    directions: np.ndarray
    stiffness: np.ndarray
    Kr: np.ndarray
    Pr: np.ndarray
    q: np.ndarray
    d: np.ndarray
    axial: np.ndarray
    stress: tuple
    reactions: np.ndarray


def bar(spans, materials, loads, free, *, si=False, prescribed=()):
    elements = tuple(
        Element(i, i + 1, *material) if isinstance(material, tuple)
        else Element(i, i + 1, spring=material)
        for i, material in enumerate(materials, 1)
    )
    return Model(tuple((x,) for x in np.r_[0, np.cumsum(spans)]), elements,
                 {n: (p,) for n, p in loads.items()},
                 tuple(Freedom(n, f"u_{n}", (1.,)) for n in free),
                 "mm" if si else "in", "kN" if si else "lb", prescribed)


def axes(*nodes):
    return tuple(Freedom(n, f"{name}_{n}", v) for n in nodes
                 for name, v in (("u", (1., 0.)), ("v", (0., 1.))))


def truss(nodes, pairs, E, A, loads, free, *, si=False, spring=None, symbolic=False):
    elements = tuple(Element(i, j, E, A) for i, j in pairs)
    if spring is not None:
        elements += (Element(*spring[:2], spring=spring[2]),)
    return Model(nodes, elements, loads, free,
                 "ft" if symbolic else "mm" if si else "in",
                 "kN" if si else "lb", symbolic=symbolic)


h = sqrt(0.5)
s60 = sqrt(3) / 2
p = 2000.
v2 = Freedom(2, "v_2", (0., 1.))
t1 = Freedom(1, "q_1", (h, -h))
t2 = Freedom(2, "q_2", (h, h))
SELECTED = {
    "2": bar((1000, 1000), ((210, 400),) * 2, {3: -5}, (2, 3), si=True),
    "3": bar((20, 50), ((30e6, 2),) * 2, {2: 8000}, (2,)),
    "4": bar((30, 30, 30), ((30e6, 4),) * 3, {2: 4000, 3: -10000}, (2, 3)),
    "5": bar((30, 30), ((30e6, 5), (15e6, 5)), {3: 15000}, (2, 3)),
    # A positive placeholder span sets the spring orientation; its length
    # does not enter the stiffness or get shown in the card.
    "7": bar((30, 1, 30), ((15e6, 3), 5000, (15e6, 3)), {3: 10000}, (2, 3)),
    "8": bar((1000, 1000), ((200, 400), (70, 200)), {3: -20}, (2, 3), si=True),
    "9": bar((2000, 2000), ((210, 400),) * 2, {2: -10}, (2,),
             si=True, prescribed=((3, 0, 25),)),
    "10": bar((2000, 2000, 1), ((70, 200), (70, 200), 2), {2: 8}, (2, 3), si=True),
    "20": truss(((0, 0), (100, 100), (200, 0)), ((1, 2), (2, 3)),
                1e6, 5, {2: (0, 10000)}, axes(2)),
    "22": truss(((100, 0), (0, 100 * sqrt(3)), (0, 0), (0, -100 / sqrt(3))),
                ((2, 1), (3, 1), (4, 1)), 10e6, 1, {1: (1000, 1000)}, axes(1)),
    "23": truss(((50, 100 * s60), (0, 0), (100, 0)), ((2, 1), (3, 1)),
                10e6, 1, {1: (12000, 0)}, axes(1)),
    "24": truss(((0, 0), (20, 0), (20, 15), (0, 15)),
                ((1, 2), (1, 3), (2, 4), (2, 3), (3, 4), (1, 4)),
                1, 1, {2: (0, 1000), 3: (0, 1000)}, axes(2, 3), symbolic=True),
    "27": truss(((0, 0), (720, 0), (360, 480), (360, 720)), ((1, 3), (2, 3), (3, 4)),
                30e6, 3, {3: (5000, -10000)}, axes(3)),
    "29": truss(((0, 0), (0, 3000), (3000 * h, 3000 * h), (3000, 0)),
                ((1, 2), (1, 3), (1, 4)), 210, 400, {1: (-10, -20)}, axes(1), si=True),
    "30": truss(((0, 0), (0, 2000), (-3000, 0), (-2500, -5000 * s60)),
                ((1, 2), (1, 3), (1, 4)), 210, 400, {1: (0, -40)}, axes(1), si=True),
    "33a": truss(((0, 0), (-5000 * h, 5000 * h), (-10000, 0), (0, -5000)),
                 ((1, 2), (1, 3)), 210, 500, {1: (0, -50)}, axes(1),
                 si=True, spring=(1, 4, 2)),
    "33b": truss(((0, 0), (-2500, 5000 * s60), (2500, 5000 * s60), (0, -5000)),
                 ((1, 2), (1, 3)), 210, 500, {1: (0, -100)}, axes(1),
                 si=True, spring=(1, 4, .004)),
    "49": truss(((0, 0), (30, 0), (0, 30)), ((1, 2), (2, 3), (1, 3)),
                30e6, 2, {2: (0, -p)}, (t1, v2)),
    "50": truss(((0, 0), (30, 30), (0, 30)), ((1, 2), (2, 3), (1, 3)),
                30e6, 2, {2: (0, -p)}, (t1, v2)),
    "51": truss(((0, 0), (30, 0), (15, 30 * s60)), ((1, 2), (2, 3), (1, 3)),
                30e6, 2, {2: (p * h, p * h)}, (t2,)),
}


def solve(model):
    nodes = np.asarray(model.nodes)
    dim = model.dim
    direction = []
    lengths = []
    stiffness = []
    dof_count = nodes.size
    K = np.zeros((dof_count, dof_count))
    element_rows = []
    for e in model.elements:
        delta = nodes[e.j - 1] - nodes[e.i - 1]
        length = np.linalg.norm(delta)
        n = delta / length
        a = np.zeros_like(nodes, dtype=float)
        a[e.i - 1], a[e.j - 1] = -n, n
        a = a.ravel()
        k = e.spring if e.spring is not None else e.E * e.A / length
        K += k * np.outer(a, a)
        element_rows.append(a)
        stiffness.append(k)
        lengths.append(length)
        direction.append(n)

    P = np.array([model.loads.get(node, (0.,) * dim)
                  for node in range(1, len(nodes) + 1)], dtype=float).ravel()
    d0 = np.zeros(dof_count)
    for node, axis, value in model.prescribed:
        d0[(node - 1) * dim + axis] = value
    T = np.zeros((dof_count, len(model.free)))
    for j, dof in enumerate(model.free):
        T[(dof.node - 1) * dim:dof.node * dim, j] = dof.direction
    Kr, Pr = T.T @ K @ T, T.T @ (P - K @ d0)
    q = np.linalg.solve(Kr, Pr)
    d = d0 + T @ q
    stress_factor = 1000 if model.stress_unit == "MPa" else 1
    axial = np.asarray(stiffness) * (np.asarray(element_rows) @ d)
    stress = tuple(None if e.spring is not None or model.symbolic else n / e.A * stress_factor
                   for e, n in zip(model.elements, axial))
    return Result(K, P, d0, T, np.asarray(lengths), np.asarray(direction),
                  np.asarray(stiffness), Kr, Pr, q, d.reshape(-1, dim), axial,
                  stress, (K @ d - P).reshape(-1, dim))

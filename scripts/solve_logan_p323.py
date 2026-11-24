"""Solve Logan 5e Problem 3.23 by the direct stiffness method."""

import numpy as np


def main() -> None:
    # Inches, pounds, and psi. Nodes 2 and 3 have zero x/y displacement.
    area = 1.0
    modulus = 10.0e6
    nodes = np.array([[50.0, 50.0 * np.sqrt(3.0)], [0.0, 0.0], [100.0, 0.0]])
    load = np.array([12_000.0, 0.0])

    # Unit vectors point from each support (2, 3) to the free node (1).
    vectors = nodes[0] - nodes[1:]
    lengths = np.linalg.norm(vectors, axis=1)
    directions = vectors / lengths[:, None]
    angles = np.degrees(np.arctan2(directions[:, 1], directions[:, 0]))
    axial_stiffness = modulus * area / lengths
    member_blocks = np.array([
        k * np.outer(n, n) for k, n in zip(axial_stiffness, directions)
    ])
    stiffness = member_blocks.sum(axis=0)
    displacement = np.linalg.solve(stiffness, load)

    # Project the relative displacement onto each member's axis.
    elongations = directions @ displacement
    stresses = modulus * elongations / lengths
    axial_forces = area * stresses
    reactions = -axial_forces[:, None] * directions
    force_residual = load + reactions.sum(axis=0)
    matrix_format = {"float_kind": lambda value: f"{value: 8.6g}"}

    print("Logan 5e, Problem 3.23 - plane truss")
    print(f"A = {area:g} in^2, E = {modulus:.6g} psi, P = ({load[0]:g}, {load[1]:g}) lb")
    for i, (x, y) in enumerate(nodes, start=1):
        print(f"Node {i}: ({x:.6g}, {y:.6g}) in")
    for i, (length, angle, direction, block) in enumerate(
        zip(lengths, angles, directions, member_blocks), start=1
    ):
        print(f"\nElement {i} ({i + 1} -> 1): L = {length:.6g} in, theta = {angle:.6g} deg")
        print(f"  (c, s) = ({direction[0]:.6g}, {direction[1]:.6g})")
        print("  Element stiffness contribution at node 1 (lb/in):")
        print(np.array2string(block, formatter=matrix_format))

    print("\nReduced system K_ff d_1 = P, DOFs (1x, 1y):")
    print("K_ff (lb/in):")
    print(np.array2string(stiffness, formatter=matrix_format))
    print(f"d_1x = {displacement[0]:.4f} in")
    print(f"d_1y = {displacement[1]:.4f} in")
    for i, (elongation, force, stress) in enumerate(
        zip(elongations, axial_forces, stresses), start=1
    ):
        state = "tension" if stress > 0 else "compression" if stress < 0 else "unstressed"
        print(
            f"Element {i}: elongation = {elongation:+.4f} in, N_{i} = {force:+.4f} lb, "
            f"sigma_{i} = {stress:+.4f} psi ({state})"
        )
    for i, (rx, ry) in enumerate(reactions, start=2):
        print(f"Support {i}: (Rx, Ry) = ({rx:+.6g}, {ry:+.6g}) lb")
    print(f"Force-equilibrium residual: ({force_residual[0]:.3e}, {force_residual[1]:.3e}) lb")

    print("\nComparison with Logan's answer key (printed page 777; PDF page 796, index 795):")
    for label, computed, reference, unit in (
        ("d_1x", displacement[0], 0.24, "in"),
        ("d_1y", displacement[1], 0.0, "in"),
        ("sigma_1", stresses[0], 12_000.0, "psi"),
    ):
        print(
            f"  {label}: book = {reference:g} {unit}, computed = {computed:.4f} {unit}, "
            f"computed - book = {computed - reference:+.3e} {unit}"
        )
    print("  sigma_2 is not listed in the answer key.")


if __name__ == "__main__":
    main()

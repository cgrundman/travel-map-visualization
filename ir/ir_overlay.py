import random

import numpy as np
import svgwrite
from scipy.spatial import Delaunay


def create_prismatic_svg(
    filename="overlay.svg",
    width=400,
    height=350,
    n_points=18000,
    seed=42
):
    random.seed(seed)
    np.random.seed(seed)

    # Persian-inspired palette
    palette = [
        ("#222222", 0.05),
        ("#222222", 0.10),
        ("#222222", 0.15),
        ("#222222", 0.00),
    ]

    # Generate random internal points
    x = np.random.uniform(0, width, n_points)
    y = np.random.uniform(0, height, n_points)

    points = np.column_stack((x, y))

    # Add boundary points so the triangulation covers the whole canvas
    boundary_points = np.array([
        [0, 0],
        [width, 0],
        [0, height],
        [width, height],

        [width / 2, 0],
        [width / 2, height],
        [0, height / 2],
        [width, height / 2],
    ])

    points = np.vstack((points, boundary_points))

    # Delaunay triangulation
    tri = Delaunay(points)

    # Create SVG
    dwg = svgwrite.Drawing(
        filename,
        size=(width, height),
        viewBox=f"0 0 {width} {height}"
    )

    # Draw triangles
    for simplex in tri.simplices:

        triangle_points = points[simplex]

        polygon_points = [
            (float(px), float(py))
            for px, py in triangle_points
        ]

        fill_color, opacity = random.choice(palette)

        dwg.add(
            dwg.polygon(
                points=polygon_points,
                fill=fill_color,
                fill_opacity=opacity*2,
                stroke="none"
            )
        )

    dwg.save()

    print(f"Saved: {filename}")


if __name__ == "__main__":
    create_prismatic_svg()
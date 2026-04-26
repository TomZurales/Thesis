import matplotlib
matplotlib.use("TkAgg")
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D


def plot_icosahedron_face_vectors(face_vectors, elev=20, azim=30):
    """
    Plot unit vectors through icosahedron face centres on a sphere.

    Parameters
    ----------
    face_vectors : array-like, shape (20, 3)
        Unit vectors through the face centres, as produced by
        icosahedron_face_vectors.py.
    elev : float
        Elevation angle of the 3-D view in degrees.
    azim : float
        Azimuth angle of the 3-D view in degrees.
    """
    vecs = np.asarray(face_vectors)
    assert vecs.shape == (20, 3), f"Expected (20,3), got {vecs.shape}"

    fig = plt.figure(figsize=(8, 8))
    ax  = fig.add_subplot(111, projection="3d")

    # ── reference sphere (wireframe) ─────────────────────────────────────────
    u, v   = np.mgrid[0 : 2*np.pi : 40j, 0 : np.pi : 20j]
    xs, ys = np.cos(u) * np.sin(v), np.sin(u) * np.sin(v)
    zs     = np.cos(v)
    ax.plot_wireframe(xs, ys, zs, color="lightgray", linewidth=0.3, alpha=0.4)

    # ── colour-code by latitude band ─────────────────────────────────────────
    ys_fc      = vecs[:, 1]
    unique_y   = np.array(sorted(set(np.round(ys_fc, 4)), reverse=True))
    band_colors = ["#E8593C", "#3B8BD4", "#1D9E75", "#888780"]   # top→bottom
    band_labels = ["top cap", "upper equat.", "lower equat.", "bottom cap"]

    for band_y, color, label in zip(unique_y, band_colors, band_labels):
        mask = np.isclose(np.round(vecs[:, 1], 4), band_y)
        pts  = vecs[mask]

        # Dots on the sphere surface
        ax.scatter(pts[:, 0], pts[:, 1], pts[:, 2],
                   color=color, s=60, zorder=5, label=label)

        # Arrows from origin → point
        for p in pts:
            ax.quiver(0, 0, 0, p[0], p[1], p[2],
                      length=1.0, color=color, alpha=0.7,
                      arrow_length_ratio=0.08, linewidth=1.2)

    # ── reference axes ────────────────────────────────────────────────────────
    for vec, col, lbl in [
        ([1.3, 0, 0], "red",   "+X"),
        ([0, 1.3, 0], "green", "+Y"),
        ([0, 0, 1.3], "blue",  "+Z"),
    ]:
        ax.quiver(0, 0, 0, *vec, color=col, linewidth=1.5,
                  arrow_length_ratio=0.1, alpha=0.6)
        ax.text(*[c * 1.15 for c in vec], lbl, color=col,
                fontsize=10, fontweight="bold", ha="center")

    # ── vertex markers (+Y pole and its antipode) ─────────────────────────────
    for p, mk, lbl in [([0, 1, 0], "^", "vertex (+Y)"),
                        ([0,-1, 0], "v", "vertex (−Y)")]:
        ax.scatter(*p, marker=mk, s=120, color="black", zorder=6)
        ax.text(p[0], p[1]*1.15, p[2], lbl, fontsize=8, ha="center")

    # ── formatting ────────────────────────────────────────────────────────────
    ax.set_xlim(-1.4, 1.4)
    ax.set_ylim(-1.4, 1.4)
    ax.set_zlim(-1.4, 1.4)
    ax.set_xlabel("X"); ax.set_ylabel("Y"); ax.set_zlabel("Z")
    ax.set_title("Icosahedron face-centre unit vectors\n"
                 "(vertex at +Y,  ref face centre in XZ plane, x > 0)",
                 fontsize=11)
    ax.view_init(elev=elev, azim=azim)
    ax.legend(loc="upper left", fontsize=9, framealpha=0.7)
    ax.set_aspect("equal")

    plt.tight_layout()
    plt.show()


# ── example usage ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    face_center_unit_vectors = np.array([
        [-0.1875924741, +0.7946544723, -0.5773502692],
        [+0.4911234732, +0.7946544723, +0.3568220898],
        [-0.6070619982, +0.7946544723, -0.0000000000],
        [+0.4911234732, +0.7946544723, -0.3568220898],
        [-0.1875924741, +0.7946544723, +0.5773502692],
        [-0.9822469464, +0.1875924741, -0.0000000000],
        [-0.3035309991, +0.1875924741, +0.9341723590],
        [+0.7946544723, +0.1875924741, -0.5773502692],
        [-0.3035309991, +0.1875924741, -0.9341723590],
        [+0.7946544723, +0.1875924741, +0.5773502692],
        [-0.7946544723, -0.1875924741, -0.5773502692],
        [+0.3035309991, -0.1875924741, +0.9341723590],
        [-0.7946544723, -0.1875924741, +0.5773502692],
        [+0.3035309991, -0.1875924741, -0.9341723590],
        [+0.9822469464, -0.1875924741, +0.0000000000],
        [+0.1875924741, -0.7946544723, -0.5773502692],
        [+0.6070619982, -0.7946544723, +0.0000000000],
        [-0.4911234732, -0.7946544723, +0.3568220898],
        [-0.4911234732, -0.7946544723, -0.3568220898],
        [+0.1875924741, -0.7946544723, +0.5773502692],
    ])

    plot_icosahedron_face_vectors(face_center_unit_vectors)
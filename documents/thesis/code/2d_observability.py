import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.text import Text


# Represents a point in cartesian and polar coordinates. Theta in radians
class Point:
    x: float
    y: float
    r: float
    theta: float

    def __init__(self, x_or_r: float, y_or_theta: float, polar: bool = False):
        if polar:
            self.r = x_or_r
            self.theta = y_or_theta
            self.x = self.r * np.cos(self.theta)
            self.y = self.r * np.sin(self.theta)
        else:
            self.x = x_or_r
            self.y = y_or_theta
            self.r = np.sqrt(self.x**2 + self.y**2)
            self.theta = np.arctan2(self.y, self.x)


class Barrier:
    p1: Point
    p2: Point

    def __init__(self, p1: Point, p2: Point):
        self.p1 = p1
        self.p2 = p2

    # Returns true if a line segment from p to the origin intersects the line segment from p1 to p2
    def intersects(self, p: Point):
        # Line segment 1: from p to origin (0,0)
        # Line segment 2: from self.p1 to self.p2

        # Get coordinates
        x1, y1 = p.x, p.y
        x2, y2 = 0.0, 0.0
        x3, y3 = self.p1.x, self.p1.y
        x4, y4 = self.p2.x, self.p2.y

        # Calculate the denominator for the intersection formula
        denom = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)

        # If denominator is 0, lines are parallel
        if abs(denom) < 1e-10:
            return False

        # Calculate parameters t and u
        t = ((x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)) / denom
        u = -((x1 - x2) * (y1 - y3) - (y1 - y2) * (x1 - x3)) / denom

        # Check if intersection point lies within both line segments
        # t should be between 0 and 1 for line segment 1 (p to origin)
        # u should be between 0 and 1 for line segment 2 (p1 to p2)
        return 0 <= t <= 1 and 0 <= u <= 1


class Observability2D:
    barriers: list[Barrier] = []

    def __init__(self):
        # Create custom colormap: red -> white -> blue
        colors = ["red", "white", "blue"]
        n_bins = 256
        self.custom_cmap = LinearSegmentedColormap.from_list(
            "red_white_blue", colors, N=n_bins
        )

    def add_barrier(self, barrier: Barrier):
        self.barriers.append(barrier)

    def check_visibility(self, p: Point):
        for barrier in self.barriers:
            if barrier.intersects(p):
                return False
        return True

    def draw_barriers(self, ax):
        for barrier in self.barriers:
            ax.plot(
                [barrier.p1.theta, barrier.p2.theta],
                [barrier.p1.r, barrier.p2.r],
                color="black",
            )

    def draw_real_observability(self, ax):
        thetas = np.linspace(0, 2 * np.pi, 360)
        rs = np.linspace(0, 1, 100)
        R, Theta = np.meshgrid(rs, thetas)
        Z = np.zeros(R.shape)
        for i in range(R.shape[0]):
            for j in range(R.shape[1]):
                p = Point(R[i, j], Theta[i, j], polar=True)
                Z[i, j] = 1 if self.check_visibility(p) else 0

        # Plot the observability map
        ax.contourf(Theta, R, Z, levels=50, cmap=self.custom_cmap, alpha=0.7)

    def draw_knn_model(self, ax, k: int, samples: list[Point]):
        thetas = np.linspace(0, 2 * np.pi, 360)
        rs = np.linspace(0, 1, 100)
        R, Theta = np.meshgrid(rs, thetas)
        Z = np.zeros(R.shape)

        # For each point in the grid, find the k nearest samples and determine visibility
        for i in range(R.shape[0]):
            for j in range(R.shape[1]):
                p = Point(R[i, j], Theta[i, j], polar=True)
                # Compute distances to all samples
                distances = [
                    np.sqrt((p.x - s.x) ** 2 + (p.y - s.y) ** 2) for s in samples
                ]
                # Get indices of k nearest samples
                knn_indices = np.argsort(distances)[:k]
                # Determine visibility based on majority vote
                votes = [self.check_visibility(samples[idx]) for idx in knn_indices]
                visible = votes.count(True) / len(votes)
                Z[i, j] = visible  # Store as 0-1 value instead of 0-1000

        # Plot the observability map
        ax.contourf(Theta, R, Z, levels=50, cmap=self.custom_cmap, alpha=0.7)

    def draw_binned_model(self, ax, samples: list[Point], num_bins: int = 6):
        thetas = np.linspace(0, 2 * np.pi, 360)
        rs = np.linspace(0, 1, 100)
        R, Theta = np.meshgrid(rs, thetas)
        Z = np.zeros(R.shape)

        # Define our bins
        n_seen = [0 for _ in range(num_bins)]
        ntotal = [0 for _ in range(num_bins)]
        max_r = [0 for _ in range(num_bins)]

        # Bin the samples
        for sample in samples:
            bin_idx = int((sample.theta / (2 * np.pi)) * num_bins) % num_bins
            if self.check_visibility(sample):
                n_seen[bin_idx] += 1
                max_r[bin_idx] = max(max_r[bin_idx], sample.r)
            ntotal[bin_idx] += 1

        for i in range(R.shape[0]):
            for j in range(R.shape[1]):
                p = Point(R[i, j], Theta[i, j], polar=True)
                bin_idx = int((p.theta / (2 * np.pi)) * num_bins) % num_bins
                if p.r <= max_r[bin_idx]:
                    Z[i, j] = (
                        n_seen[bin_idx] / ntotal[bin_idx] if ntotal[bin_idx] > 0 else 0
                    )
                else:
                    Z[i, j] = 0

        # Plot the observability map
        ax.contourf(Theta, R, Z, levels=50, cmap=self.custom_cmap, alpha=0.7)

    def draw_samples(self, ax, samples: list[Point]):
        for sample in samples:
            if self.check_visibility(sample):
                ax.plot(sample.theta, sample.r, marker="+", color="blue")
            else:
                ax.plot(sample.theta, sample.r, marker="_", color="red")


# Create figure with side-by-side polar subplots
fig, (ax1, ax2) = plt.subplots(
    1, 2, subplot_kw=dict(projection="polar"), figsize=(14, 8)
)

obs = Observability2D()
# Add 5 random barriers
# for _ in range(5):
#     r1 = np.random.uniform(0.1, 1)
#     theta1 = np.random.uniform(0, 2 * np.pi)
#     r2 = np.random.uniform(0.1, 1)
#     theta2 = np.random.uniform(0, 2 * np.pi)
#     obs.add_barrier(Barrier(Point(r1, theta1, True), Point(r2, theta2, True)))

obs.add_barrier(Barrier(Point(0.4, np.pi / 4, True), Point(0.4, -np.pi / 4, True)))
obs.add_barrier(Barrier(Point(0.4, np.pi / 4, True), Point( 0.4, 3 *np.pi / 4,True)))

samples = []
num_samples = 50
for _ in range(num_samples):
    r = np.random.uniform(0.1, 1)
    theta = np.random.uniform(0, 2 * np.pi)
    samples.append(Point(r, theta, True))

# Left plot: Real observability
ax1.plot(0, 0, "ro", markersize=8, label="p", color="black")
ax1.text(-np.pi/4, 0.03, "$p$", ha="left", va="top", fontsize=12)
obs.draw_barriers(ax1)
obs.draw_real_observability(ax1)
ax1.set_title("True Observability")

# Add legend for observability regions
from matplotlib.patches import Patch
legend_elements = [
    Patch(facecolor='blue', alpha=0.8, label='Observable'),
    Patch(facecolor='red', alpha=0.8, label='Not Observable')
]
ax1.legend(handles=legend_elements, loc='upper right', bbox_to_anchor=(1.05, 1.05))

# Right plot: KNN model
ax2.plot(0, 0, "ro", markersize=8, label="p", color="black")
ax2.text(-np.pi/4, 0.03, "$p$", ha="left", va="top", fontsize=12)
obs.draw_barriers(ax2)
obs.draw_samples(ax2, samples)
# obs.draw_knn_model(ax2, 1, samples)
ax2.set_title("Sampled Observability")

# Add legend for observation samples
from matplotlib.lines import Line2D
legend_elements = [
    Line2D([0], [0], marker='+', color='blue', linestyle='None', markersize=8, label='Positive Observation'),
    Line2D([0], [0], marker='_', color='red', linestyle='None', markersize=8, label='Negative Observation')
]
ax2.legend(handles=legend_elements, loc='upper right', bbox_to_anchor=(1.05, 1.05))

# # Right plot: Binned model
# ax3.plot(0, 0, "ro", markersize=8, label="p")
# ax3.text(0, 0.1, "$p$", ha="center", va="bottom", fontsize=12)
# obs.draw_barriers(ax3)
# obs.draw_samples(ax3, samples)
# obs.draw_binned_model(ax3, samples, 20)
# ax3.set_title("Binned Model")

# random_observations = []
# num_samples = 100
# for _ in range(num_samples):
#     r = np.random.uniform(0.1, 1)
#     theta = np.random.uniform(0, 2 * np.pi)
#     p = Point(r, theta, True)
#     visible = obs.check_visibility(p)
#     random_observations.append((p, visible))
#     color = "green" if visible else "red"
#     ax.plot(p.theta, p.r, "o", color=color)

# Set up all plots
for ax in [ax1, ax2]:
    ax.set_ylim(0, 1.05)
    # ax.get_yticklabels()
    ax.set_yticklabels([Text(0, 0, ''), Text(0, 0, ''), Text(0, 0, ''), Text(0, 0, ''), Text(0, 0, '$d_{max}$')])  # Remove radial distance labels
    # Create radian labels as fractions of pi
    radian_labels = ["0", "π/4", "π/2", "3π/4", "π", "5π/4", "3π/2", "7π/4"]
    ax.set_thetagrids(
        np.degrees(np.linspace(0, 2 * np.pi, 8, endpoint=False)), labels=radian_labels
    )
    ax.grid(True)

plt.tight_layout()
plt.show()

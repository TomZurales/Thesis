import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.colors as mcolors
from viewpoint import Viewpoint
from observation import Observation
from constants import ObservationState

class ErrorPlot:
    def __init__(self):
        # Create figure and 3D axis
        self.fig = plt.figure(figsize=(10, 8))
        self.ax = self.fig.add_subplot(111, projection='3d')
        
        # Set up the plot
        self.ax.set_xlabel('X')
        self.ax.set_ylabel('Y')
        self.ax.set_zlabel('Z')
        self.ax.set_title('Error Plot')
        
        # Lock axes to -1 to 1 range
        self.ax.set_xlim(-1, 1)
        self.ax.set_ylim(-1, 1)
        self.ax.set_zlim(-1, 1)
        
        # Store scatter plot object for updates
        self.scatter = None
        
        # Show the plot
        plt.show(block=False)
        plt.draw()
    
    def update(self, viewpoints: list[Viewpoint], values: list[float], errors: list[float]):
        """
        Update the plot with new data.
        
        Args:
            viewpoints: List of 3D points [(x1, y1, z1), (x2, y2, z2), ...]
            values: List of values from 0 to 1 for color mapping
            errors: List of error values from 0 to 1 for opacity
        """
        # Clear previous scatter plot
        if self.scatter is not None:
            self.scatter.remove()
        
        # Convert inputs to numpy arrays
        viewpoints_np = np.array([[vp.x, vp.y, vp.z] for vp in viewpoints])
        values_np = np.array(values)
        errors_np = np.array(errors)
        
        # Create color map: red for 0, green for 1
        colors = []
        for value in values_np:
            if value == 0:
                colors.append([1.0, 0.0, 0.0])  # Red
            else:  # value == 1
                colors.append([0.0, 1.0, 0.0])  # Green
        
        colors = np.array(colors)
        
        # Set alpha values based on errors (1 = fully opaque, 0 = transparent)
        alphas = errors_np
        
        # Create RGBA colors
        rgba_colors = np.column_stack([colors, alphas])
        
        # Create the scatter plot
        self.scatter = self.ax.scatter(
            viewpoints_np[:, 0], 
            viewpoints_np[:, 1], 
            viewpoints_np[:, 2],
            c=rgba_colors,
            s=20
        )
        
        # Refresh the plot
        self.fig.canvas.draw()
        self.fig.canvas.flush_events()

class RepresentativeObservationsPlot:
    def __init__(self):
        # Create figure and 3D axis
        self.fig = plt.figure(figsize=(10, 8))
        self.ax = self.fig.add_subplot(111, projection='3d')
        
        # Set up the plot
        self.ax.set_xlabel('X')
        self.ax.set_ylabel('Y')
        self.ax.set_zlabel('Z')
        self.ax.set_title('Representative Observations Plot')
        
        # Lock axes to -1 to 1 range
        self.ax.set_xlim(-1, 1)
        self.ax.set_ylim(-1, 1)
        self.ax.set_zlim(-1, 1)
        
        # Store scatter plot object for updates
        self.scatter = None
        
        # Show the plot
        plt.show(block=False)
        plt.draw()
    
    def update(self, observations: list[Observation]):
        """
        Update the plot with observation data.
        
        Args:
            observations: List of observations with viewpoint and ObservationState
        """
        # Clear previous scatter plot
        if self.scatter is not None:
            self.scatter.remove()
        
        if not observations:
            # Refresh the plot even if empty
            self.fig.canvas.draw()
            self.fig.canvas.flush_events()
            return
        
        # Extract viewpoints and states
        viewpoints = []
        colors = []
        
        for obs in observations:
            # Extract viewpoint coordinates
            viewpoints.append([obs.viewpoint.x, obs.viewpoint.y, obs.viewpoint.z])
            
            # Color based on observation state (green for seen, red for not seen)
            if obs.state == ObservationState.SEEN:
                colors.append([0.0, 1.0, 0.0])  # Green
            else:
                colors.append([1.0, 0.0, 0.0])  # Red
        
        # Convert to numpy arrays
        viewpoints_np = np.array(viewpoints)
        colors_np = np.array(colors)
        
        # Create the scatter plot
        self.scatter = self.ax.scatter(
            viewpoints_np[:, 0], 
            viewpoints_np[:, 1], 
            viewpoints_np[:, 2],
            c=colors_np,
            s=20,
            alpha=0.8
        )
        
        # Refresh the plot
        self.fig.canvas.draw()
        self.fig.canvas.flush_events()
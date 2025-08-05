# n_converge - The number of random observations needed for the global error to converge to a stable value
# e_converge - The global error value at which the model is considered converged
# n_evolve - The number of observations needed for the model to re-converge after a world evolution
# e_evolve - The global error value at which the model is considered re-converged after a world evolution
# n_eliminate - The number of what would previously have been positive observations needed for p(exists) to drop below 0.2 after the point is eliminated

from viewpoint import Viewpoint
from world import World
from constants import ObservationState, CONVERGE_THRESHOLD, CONVERGENCE_WINDOW,\
    MAX_CONVERGENCE_ITERATIONS, NUM_WORLDS, N_MIN_OBSERVATIONS_TO_DELETE, DELETE_THRESHOLD
from model import Model
from models.knn import knn
from models.always_unseen import AlwaysUnseen
from existence_prob_estimator import ExistenceProbEstimator
import random
from plotting import ErrorPlot, RepresentativeObservationsPlot
import multiprocessing as mp
import matplotlib.pyplot as plt
import numpy as np

def compute_convergence_iterations(world: World, epe: ExistenceProbEstimator) -> int:
    # Computes the number of observations needed for the model's probability of existence to converge
    # to a stable value.
    # Returns -1 if the model does not converge within MAX_CONVERGENCE_ITERATIONS.
    # Returns -1 if at any point after N_MIN_OBSERVATIONS_TO_DELETE observations, p(exists) drops below DELETE_THRESHOLD
    first_observation = True
    n = 0
    prob_exists_history = []
    while n < MAX_CONVERGENCE_ITERATIONS:
        n += 1
        obs = world.observe(Viewpoint.random())
        if first_observation: # First observation is always seen
            first_observation = False
            while obs.state != ObservationState.SEEN:
                obs = world.observe(Viewpoint.random())
        while obs.state == ObservationState.INVALID:
            obs = world.observe(Viewpoint.random())
        if(len(prob_exists_history) == CONVERGENCE_WINDOW):
            prob_exists_history.pop(0)
        new_pe = epe.update(obs)
        prob_exists_history.append(new_pe)

        if len(prob_exists_history) == CONVERGENCE_WINDOW:
            std_dev = (sum((x - sum(prob_exists_history) / len(prob_exists_history)) ** 2 for x in prob_exists_history) / len(prob_exists_history)) ** 0.5
            if std_dev < CONVERGE_THRESHOLD:
                return n
            
        if n > N_MIN_OBSERVATIONS_TO_DELETE and new_pe < DELETE_THRESHOLD:
            return -1
    return -1

def compute_average_loop_time(args):
    pass

def process_world(args):
    """Process a single world and return the results."""
    world_index, k = args
    world = World(world_index)
    epe = ExistenceProbEstimator('knn', [0.5, 0.5, 0.1, 0.5, 0.005, 0.1, k, 100, 3.141 / 8, 1])
    results = []
    
    # Calculate convergence
    results.append(compute_convergence_iterations(world, epe))
    # results.append(epe.p_exists)
    
    # # Calculate elimination observations
    # n = 0
    # n_2 = 0
    # while epe.p_exists > 0.2:
    #     obs = world.observe(Viewpoint.random())
    #     while obs.state == ObservationState.INVALID:
    #         obs = world.observe(Viewpoint.random())
    #     if obs.state == ObservationState.SEEN:
    #         n = n + 1
    #     n_2 += 1
    #     obs.state = ObservationState.NOT_SEEN
    #     new_pe = epe.update(obs)
    #     if new_pe < 0.2:
    #         break
    #     if n_2 > 1000:
    #         n = -1
    #         break
    
    # results.append(n)
    return world_index, results

if __name__ == '__main__':
    # Define k values to test
    k_values = range(1, 201, 50)  # Example: [1, 51, 101, 151, 201]
    
    # Store results for each k value
    all_results = {}
    
    # Use multiprocessing to process worlds in parallel
    with mp.Pool() as pool:
        for k in k_values:
            print(f"Processing k={k}...")
            world_indices = [(i, k) for i in range(0, NUM_WORLDS)]
            results = pool.map(process_world, world_indices)
            
            # Extract convergence iterations from results (filter out -1 values)
            convergence_iterations = []
            for world_index, result in results:
                if result[0] != -1:  # Only include successful convergences
                    convergence_iterations.append(result[0])
            
            all_results[k] = convergence_iterations
            print(f"k={k}: {len(convergence_iterations)}/{NUM_WORLDS} successful convergences")
        
        # Prepare data for line plot
        k_vals = []
        means = []
        stds = []
        
        for k in k_values:
            if all_results[k]:  # Only include k values with successful convergences
                data = all_results[k]
                k_vals.append(k)
                means.append(np.mean(data))
                stds.append(np.std(data))
        
        # Create line plot with variance shading
        if k_vals:
            plt.figure(figsize=(10, 6))
            
            # Convert to numpy arrays for easier manipulation
            k_vals = np.array(k_vals, dtype=float)
            means = np.array(means, dtype=float)
            stds = np.array(stds, dtype=float)
            
            # Plot the main line
            plt.plot(k_vals, means, 'b-', linewidth=2, marker='o', markersize=6, label='Mean Convergence Iterations')
            
            # Add shaded region for variance (mean ± std)
            upper_bound = means + stds
            lower_bound = means - stds
            plt.fill_between(k_vals, lower_bound, upper_bound, alpha=0.3, color='blue', label='±1 Standard Deviation')
            
            # Customize the plot
            plt.xlabel('K Value (Number of Nearest Neighbors)')
            plt.ylabel('Number of Iterations to Converge')
            plt.title('Convergence Performance vs K Value')
            plt.grid(True, alpha=0.3)
            plt.legend()
            
            # Add data points for better visibility
            plt.scatter(k_vals, means, color='blue', s=50, zorder=5)
            
            # Annotate points with mean values
            for i, (k, mean_val) in enumerate(zip(k_vals, means)):
                plt.annotate(f'{mean_val:.1f}', (k, mean_val), 
                           textcoords="offset points", xytext=(0,10), ha='center')
            
            plt.tight_layout()
            plt.show()
            
            # Print summary statistics
            print("\nSummary Statistics:")
            for k, data in all_results.items():
                if data:
                    print(f"k={k}: Mean={np.mean(data):.1f}, Std={np.std(data):.1f}, n={len(data)}")
        else:
            print("No successful convergences to plot!")
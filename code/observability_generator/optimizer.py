import optuna
import multiprocessing as mp
import numpy as np
from viewpoint import Viewpoint
from world import World
from constants import ObservationState, CONVERGE_THRESHOLD, CONVERGENCE_WINDOW,\
    MAX_CONVERGENCE_ITERATIONS, NUM_WORLDS, N_MIN_OBSERVATIONS_TO_DELETE, DELETE_THRESHOLD
from existence_prob_estimator import ExistenceProbEstimator

def compute_convergence_iterations(world: World, epe: ExistenceProbEstimator) -> int:
    """
    Computes the number of observations needed for the model's probability of existence to converge
    to a stable value.
    Returns -1 if the model does not converge within MAX_CONVERGENCE_ITERATIONS.
    Returns -1 if at any point after N_MIN_OBSERVATIONS_TO_DELETE observations, p(exists) drops below DELETE_THRESHOLD
    """
    first_observation = True
    n = 0
    prob_exists_history = []
    while n < MAX_CONVERGENCE_ITERATIONS:
        n += 1
        obs = world.observe(Viewpoint.random())
        if first_observation:  # First observation is always seen
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

def process_world_with_params(args):
    """Process a single world with given k and n parameters."""
    world_index, k, n = args
    world = World(world_index)
    # Using the parameter structure from calculator.py with k and n as variables
    epe = ExistenceProbEstimator('knn', [0.5, 0.5, 0.1, 0.5, 0.005, 0.1, k, n, 3.141 / 8, 1])
    
    # Calculate convergence
    result = compute_convergence_iterations(world, epe)
    return world_index, result

def evaluate_parameters(k, n, num_worlds=None):
    """
    Evaluate the performance of given k and n parameters.
    Returns a tuple: (average convergence iterations, failure count).
    """
    if num_worlds is None:
        num_worlds = min(NUM_WORLDS, 100)  # Use subset for faster optimization
    
    # Use multiprocessing to process worlds in parallel
    with mp.Pool() as pool:
        world_indices = [(i, k, n) for i in range(num_worlds)]
        results = pool.map(process_world_with_params, world_indices)
        
        # Extract convergence iterations and count failures
        convergence_iterations = []
        failure_count = 0
        for world_index, result in results:
            if result != -1:  # Successful convergence
                convergence_iterations.append(result)
            else:  # Failed convergence
                failure_count += 1
        
        # Return average convergence iterations and failure count
        if convergence_iterations:
            avg_convergence = float(np.mean(convergence_iterations))
        else:
            avg_convergence = float('inf')  # Penalty for no successful convergences
        
        return avg_convergence, failure_count

def objective(trial):
    """
    Optuna objective function to minimize average convergence iterations.
    """
    # Suggest parameter values
    n = trial.suggest_int('n', 10, 100)
    k = trial.suggest_int('k', 1, n)
    
    # Evaluate parameters
    avg_convergence, failure_count = evaluate_parameters(k, n)
    
    # Log the trial results
    print(f"Trial {trial.number}: k={k}, n={n}, avg_convergence={avg_convergence:.2f}, failures={failure_count}")
    
    return avg_convergence

def multi_objective(trial):
    """
    Multi-objective Optuna function to minimize both convergence iterations and failure count.
    """
    # Suggest parameter values
    n = trial.suggest_int('n', 10, 100)
    k = trial.suggest_int('k', 1, n)
    
    # Evaluate parameters
    avg_convergence, failure_count = evaluate_parameters(k, n)
    
    # Log the trial results
    print(f"Trial {trial.number}: k={k}, n={n}, avg_convergence={avg_convergence:.2f}, failures={failure_count}")
    
    return avg_convergence, failure_count

def optimize_parameters(n_trials=50, study_name="knn_parameter_optimization"):
    """
    Run Optuna optimization to find best k and n parameters.
    """
    print(f"Starting optimization with {n_trials} trials...")
    
    # Create study
    study = optuna.create_study(
        direction='minimize',  # Minimize convergence iterations
        study_name=study_name,
        sampler=optuna.samplers.TPESampler(seed=42)
    )
    
    # Run optimization
    study.optimize(objective, n_trials=n_trials)
    
    # Print results
    print("\nOptimization completed!")
    print(f"Best trial: {study.best_trial.number}")
    print(f"Best parameters: {study.best_params}")
    print(f"Best value (avg convergence): {study.best_value:.2f}")
    
    # Print top 5 trials
    print("\nTop 5 trials:")
    top_trials = sorted(study.trials, key=lambda t: t.value if t.value is not None else float('inf'))[:5]
    for i, trial in enumerate(top_trials, 1):
        if trial.value is not None:
            print(f"{i}. k={trial.params['k']}, n={trial.params['n']}, "
                  f"avg_convergence={trial.value:.2f}")
    
    return study

def optimize_parameters_multi_objective(n_trials=50, study_name="knn_multi_objective_optimization"):
    """
    Run multi-objective Optuna optimization to find best k and n parameters.
    Minimizes both convergence iterations and failure count.
    """
    print(f"Starting multi-objective optimization with {n_trials} trials...")
    
    # Create multi-objective study
    study = optuna.create_study(
        directions=['minimize', 'minimize'],  # Minimize both convergence iterations and failure count
        study_name=study_name,
        sampler=optuna.samplers.TPESampler(seed=42)
    )
    
    # Run optimization
    study.optimize(multi_objective, n_trials=n_trials)
    
    # Print results
    print("\nMulti-objective optimization completed!")
    print(f"Number of Pareto optimal solutions: {len(study.best_trials)}")
    
    # Print Pareto optimal solutions
    print("\nPareto optimal solutions:")
    for i, trial in enumerate(study.best_trials):
        print(f"{i+1}. k={trial.params['k']}, n={trial.params['n']}, "
              f"avg_convergence={trial.values[0]:.2f}, failures={trial.values[1]}")
    
    return study

def validate_best_parameters(study, num_worlds=None):
    """
    Validate the best parameters found by Optuna using full dataset.
    """
    if num_worlds is None:
        num_worlds = NUM_WORLDS
    
    best_params = study.best_params
    k = best_params['k']
    n = best_params['n']
    
    print(f"\nValidating best parameters: k={k}, n={n}")
    print(f"Using {num_worlds} worlds for validation...")
    
    avg_convergence, failure_count = evaluate_parameters(k, n, num_worlds)
    
    print(f"Validation result: Average convergence = {avg_convergence:.2f}, Failures = {failure_count}")
    return avg_convergence, failure_count

if __name__ == '__main__':
    # Run single-objective optimization (minimizing convergence iterations)
    print("Running single-objective optimization...")
    study = optimize_parameters(n_trials=100)
    
    # Validate with full dataset
    validate_best_parameters(study)
    
    print("\n" + "="*60 + "\n")
    
    # Run multi-objective optimization (minimizing both convergence iterations and failures)
    print("Running multi-objective optimization...")
    multi_study = optimize_parameters_multi_objective(n_trials=100)
    
    # Validate the first Pareto optimal solution
    if multi_study.best_trials:
        best_trial = multi_study.best_trials[0]
        print(f"\nValidating first Pareto optimal solution: k={best_trial.params['k']}, n={best_trial.params['n']}")
        validate_best_parameters(type('MockStudy', (), {'best_params': best_trial.params})())
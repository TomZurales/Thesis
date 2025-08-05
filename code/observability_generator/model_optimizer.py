import logging
import sys
import optuna
import multiprocessing as mp
from models.knn import knn
from constants import NUM_WORLDS
import random
from plotly.io import show

def knn_objective(trial: optuna.Trial) -> tuple[float, float, int]:
    # Suggest parameter values
    n = trial.suggest_int('n', 10, 200)
    k = trial.suggest_int('k', 1, n)
    a_max = trial.suggest_float('a_max', 3.141 / 16, 3.141 / 2)
    feedback_threshold = trial.suggest_float('feedback_threshold', 0.0, 1.0)
    
    with mp.Pool() as pool:
        world_indices = [(i, k, n, a_max, feedback_threshold) for i in random.sample(range(NUM_WORLDS), 1000)]
        results = pool.map(knn.objective, world_indices)
    
    all_errors = []
    all_times = []
    all_sizes = []
    for result in results:
        all_errors.append(result[0])
        all_times.append(result[1])
        all_sizes.append(result[2])
    return (sum(all_errors) / len(all_errors), sum(all_times) / len(all_times), int(sum(all_sizes) / len(all_sizes)))

if __name__ == "__main__":
    # Create a study and optimize
    optuna.logging.get_logger("optuna").addHandler(logging.StreamHandler(sys.stdout))
    study_name = "knn-study"
    storage_name = "sqlite:///{}.db".format(study_name)
    study = optuna.create_study(directions=['minimize', 'minimize', 'minimize'], study_name=study_name, storage=storage_name, load_if_exists=True)
    study.optimize(knn_objective, n_trials=100, n_jobs=6, show_progress_bar=True)
    
    # Get Pareto optimal solutions
    pareto_trials = study.best_trials
    print(f"Number of Pareto optimal solutions: {len(pareto_trials)}")

    fig = optuna.visualization.plot_pareto_front(study)
    show(fig)
    for i, trial in enumerate(pareto_trials):
        print(f"Trial {i}:")
        print(f"  Values: {trial.values}")
        print(f"  Params: {trial.params}")
# n_converge - The number of random observations needed for the global error to converge to a stable value
# e_converge - The global error value at which the model is considered converged
# n_evolve - The number of observations needed for the model to re-converge after a world evolution
# e_evolve - The global error value at which the model is considered re-converged after a world evolution
# n_eliminate - The number of what would previously have been positive observations needed for p(exists) to drop below 0.2 after the point is eliminated

from viewpoint import Viewpoint
from world import World
from constants import ObservationState, CONVERGE_THRESHOLD, CONVERGENCE_WINDOW, MAX_CONVERGENCE_ITERATIONS, NUM_WORLDS
from model import Model
from models.knn import knn
from models.always_unseen import AlwaysUnseen
from existence_prob_estimator import ExistenceProbEstimator
import random
from plotting import ErrorPlot, RepresentativeObservationsPlot

def calculate_n_converge(world: World, epe: ExistenceProbEstimator) -> int:
    first_observation = True
    n = 0
    global_errors = []
    errorPlot = None
    while n < MAX_CONVERGENCE_ITERATIONS:
        obs = world.observe(Viewpoint.random())
        if first_observation: # First observation is always seen
            first_observation = False
            while obs.state != ObservationState.SEEN:
                obs = world.observe(Viewpoint.random())
        while obs.state == ObservationState.INVALID:
            obs = world.observe(Viewpoint.random())
        if(len(global_errors) == CONVERGENCE_WINDOW):
            global_errors.pop(0)
        # ge = world.global_error(model, errorPlot)
        new_pe = epe.update(obs)
        global_errors.append(new_pe)
        # print(n)
        # print(f"P(E): {new_pe}")
        # print(f"Global Error: {ge}")
        n += 1

        if len(global_errors) == CONVERGENCE_WINDOW:
            std_dev = (sum((x - sum(global_errors) / len(global_errors)) ** 2 for x in global_errors) / len(global_errors)) ** 0.5
            # print(f"Std Dev: {std_dev}")

            if std_dev < CONVERGE_THRESHOLD:
                # print(f"Converged after {n} observations with std_dev {std_dev}")
                return n
            # if epe.p_exists < 0.2:
            #     print("Failure. Point eleiminated before convergence.")
            #     return -1
            
        # Wait for enter to be pressed to continue
    # print(f"Did not converge after {n} observations")
    return -1

for i in range(0, NUM_WORLDS):
# for i in [3294]:
    world = World(i)
    # world = World(1738)
    # model = AlwaysUnseen([])
    epe = ExistenceProbEstimator('knn', [0.5, 0.5, 0.1, 0.5, 0.005, 0.1, 90, 90, 3.141 / 4, 0.5])
    results = []
    results.append(calculate_n_converge(world, epe))
    results.append(epe.p_exists)
    # # print("Evolving world...")
    # world = World(random.randint(0, NUM_WORLDS - 1))
    # print("World evolved into ", world.world)
    # epe.p_exists = 0.5
    # results.append(calculate_n_converge(world, model, epe))
    # results.append(epe.p_exists)

    n = 0
    n_2 = 0
    while epe.p_exists > 0.2:
        # print(f"p_exists: {epe.p_exists}")
        obs = world.observe(Viewpoint.random())
        while obs.state == ObservationState.INVALID:
            obs = world.observe(Viewpoint.random())
        if obs.state == ObservationState.SEEN:
            n = n + 1
        n_2 += 1
        obs.state = ObservationState.NOT_SEEN
        new_pe = epe.update(obs)
        if new_pe < 0.2:
            # print("Point eliminated")
            break
        if n_2 > 1000:
            n = -1
            break
    # print(f"Point eliminated after {n} observations with p(exists) = {epe.p_exists}")
    results.append(n)
    print (i, results)
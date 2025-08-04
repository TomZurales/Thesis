from constants import NUM_WORLDS, WORLDS_FILE_PATH, VIEWPOINTS_FILE_PATH
import data_generator
from world import World
from models.knn import knn

data_generator.gen_all_worlds(WORLDS_FILE_PATH)
data_generator.gen_random_viewpoints(1000, VIEWPOINTS_FILE_PATH)

all_worlds = data_generator.gen_all_worlds()
global_viewpoints = data_generator.gen_random_viewpoints(1000)

# Measure n_convergence and e_convergence for all worlds
n_convergence = [-1 for _ in range(NUM_WORLDS)]
e_convergence = [-1 for _ in range(NUM_WORLDS)]

m = knn([5, 100, 3.141 / 8, 0.3])


for world_num in range(NUM_WORLDS):
    world = World(world_num)
    print(f"Testing world {world_num} with configuration: {world.world}")

    # Check convergence
    n_convergence[world_num] = world.check_n_convergence()
    e_convergence[world_num] = world.check_e_convergence()

for world_num in range(NUM_WORLDS):
    world = World(world_num)
    print(world_num)
    # print(f"Testing world {world_num} with configuration: {world.configuration}")

    # num_observations = 0
    # prev_error = 0

    # with open(f'world_evolutions/{world_num}.txt', 'w') as evolution_file:
    #     window_size = 50
    #     window = []
    #     while num_observations < 1000:
    #         global_error = world.calculate_global_error()
    #         evolution_file.write(f"{num_observations} {global_error}\n")
    #         num_observations += 1
    #         if len(window) == window_size:
    #             window.pop(0)
    #         window.append(global_error)
    #         if len(window) == window_size:
    #             std_dev = (sum((x - sum(window) / len(window)) ** 2 for x in window) / len(window)) ** 0.5 if len(window) > 1 else 0
    #             if std_dev < 0.2:
    #                 print(f"Stopping early at observation {num_observations} with std_dev {std_dev}")
    #                 break

    #         # Generate a random pose
    #         result = 2
    #         pose = [0, 0, 0]
    #         while result == 2:
    #             pose = [random.uniform(-1, 1) for _ in range(3)]
    #             length = sum(x ** 2 for x in pose) ** 0.5
    #             if(length < 0.1 or length > 1.0):
    #                 continue
    #             result = world.test_pose(*pose)
    #         obs = world.create_observation(pose[0], pose[1], pose[2], result == 1)
    #         world.integrate(obs, prev_error)
    #         prev_error = abs((1.0 if obs.seen else 0.0) - world.predict(obs))

    # world.display()
    # world.plot_evolution()
from models.knn import knn
import random
from data_generator import test_world
from utility import Observation

knn_model = knn("KNN Model", [1, 100, 3.141 / 8, 0.3])

world_num = random.randint(0, 3294)
# world_num = 3294

world = [0, 0, 0, 0, 0, 0]  # Default world configuration
with open('worlds.csv', 'r') as worlds_file:
    worlds = [line.strip().split(',') for line in worlds_file.readlines()]
    world_strings = worlds[world_num]
    world = [int(x) for x in world_strings]

print(f"Testing world {world_num} with configuration: {world}")

num_observations = 0

prev_error = 0

with open(f'world_evolutions/{world_num}.txt', 'w') as evolution_file:
    window_size = 50
    window = []
    while num_observations < 1000:
        global_error = knn_model.calculate_global_error(world_num)
        evolution_file.write(f"{num_observations} {global_error}\n")
        num_observations += 1
        if len(window) == window_size:
            window.pop(0)
        window.append(global_error)
        if len(window) == window_size:
            std_dev = (sum((x - sum(window) / len(window)) ** 2 for x in window) / len(window)) ** 0.5 if len(window) > 1 else 0
            if std_dev < 0.2:
                print(f"Stopping early at observation {num_observations} with std_dev {std_dev}")
                break

        # Generate a random pose
        result = 2
        pose = [0, 0, 0]
        while result == 2:
            pose = [random.uniform(-1, 1) for _ in range(3)]
            length = sum(x ** 2 for x in pose) ** 0.5
            if(length < 0.1 or length > 1.0):
                continue
            result = test_world(world, *pose)
        obs = Observation(pose[0], pose[1], pose[2], result == 1)
        knn_model.integrate(obs, prev_error)
        prev_error = abs((1.0 if obs.seen else 0.0) - knn_model.predict(obs))

knn_model.display()
with open(f'world_evolutions/{world_num}.txt', 'r') as evolution_file:
    import matplotlib.pyplot as plt

    lines = evolution_file.readlines()
    x_values = []
    y_values = []

    for line in lines:
        parts = line.strip().split()
        x_values.append(int(parts[0]))
        y_values.append(float(parts[1]))

    plt.figure(figsize=(10, 6))
    plt.plot(x_values, y_values)
    plt.xlabel('Observation Number')
    plt.ylabel('Global Error')
    plt.title(f'World {world_num} Evolution')
    plt.grid(True)
    plt.show()
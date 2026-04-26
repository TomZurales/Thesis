
from random import random
import numpy as np

class VBEE:
    def __init__(self, position: tuple[int, int], obs_model):
        self.obs_model = obs_model
        self._pe = 0.9
        self.position = position

    def step(self, observations: list[tuple[float, float, bool]]) -> float:
        # 1. Count the number of positive observations
        positive_count = sum(1 for obs in observations if obs[2])

        prior_observability = self.obs_model.getObservability()

        bayesian_update_impacts = [(0, 0) for _ in range(len(observations))]

        if positive_count == 0:
            for i, obs in enumerate(observations):
                top = (1 - self.obs_model.query((obs[0], obs[1]))) * self._pe
                bottom = top + (1 - self._pe)
                update = top / bottom
                posterior_observability = self.obs_model.update(obs)
                try:
                    impact = abs((posterior_observability - prior_observability) / prior_observability)
                except ZeroDivisionError:
                    impact = 1.0

                impact += 0.01

                bayesian_update_impacts[i] = (update, impact)
            # Calculate new P(E) based on bayesian_update_impacts
            total_impact = sum(impact for _, impact in bayesian_update_impacts)
            if total_impact > 0:
                new_pe = sum(update * impact for update, impact in bayesian_update_impacts) / total_impact
                delta = max(-1 * total_impact, min(total_impact, new_pe - self._pe))
                self._pe += delta
        else:
            for i, obs in enumerate(observations):
                posterior_observability = self.obs_model.update(obs)
            self._pe = min(max(1 - (0.01 ** positive_count), 0.1), 0.9)
        print(self._pe)

    def query(self, position: tuple[int, int]) -> float:
        return self.obs_model.query(position)

if __name__ == "__main__":
    from observability_models.discrete_boundary import DiscreteBoundary
    obs_model = DiscreteBoundary(10)
    vbee = VBEE((0, 0), obs_model)

    observations = []
    for _ in range(100):
        x = np.random.uniform(-10, 10)
        y = np.random.uniform(-10, 10)
        seen = (x > 0 or y > 0) and (x**2 + y**2)**0.5 < 9
        observations.append((x, y, seen))
    vbee.step(observations)

    for _ in range(10):
        observations = [(np.random.uniform(-10, 10), np.random.uniform(-10, 10), False) for _ in range(500)]
        vbee.step(observations)


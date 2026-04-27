
import math
import numpy as np

class VBEE:
    def __init__(self, position: tuple[float, float, float], obs_model,
                 false_negative_rate: float = 0.01, false_positive_rate: float = 0.01):
        self.obs_model = obs_model
        self._pe = 0.9
        self.false_negative_rate = false_negative_rate
        self.false_positive_rate = false_positive_rate
        self.position = position

    def step(self, observations: list[tuple[float, float, float, bool]]) -> float:
        prior_observability = self.obs_model.getObservability()
        neg_obs_data = []
        positive_count = 0

        for obs in observations:
            x, y, z, seen = obs
            if seen:
                positive_count += 1
                self.obs_model.update(obs)
            else:
                query_val = self.obs_model.query((x, y, z))
                posterior_observability = self.obs_model.update(obs)
                if prior_observability == 0:
                    impact = 1.0
                else:
                    impact = abs((posterior_observability - prior_observability) / prior_observability)
                impact += 1 / len(observations)
                neg_obs_data.append((query_val, impact))
                prior_observability = posterior_observability

        log_L = positive_count * math.log(1 / self.false_positive_rate)

        if neg_obs_data:
            total_neg_impact = sum(impact for _, impact in neg_obs_data)
            log_L += sum(
                (impact / total_neg_impact) * math.log(1 - (1 - self.false_negative_rate) * q)
                for q, impact in neg_obs_data
            )

        L = math.exp(log_L)
        self._pe = max(0.01, min(0.99, (self._pe * L) / (self._pe * L + (1 - self._pe))))
        print(self._pe)
        return self._pe

    def query(self, position: tuple[float, float, float]) -> float:
        return self.obs_model.query(position)

if __name__ == "__main__":
    from observability_models.discrete_boundary import DiscreteBoundary
    obs_model = DiscreteBoundary()
    vbee = VBEE((0, 0, 0), obs_model)

    observations = []
    for _ in range(100):
        x = np.random.uniform(-10, 10)
        y = np.random.uniform(-10, 10)
        z = np.random.uniform(-10, 10)
        seen = (x > 0 or y > 0 or z > 0) and (x**2 + y**2 + z**2)**0.5 < 9
        observations.append((x, y, z, seen))
    vbee.step(observations)

    for _ in range(10):
        observations = [(np.random.uniform(-10, 10), np.random.uniform(-10, 10), np.random.uniform(-10, 10), False) for _ in range(10)]
        vbee.step(observations)

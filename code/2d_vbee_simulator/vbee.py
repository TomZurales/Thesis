from observability_models.discrete_boundary import DiscreteBoundary


class VBEE:
    def __init__(self):
        self.obs_models = {}
        self.obs_models["KNN (k=1)"] = DiscreteBoundary(360)
        self.obs_models["KNN (k=5)"] = DiscreteBoundary(360)
        self.obs_models["Discrete Boundary (n=4)"] = DiscreteBoundary(4)
        self.obs_models["Discrete Boundary (n=20)"] = DiscreteBoundary(20)

    def query(self, position: tuple[int, int], model: str) -> float:
        return self.obs_models[model].query(position)
    
    def integrate(self, observations:list[tuple[float, float, bool]]):
        for model in self.obs_models.values():
            model.integrate(observations)
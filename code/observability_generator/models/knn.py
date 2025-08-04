import matplotlib.pyplot as plt
from model import Model
from observation import Observation
from constants import ObservationState
from viewpoint import Viewpoint
from plotting import RepresentativeObservationsPlot

class knn(Model):
    observations: list[Observation]

    def __init__(self, parameters):
        super().__init__("KNN", parameters)
        self.k = parameters[0]
        self.n = parameters[1]
        self.a_max = parameters[2]
        self.feedback_threshold = parameters[3]
        self.observations = []

    def predict(self, vp: Viewpoint):
        candidates = []
        
        for obs in self.observations:
            if obs.viewpoint.angular_distance(vp) <= self.a_max:
                candidates.append(obs)

        # Sort candidates by euclidean distance
        candidates.sort(key=lambda obs: obs.viewpoint.euclidean_distance(vp))

        if len(candidates) == 0:
            return 0.5
        
        candidates = candidates[:min(self.k, len(candidates))]
        n_seen = sum(1 for obs in candidates if obs.state == ObservationState.SEEN)
        return n_seen / len(candidates)

    def integrate(self, o: Observation, feedback = None, plot: RepresentativeObservationsPlot | None = None):
        if feedback == None:
            print("This model needs feedback. Exiting.")
            return
        if plot is not None:
            plot.update(self.observations)
        for obs in self.observations:
            obs.age += 1
        if len(self.observations) < self.n:
            self.observations.append(o)
            return
        if feedback < self.feedback_threshold:
            return
        self.observations.sort(key=lambda obs: o.viewpoint.euclidean_distance(obs.viewpoint))
        max_age = 0
        max_obs = self.observations[0]
        for obs in self.observations:
            if obs.age > max_age:
                max_age = obs.age
                max_obs = obs
            if o.state == obs.state:
                continue
            else:
                self.observations.remove(obs)
                self.observations.append(o)
                return
        self.observations.remove(max_obs)
        self.observations.append(o)
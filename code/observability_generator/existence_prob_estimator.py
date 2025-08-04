from model import Model
from observation import Observation
from constants import ObservationState
from plotting import RepresentativeObservationsPlot
from models.always_half import AlwaysHalf
from models.always_unseen import AlwaysUnseen
from models.knn import knn

def clamp(value: float, min_value: float, max_value: float) -> float:
    return max(min(value, max_value), min_value)

N_PARAMETERS = 6

class ExistenceProbEstimator:
    p_exists: float # Probability that the point exists
    observability: float # Inverse of the estimated overall observability of the point
    observability_update_factor: float # How much the observability is updated by each observation
    damping_coefficient: float # Damping coefficient for the estimate

    false_positive_rage: float # Probability of the point being seen when it is not there
    false_negative_rate: float # Probability of the point not being seen when it is there

    def __init__(self, model: str, parameters: list):
        self.plot = None

        if len(parameters) >= N_PARAMETERS:
            self.p_exists = parameters[0]
            self.observability = parameters[1]
            self.observability_update_factor = parameters[2]
            self.damping_coefficient = parameters[3]
            self.false_positive_rage = parameters[4]
            self.false_negative_rate = parameters[5]

        if model == "always_half":
            self.model = AlwaysHalf(parameters[N_PARAMETERS:])
        elif model == "always_unseen":
            self.model = AlwaysUnseen(parameters[N_PARAMETERS:])
        elif model == "knn":
            self.model = knn(parameters[N_PARAMETERS:])
        else:
            raise ValueError(f"Unknown model: {model}")

    def update(self, observation: Observation):
        prior = self.p_exists

        # Model estimation is clamped to [0.001, 0.999] to avoid division by zero or extreme values
        model_estimation = clamp(self.model.predict(observation.viewpoint), 0.001, 0.999)

        if observation.state == ObservationState.SEEN:
            numerator = model_estimation * (1 - self.false_negative_rate) * prior
            denominator = (model_estimation * (1 - self.false_negative_rate) * prior) + (self.false_positive_rage * (1 - prior))
            posterior = numerator / denominator
            
        else:
            numerator = (1 - (model_estimation * (1 - self.false_negative_rate)))*prior
            denominator = ((1 - (model_estimation * (1 - self.false_negative_rate)))*prior) + ((1 - self.false_positive_rage) * (1 - prior))
            posterior = numerator / denominator
            
        if posterior < 0 or posterior > 1:
                raise ValueError(f"Posterior probability out of bounds: {posterior}")

        # If the estimated observability of the point is lower than the actual, we increate the overall observability
        # Otherwise we decrease it
        self.observability = clamp(self.observability + (self.observability_update_factor * (observation.state.value - model_estimation)), 0.25, 0.75)
        
        # The more observable the point is, the more we dampen the update
        self.p_exists = clamp(self.p_exists + (posterior - prior) * (1 - self.observability) * self.damping_coefficient, 0.001, 0.999)
        
        self.model.integrate(observation, abs(self.p_exists - prior), self.plot)

        return self.p_exists
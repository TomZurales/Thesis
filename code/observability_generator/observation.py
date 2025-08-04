from constants import ObservationState
from viewpoint import Viewpoint

class Observation:
    viewpoint: Viewpoint
    state: ObservationState
    age: int = 0

    def __init__(self, viewpoint: Viewpoint, state: ObservationState):
        self.viewpoint = viewpoint
        self.state = state
        
    def __repr__(self):
        return f"Observation(viewpoint={self.viewpoint}, state={self.state}, age={self.age})"
    
    def increment_age(self):
        self.age += 1

if __name__ == "__main__":
    # Example usage
    vp = Viewpoint.random()
    obs = Observation(vp, ObservationState.SEEN)
    print(obs)
    
    obs.increment_age()
    print(obs)
    
    try:
        invalid_obs = Observation(Viewpoint(2, 2, 2), ObservationState.INVALID)  # This should raise an error
    except ValueError as e:
        print(e)
    
    valid_obs = Observation(Viewpoint(0.5, 0.5, 0.5), ObservationState.NOT_SEEN)
    print(valid_obs)    
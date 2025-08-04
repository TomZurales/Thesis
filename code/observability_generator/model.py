from observation import Observation
from viewpoint import Viewpoint
from plotting import ErrorPlot, RepresentativeObservationsPlot

class Model:
    def __init__(self, name: str, parameters):
        self.name = name
        self.parameters = parameters

    def predict(self, vp: Viewpoint) -> float:
        return 0.5
    
    def integrate(self, o: Observation, feedback: float | None = None, plot: RepresentativeObservationsPlot | None = None) -> None:
        return
            
    def display(self):
        print(f"Model: {self.name}, Parameters: {self.parameters}")
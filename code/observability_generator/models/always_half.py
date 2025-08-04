import matplotlib.pyplot as plt
from model import Model
from observation import Observation
from constants import ObservationState
from viewpoint import Viewpoint
from plotting import RepresentativeObservationsPlot

class AlwaysHalf(Model):

    def __init__(self, parameters):
        super().__init__("Always Half", parameters)

    def predict(self, vp: Viewpoint):
        return 0.5

    def integrate(self, o: Observation, feedback = None, plot: RepresentativeObservationsPlot | None = None):
        return
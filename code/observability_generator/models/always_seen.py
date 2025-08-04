import matplotlib.pyplot as plt
from model import Model
from observation import Observation
from constants import ObservationState
from viewpoint import Viewpoint
from plotting import RepresentativeObservationsPlot

class AlwaysSeen(Model):

    def __init__(self, parameters):
        super().__init__("Always Seen", parameters)

    def predict(self, vp: Viewpoint):
        return 0.99

    def integrate(self, o: Observation, feedback = None, plot: RepresentativeObservationsPlot | None = None):
        return
import matplotlib.pyplot as plt
from model import Model
from observation import Observation
from constants import ObservationState
from viewpoint import Viewpoint
from plotting import RepresentativeObservationsPlot

class AlwaysUnseen(Model):

    def __init__(self, parameters):
        super().__init__("Always Unseen", parameters)

    def predict(self, vp: Viewpoint):
        return 0.01

    def integrate(self, o: Observation, feedback = None, plot: RepresentativeObservationsPlot | None = None):
        return
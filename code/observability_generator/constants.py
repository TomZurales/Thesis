from enum import Enum

NUM_WORLDS: int = 3295

MIN_OBS_DIST: float = 0.1
MAX_OBS_DIST: float = 1

CONVERGE_THRESHOLD: float = 0.02
CONVERGENCE_WINDOW: int = 50
MAX_CONVERGENCE_ITERATIONS: int = 1000

WORLDS_FILE_PATH: str = 'data/worlds.csv'
VIEWPOINTS_FILE_PATH: str = 'data/viewpoints.csv'

N_GLOBAL_OBSERVATIONS: int = 1000

class ObservationState(Enum):
    NOT_SEEN = 0.0
    SEEN = 1.0
    INVALID = 2

class WorldWallTypes(Enum):
    T_NEAR = 0
    T_FAR = 1
    X_NEAR = 2
    X_FAR = 3
    T_NEAR_X_FAR = 4
    NONE = 5
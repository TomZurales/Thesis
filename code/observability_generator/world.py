from observation import Observation
from enum import Enum
import data_generator
import os
from constants import WORLDS_FILE_PATH, WorldWallTypes, ObservationState
from model import Model
from plotting import ErrorPlot
import random

from viewpoint import Viewpoint

class World:
    def __init__(self, world_num):
        if world_num < 0 or world_num > 3294:
            raise ValueError(f"World number must be between 0 and 3294, got {world_num}")
        
        self.world_num = world_num

        # If worlds.csv does not exist, generate it with gen_all_worlds
        if not os.path.exists(WORLDS_FILE_PATH):
            data_generator.gen_all_worlds(WORLDS_FILE_PATH)

        # Read only the specific line we need
        with open(WORLDS_FILE_PATH, 'r') as worlds_file:
            for i, line in enumerate(worlds_file):
                if i == world_num:
                    world_strings = line.strip().split(',')
                    self.world = [int(x) for x in world_strings]
                    break

    def __repr__(self):
        return f"World {self.world_num} with configuration: {self.world}"
    
    def global_error(self, model: Model, plot: ErrorPlot | None = None) -> float:
        global_error = 0.0
        vps = []
        errors = []
        true_values = []
        for _ in range(1000):
            vp = Viewpoint.random()
            while self.observe(vp).state == ObservationState.INVALID:
                vp = Viewpoint.random()
            vps.append(vp)
            true_observation = self.observe(vp)
            true_values.append(true_observation.state.value)
            error = abs(model.predict(vp) - true_observation.state.value)
            errors.append(error)
            global_error += error
        if plot != None:
            plot.update(vps, true_values, errors)
    
        return global_error

    def observe(self, vp: Viewpoint) -> Observation:
        seen_state = ObservationState.INVALID
        # Left
        if self.world[0] == WorldWallTypes.X_NEAR.value and vp.x < 0:
            seen_state = ObservationState.INVALID
        elif self.world[0] == WorldWallTypes.X_FAR.value and vp.x < -0.5:
            seen_state = ObservationState.INVALID
        elif self.world[0] == WorldWallTypes.T_NEAR_X_FAR.value and vp.x < -0.5:
            seen_state = ObservationState.INVALID
        # Top
        elif self.world[1] == WorldWallTypes.X_NEAR.value and vp.y > 0:
            seen_state = ObservationState.INVALID
        elif self.world[1] == WorldWallTypes.X_FAR.value and vp.y > 0.5:
            seen_state = ObservationState.INVALID
        elif self.world[1] == WorldWallTypes.T_NEAR_X_FAR.value and vp.y > 0.5:
            seen_state = ObservationState.INVALID
        # Front
        elif self.world[2] == WorldWallTypes.X_NEAR.value and vp.z > 0:
            seen_state = ObservationState.INVALID
        elif self.world[2] == WorldWallTypes.X_FAR.value and vp.z > 0.5:
            seen_state = ObservationState.INVALID
        elif self.world[2] == WorldWallTypes.T_NEAR_X_FAR.value and vp.z > 0.5:
            seen_state = ObservationState.INVALID
        # Right
        elif self.world[3] == WorldWallTypes.X_NEAR.value and vp.x > 0:
            seen_state = ObservationState.INVALID
        elif self.world[3] == WorldWallTypes.X_FAR.value and vp.x > 0.5:
            seen_state = ObservationState.INVALID
        elif self.world[3] == WorldWallTypes.T_NEAR_X_FAR.value and vp.x > 0.5:
            seen_state = ObservationState.INVALID
        # Bottom
        elif self.world[4] == WorldWallTypes.X_NEAR.value and vp.y < 0:
            seen_state = ObservationState.INVALID
        elif self.world[4] == WorldWallTypes.X_FAR.value and vp.y < -0.5:
            seen_state = ObservationState.INVALID
        elif self.world[4] == WorldWallTypes.T_NEAR_X_FAR.value and vp.y < -0.5:
            seen_state = ObservationState.INVALID
        # Back
        elif self.world[5] == WorldWallTypes.X_NEAR.value and vp.z < 0:
            seen_state = ObservationState.INVALID
        elif self.world[5] == WorldWallTypes.X_FAR.value and vp.z < -0.5:
            seen_state = ObservationState.INVALID
        elif self.world[5] == WorldWallTypes.T_NEAR_X_FAR.value and vp.z < -0.5:
            seen_state = ObservationState.INVALID

        # WorldWallTypes.T_NEAR and WorldWallTypes.T_FAR and WorldWallTypes.T_NEAR_X_FAR
        # Left
        elif self.world[0] == WorldWallTypes.T_NEAR.value and vp.x < 0:
            seen_state = ObservationState.NOT_SEEN
        elif self.world[0] == WorldWallTypes.T_FAR.value and vp.x < -0.5:
            seen_state = ObservationState.NOT_SEEN
        elif self.world[0] == WorldWallTypes.T_NEAR_X_FAR.value and vp.x < -0.5:
            seen_state = ObservationState.NOT_SEEN
        # Top
        elif self.world[1] == WorldWallTypes.T_NEAR.value and vp.y > 0:
            seen_state = ObservationState.NOT_SEEN
        elif self.world[1] == WorldWallTypes.T_FAR.value and vp.y > 0.5:
            seen_state = ObservationState.NOT_SEEN
        elif self.world[1] == WorldWallTypes.T_NEAR_X_FAR.value and vp.y > 0.5:
            seen_state = ObservationState.NOT_SEEN
        # Front
        elif self.world[2] == WorldWallTypes.T_NEAR.value and vp.z > 0:
            seen_state = ObservationState.NOT_SEEN
        elif self.world[2] == WorldWallTypes.T_FAR.value and vp.z > 0.5:
            seen_state = ObservationState.NOT_SEEN
        elif self.world[2] == WorldWallTypes.T_NEAR_X_FAR.value and vp.z > 0.5:
            seen_state = ObservationState.NOT_SEEN
        # Right
        elif self.world[3] == WorldWallTypes.T_NEAR.value and vp.x > 0:
            seen_state = ObservationState.NOT_SEEN
        elif self.world[3] == WorldWallTypes.T_FAR.value and vp.x > 0.5:
            seen_state = ObservationState.NOT_SEEN
        elif self.world[3] == WorldWallTypes.T_NEAR_X_FAR.value and vp.x > 0.5:
            seen_state = ObservationState.NOT_SEEN
        # Bottom
        elif self.world[4] == WorldWallTypes.T_NEAR.value and vp.y < 0:
            seen_state = ObservationState.NOT_SEEN
        elif self.world[4] == WorldWallTypes.T_FAR.value and vp.y < -0.5:
            seen_state = ObservationState.NOT_SEEN
        elif self.world[4] == WorldWallTypes.T_NEAR_X_FAR.value and vp.y < -0.5:
            seen_state = ObservationState.NOT_SEEN
        # Back
        elif self.world[5] == WorldWallTypes.T_NEAR.value and vp.z < 0:
            seen_state = ObservationState.NOT_SEEN
        elif self.world[5] == WorldWallTypes.T_FAR.value and vp.z < -0.5:
            seen_state = ObservationState.NOT_SEEN
        elif self.world[5] == WorldWallTypes.T_NEAR_X_FAR.value and vp.z < -0.5:
            seen_state = ObservationState.NOT_SEEN
        else:
            # If we reach here, the point is visible
            seen_state = ObservationState.SEEN
        return Observation(vp, seen_state)
    # def check_viewpoint(self, vp: Viewpoint):
    #     pass
    
    # def calculate_global_error(self, world_num: int) -> float:
    #     with open('poses.csv', 'r') as poses_file:
    #         with open(f'observations/{world_num}.csv', 'r') as observations_file:
    #             poses = [line.strip().split(',') for line in poses_file.readlines()]
    #             observations = [line.strip().split(',') for line in observations_file.readlines()]

    #             total_error = 0.0
    #             for observation in observations:
    #                 if observation[1] == '2': # Invalid pose
    #                     continue
    #                 pose = poses[int(observation[0])]
    #                 obs = Observation(float(pose[0]), float(pose[1]), float(pose[2]), True if observation[1] == '1' else False)
    #                 prediction = self.predict(obs)
    #                 total_error += abs(prediction - (1.0 if obs.seen else 0.0))
    #             return total_error
            
    # def check_viewpoint(self, vp: Viewpoint):
    # # Start with the exclusion zones

    
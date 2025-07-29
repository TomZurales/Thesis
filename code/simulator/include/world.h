#pragma once

#include "viewpoint.h"
#include "observation.h"

#include <math.h>
#include <vector>

/*
 * The world class represents the world surrounding a single map point sitting at the origin of a 3D polar plot
 * It contains:
 *     Obstructions - Objects which, if they fall between the observer and the map point, will cause the observation to fail
 *     Keep-Out Zones - Areas where the observer cannot be. May represent under ground or outside a building where the robot operates
 * Public Functions:
 *     OBS_STATUS observe(theta, phi, d) - Returns SEEN if the origin can be seen from this point, NOT_SEEN if it can't, and INVALID if taken from within a keepout zone
 */

typedef enum
{
    KEEP_OUT,
    THIN_WALL,
    NONE
} ObstructionType;

class World
{
public:
    // Obstructions take the form:

    World(std::vector<ObstructionType> walls);

    Observation observe(Viewpoint);

    void addObstruction(const Viewpoint &obstruction);
    void addKeepOutZone(const Viewpoint &keepOutZone);
};
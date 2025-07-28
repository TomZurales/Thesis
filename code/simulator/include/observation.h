#pragma once

#include "viewpoint.h"

typedef enum ObservationStatus_t
{
    INVALID = -1,
    SEEN = 1,
    NOT_SEEN = 0
} ObservationStatus;

class Observation
{
    Viewpoint viewpoint;
    ObservationStatus status;

public:
    Observation() : viewpoint(Viewpoint()), status(INVALID) {}
    Observation(Viewpoint vp, ObservationStatus stat) : viewpoint(vp), status(stat) {}

    Viewpoint getViewpoint() const { return viewpoint; }
    ObservationStatus getStatus() const { return status; }
};
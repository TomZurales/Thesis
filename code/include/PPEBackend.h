#pragma once

#include <eigen3/Eigen/Core>
#include "Point.h"

// This class is the interface for the backend model of the Point Probability Engine (PPE).
// The interface implements an addObservation method, which is called by the PPE and contains
// the camera pose, and the set of points which are seen and not seen which fall in the camera's view.
// The backend model is responsible for updating the probability of existence of the point
// based on the observations.
class PPEBackend
{
protected:
    std::map<Point *, float> pointProbExists;

public:
    virtual void addObservation(Eigen::Matrix4f cameraPose, std::vector<Point *> seen, std::vector<Point *> notSeen) = 0;
    virtual void showState() = 0;
};
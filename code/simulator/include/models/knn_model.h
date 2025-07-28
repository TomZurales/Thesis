#pragma once

#include "model_interface.h"

#include <queue>
#include <algorithm>
#include <iostream>
#include <vector>

class KNNModel : public ModelInterface
{
private:
    std::vector<std::pair<float, Observation>> distances;
    Observation nearestSame;
    Observation nearestOpposite;

private:
    // Parameters
    int k;
    int numObservations;
    float distanceThreshold;
    float feedbackThreshold;

    // Internal Representation
    std::vector<Observation> observations;

public:
    void initialize(std::vector<float> parameters) override;
    float predict(Viewpoint vp) override;
    void integrateObservation(Observation observation) override;
    void feedback(float value) override;
};
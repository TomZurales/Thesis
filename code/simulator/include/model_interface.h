#pragma once

#include "observation.h"

#include <vector>

class ModelInterface
{
public:
    virtual ~ModelInterface() = default;

    virtual void initialize(std::vector<float>) = 0;
    virtual float predict(Viewpoint) = 0;
    float predict(Observation o)
    {
        float prediction = predict(o.getViewpoint());
        integrateObservation(o);
        return prediction;
    }
    virtual void integrateObservation(Observation) = 0;
    virtual void feedback(float) {};
};
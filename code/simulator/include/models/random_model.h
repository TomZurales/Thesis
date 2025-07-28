#pragma once

#include "model_interface.h"

class RandomModel : public ModelInterface
{
private:
    // Parameters
    float minVal;
    float maxVal;
    // Internal Representation

public:
    void initialize(std::vector<float> parameters) override;
    float predict(Viewpoint vp) override;
    void integrateObservation(Observation observation) override;
};
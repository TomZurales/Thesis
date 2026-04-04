#pragma once

#include "model_interface.h"

class BinnedModel : public ModelInterface
{
private:
    // Parameters

    // Internal Representation

public:
    void initialize(std::vector<float> parameters) override;
    float predict(Viewpoint vp) override;
    void integrateObservation(Observation observation) override;
};
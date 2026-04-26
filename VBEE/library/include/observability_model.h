#pragma once

#include <vector>
#include <Eigen/Core>

class ObservabilityModel
{
  public:
    virtual std::vector<float> EstimateAndIntegrate(const Eigen::Vector3f &viewpoint) = 0;
};
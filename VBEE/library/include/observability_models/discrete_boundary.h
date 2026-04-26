#pragma once

#include "observability_model.h"

class DiscreteBoundary : public ObservabilityModel
{
private:
    int n;
    std::vector<Eigen::Vector3f> face_centers;

public:
    DiscreteBoundary(int n);

private:
    void generateFaceCenters(int n);
    int getBinIndex(const Eigen::Vector3f &viewpoint);
};
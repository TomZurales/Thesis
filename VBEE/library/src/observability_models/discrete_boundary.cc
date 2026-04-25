#include <vector>
#include <Eigen/Core>
#include "observability_models/discrete_boundary.h"
#include <iostream>

DiscreteBoundary::DiscreteBoundary(int n) : n(n)
{
    generateFaceCenters(n);
}

void DiscreteBoundary::generateFaceCenters(int n)
{
    face_centers.reserve(n);

    // Generate n faces using the fibonacci sphere algorithm
    const double golden_ratio = (1.0 + std::sqrt(5.0)) / 2.0;
    const double angle_increment = 2.0 * M_PI / golden_ratio;

    for (int i = 0; i < n; ++i)
    {
        double t = static_cast<double>(i) / static_cast<double>(n);
        double inclination = std::acos(1.0 - 2.0 * t); // polar angle from north pole
        double azimuth = angle_increment * i;          // longitude

        face_centers.emplace_back(
            std::sin(inclination) * std::cos(azimuth),
            std::sin(inclination) * std::sin(azimuth),
            std::cos(inclination));
    }

    for (auto &center : face_centers)
    {
        std::cout << "Face center: " << center.transpose() << std::endl;
    }

}
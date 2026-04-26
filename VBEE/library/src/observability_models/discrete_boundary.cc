#include <vector>
#include <Eigen/Core>
#include "observability_models/discrete_boundary.h"
#include <iostream>

const std::vector<Eigen::Vector3f> ICOS_CENTERS = {
        {-0.1875924741, 0.7946544723, -0.5773502692},
        {0.4911234732, 0.7946544723, 0.3568220898},
        {-0.6070619982, 0.7946544723, -0.0000000000},
        {0.4911234732, 0.7946544723, -0.3568220898},
        {-0.1875924741, 0.7946544723, 0.5773502692},
        {-0.9822469464, 0.1875924741, -0.0000000000},
        {-0.3035309991, 0.1875924741, 0.9341723590},
        {0.7946544723, 0.1875924741, -0.5773502692},
        {-0.3035309991, 0.1875924741, -0.9341723590},
        {0.7946544723, 0.1875924741, 0.5773502692},
        {-0.7946544723, -0.1875924741, -0.5773502692},
        {0.3035309991, -0.1875924741, 0.9341723590},
        {-0.7946544723, -0.1875924741, 0.5773502692},
        {0.3035309991, -0.1875924741, -0.9341723590},
        {0.9822469464, -0.1875924741, 0.0000000000},
        {0.1875924741, -0.7946544723, -0.5773502692},
        {0.6070619982, -0.7946544723, 0.0000000000},
        {-0.4911234732, -0.7946544723, 0.3568220898},
        {-0.4911234732, -0.7946544723, -0.3568220898},
        {0.1875924741, -0.7946544723, 0.5773502692},
};

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
#include "viewpoint.h"

float Viewpoint::distanceTo(const Viewpoint &other) const
{
    // Convert both viewpoints to Cartesian coordinates
    // Assuming spherical coordinates: (d, theta, phi)
    // where theta is azimuth, phi is elevation

    float x1 = d * std::cos(phi) * std::cos(theta);
    float y1 = d * std::cos(phi) * std::sin(theta);
    float z1 = d * std::sin(phi);

    float x2 = other.d * std::cos(other.phi) * std::cos(other.theta);
    float y2 = other.d * std::cos(other.phi) * std::sin(other.theta);
    float z2 = other.d * std::sin(other.phi);

    float dx = x1 - x2;
    float dy = y1 - y2;
    float dz = z1 - z2;

    return std::sqrt(dx * dx + dy * dy + dz * dz);
}
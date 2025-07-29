#pragma once

#include <math.h>

class Viewpoint
{
public:
    float theta;
    float phi;
    float d;
    Viewpoint() : theta(0), phi(0), d(0) {}
    Viewpoint(float theta, float phi, float d) : theta(theta), phi(phi), d(d) {}

    float distanceTo(const Viewpoint &other) const;

    static Viewpoint random()
    {
        float theta = (static_cast<float>(rand()) / static_cast<float>(RAND_MAX)) * 2 * M_PI;
        float phi = (static_cast<float>(rand()) / static_cast<float>(RAND_MAX)) * M_PI - M_PI / 2;
        float d = (static_cast<float>(rand()) / static_cast<float>(RAND_MAX)) * 10;
        return Viewpoint(theta, phi, d);
    }
};
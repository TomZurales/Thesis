#pragma once

#include <math.h>
#include <random>

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
        static thread_local std::random_device rd;
        static thread_local std::mt19937 gen(rd());
        static thread_local std::uniform_real_distribution<float> uniform(0.0f, 1.0f);
        
        float theta = uniform(gen) * 2 * M_PI; // Random angle in [0, 2π]
        float phi = uniform(gen) * M_PI - M_PI/2; // Random angle in [-π/2, π/2]
        float d = uniform(gen) * 10;           // Random distance in [0, 10]
        return Viewpoint(theta, phi, d);
    }
};
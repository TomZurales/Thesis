#include "models/random_model.h"

#include <random>

void RandomModel::initialize(std::vector<float> parameters)
{
    minVal = parameters[0];
    maxVal = parameters[1];
}

float RandomModel::predict(Viewpoint vp)
{
    // Generate a random prediction
    std::random_device rd;                                  // Obtain a random number from hardware
    std::mt19937 eng(rd());                                 // Seed the generator
    std::uniform_real_distribution<> distr(minVal, maxVal); // Define the range

    return distr(eng); // Return a random float between 0.0 and 1.0
}

void RandomModel::integrateObservation(Observation observation)
{
}

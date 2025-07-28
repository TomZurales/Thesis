#pragma once

#include "experiment.h"
#include <vector>
#include <functional>

class Optimizer
{
private:
    std::function<float(const std::vector<float>&)> objectiveFunction;
    
public:
    // Constructor takes a function that evaluates the objective given parameters
    Optimizer(std::function<float(const std::vector<float>&)> func);
    
    // Optimize the parameters using Ceres solver
    // Returns the optimized parameters
    std::vector<float> optimize(const std::vector<float>& initialGuess);
    
    // Multi-start optimization to find global minimum
    std::vector<float> optimizeMultiStart(const std::vector<float>& initialGuess, int numStarts = 5);
    
    // Helper function to create an objective function from an experiment
    static std::function<float(const std::vector<float>&)> createExperimentObjective(
        const std::vector<ModelInterface*>& models);
};

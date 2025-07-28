// Example usage of the Optimizer class
// To use this, replace the main function in simulator.cc with this code
// or create a separate executable

#include "optimizer.h"
#include "models/knn_model.h"
#include <iostream>

void exampleOptimization()
{
    // Create models to optimize
    std::vector<ModelInterface*> models;
    models.push_back(new KNNModel());
    
    // Create optimizer with the experiment objective
    auto objective = Optimizer::createExperimentObjective(models);
    Optimizer optimizer(objective);
    
    // Initial guess: k=2, numObservations=500, distanceThreshold=PI/4, feedbackThreshold=0.1
    std::vector<float> initialGuess = {2.0f, 500.0f, M_PI_4, 0.1f};
    
    std::cout << "Starting optimization with initial parameters:" << std::endl;
    std::cout << "k (v[0]): " << initialGuess[0] << std::endl;
    std::cout << "numObservations (v[1]): " << initialGuess[1] << std::endl;
    std::cout << "distanceThreshold (v[2]): " << initialGuess[2] << std::endl;
    std::cout << "feedbackThreshold (v[3]): " << initialGuess[3] << std::endl;
    std::cout << std::endl;
    
    // Optimize parameters
    std::vector<float> optimized = optimizer.optimize(initialGuess);
    
    std::cout << "\nOptimized parameters:" << std::endl;
    std::cout << "k (v[0]): " << optimized[0] << std::endl;
    std::cout << "numObservations (v[1]): " << optimized[1] << std::endl;
    std::cout << "distanceThreshold (v[2]): " << optimized[2] << std::endl;
    std::cout << "feedbackThreshold (v[3]): " << optimized[3] << std::endl;
    
    // Test the optimized parameters
    std::cout << "\nTesting optimized parameters..." << std::endl;
    float finalError = objective(optimized);
    std::cout << "Final error with optimized parameters: " << finalError << std::endl;
    
    // Clean up
    for (auto* model : models)
    {
        delete model;
    }
}

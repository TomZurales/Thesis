#include <iostream>
#include "experiment.h"
#include "models/knn_model.h"
#include "optimizer.h"

int main(int argc, char **argv)
{
    std::cout << "Simulator started with " << argc << " arguments." << std::endl;

    // Create models for optimization
    std::vector<ModelInterface*> models;
    models.push_back(new KNNModel());

    std::cout << "\n=== Parameter Optimization Phase ===" << std::endl;
    
    // Create optimizer with the experiment objective
    auto objective = Optimizer::createExperimentObjective(models);
    Optimizer optimizer(objective);
    
    // Initial guess: k=2, numObservations=500, distanceThreshold=PI/4, feedbackThreshold=0.1
    std::vector<float> initialGuess = {2.0f, 500.0f, M_PI_4, 0.1f};
    
    std::cout << "Starting optimization with initial parameters:" << std::endl;
    std::cout << "  k (v[0]): " << initialGuess[0] << std::endl;
    std::cout << "  numObservations (v[1]): " << initialGuess[1] << std::endl;
    std::cout << "  distanceThreshold (v[2]): " << initialGuess[2] << " (" << initialGuess[2] * 180.0f / M_PI << " degrees)" << std::endl;
    std::cout << "  feedbackThreshold (v[3]): " << initialGuess[3] << std::endl;
    
    // Evaluate initial parameters
    std::cout << "\nEvaluating initial parameters (this may take a while with 1M iterations)..." << std::endl;
    float initialError = objective(initialGuess);
    std::cout << "Initial error: " << initialError << std::endl;
    std::cout << "\nStarting multi-start Ceres optimization (this will take significantly longer)...\n" << std::endl;
    
    // Use multi-start optimization to find better parameters
    std::vector<float> optimized = optimizer.optimizeMultiStart(initialGuess, 3);
    
    std::cout << "\n=== Optimization Results ===" << std::endl;
    std::cout << "Optimized parameters:" << std::endl;
    std::cout << "  k (v[0]): " << optimized[0] << std::endl;
    std::cout << "  numObservations (v[1]): " << optimized[1] << std::endl;
    std::cout << "  distanceThreshold (v[2]): " << optimized[2] << " (" << optimized[2] * 180.0f / M_PI << " degrees)" << std::endl;
    std::cout << "  feedbackThreshold (v[3]): " << optimized[3] << std::endl;
    
    // Test the optimized parameters
    float finalError = objective(optimized);
    std::cout << "\nFinal error with optimized parameters: " << finalError << std::endl;
    std::cout << "Improvement: " << (initialError - finalError) << " (" << ((initialError - finalError) / initialError * 100.0f) << "% reduction)" << std::endl;

    std::cout << "\n=== Running Full Experiment with Optimized Parameters ===" << std::endl;
    
    // Now run the full experiment with optimized parameters
    Experiment experiment;
    auto knnModel = new KNNModel();
    experiment.addModel(knnModel);
    
    // Initialize with optimized parameters
    knnModel->initialize(optimized);
    
    experiment.run(true); // Skip initialization since we already set optimized parameters

    std::cout << "Experiment completed with optimized parameters." << std::endl;

    // Clean up
    for (auto* model : models)
    {
        delete model;
    }
    delete knnModel;

    return 0;
}
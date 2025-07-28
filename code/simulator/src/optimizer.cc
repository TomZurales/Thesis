#include "optimizer.h"
#include "world.h"
#include "models/knn_model.h"
#include <ceres/ceres.h>
#include <iostream>
#include <cmath>
#include <random>
#include <limits>

// Cost functor for Ceres with analytical gradient
class ParameterOptimizationCostFunctor
{
private:
    std::function<float(const std::vector<float>&)> objectiveFunction;

public:
    explicit ParameterOptimizationCostFunctor(std::function<float(const std::vector<float>&)> func)
        : objectiveFunction(func) {}

    bool operator()(const double* const parameters, double* residual) const
    {
        // Convert Ceres parameters to vector
        std::vector<float> params(4);
        params[0] = static_cast<float>(parameters[0]);
        params[1] = static_cast<float>(parameters[1]);
        params[2] = static_cast<float>(parameters[2]);
        params[3] = static_cast<float>(parameters[3]);
        
        // Evaluate objective function
        float result = objectiveFunction(params);
        residual[0] = static_cast<double>(result);
        
        return true;
    }
    
    static ceres::CostFunction* Create(std::function<float(const std::vector<float>&)> func)
    {
        // Use numerical differentiation with forward differences
        return new ceres::NumericDiffCostFunction<
            ParameterOptimizationCostFunctor, ceres::FORWARD, 1, 4>(
            new ParameterOptimizationCostFunctor(func));
    }
};

Optimizer::Optimizer(std::function<float(const std::vector<float>&)> func)
    : objectiveFunction(func)
{
}

std::vector<float> Optimizer::optimize(const std::vector<float>& initialGuess)
{
    // Add some random perturbation to initial guess to encourage exploration
    std::random_device rd;
    std::mt19937 gen(rd());
    std::uniform_real_distribution<double> perturbation(-0.1, 0.1);
    
    // Initialize parameters with perturbation
    double parameters[4];
    parameters[0] = std::max(1.0, std::min(1000.0, static_cast<double>(initialGuess[0]) + perturbation(gen) * initialGuess[0]));
    parameters[1] = std::max(10.0, std::min(1000.0, static_cast<double>(initialGuess[1]) + perturbation(gen) * initialGuess[1]));
    parameters[2] = std::max(M_PI/8.0, std::min(M_PI/2.0, static_cast<double>(initialGuess[2]) + perturbation(gen) * initialGuess[2]));
    parameters[3] = std::max(0.0, std::min(1.0, static_cast<double>(initialGuess[3]) + perturbation(gen) * initialGuess[3]));
    
    std::cout << "Starting with perturbed parameters:" << std::endl;
    std::cout << "  k: " << parameters[0] << " (was " << initialGuess[0] << ")" << std::endl;
    std::cout << "  numObs: " << parameters[1] << " (was " << initialGuess[1] << ")" << std::endl;
    std::cout << "  distThresh: " << parameters[2] << " (was " << initialGuess[2] << ")" << std::endl;
    std::cout << "  feedThresh: " << parameters[3] << " (was " << initialGuess[3] << ")" << std::endl;
    
    // Build the problem
    ceres::Problem problem;
    
    // Add residual block
    ceres::CostFunction* cost_function = 
        ParameterOptimizationCostFunctor::Create(objectiveFunction);
    problem.AddResidualBlock(cost_function, nullptr, parameters);
    
    // Set parameter bounds - make them looser to allow more exploration
    problem.SetParameterLowerBound(parameters, 0, 1.0);
    problem.SetParameterUpperBound(parameters, 0, 1000.0);
    
    problem.SetParameterLowerBound(parameters, 1, 10.0);
    problem.SetParameterUpperBound(parameters, 1, 1000.0);
    
    problem.SetParameterLowerBound(parameters, 2, M_PI / 8.0);
    problem.SetParameterUpperBound(parameters, 2, M_PI / 2.0);
    
    problem.SetParameterLowerBound(parameters, 3, 0.0);
    problem.SetParameterUpperBound(parameters, 3, 1.0);
    
    // Configure solver options for more aggressive exploration
    ceres::Solver::Options options;
    options.linear_solver_type = ceres::DENSE_QR;
    options.minimizer_progress_to_stdout = true;
    options.max_num_iterations = 50; // Fewer iterations but allow bigger steps
    
    // More aggressive tolerances to allow bigger moves
    options.function_tolerance = 1e-4; // Looser tolerance
    options.gradient_tolerance = 1e-6; // Looser tolerance  
    options.parameter_tolerance = 1e-4; // Looser tolerance
    
    // Trust region settings for more aggressive steps
    options.initial_trust_region_radius = 100.0; // Much larger initial trust region
    options.max_trust_region_radius = 1000.0;    // Much larger max trust region
    options.min_trust_region_radius = 1e-8;
    
    // Line search settings
    options.use_nonmonotonic_steps = true; // Allow non-monotonic improvements
    options.max_consecutive_nonmonotonic_steps = 10;
    
    // Solve
    ceres::Solver::Summary summary;
    
    ceres::Solve(options, &problem, &summary);
    
    // Print summary
    std::cout << summary.BriefReport() << std::endl;
    
    // Final constraint enforcement (only round integers at the very end)
    parameters[0] = std::round(parameters[0]);
    parameters[1] = std::round(parameters[1]);
    
    // Ensure v[0] <= v[1]
    if (parameters[0] > parameters[1])
    {
        parameters[0] = parameters[1];
    }
    
    // Ensure bounds are respected
    parameters[0] = std::max(1.0, std::min(parameters[0], parameters[1]));
    parameters[1] = std::max(10.0, std::min(1000.0, parameters[1]));
    parameters[2] = std::max(M_PI/8.0, std::min(M_PI/2.0, parameters[2]));
    parameters[3] = std::max(0.0, std::min(1.0, parameters[3]));
    
    // Convert back to vector
    std::vector<float> result(4);
    for (int i = 0; i < 4; ++i)
    {
        result[i] = static_cast<float>(parameters[i]);
    }
    
    return result;
}

std::vector<float> Optimizer::optimizeMultiStart(const std::vector<float>& initialGuess, int numStarts)
{
    std::cout << "Starting multi-start optimization with " << numStarts << " different starting points..." << std::endl;
    
    std::vector<float> bestResult = initialGuess;
    float bestError = std::numeric_limits<float>::max();
    
    for (int start = 0; start < numStarts; ++start)
    {
        std::cout << "\n=== Starting point " << (start + 1) << "/" << numStarts << " ===" << std::endl;
        
        // Try optimization from this starting point
        std::vector<float> result = optimize(initialGuess);
        float error = objectiveFunction(result);
        
        std::cout << "Result from start " << (start + 1) << ": error = " << error << std::endl;
        
        if (error < bestError)
        {
            bestError = error;
            bestResult = result;
            std::cout << "*** New best result found! ***" << std::endl;
        }
    }
    
    std::cout << "\n=== Multi-start optimization complete ===" << std::endl;
    std::cout << "Best error found: " << bestError << std::endl;
    std::cout << "Best parameters:" << std::endl;
    std::cout << "  k: " << bestResult[0] << std::endl;
    std::cout << "  numObs: " << bestResult[1] << std::endl;
    std::cout << "  distThresh: " << bestResult[2] << std::endl;
    std::cout << "  feedThresh: " << bestResult[3] << std::endl;
    
    return bestResult;
}

std::function<float(const std::vector<float>&)> Optimizer::createExperimentObjective(
    const std::vector<ModelInterface*>& models)
{
    return [models](const std::vector<float>& params) -> float
    {
        // Create fresh instances of models for this evaluation to avoid state contamination
        std::vector<ModelInterface*> freshModels;
        for (auto& model : models)
        {
            // Create a new instance of the same model type
            // For now, assuming KNNModel - this could be made more generic with a factory pattern
            freshModels.push_back(new KNNModel());
        }
        
        // Initialize fresh models with the given parameters
        for (auto& model : freshModels)
        {
            model->initialize(params);
        }
        
        // Run the experiment logic (similar to Experiment::run but without output)
        World w;
        Viewpoint vp;
        Observation o;
        bool firstRun = true;
        float totalError = 0.0f;
        
        // Use 1 million iterations for more accurate optimization
        for (int i = 0; i < 100000; ++i)
        {
            vp = Viewpoint::random();
            o = w.observe(vp);
            
            // Ensure the observation is valid, and if it's the first run, we have a seen observation
            while (o.getStatus() == INVALID || (firstRun && o.getStatus() != SEEN))
            {
                vp = Viewpoint::random();
                o = w.observe(vp);
            }
            firstRun = false;
            
            for (auto& model : freshModels)
            {
                float prediction = model->predict(o);
                model->feedback(std::abs(prediction - o.getStatus()));
                totalError += std::abs(prediction - o.getStatus());
            }
        }
        
        // Clean up fresh models
        for (auto* model : freshModels)
        {
            delete model;
        }
        
        return totalError;
    };
}

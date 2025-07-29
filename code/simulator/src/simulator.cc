#include <iostream>
#include "experiment.h"
#include "models/knn_model.h"

int main(int argc, char **argv)
{
    std::cout << "Simulator started with " << argc << " arguments." << std::endl;

    // Initialize an Experiment instance
    Experiment experiment;

    auto knnModel = new KNNModel();
    experiment.addModel(knnModel);

    experiment.run();

    // Here you would typically set up the experiment parameters, run simulations, etc.
    // For now, we will just print a message indicating that the experiment is ready to run.
    std::cout << "Experiment is ready to run." << std::endl;

    return 0;
}
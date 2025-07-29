#pragma once

#include "world.h"
#include "model_interface.h"

/*
 * The Experiment class is the main interface for running simulations.
 * Experiments take the following parameters:
 *  - Number of worlds: This is the total number of worlds which will be generated and optimized over
 *  - Number of iterations: The max number of iterations the optimizer has to optimize the model's parameters
 * For each model, it collects the following data:
 *    -
 */
class Experiment
{
    std::vector<ModelInterface *> models;

public:
    void addModel(ModelInterface *model);

    void run();
};
#include "experiment.h"

#include <iostream>

void Experiment::addModel(ModelInterface *model)
{
    models.push_back(model);
}

void Experiment::run()
{
    std::cout << "Running experiment with " << models.size() << " models." << std::endl;

    for (auto &model : models)
    {
        model->initialize({2.0f, 500.0f, M_PI_4, 0.1f});
    }

    World w;
    Viewpoint vp;
    Observation o;
    bool firstRun = true;
    float totalError = 0.0f;
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

        for (auto &model : models)
        {
            float prediction = model->predict(o);
            model->feedback(std::abs(prediction - o.getStatus()));
            totalError += std::abs(prediction - o.getStatus());
        }
    }
    std::cout << "Total error after 100000 iterations: " << totalError << std::endl;
}
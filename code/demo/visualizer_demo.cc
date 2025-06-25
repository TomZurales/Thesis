// #include "Visualizer.h"
#include <memory>
#include <iostream>
#include <cmath>
#include <eigen3/Eigen/Core>

#include "PointProbabilityEngine.h"
#include "Camera.h"
#include "Point.h"
#include "Utility.h"

int main()
{
    auto engine = std::make_shared<PointProbabilityEngine>(Camera(1920, 1080, 0.2, 0.2));

    Point *thePoint(new Point(Eigen::Vector3f(0, 0, 0)));

    // Create the visualizer with the engine
    // Visualizer visualizer(engine, 800, 600, "OpenGL Visualizer Demo");

    // if (!visualizer.initialize())
    // {
    //     std::cerr << "Failed to initialize visualizer" << std::endl;
    //     return -1;
    // }

    // Set up camera
    Eigen::Vector3f cameraPos(3.0f, 0.0f, 0.0f);
    Eigen::Vector3f lookAt(0.0f, 0.0f, 0.0f);

    float time = 0.0f;
    while (!engine->getShouldClose())
    {
        // Calculate camera position in a circle around the origin
        float radius = 30.0f + cos(time); // Vary radius slightly for effect
        float x = radius * std::cos(time);
        float z = radius * std::sin(time);
        float y = 10.0f + std::sin(time); // Keep camera slightly above the cube

        // Update camera position and look at origin
        cameraPos = Eigen::Vector3f(x, y, z);
        lookAt = Eigen::Vector3f(0.0f, 0.0f, 0.0f);

        std::vector<Point *> seenPoints = {};
        if (time <= M_PI + 0.5)
            seenPoints.push_back(thePoint);

        engine->Update(LookAtTransform(cameraPos, lookAt), seenPoints);

        // Render the scene
        // visualizer.update(cameraPos, lookAt);
        // visualizer.render();

        // Handle events
        // visualizer.pollEvents();

        // Increment time for smooth rotation
        time += 0.01f;
        if (time >= 2 * M_PI)
            time = 0;
    }
    return 0;
}
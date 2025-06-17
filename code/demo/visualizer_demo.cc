#include "Visualizer.h"
#include <memory>
#include <iostream>
#include <cmath>

#include "Utility.h"

int main()
{
    auto engine = std::make_shared<PointProbabilityEngine>();

    Point *thePoint(new Point(Eigen::Vector3f(0, 0, 0)));

    // Create the visualizer with the engine
    Visualizer visualizer(engine, 800, 600, "OpenGL Visualizer Demo");

    if (!visualizer.initialize())
    {
        std::cerr << "Failed to initialize visualizer" << std::endl;
        return -1;
    }

    // Set up camera
    glm::vec3 cameraPos(3.0f, 0.0f, 0.0f);
    glm::vec3 lookAt(0.0f, 0.0f, 0.0f);

    float time = 0.0f;
    while (!visualizer.shouldClose())
    {
        // Calculate camera position in a circle around the origin
        float radius = 3.0f;
        float x = radius * std::cos(time);
        float z = radius * std::sin(time);
        float y = 0.5f * std::sin(time); // Keep camera slightly above the cube

        // Update camera position and look at origin
        cameraPos = glm::vec3(x, y, z);
        lookAt = glm::vec3(0.0f, 0.0f, 0.0f);

        std::vector<Point *> seenPoints = {};
        if (time <= M_PI)
            seenPoints.push_back(thePoint);

        engine->Update(LookAtTransform(Eigen::Vector3f(cameraPos.x, cameraPos.y, cameraPos.z), Eigen::Vector3f(lookAt.x, lookAt.y, lookAt.z)), seenPoints);

        // Render the scene
        visualizer.update(cameraPos, lookAt);
        visualizer.render();

        // Handle events
        visualizer.pollEvents();

        // Increment time for smooth rotation
        time += 0.01f;
        if (time >= 2 * M_PI)
            time = 0;
    }
    return 0;
}
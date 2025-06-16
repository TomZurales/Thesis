#include "Visualizer.h"
#include <memory>
#include <iostream>
#include <cmath>

int main() {
    auto engine = std::make_shared<PointProbabilityEngine>();
    
    // Add some test points
    engine->Update(Eigen::Matrix4f::Identity(), {new Point(Eigen::Vector3f(0, 0, 0)), new Point(Eigen::Vector3f(0.5, 0.5, 0.5))});

    // Create the visualizer with the engine
    Visualizer visualizer(engine, 800, 600, "OpenGL Visualizer Demo");
    
    if (!visualizer.initialize()) {
        std::cerr << "Failed to initialize visualizer" << std::endl;
        return -1;
    }

    // Set up camera
    glm::vec3 cameraPos(3.0f, 0.0f, 0.0f);
    glm::vec3 lookAt(0.0f, 0.0f, 0.0f);

    float time = 0.0f;
    while (!visualizer.shouldClose()) {
        // Calculate camera position in a circle around the origin
        float radius = 3.0f;
        float x = radius * std::cos(time);
        float z = radius * std::sin(time);
        float y = 1.0f; // Keep camera slightly above the cube

        // Update camera position and look at origin
        cameraPos = glm::vec3(x, y, z);
        lookAt = glm::vec3(0.0f, 0.0f, 0.0f);

        // Render the scene
        visualizer.update(cameraPos, lookAt);
        visualizer.render();
        
        // Handle events
        visualizer.pollEvents();

        // Increment time for smooth rotation
        time += 0.01f;
    }
    return 0;
} 
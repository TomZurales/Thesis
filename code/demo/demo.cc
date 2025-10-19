#include <iostream>
#include <eigen3/Eigen/Core>
#include <bits/this_thread_sleep.h>

#include <Eigen/Geometry>

#include "PointProbabilityEngine.h"
#include "Visualizer.h"

Eigen::Quaternionf lookAt(const Eigen::Vector3f &from, const Eigen::Vector3f &to)
{
  Eigen::Vector3f forward = (to - from).normalized();
  Eigen::Vector3f up = Eigen::Vector3f::UnitZ();

  // Handle the case when forward and up are parallel
  if (std::abs(forward.dot(up)) > 0.999f)
  {
    up = Eigen::Vector3f::UnitY();
  }

  Eigen::Vector3f right = up.cross(forward).normalized();
  Eigen::Vector3f newUp = forward.cross(right);

  Eigen::Matrix3f rot;
  rot.col(0) = right;
  rot.col(1) = newUp;
  rot.col(2) = forward;

  return Eigen::Quaternionf(rot);
}

Eigen::Matrix4f makeTransform(const Eigen::Vector3f &position, const Eigen::Quaternionf &orientation)
{
  Eigen::Matrix4f transform = Eigen::Matrix4f::Identity();
  transform.block<3, 3>(0, 0) = orientation.toRotationMatrix();
  transform.block<3, 1>(0, 3) = position;
  return transform;
}

int main(int argc, char **argv)
{
    std::cout << "Point Probability Engine Demo" << std::endl;
    std::cout << "Creating visualizer..." << std::endl;

    // Create visualizer
    Visualizer vis(800, 600, "Point Probability Engine Demo");

    std::cout << "Entering render loop..." << std::endl;

    // Main render loop
    while (!vis.shouldClose())
    {
        // Render the scene
        vis.render();
        
        // Handle events and swap buffers
        vis.pollEvents();
        vis.swapBuffers();
        
        // Cap the frame rate
        std::this_thread::sleep_for(std::chrono::milliseconds(16)); // ~60 FPS
    }

    std::cout << "Exiting..." << std::endl;
    return 0;
}
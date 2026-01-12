#pragma once

#include <eigen3/Eigen/Core>
#include <vector>

class ObservabilityScenario {
private:
  bool valid = true;
  std::vector<Eigen::Vector3f> blockers;

public:
  ObservabilityScenario() = default;
  ObservabilityScenario(int n_blockers, float goal_blocked_rate);

  bool isInKeepout(Eigen::Vector3f point) const { return false; }

  bool isSeen(Eigen::Vector3f point) const;

  bool isValid() const { return valid; }
};

inline Eigen::Vector3f randomPosition() {
  float u = static_cast<float>(rand()) / static_cast<float>(RAND_MAX);
  float v = static_cast<float>(rand()) / static_cast<float>(RAND_MAX);
  float w = static_cast<float>(rand()) / static_cast<float>(RAND_MAX);
  
  float theta = 2.0f * M_PI * u;
  float phi = std::acos(2.0f * v - 1.0f);
  float r = 5.0f * std::cbrt(w);
  
  // Convert to Cartesian coordinates
  float x = r * std::sin(phi) * std::cos(theta);
  float y = r * std::sin(phi) * std::sin(theta);
  float z = r * std::cos(phi);
  
  return Eigen::Vector3f(x, y, z);
}
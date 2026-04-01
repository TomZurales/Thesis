#pragma once

#include <eigen3/Eigen/Core>
#include <vector>
#include <boost/serialization/access.hpp>
#include <boost/serialization/vector.hpp>
#include <boost/serialization/version.hpp>

class ObservabilityScenario {
private:
  std::vector<Eigen::Vector3f> blockers;
  
  friend class boost::serialization::access;
  template<class Archive>
  void serialize(Archive & ar, const unsigned int version)
  {
    ar & blockers;
  }

public:
  ObservabilityScenario() = default;
  ObservabilityScenario(float goal_blocked_rate);

  bool isInKeepout(Eigen::Vector3f point) const { return false; }

  bool isSeen(Eigen::Vector3f point) const;
};

inline Eigen::Vector3f randomPosition() {
  // Generate uniform random point inside unit sphere
  float u1 = static_cast<float>(rand()) / static_cast<float>(RAND_MAX);
  float u2 = static_cast<float>(rand()) / static_cast<float>(RAND_MAX);
  float u3 = static_cast<float>(rand()) / static_cast<float>(RAND_MAX);
  
  // Convert to spherical coordinates for uniform distribution
  float theta = 2.0f * M_PI * u1;  // Azimuthal angle [0, 2π]
  float phi = std::acos(2.0f * u2 - 1.0f);  // Polar angle [0, π] 
  float r = std::cbrt(u3);  // Radius with cube root for uniform volume distribution
  
  // Convert to Cartesian coordinates
  float x = r * std::sin(phi) * std::cos(theta);
  float y = r * std::sin(phi) * std::sin(theta);
  float z = r * std::cos(phi);
  
  return Eigen::Vector3f(x, y, z);
}
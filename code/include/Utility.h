#pragma once

#include <Eigen/Core>
#include <Eigen/Geometry>

Eigen::Matrix4f LookAtTransform(const Eigen::Vector3f &position, const Eigen::Vector3f &lookAt);
std::vector<float> colorMap(float value, float minValue = 0.0f, float maxValue = 1.0f);
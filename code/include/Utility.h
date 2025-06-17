#pragma once

#include <Eigen/Core>
#include <Eigen/Geometry>

Eigen::Matrix4f LookAtTransform(const Eigen::Vector3f &position, const Eigen::Vector3f &lookAt);
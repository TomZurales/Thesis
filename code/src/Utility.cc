#include "Utility.h"

Eigen::Matrix4f LookAtTransform(const Eigen::Vector3f &position, const Eigen::Vector3f &lookAt)
{
    // ORB_SLAM3 up vector (Y-down)
    Eigen::Vector3f up(0.0f, 1.0f, 0.0f);

    // Forward vector (Z+)
    Eigen::Vector3f forward = (lookAt - position).normalized();

    // Right vector (X+)
    Eigen::Vector3f right = up.cross(forward).normalized();

    // Recompute up to ensure orthogonality
    Eigen::Vector3f trueUp = forward.cross(right).normalized();

    Eigen::Matrix4f transform = Eigen::Matrix4f::Identity();
    // Set rotation (columns: right, up, forward)
    transform.block<3, 1>(0, 0) = right;
    transform.block<3, 1>(0, 1) = trueUp;
    transform.block<3, 1>(0, 2) = forward;
    // Set translation
    transform.block<3, 1>(0, 3) = position;

    return transform;
}
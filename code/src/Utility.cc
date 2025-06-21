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

std::vector<float> colorMap(float value, float min, float max)
{
    // Normalize value to [0, 1]
    float t = (value - min) / (max - min);
    t = std::clamp(t, 0.0f, 1.0f);

    // 5 color stops: blue, cyan, green, yellow, red
    // blue  (0,0,1)
    // cyan  (0,1,1)
    // green (0,1,0)
    // yellow(1,1,0)
    // red   (1,0,0)
    struct Color
    {
        float r, g, b;
    };
    static const Color colors[] = {
        {0.0f, 0.0f, 1.0f}, // blue
        {0.0f, 1.0f, 1.0f}, // cyan
        {0.0f, 1.0f, 0.0f}, // green
        {1.0f, 1.0f, 0.0f}, // yellow
        {1.0f, 0.0f, 0.0f}  // red
    };

    float idx = t * 4.0f;
    int idx0 = static_cast<int>(std::floor(idx));
    int idx1 = std::min(idx0 + 1, 4);
    float frac = idx - idx0;

    const Color &c0 = colors[idx0];
    const Color &c1 = colors[idx1];

    float r = c0.r + (c1.r - c0.r) * frac;
    float g = c0.g + (c1.g - c0.g) * frac;
    float b = c0.b + (c1.b - c0.b) * frac;

    return {r, g, b};
}
#pragma once

#include <eigen3/Eigen/Core>
#include <eigen3/Eigen/Geometry>

class Camera {
public:
    // Constructor with position, orientation (quaternion), and intrinsic parameters
    Camera(const Eigen::Vector3f& position = Eigen::Vector3f::Zero(),
           const Eigen::Quaternionf& orientation = Eigen::Quaternionf::Identity(),
           float fx = 525.0f, float fy = 525.0f,
           float cx = 320.0f, float cy = 240.0f,
           int width = 640, int height = 480);

    // Constructor with position, look direction, and intrinsic parameters
    Camera(const Eigen::Vector3f& position,
           const Eigen::Vector3f& look_at,
           const Eigen::Vector3f& up = Eigen::Vector3f::UnitY(),
           float fx = 525.0f, float fy = 525.0f,
           float cx = 320.0f, float cy = 240.0f,
           int width = 640, int height = 480);

    // Check if a 3D world point projects into the image
    bool isPointVisible(const Eigen::Vector3f& world_point) const;

    // Project a 3D world point to 2D image coordinates
    Eigen::Vector2f project(const Eigen::Vector3f& world_point) const;

    // Transform world point to camera coordinates
    Eigen::Vector3f worldToCameraCoordinates(const Eigen::Vector3f& world_point) const;

    // Getters
    const Eigen::Vector3f& getPosition() const { return position_; }
    const Eigen::Quaternionf& getOrientation() const { return orientation_; }
    const Eigen::Matrix4f& getExtrinsicMatrix() const { return extrinsic_matrix_; }
    const Eigen::Matrix3f& getIntrinsicMatrix() const { return intrinsic_matrix_; }
    int getWidth() const { return width_; }
    int getHeight() const { return height_; }
    float getFocalLengthX() const { return fx_; }
    float getFocalLengthY() const { return fy_; }

    // Setters
    void setPosition(const Eigen::Vector3f& position);
    void setOrientation(const Eigen::Quaternionf& orientation);
    void setPose(const Eigen::Vector3f& position, const Eigen::Quaternionf& orientation);
    void lookAt(const Eigen::Vector3f& target, const Eigen::Vector3f& up = Eigen::Vector3f::UnitY());

    // Visualization
    void draw(float frustum_size = 0.5f) const;

private:
    // Camera pose
    Eigen::Vector3f position_;
    Eigen::Quaternionf orientation_;

    // Intrinsic parameters
    float fx_, fy_;  // focal lengths
    float cx_, cy_;  // principal point
    int width_, height_;  // image dimensions

    // Precomputed matrices
    Eigen::Matrix4f extrinsic_matrix_;  // World to camera transformation
    Eigen::Matrix3f intrinsic_matrix_;  // Camera intrinsic matrix

    // Update the extrinsic matrix when pose changes
    void updateExtrinsicMatrix();
    void updateIntrinsicMatrix();
};

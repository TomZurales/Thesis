#include "camera.h"
#include <iostream>
#include <GL/gl.h>

Camera::Camera(const Eigen::Vector3f& position,
               const Eigen::Quaternionf& orientation,
               float fx, float fy, float cx, float cy,
               int width, int height)
    : position_(position), orientation_(orientation),
      fx_(fx), fy_(fy), cx_(cx), cy_(cy),
      width_(width), height_(height) {
    updateIntrinsicMatrix();
    updateExtrinsicMatrix();
}

Camera::Camera(const Eigen::Vector3f& position,
               const Eigen::Vector3f& look_at,
               const Eigen::Vector3f& up,
               float fx, float fy, float cx, float cy,
               int width, int height)
    : position_(position),
      fx_(fx), fy_(fy), cx_(cx), cy_(cy),
      width_(width), height_(height) {
    lookAt(look_at, up);
    updateIntrinsicMatrix();
    updateExtrinsicMatrix();
}

bool Camera::isPointVisible(const Eigen::Vector3f& world_point) const {
    // Transform to camera coordinates
    Eigen::Vector3f camera_point = worldToCameraCoordinates(world_point);
    
    // Check if point is in front of camera (positive Z in camera coordinates)
    if (camera_point.z() <= 0) {
        return false;
    }
    
    // Project to image coordinates
    Eigen::Vector2f image_point = project(world_point);
    
    // Check if projection is within image bounds
    return (image_point.x() >= 0 && image_point.x() < width_ &&
            image_point.y() >= 0 && image_point.y() < height_);
}

Eigen::Vector2f Camera::project(const Eigen::Vector3f& world_point) const {
    // Transform to camera coordinates
    Eigen::Vector3f camera_point = worldToCameraCoordinates(world_point);
    
    // Project using pinhole model: [u, v, 1]^T = K * [X/Z, Y/Z, 1]^T
    float x = camera_point.x() / camera_point.z();
    float y = camera_point.y() / camera_point.z();
    
    float u = fx_ * x + cx_;
    float v = fy_ * y + cy_;
    
    return Eigen::Vector2f(u, v);
}

Eigen::Vector3f Camera::worldToCameraCoordinates(const Eigen::Vector3f& world_point) const {
    // Transform world point to camera coordinates using extrinsic matrix
    Eigen::Vector4f world_homogeneous(world_point.x(), world_point.y(), world_point.z(), 1.0f);
    Eigen::Vector4f camera_homogeneous = extrinsic_matrix_ * world_homogeneous;
    
    return camera_homogeneous.head<3>();
}

void Camera::setPosition(const Eigen::Vector3f& position) {
    position_ = position;
    updateExtrinsicMatrix();
}

void Camera::setOrientation(const Eigen::Quaternionf& orientation) {
    orientation_ = orientation.normalized();
    updateExtrinsicMatrix();
}

void Camera::setPose(const Eigen::Vector3f& position, const Eigen::Quaternionf& orientation) {
    position_ = position;
    orientation_ = orientation.normalized();
    updateExtrinsicMatrix();
}

void Camera::lookAt(const Eigen::Vector3f& target, const Eigen::Vector3f& up) {
    // Calculate forward direction (camera looks along negative Z axis)
    Eigen::Vector3f forward = (target - position_).normalized();
    
    // Calculate right direction
    Eigen::Vector3f right = forward.cross(up.normalized()).normalized();
    
    // Recalculate up direction to ensure orthogonality
    Eigen::Vector3f actual_up = right.cross(forward).normalized();
    
    // Create rotation matrix (camera coordinate system)
    // In camera coordinates: X = right, Y = up, Z = -forward
    Eigen::Matrix3f rotation_matrix;
    rotation_matrix.col(0) = right;
    rotation_matrix.col(1) = actual_up;
    rotation_matrix.col(2) = -forward;
    
    // Convert to quaternion
    orientation_ = Eigen::Quaternionf(rotation_matrix);
    orientation_.normalize();
    
    updateExtrinsicMatrix();
}

void Camera::updateExtrinsicMatrix() {
    // Create world-to-camera transformation matrix
    // T = [R^T  -R^T*t]
    //     [0    1     ]
    
    Eigen::Matrix3f rotation = orientation_.toRotationMatrix().transpose();
    Eigen::Vector3f translation = -rotation * position_;
    
    extrinsic_matrix_ = Eigen::Matrix4f::Identity();
    extrinsic_matrix_.block<3,3>(0,0) = rotation;
    extrinsic_matrix_.block<3,1>(0,3) = translation;
}

void Camera::updateIntrinsicMatrix() {
    intrinsic_matrix_ = Eigen::Matrix3f::Zero();
    intrinsic_matrix_(0,0) = fx_;
    intrinsic_matrix_(1,1) = fy_;
    intrinsic_matrix_(0,2) = cx_;
    intrinsic_matrix_(1,2) = cy_;
    intrinsic_matrix_(2,2) = 1.0f;
}

void Camera::draw(float frustum_size) const {
    // Calculate the four corners of the image plane at the specified distance
    float half_width = (width_ * frustum_size) / (2.0f * fx_);
    float half_height = (height_ * frustum_size) / (2.0f * fy_);
    
    // Image plane corners in camera coordinates
    Eigen::Vector3f corners_camera[4] = {
        Eigen::Vector3f(-half_width, -half_height, frustum_size),  // top-left
        Eigen::Vector3f(half_width, -half_height, frustum_size),   // top-right
        Eigen::Vector3f(half_width, half_height, frustum_size),    // bottom-right
        Eigen::Vector3f(-half_width, half_height, frustum_size)    // bottom-left
    };
    
    // Transform corners to world coordinates
    Eigen::Matrix3f rotation = orientation_.toRotationMatrix();
    Eigen::Vector3f corners_world[4];
    for (int i = 0; i < 4; i++) {
        corners_world[i] = rotation * corners_camera[i] + position_;
    }
    
    // Set line color (cyan for camera frustum)
    glColor3f(0.0f, 1.0f, 1.0f);
    glLineWidth(1.5f);
    
    glBegin(GL_LINES);
    
    // Draw lines from camera position to each corner
    for (int i = 0; i < 4; i++) {
        // Line from camera center to corner
        glVertex3f(position_.x(), position_.y(), position_.z());
        glVertex3f(corners_world[i].x(), corners_world[i].y(), corners_world[i].z());
    }
    
    // Draw the rectangle of the image plane
    for (int i = 0; i < 4; i++) {
        int next = (i + 1) % 4;
        glVertex3f(corners_world[i].x(), corners_world[i].y(), corners_world[i].z());
        glVertex3f(corners_world[next].x(), corners_world[next].y(), corners_world[next].z());
    }
    
    glEnd();
    
    // Draw a small sphere at the camera position
    glColor3f(1.0f, 0.5f, 0.0f); // Orange for camera center
    glPushMatrix();
    glTranslatef(position_.x(), position_.y(), position_.z());
    
    // Draw a simple point for the camera center
    glPointSize(8.0f);
    glBegin(GL_POINTS);
    glVertex3f(0.0f, 0.0f, 0.0f);
    glEnd();
    
    glPopMatrix();
}

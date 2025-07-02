#pragma once

#include <eigen3/Eigen/Core>

class Camera
{
private:
  float width, height, fx, fy;
  Eigen::Matrix3f cameraMatrix;
  Eigen::Matrix4f pose; // Assuming pose is a 4x4 matrix for transformation

public:
  Camera(float width, float height, float fx, float fy);
  void setPose(const Eigen::Matrix4f &newPose) { pose = newPose; }
  Eigen::Matrix4f getPose() const { return pose; }

  Eigen::Matrix3f getCameraMatrix() { return cameraMatrix; }
  float getWidth() const { return width; }
  float getHeight() const { return height; }
  float getFx() const { return fx; }
  float getFy() const { return fy; }
  float getFov() const { return 2 * atan((width / 2) / fx); } // Horizontal FOV in radians
};
#pragma once

#include <eigen3/Eigen/Core>

class Camera
{
private:
  float width, height, fx, fy;
  Eigen::Matrix3f cameraMatrix;

public:
  Camera(float width, float height, float fx, float fy);

  Eigen::Matrix3f getCameraMatrix() { return cameraMatrix; }
  float getWidth() const { return width; }
  float getHeight() const { return height; }
  float getFx() const { return fx; }
  float getFy() const { return fy; }
};
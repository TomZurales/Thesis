#include "Camera.h"

Camera::Camera(float width, float height, float fx, float fy) : width(width), height(height), fx(fx), fy(fy)
{
  cameraMatrix = Eigen::Matrix3f::Identity();
  cameraMatrix(0, 0) = fx;
  cameraMatrix(1, 1) = fy;
  cameraMatrix(0, 2) = width / 2.0f;
  cameraMatrix(1, 2) = height / 2.0f;
}
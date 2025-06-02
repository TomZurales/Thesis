#include <iostream>
#include <eigen3/Eigen/Core>
#include <bits/this_thread_sleep.h>

#include <Eigen/Geometry>

#include "PointProbabilityEngine.h"

Eigen::Quaternionf lookAt(const Eigen::Vector3f &from, const Eigen::Vector3f &to)
{
  Eigen::Vector3f forward = (to - from).normalized();
  Eigen::Vector3f up = Eigen::Vector3f::UnitZ();

  // Handle the case when forward and up are parallel
  if (std::abs(forward.dot(up)) > 0.999f)
  {
    up = Eigen::Vector3f::UnitY();
  }

  Eigen::Vector3f right = up.cross(forward).normalized();
  Eigen::Vector3f newUp = forward.cross(right);

  Eigen::Matrix3f rot;
  rot.col(0) = right;
  rot.col(1) = newUp;
  rot.col(2) = forward;

  return Eigen::Quaternionf(rot);
}

Eigen::Matrix4f makeTransform(const Eigen::Vector3f &position, const Eigen::Quaternionf &orientation)
{
  Eigen::Matrix4f transform = Eigen::Matrix4f::Identity();
  transform.block<3, 3>(0, 0) = orientation.toRotationMatrix();
  transform.block<3, 1>(0, 3) = position;
  return transform;
}

int main(int argc, char **argv)
{
  std::cout << "Point Probability Engine Demo for a single point which is periodically visible." << std::endl;

  // In this demo, there is a single keypoint at the origin. The keypoint lies on a
  // wall which is smaller than the radius around which the camera rotates.
  // The camera is always looking directly at the map point, but can only see
  // it when it is in front of the wall between a rotation of 0 and pi radians.

  PointProbabilityEngine ppe;
  Point p(Eigen::Vector3f(0., 0., 0.));

  // Changable parameters
  float radius = 5;
  float speed = 0.1;

  // Initial parameters
  float r = 3 * M_PI_2;
  Eigen::Vector3f cameraPose(radius * cos(r), radius * sin(r), 0.);
  Eigen::Quaternionf cameraRotation = lookAt(cameraPose, p.getPose());
  Eigen::Matrix4f tCamera = makeTransform(cameraPose, cameraRotation);
  bool seesPoint = false;

  int count = 0;
  while (true)
  {
    if (seesPoint)
    {
      std::vector<Point *> points = {&p};
      ppe.Update(tCamera, points);
    }
    else
    {
      // Can't see the point, send an empty list
      std::vector<Point *> points = {};
      ppe.Update(tCamera, points);
    }
    r += speed;
    r = std::fmod(r, 2 * M_PI);

    cameraPose = Eigen::Vector3f(radius * cos(r), radius * sin(r), 0.);
    cameraRotation = lookAt(cameraPose, p.getPose());
    tCamera = makeTransform(cameraPose, cameraRotation);

    if (r > M_PI_2 && r < (3 * M_PI_2) || count >= 1000)
    {
      seesPoint = false;
    }
    else
    {
      seesPoint = true;
    }

    std::this_thread::sleep_for(std::chrono::milliseconds(33));
    if (count <= 1000)
      count++;
    if (count == 1000)
      std::cout << "Hiding Point" << std::endl;
  }
}
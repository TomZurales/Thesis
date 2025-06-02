#pragma once

#include <eigen3/Eigen/Core>

class Point
{
  static int nextId;
  int id;
  Eigen::Vector3f worldPose;

public:
  Point(Eigen::Vector3f pose) : worldPose(pose)
  {
    id = nextId;
    nextId++;
  }

  Eigen::Vector3f getPose() { return worldPose; }
};

// Definition of static member
inline int Point::nextId = 0;
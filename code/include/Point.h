#pragma once

#include <eigen3/Eigen/Core>

class Point
{
  static int nextId;
  int id;
  Eigen::Vector3f worldPose;

  // Flags for visualization
  bool isCurrentlyInView = false;
  bool isCurrentlyVisible = false;
  bool isInMap = true;

public:
  Point(Eigen::Vector3f pose) : worldPose(pose)
  {
    id = nextId;
    nextId++;
  }

  int getId() const { return id; }

  Eigen::Vector3f getPose() const { return worldPose; }

  bool isInView() const { return isCurrentlyInView; }
  bool isVisible() const { return isCurrentlyVisible; }
  bool inMap() const { return isInMap; }

  void setInView(bool inView) { isCurrentlyInView = inView; }
  void setVisible(bool visible) { isCurrentlyVisible = visible; }
  void setInMap(bool inMap) { isInMap = inMap; }
};

// Definition of static member
inline int Point::nextId = 0;
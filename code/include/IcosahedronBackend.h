#pragma once

#include <vector>
#include <map>
#include <eigen3/Eigen/Core>
#include <iostream>

#include <imgui.h>

#include "PPEBackend.h"
#include "Point.h"
#include "Icosahedron.h"
#include "Utility.h"

class IcosahedronBackend : public PPEBackend
{
private:
  std::map<Point *, Icosahedron *> pointIcosMap = std::map<Point *, Icosahedron *>();
  void failedObservation(Eigen::Matrix4f observerPose, Point *point);
  void successfulObservation(Eigen::Matrix4f observerPose, Point *point);

  // Visualization parameters
  std::map<Point *, Icosahedron *>::iterator pointIcosMapIndex = pointIcosMap.begin();

  Eigen::Matrix4f lastCameraPose = Eigen::Matrix4f::Identity();

public:
  IcosahedronBackend() = default;

  void addObservation(Eigen::Matrix4f cameraPose, std::vector<Point *> seen, std::vector<Point *> notSeen) override
  {
    lastCameraPose = cameraPose;
    for (auto *point : seen)
    {
      successfulObservation(cameraPose, point);
    }
    for (auto *point : notSeen)
    {
      failedObservation(cameraPose, point);
    }
  }

  void showState() override;

  void show2DView(std::string name, Icosahedron *selectedIcos, int currentFace, bool isPointInView, bool isPointVisible) const;
};
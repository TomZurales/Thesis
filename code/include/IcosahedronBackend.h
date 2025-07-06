#pragma once

#include <vector>
#include <map>
#include <eigen3/Eigen/Core>
#include <iostream>

#include "imgui.h"

#include "PPEBackend.h"
#include "Point.h"
#include "Icosahedron.h"
#include "Utility.h"

class IcosahedronBackend : public PPEBackend
{
private:
  std::map<Point *, Icosahedron *> pointIcosMap = std::map<Point *, Icosahedron *>();

  // Visualization parameters
  std::map<Point *, Icosahedron *>::iterator pointIcosMapIndex = pointIcosMap.begin();

public:
  IcosahedronBackend() = default;

  void _addFailedObservation(Point *point) override;
  void _addSuccessfulObservation(Point *point) override;

  void showState() override;

  Point *getActivePoint() const override;

  void show2DView(std::string name, Icosahedron *selectedIcos, int currentFace, bool isPointInView, bool isPointVisible) const;
  Icosahedron *getActiveIcosahedron() const;
};
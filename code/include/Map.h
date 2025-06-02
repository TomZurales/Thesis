#pragma once

#include <vector>

#include "Point.h"

class Map
{
  std::vector<Point *> mapPoints;

public:
  void addMapPoint(Point *point) { mapPoints.push_back(point); }
};
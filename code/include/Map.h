#pragma once

#include <vector>

#include "Point.h"

class Map
{
  std::vector<Point *> mapPoints;

public:
  void addMapPoint(Point *point) { mapPoints.push_back(point); }
  void addNewMapPoints(std::vector<Point *> points)
  {
    for (auto *point : points)
    {
      bool found = false;
      for (auto *mp : mapPoints)
      {
        if (mp->getId() == point->getId())
        {
          found = true;
          break;
        }
      }
      if (!found)
        mapPoints.push_back(point);
    }
  }
  const std::vector<Point *> &getMapPoints() const { return mapPoints; }
};
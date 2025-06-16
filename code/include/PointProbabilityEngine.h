#pragma once

#include <vector>
#include <map>
#include <iostream>
#include <memory>

#include "IcosMetadata.h"
#include "Point.h"
#include "Camera.h"

class PointProbabilityEngine
{
  std::map<Point *, std::shared_ptr<IcosMetadata>> pointData;

  Camera camera;

public:
  PointProbabilityEngine();

  void Update(Eigen::Matrix4f cameraPose, std::vector<Point *> visiblePoints);
  
  // Getter for points
  const std::map<Point *, std::shared_ptr<IcosMetadata>>& getPointData() const { return pointData; }
};
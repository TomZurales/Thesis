#pragma once

#include <unordered_set>
#include <vector>
#include <pcl/point_cloud.h>
#include <pcl/point_types.h>
#include <pcl/common/common.h>
#include <pcl/filters/frustum_culling.h>
#include "Point.h"
#include "PointXYZID.h"

class Map
{
  std::map<int, Point *> mapPoints;

  pcl::PointCloud<PointXYZID>::Ptr pointCloud;

public:
  Map() : pointCloud(new pcl::PointCloud<PointXYZID>) {}

  void addNewMapPoints(std::vector<Point *> points)
  {
    for (auto *point : points)
    {
      // If point already exists in mapPoints, skip it
      if (mapPoints[point->getId()] != nullptr)
        continue; // Point already exists in the map

      PointXYZID pclPoint;
      pclPoint.x = point->getPose().x();
      pclPoint.y = point->getPose().y();
      pclPoint.z = point->getPose().z();
      pclPoint.id = point->getId();

      pointCloud->points.push_back(pclPoint);
      mapPoints[point->getId()] = point; // Store the pointer to the point in the map
    }
  }

  const std::vector<Point *> &getMapPoints() const
  {
    static std::vector<Point *> points;
    points.clear();
    for (const auto &pair : mapPoints)
    {
      points.push_back(pair.second); // Use the pointer stored in the map
    }
    return points;
  }

  std::vector<Point *> getPointsInCameraView(const Camera &camera)
  {
    pcl::FrustumCulling<PointXYZID> fc;
    fc.setInputCloud(pointCloud);
    fc.setCameraPose(camera.getPose());
    fc.setVerticalFOV(camera.getFov());
    fc.setHorizontalFOV(camera.getFov());
    fc.setNearPlaneDistance(0.1f);
    fc.setFarPlaneDistance(100.0f);

    pcl::PointCloud<PointXYZID> filteredCloud;
    fc.filter(filteredCloud);
    std::vector<Point *> pointsInView;
    for (auto pcl_point : filteredCloud.points)
    {
      pointsInView.push_back(mapPoints[pcl_point.id]);
    }
    return pointsInView;
  }
};
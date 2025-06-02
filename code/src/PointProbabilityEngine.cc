#include "PointProbabilityEngine.h"
#include <eigen3/Eigen/LU>

PointProbabilityEngine::PointProbabilityEngine() : camera(Camera(1920, 1080, 0.2, 0.2))
{
}

void PointProbabilityEngine::Update(Eigen::Matrix4f cameraPose, std::vector<Point *> visiblePoints)
{
  for (auto *point : visiblePoints)
  {
    if (pointData.find(point) == pointData.end())
    {
      pointData[point] = std::make_shared<IcosMetadata>(point);
      std::cout << "Adding new point" << std::endl;
    }
  }

  // Get the camera matrix
  Eigen::Matrix3f camMatrix = camera.getCameraMatrix();

  // Get the camera position from the pose (assuming last column is translation)
  Eigen::Vector3f camPosition = cameraPose.block<3, 1>(0, 3);

  for (const auto &entry : pointData)
  {
    Point *point = entry.first;

    // Get the point position
    Eigen::Vector3f pointPosition = point->getPose();

    // Transform point to camera coordinates
    Eigen::Vector4f pointHomogeneous(pointPosition.x(), pointPosition.y(), pointPosition.z(), 1.0f);
    Eigen::Vector4f pointInCamera = cameraPose.inverse() * pointHomogeneous;

    // Check if point is in front of the camera (z > 0 in camera coordinates)
    bool isInCameraView = pointInCamera.z() > 0;

    // Project to image plane and check if within image bounds
    if (isInCameraView)
    {
      Eigen::Vector3f projected = camMatrix * pointInCamera.head<3>();
      float x = projected.x() / projected.z();
      float y = projected.y() / projected.z();

      if (x < 0 || x >= camera.getWidth() || y < 0 || y >= camera.getHeight())
        isInCameraView = false;
    }

    // Do something if not visible
    if (isInCameraView)
    {
      // This will run for every point which should be in the camera view.
      if (std::find(visiblePoints.begin(), visiblePoints.end(), point) != visiblePoints.end())
      {
        // Points which we expect to see, and do see
        pointData[point]->addSuccessfulObservation(cameraPose, point->getPose());
      }
      else
      {
        // Points which we expect to see, but do not
        pointData[point]->addFailedObservation(cameraPose, point->getPose());
      }
    }
  }
}
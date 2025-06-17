#pragma once

#include <vector>
#include <eigen3/Eigen/Core>
#include <iostream>

#include "Point.h"
#include "Icosahedron.h"

class IcosMetadata
{
private:
  Point *pPoint;
  float pExists = 0.5;
  const float alpha = 0.02;
  std::vector<float> faceWeights = std::vector<float>(20, 0.0f);
  std::vector<float> faceDists = std::vector<float>(20, 1.0f);

  std::vector<Eigen::Vector3f> icosVertices = {
      Eigen::Vector3f(0.0f, 0.0f, 0.0f) // Placeholder vertex, actual vertices will be set later
  };

public:
  Icosahedron icos;

  IcosMetadata(Point *point) : pPoint(point) {};

  float getPexists();
  void offsetProbExists(float offset);
  void setIcosDist(int face, float dist);
  float getIcosDist(int face);

  void addFailedObservation(Eigen::Matrix4f observerPose, Eigen::Vector3f pointPose);
  void addSuccessfulObservation(Eigen::Matrix4f observerPose, Eigen::Vector3f pointPose);
};
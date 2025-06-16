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

  int getClosestIcosFaceIndex(Eigen::Vector3f cameraPose);

  std::vector<Eigen::Vector3f> icosVertices = {
      Eigen::Vector3f(0.0f, 0.0f, 0.0f) // Placeholder vertex, actual vertices will be set later
  };

  std::vector<Eigen::Vector3f> faceCenterVecs = {
      Eigen::Vector3f(-0.57735027, -0.57735027, -0.57735027),
      Eigen::Vector3f(-0.57735027, 0.57735027, -0.57735027),
      Eigen::Vector3f(0.35682209, 0., -0.93417236),
      Eigen::Vector3f(-0.35682209, 0., -0.93417236),
      Eigen::Vector3f(0., -0.93417236, 0.35682209),
      Eigen::Vector3f(0.57735027, -0.57735027, -0.57735027),
      Eigen::Vector3f(0., -0.93417236, -0.35682209),
      Eigen::Vector3f(-0.93417236, 0.35682209, 0.),
      Eigen::Vector3f(-0.93417236, -0.35682209, 0.),
      Eigen::Vector3f(-0.57735027, -0.57735027, 0.57735027),
      Eigen::Vector3f(-0.35682209, 0., 0.93417236),
      Eigen::Vector3f(-0.57735027, 0.57735027, 0.57735027),
      Eigen::Vector3f(0., 0.93417236, 0.35682209),
      Eigen::Vector3f(0., 0.93417236, -0.35682209),
      Eigen::Vector3f(0.57735027, 0.57735027, -0.57735027),
      Eigen::Vector3f(0.93417236, -0.35682209, 0.),
      Eigen::Vector3f(0.35682209, 0., 0.93417236),
      Eigen::Vector3f(0.57735027, -0.57735027, 0.57735027),
      Eigen::Vector3f(0.57735027, 0.57735027, 0.57735027),
      Eigen::Vector3f(0.93417236, 0.35682209, 0.)};

public:
  IcosMetadata(Point *point) : pPoint(point) {};

  float getPexists();
  void offsetProbExists(float offset);
  void setIcosDist(int face, float dist);
  float getIcosDist(int face);

  void addFailedObservation(Eigen::Matrix4f observerPose, Eigen::Vector3f pointPose);
  void addSuccessfulObservation(Eigen::Matrix4f observerPose, Eigen::Vector3f pointPose);
};
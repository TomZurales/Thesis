#pragma once

#include <vector>
#include <map>
#include <iostream>
#include <memory>

#include "IcosahedronBackend.h"
#include "Point.h"
#include "Camera.h"
#include "Map.h"
#include "PPEBackend.h"

enum Model
{
  ICOSAHEDRON,
  SPHERE
};

class Viewer; // Forward declaration to avoid circular dependency

class PointProbabilityEngine
{
  Camera camera;
  Model model;
  PPEBackend *backend;
  Map map;
  Viewer *viewer; // Pointer to the viewer, if used

  Eigen::Matrix4f cameraPose; // Current camera pose

  bool useViewer;
  bool shouldClose = false;

  // Visualization Parameters
  bool isPaused = false;
  bool doStep = false;

public:
  PointProbabilityEngine(Camera camera, Model model = ICOSAHEDRON, Map map = Map(), bool useViewer = true);

  void Update(Eigen::Matrix4f cameraPose, std::vector<Point *> visiblePoints);

  Map &getMap() { return map; }

  Eigen::Matrix4f getCameraPose() const { return cameraPose; }

  bool getShouldClose() const { return shouldClose; }

  // Visualization methods
  void showState() const;
  void showControls();
  void showBackendState() const;
  void show3DView() const;
};
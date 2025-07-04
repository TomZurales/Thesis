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
#include "FloorPlane.h"
#include "PointCloud.h"
#include "IcosModel.h"
#include "ShaderManager.h"

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

  bool useViewer;
  bool shouldClose = false;

  // Visualization Parameters
  bool isPaused = false;
  bool doStep = false;

public:
  PointProbabilityEngine(Camera camera, Model model = ICOSAHEDRON, Map map = Map(), bool useViewer = true);

  void Update(Eigen::Matrix4f, std::vector<Point *>);

  Map &getMap() { return map; }

  bool getShouldClose() const { return shouldClose; }

  // Visualization methods
  void showState() const;
  void showControls();
  void showBackendState() const;

  // Stuff related to the 3D View
private:
  uint fbo;
  uint texture;
  GLuint rbo;

  Shader *solidColor3DShader = nullptr;
  Shader *heatmap3DShader = nullptr;

  FloorPlane *floorPlane = nullptr;
  PointCloud *pointCloud = nullptr;
  IcosModel *icosModel = nullptr;

public:
  void init3DView();
  void show3DView() const;
};
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
#include "CameraModel.h"

enum Model
{
  ICOSAHEDRON,
  SPHERE
};

class Viewer; // Forward declaration to avoid circular dependency

class PointProbabilityEngine
{
  Camera *camera;
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
  PointProbabilityEngine() = default;
  PointProbabilityEngine(Camera *camera, Model model = ICOSAHEDRON, Map map = Map(), bool useViewer = true);

  void Update(Eigen::Matrix4f, std::vector<Point *>);

  Map &getMap() { return map; }

  bool getShouldClose() const { return shouldClose; }

  // Visualization methods
  void showState() const;
  void showControls();
  void showBackendState() const;

  // Stuff related to the 3D View
private:
  uint camera_fbo;
  uint camera_texture;
  GLuint camera_rbo;

  uint static_fbo;
  uint static_texture;
  GLuint static_rbo;

  FloorPlane *floorPlane = nullptr;
  PointCloud *pointCloud = nullptr;
  IcosModel *icosModel = nullptr;
  CameraModel *cameraModel = nullptr;

  glm::mat4 staticViewMatrix = glm::lookAt(
      glm::vec3(10.0f, 10.0f, 30.0f), // Static camera position
      glm::vec3(0.0f, 0.0f, 0.0f),    // Look at point
      glm::vec3(0.0f, 1.0f, 0.0f)     // Up vector
  );

public:
  void init3DView();
  void showCameraView() const;
  void showStaticView();
};
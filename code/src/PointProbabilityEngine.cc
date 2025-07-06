#include "PointProbabilityEngine.h"
#include "Viewer.h"

PointProbabilityEngine::PointProbabilityEngine(Camera *camera, Model model, Map map, bool useViewer) : camera(camera), model(model), map(map), useViewer(useViewer)
{
  backend = nullptr;

  switch (model)
  {
  case ICOSAHEDRON:
    backend = new IcosahedronBackend();
    break;

  case SPHERE:
    // Initialize for Sphere model
    break;

  default:
    std::cerr << "Unknown model type!" << std::endl;
    exit(EXIT_FAILURE);
  }

  if (useViewer)
  {
    std::cout << "Visualizer enabled." << std::endl;
    viewer = new Viewer(this);
    init3DView(); // Initialize the 3D view if the viewer is used
  }
}

void PointProbabilityEngine::Update(Eigen::Matrix4f observationPose, std::vector<Point *> visiblePoints)
{
  if (!isPaused || doStep)
  {
    // Update the camera pose
    camera->setPose(observationPose);

    // If a point is not in the map, add it
    map.addNewMapPoints(visiblePoints);

    // Get the camera matrix
    Eigen::Matrix3f camMatrix = camera->getCameraMatrix();

    // Get the camera position from the pose (assuming last column is translation)
    Eigen::Vector3f camPosition = camera->getPose().block<3, 1>(0, 3);

    // Determine which points are in the camera's view frustum
    // TODO: This is broken, pushing all points as in view for now
    // Ideally, we would check if the point is within the camera's field of view
    std::vector<Point *> pointsInView;
    for (auto *point : map.getMapPoints())
    {
      point->setInView(false);
      point->setVisible(false);
      Eigen::Vector3f pointPos = point->getPose();
      Eigen::Vector3f dirToPoint = pointPos - camPosition;
      float distance = dirToPoint.norm();
      dirToPoint.normalize();
      Eigen::Vector3f camForward = camera->getPose().block<3, 1>(0, 2); // Assuming Z-forward
      float angle = std::acos(camForward.dot(dirToPoint));
      // if (angle < camera.getFov() / 2)
      // {
      pointsInView.push_back(point);
      // }
    }
    // Separate visible points into seen and not seen
    std::vector<Point *> seenPoints;
    std::vector<Point *> notSeenPoints;

    backend->beginObservation(camera->getPose());
    for (auto *point : pointsInView)
    {
      point->setInView(true);
      if (std::find(visiblePoints.begin(), visiblePoints.end(), point) != visiblePoints.end())
      {
        point->setVisible(true);
        backend->addSuccessfulObservation(point);
      }
      else
      {
        point->setVisible(false);
        backend->addFailedObservation(point);
      }
    }
    backend->endObservation();
    // // Call the backend to update probabilities
    // backend->addObservation(camera->getPose(), seenPoints, notSeenPoints);
  }

  // If a viewer is used, update it with the current state
  if (useViewer)
  {
    viewer->update();
    viewer->render();
    if (viewer->getShouldClose())
    {
      delete viewer;
      viewer = nullptr;
      useViewer = false;
      std::cout << "Visualizer closed." << std::endl;

      // Shut down the engine
      shouldClose = true;
    }
  }
}

void PointProbabilityEngine::showState() const
{
  ImGui::Begin("Point Probability Engine State");

  ImGui::Text("# Map Points: %zu    ", map.getMapPoints().size());
  ImGui::SameLine();
  ImGui::Text("Camera Pose: (%.2f, %.2f, %.2f)", camera->getPose()(0, 3), camera->getPose()(1, 3), camera->getPose()(2, 3));
  ImGui::End();
}

void PointProbabilityEngine::showControls()
{
  ImGui::Begin("Controls");

  ImGui::Checkbox("Pause", &isPaused);
  if (isPaused)
    doStep = ImGui::Button("Step");
  else
    doStep = false;

  ImGui::End();
}

void PointProbabilityEngine::showBackendState() const
{
  backend->showState(); // Assuming the backend has a method to show its state
}
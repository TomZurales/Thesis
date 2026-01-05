#include "camera.h"
#include "observability_scenario.h"
#include <Eigen/src/Core/Matrix.h>
#include <pangolin/pangolin.h>
#include <GL/gl.h>
#include <chrono>
#include <cmath>

VBEESettings global_vbee_settings;

const std::string SCENARIOS_FILE = "data/scenarios.bin";

int main(int argc, char **argv) {
  chdir("/home/tom/workspace/Thesis/analysis");

  std::vector<ObservabilityScenario> scenarios =
      ObservabilityScenario::LoadOrCreate(SCENARIOS_FILE, 10, 0.05f);

  std::vector<Eigen::Vector3f> poses(scenarios.size());

  // Distribute all scenarios randomly in a 10x10 area
  for (size_t i = 0; i < poses.size(); i++) {
    poses[i] =
        Eigen::Vector3f(-5.0f + static_cast<float>(rand()) /
                                    static_cast<float>(RAND_MAX) * 10.0f,
                        -5.0f + static_cast<float>(rand()) /
                                    static_cast<float>(RAND_MAX) * 10.0f,
                        -5.0f + static_cast<float>(rand()) /
                                    static_cast<float>(RAND_MAX) * 10.0f);
  }

  // Initialize Pangolin
  pangolin::CreateWindowAndBind("VBEE Visualizer", 1024, 768);

  Camera camera(Eigen::Vector3f(0, 0, -5), Eigen::Vector3f(0, 0, -20));

  // Enable depth testing
  glEnable(GL_DEPTH_TEST);

  // Define Camera Render Object (for view / scene browsing)
  pangolin::OpenGlRenderState s_cam(
      pangolin::ProjectionMatrix(1024, 768, 500, 500, 512, 389, 0.1, 1000),
      pangolin::ModelViewLookAt(-10, 2, -30, 0, 0, 0, pangolin::AxisY));

  // Add named OpenGL viewport to window and provide 3D Handler
  pangolin::View &d_cam = pangolin::CreateDisplay()
                              .SetBounds(0.0, 1.0, pangolin::Attach::Pix(175),
                                         1.0, -1024.0f / 768.0f)
                              .SetHandler(new pangolin::Handler3D(s_cam));

  // Create Panel
  pangolin::CreatePanel("menu").SetBounds(0.0, 1.0, 0.0,
                                          pangolin::Attach::Pix(175));

  // Add some variables to the panel
  pangolin::Var<bool> menu_show_scenarios("menu.Show Scenarios", true, true);
  pangolin::Var<bool> menu_show_poses("menu.Show Poses", true, true);
  pangolin::Var<float> menu_point_size("menu.Point Size", 3.0, 1.0, 10.0);

  std::cout << "Starting Pangolin visualization loop..." << std::endl;
  std::cout << "Loaded " << scenarios.size() << " scenarios." << std::endl;

  // Camera motion variables
  auto start_time = std::chrono::high_resolution_clock::now();
  float motion_speed = 0.5f;  // Units per second
  float rotation_speed = 0.3f;  // Radians per second
  
  // Random motion parameters - different frequencies for each axis
  float freq_x1 = 0.7f, freq_x2 = 1.3f, freq_x3 = 2.1f;
  float freq_y1 = 0.9f, freq_y2 = 1.7f, freq_y3 = 2.5f;
  float freq_z1 = 1.1f, freq_z2 = 1.9f, freq_z3 = 2.3f;
  
  // Amplitude scaling
  float amplitude = 4.5f;  // Max distance from center (within ±5.0 bounds)

  // Main rendering loop
  while (!pangolin::ShouldQuit()) {
    // Calculate time for smooth motion
    auto current_time = std::chrono::high_resolution_clock::now();
    float elapsed = std::chrono::duration<float>(current_time - start_time).count();
    
    // Complete random motion using multiple overlapping sine waves
    Eigen::Vector3f new_position;
    new_position.x() = amplitude * (
        0.4f * std::sin(elapsed * freq_x1) + 
        0.3f * std::cos(elapsed * freq_x2) + 
        0.3f * std::sin(elapsed * freq_x3 + 1.5f)
    );
    new_position.y() = amplitude * (
        0.4f * std::cos(elapsed * freq_y1 + 0.5f) + 
        0.3f * std::sin(elapsed * freq_y2 + 2.0f) + 
        0.3f * std::cos(elapsed * freq_y3 + 3.0f)
    );
    new_position.z() = amplitude * (
        0.4f * std::sin(elapsed * freq_z1 + 1.0f) + 
        0.3f * std::cos(elapsed * freq_z2 + 2.5f) + 
        0.3f * std::sin(elapsed * freq_z3 + 4.0f)
    );
    
    // Clamp position to ±5.0 bounds
    new_position.x() = std::max(-5.0f, std::min(5.0f, new_position.x()));
    new_position.y() = std::max(-5.0f, std::min(5.0f, new_position.y()));
    new_position.z() = std::max(-5.0f, std::min(5.0f, new_position.z()));
    
    // Random rotation components
    float yaw = 0.8f * std::sin(elapsed * 0.6f) + 0.4f * std::cos(elapsed * 1.4f);
    float pitch = 0.5f * std::cos(elapsed * 0.8f) + 0.3f * std::sin(elapsed * 1.8f);
    float roll = 0.3f * std::sin(elapsed * 1.2f) + 0.2f * std::cos(elapsed * 2.2f);
    
    // Random look target that moves independently
    Eigen::Vector3f look_target;
    look_target.x() = 3.0f * std::sin(elapsed * 0.5f + 1.0f);
    look_target.y() = 2.0f * std::cos(elapsed * 0.7f + 2.0f);
    look_target.z() = 2.5f * std::sin(elapsed * 0.9f + 3.0f);
    
    camera.setPosition(new_position);
    camera.lookAt(look_target);
    
    // Apply additional random rotation using all three axes
    Eigen::AngleAxisf yaw_rotation(yaw, Eigen::Vector3f::UnitY());
    Eigen::AngleAxisf pitch_rotation(pitch, Eigen::Vector3f::UnitX());
    Eigen::AngleAxisf roll_rotation(roll, Eigen::Vector3f::UnitZ());
    Eigen::Quaternionf additional_rot = yaw_rotation * pitch_rotation * roll_rotation;
    camera.setOrientation(camera.getOrientation() * additional_rot);
    
    // Clear screen and activate view to render into
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);
    d_cam.Activate(s_cam);

    // Draw coordinate axes
    glLineWidth(2);
    pangolin::glDrawAxis(3.0f);

    if (menu_show_scenarios) {
      // Draw scenario positions (you can extend this based on scenario data)
      glPointSize(menu_point_size * 0.5f);

      for (size_t i = 0; i < scenarios.size(); i++) {
        glColor3f(1.0f, 0.0f, 0.0f); // Red points
        if(camera.isPointVisible(poses[i]))
        {
            glColor3f(0.0f, 1.0f, 0.0f); // Green if visible
        }
        glBegin(GL_POINTS);
        // For now, just draw at the pose locations
        // You can modify this to draw actual scenario-specific data
        glVertex3f(poses[i].x(), poses[i].y(), poses[i].z());
        glEnd();
      }
    }

    camera.draw();

    // Swap frames and Process Events
    pangolin::FinishFrame();
  }

  return 0;
}
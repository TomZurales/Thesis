#pragma once

#include "JoystickManager.h"

#include <iostream>
#include <gz/sim9/gz/sim.hh>
#include <gz/plugin3/gz/plugin.hh>
#include <gz/plugin3/gz/plugin/Register.hh>
#include <gz/math8/gz/math.hh>
#include <gz/sdformat15/sdformat.hh> 
#include <fcntl.h>
#include <unistd.h>
#include <vector>
#include <fstream>
#include <memory>
#include <iomanip>

#define map_range(value, in_min, in_max, out_min, out_max) \
  ((value - in_min) * (out_max - out_min) / (in_max - in_min) + out_min)

#define signof(x) (x >= 0 ? 1 : -1)

#define min(x, y) ((x) < (y) ? (x) : (y))
 
namespace dataset_generation
{
  class ObserverRobotController: public gz::sim::System, public gz::sim::ISystemConfigure, public gz::sim::ISystemPreUpdate, public gz::sim::ISystemPostUpdate
  {
  private:
    int joystick_fd = -1;

    std::unique_ptr<JoystickManager> jm;

    float ax, ay, twz = 0;
    float az = -9.81;

    float vx, vy, wz = 0;

    float max_accel = 0.001;

    gz::sim::Joint z_slider_joint;
    double z_slider_joint_min;
    double z_slider_joint_max;
    const double z_slider_joint_force = 5.0;
    const double z_slider_joint_deadzone = 0.1;

    // hasInput = true if usable joystick input was detected the last time ReadJoystick was called
    // This is used to determine if the forces should be recorded at the current step
    bool hasInput = false;

    bool startCounting = false;

    // The current step of the simulation. This is used for recording forces to a file
    uint64_t step = 0;

    std::ofstream controlFile;

  public: 
    ObserverRobotController();
    ~ObserverRobotController() override;

    void Configure(const gz::sim::Entity &_entity, const std::shared_ptr<const sdf::Element> &_sdf,
        gz::sim::EntityComponentManager &_ecm, gz::sim::EventManager &_eventManager) override;
    
    void PreUpdate(const gz::sim::UpdateInfo &_info,
        gz::sim::EntityComponentManager &_ecm) override;

    void PostUpdate(const gz::sim::UpdateInfo &_info,
          const gz::sim::EntityComponentManager &_ecm) override;

    // void Reset(const gz::sim::UpdateInfo &_info,
    //     const gz::sim::EntityComponentManager &_ecm) override;
  };
}

GZ_ADD_PLUGIN(
  dataset_generation::ObserverRobotController,
  gz::sim::System,
  dataset_generation::ObserverRobotController::ISystemConfigure,
  dataset_generation::ObserverRobotController::ISystemPreUpdate,
  dataset_generation::ObserverRobotController::ISystemPostUpdate);
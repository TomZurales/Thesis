#include "ObserverRobotController.h"

using namespace dataset_generation;

ObserverRobotController::ObserverRobotController()
{
    jm = std::unique_ptr<JoystickManager>(new JoystickManager());
}

ObserverRobotController::~ObserverRobotController()
{
    if (joystick_fd >= 0)
        close(joystick_fd);

    std::cout << "[ObserverRobotController] Closing control file..." << std::endl;
    jm->~JoystickManager();
    controlFile.close();
}

void ObserverRobotController::Configure(const gz::sim::Entity &_entity, const std::shared_ptr<const sdf::Element> &_sdf,
                                        gz::sim::EntityComponentManager &_ecm, gz::sim::EventManager &_eventManager)
{
    std::cout << "[ObserverRobotController] Initializing..." << std::fixed << std::setprecision(3) << std::endl;
    try
    {
        z_slider_joint = gz::sim::Joint(_ecm.EntityByName("z_slider_joint").value());
        z_slider_joint.EnablePositionCheck(_ecm, true);
        z_slider_joint_min = z_slider_joint.Axis(_ecm).value()[0].Upper();
        z_slider_joint_max = z_slider_joint.Axis(_ecm).value()[0].Lower();
        if (z_slider_joint_min > z_slider_joint_max)
        {
            auto tmp = z_slider_joint_min;
            z_slider_joint_min = z_slider_joint_max;
            z_slider_joint_max = tmp;
        }
        z_slider_joint_min = z_slider_joint_min + 1;
        z_slider_joint_max = z_slider_joint_max - 1;
        std::cout << "[ObserverRobotController] z_slider_joint_min: " << z_slider_joint_min << std::endl;
        std::cout << "[ObserverRobotController] z_slider_joint_max: " << z_slider_joint_max << std::endl;
    }
    catch (const std::exception &e)
    {
        std::cerr << "[ObserverRobotController] Setup Failed, verify observer model is loaded.\nError: " << e.what() << std::endl;
        return;
    }

    std::string outputFilePath = "/tmp/forces.txt";
    controlFile.open(outputFilePath, std::ios::out | std::ios::trunc);
    if (!controlFile.is_open())
    {
        std::cerr << "[ObserverRobotController] Failed to open output file " << outputFilePath << std::endl;
        exit(1);
    }
    std::cout << "[ObserverRobotController] Opening output file " << outputFilePath << std::endl;
    std::cout << "[ObserverRobotController] Done Initializing" << std::endl;

    // sdf::SDFPtr loadedSDF(new sdf::SDF());
    // sdf::init(loadedSDF);
    // if (!sdf::readFile("/home/tom/workspace/thesis/dataset_generation/world_1/warehouse.sdf", loadedSDF))
    // {
    //   std::cerr << " is not a valid SDF file!" << std::endl;
    // }
    // gz::sim::SdfEntityCreator creator(_ecm, _eventManager);
    // sdf::Model model;
    // // sdf::World world;
    // model.Load(loadedSDF->Root()->GetElement("model"));
    // creator.CreateEntities(&model);
}

void ObserverRobotController::PreUpdate(const gz::sim::UpdateInfo &_info,
                                        gz::sim::EntityComponentManager &_ecm)
{
    if (_info.paused)
        return;

    JoystickData jd = jm->readJoystick();

    // Set z_slider_joint force based on setpoint
    double z_slider_joint_setpoint = map_range(jd.lv, -1.0, 1.0, z_slider_joint_min, z_slider_joint_max);
    double z_slider_joint_position = z_slider_joint.Position(_ecm).value()[0];

    if (abs(z_slider_joint_setpoint - z_slider_joint_position) > z_slider_joint_deadzone)
    {
        z_slider_joint.SetForce(_ecm, {z_slider_joint_force * min(z_slider_joint_setpoint - z_slider_joint_position, 1)});
    }

    auto box_entity = _ecm.EntityByName("observer_link");
    auto camera_entity = _ecm.EntityByName("observer_camera_joint");
    if (camera_entity.has_value())
    {
        auto joint = gz::sim::v9::Joint(camera_entity.value());
        joint.EnablePositionCheck(_ecm, true);
        // joint.ResetPosition(_ecm, {axes[0] * -0.5});
    }
    if (box_entity.has_value())
    {
        auto link = gz::sim::v9::Link(box_entity.value());
        auto body = gz::sim::v9::Model(link.ParentModel(_ecm).value());

        // Get the link's rotation about the z axis
        auto pose = link.WorldPose(_ecm).value();
        auto body_rotation = pose.Rot().Yaw();

        auto body_force_vec = gz::math::v8::Vector3d(jd.rv * 6, -jd.lh * 6, 0.0);
        auto world_force_vec = gz::math::v8::Vector3d(
            body_force_vec.X() * cos(body_rotation) - body_force_vec.Y() * sin(body_rotation),
            body_force_vec.X() * sin(body_rotation) + body_force_vec.Y() * cos(body_rotation),
            0.0);
        // link.SetLinearVelocity(_ecm, gz::math::v7::Vector3d(axes[2], -axes[1], 0.0));
        link.AddWorldWrench(_ecm, world_force_vec, gz::math::v8::Vector3d(0.0, 0.0, -jd.rh * 5));
        // // link.SetAngularVelocity(_ecm, gz::math::v7::Vector3d(0.0, 0.0, -axes[3]));
        // link.EnableVelocityChecks(_ecm, true);
        // // Get the current linear and angular velocities
        // if(link.WorldLinearVelocity(_ecm).has_value())
        // {
        // auto vel = link.WorldLinearVelocity(_ecm).value();
        // auto ang_vel = link.WorldAngularVelocity(_ecm).value();

        // // Add in some air resistance
        // // There should always be some force acting against the direction of motion proportional to the velocity
        // link.AddWorldWrench(_ecm, gz::math::v7::Vector3d(vel.X() * -3, vel.Y() * -3, 0), gz::math::v7::Vector3d(0.0, 0.0, ang_vel.Z() * -3));
        // }
    }

    if (startCounting)
    {
        step++;
        // if(hasInput)
        // controlFile << std::fixed << std::setprecision(3) << step << " " << axes[0] << " " << axes[1] << " " << axes[2] << " " << axes[3] << std::endl;
    }
}

void ObserverRobotController::PostUpdate(const gz::sim::UpdateInfo &_info,
                                         const gz::sim::EntityComponentManager &_ecm)
{
    // if(_info.paused)
    //     return;

    // auto box_entity = _ecm.EntityByName("observer_link");
    // if(box_entity.has_value())
    // {
    //     auto link = gz::sim::v8::Link(box_entity.value());
    //     auto body = gz::sim::v8::Model(link.ParentModel(_ecm).value());
    //     link.SetLinearVelocity(_ecm, gz::math::v7::Vector3d(0.0, 0.0, 0.0));
    //     body.SetWorldPoseCmd(_ecm, gz::math::v7::Pose3d(link.WorldPose().value().Coor, gz::math::v7::Quaterniond(0.0, 0.0, 0.0, 1.0)));
    // }
}

// void ObserverRobotController::Reset(const gz::sim::UpdateInfo &_info,
//                                     gz::sim::EntityComponentManager &_ecm)
// {
//     std::cout << "[ObserverRobotController] Closing control file..." << std::endl;
//     controlFile.close();
// }
// // TODO: Create a UI element with a file selector and a record button

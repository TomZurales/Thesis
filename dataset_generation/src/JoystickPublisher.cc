#include <gz/sim/System.hh>
#include <gz/transport/Node.hh>
#include <gz/msgs/joystick.pb.h>
#include <gz/plugin/Register.hh>

#include <linux/joystick.h>
#include <fcntl.h>
#include <unistd.h>
#include <thread>
#include <vector>
#include <iostream>

using namespace gz;
using namespace sim;



class JoystickPlugin : public System, public ISystemConfigure
{
public:
    void Configure(const Entity &, const std::shared_ptr<const sdf::Element> &,
                   EntityComponentManager &, EventManager &) override
    {
        std::cout << "[JoystickPlugin] Initializing..." << std::endl;
        
        // Open joystick device
        joystick_fd = open("/dev/input/js0", O_RDONLY | O_NONBLOCK);
        if (joystick_fd < 0)
        {
            std::cerr << "[JoystickPlugin] Failed to open /dev/input/js0" << std::endl;
            return;
        }

        // Start joystick reading thread
        running = true;
        joystickThread = std::thread(&JoystickPlugin::ReadJoystick, this);
    }

    ~JoystickPlugin()
    {
        running = false;
        if (joystickThread.joinable())
            joystickThread.join();
        
        if (joystick_fd >= 0)
            close(joystick_fd);
    }

private:
    transport::Node node;
    int joystick_fd = -1;
    std::thread joystickThread;
    bool running = false;

    void ReadJoystick()
    {
        struct js_event js;
        std::vector<float> axes(6, 0.0f);  // Assuming max 6 axes
        std::vector<int> buttons(12, 0);   // Assuming max 12 buttons

        while (running)
        {
            ssize_t bytes = read(joystick_fd, &js, sizeof(js_event));
            if (bytes > 0)
            {
                // Parse event
                switch (js.type & ~JS_EVENT_INIT)
                {
                case JS_EVENT_AXIS:
                    if (js.number < axes.size())
                        axes[js.number] = js.value / 32767.0f; // Normalize to -1.0 to 1.0
                    break;
                case JS_EVENT_BUTTON:
                    if (js.number < buttons.size())
                        buttons[js.number] = js.value;
                    break;
                }

                // Publish joystick message
                msgs::Joystick msg;
                for (float axis : axes)
                    std::cout << axis << " ";
                for (int button : buttons)
                    msg.add_buttons(button);
                
                node.Request("/joystick", msg);
            }
            std::this_thread::sleep_for(std::chrono::milliseconds(10));
        }
    }
};

GZ_ADD_PLUGIN(
    JoystickPlugin,
    gz::sim::System,
    JoystickPlugin::ISystemConfigure);
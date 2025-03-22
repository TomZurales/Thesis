#pragma once

struct JoystickData
{
    float lh = 0;
    float lv = 0;
    float rh = 0;
    float rv = 0;

    std::string toString()
    {
        std::cout << "lh: " << lh << ", " << "lv: " << lv  << "rh: " << rh << ", " << "rv: " << rv << std::endl;
    }
};

class JoystickManager
{
private:
    int joystick_fd = -1;
    bool connected = false;

public:
    JoystickManager();
    ~JoystickManager();

    JoystickData readJoystick();
};
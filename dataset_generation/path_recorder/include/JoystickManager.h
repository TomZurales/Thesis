#pragma once

#include <sstream>
#include <stdio_ext.h>

struct JoystickData
{
    float lh = 0;
    float lv = 0;
    float rh = 0;
    float rv = 0;

    std::string toString()
    {
        std::stringstream ss;
        ss << "lh: " << lh << ", lv: " << lv << ", rh: " << rh << ", rv: " << rv;
        return ss.str();
    }
};

class JoystickManager
{
private:
    int joystick_fd = -1;
    bool connected = false;
    struct JoystickData data;

public:
    JoystickManager();
    ~JoystickManager();

    JoystickData readJoystick();
};
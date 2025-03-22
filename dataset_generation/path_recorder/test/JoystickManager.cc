#include "JoystickManager.h"

#include <iostream>
#include <thread>

int main(int argc, char** argv)
{
    std::cout << "Testing Joystick Manager" << std::endl;

    std::cout << "Calling Constructor" << std::endl;
    JoystickManager jm;
    
    std::cout << "Starting Read Loop" << std::endl;
    while(true)
    {
        JoystickData jd = jm.readJoystick();

        std::cout << jd.toString() << std::endl;
        std::this_thread::sleep_for(std::chrono::milliseconds(1));
    }
    return 0;

}
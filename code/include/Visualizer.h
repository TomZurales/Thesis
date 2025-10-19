#pragma once

#define GLFW_INCLUDE_NONE
#include <GLFW/glfw3.h>
#include <glad/glad.h>
#include <memory>
#include <Eigen/Core>
#include <Eigen/Geometry>
#include <Eigen/Dense>

class Visualizer {
public:
    Visualizer(int width = 800, int height = 600, const char* title = "Visualizer");
    ~Visualizer();

    // Delete copy constructor and assignment operator
    Visualizer(const Visualizer&) = delete;
    Visualizer& operator=(const Visualizer&) = delete;

    bool shouldClose() const;
    void pollEvents();
    void swapBuffers();
    void render();

    // Camera control
    void setCameraPosition(const Eigen::Vector3f& position);
    void setCameraTarget(const Eigen::Vector3f& target);
    void setCameraUp(const Eigen::Vector3f& up);
    void setFOV(float fov);
    void setAspectRatio(float aspect);

private:
    void initializeShaders();
    void initializeAxisLines();
    void renderAxisLines();

    GLFWwindow* window_;
    int width_;
    int height_;

    // Camera parameters
    Eigen::Vector3f camera_position_{5.0f, 0.0f, 0.0f};
    Eigen::Vector3f camera_target_{0.0f, 0.0f, 0.0f};
    Eigen::Vector3f camera_up_{0.0f, 0.0f, 1.0f};
    float fov_{45.0f};
    float aspect_ratio_{1.0f};
    float near_plane_{0.1f};
    float far_plane_{100.0f};

    // Shader program
    GLuint shader_program_;
    
    // Axis lines
    GLuint axis_vao_;
    GLuint axis_vbo_;
    GLuint axis_ebo_;
}; 
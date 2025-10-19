#include "Visualizer.h"
#include <stdexcept>
#include <iostream>
#include <fstream>
#include <sstream>
#include <string>
#include <filesystem>

// Helper function to read shader file
std::string readShaderFile(const char* filePath) {
    std::ifstream shaderFile;
    std::stringstream shaderStream;
    
    shaderFile.exceptions(std::ifstream::failbit | std::ifstream::badbit);
    try {
        shaderFile.open(filePath);
        shaderStream << shaderFile.rdbuf();
        shaderFile.close();
        std::cout << "Successfully loaded shader: " << filePath << std::endl;
        return shaderStream.str();
    }
    catch(std::ifstream::failure& e) {
        std::cerr << "Failed to read shader file: " << filePath << std::endl;
        std::cerr << "Current working directory: " << std::filesystem::current_path() << std::endl;
        throw std::runtime_error("Failed to read shader file: " + std::string(filePath));
    }
}

// Helper function to compile shader
GLuint compileShader(GLenum type, const char* source) {
    GLuint shader = glCreateShader(type);
    glShaderSource(shader, 1, &source, nullptr);
    glCompileShader(shader);

    // Check for compilation errors
    GLint success;
    GLchar infoLog[512];
    glGetShaderiv(shader, GL_COMPILE_STATUS, &success);
    if (!success) {
        glGetShaderInfoLog(shader, 512, nullptr, infoLog);
        throw std::runtime_error("Shader compilation failed: " + std::string(infoLog));
    }
    return shader;
}

Visualizer::Visualizer(int width, int height, const char* title)
    : width_(width), height_(height), aspect_ratio_(static_cast<float>(width) / height) {
    
    // Initialize GLFW
    if (!glfwInit()) {
        throw std::runtime_error("Failed to initialize GLFW");
    }

    // Configure GLFW
    glfwWindowHint(GLFW_CONTEXT_VERSION_MAJOR, 3);
    glfwWindowHint(GLFW_CONTEXT_VERSION_MINOR, 3);
    glfwWindowHint(GLFW_OPENGL_PROFILE, GLFW_OPENGL_CORE_PROFILE);

    // Create window
    window_ = glfwCreateWindow(width, height, title, nullptr, nullptr);
    if (!window_) {
        std::cout << "Failed to create GLFW window" << std::endl;
        std::cout << "GLFW version: " << glfwGetVersionString() << std::endl;
        std::cout << "GLFW error: " << glfwGetError(nullptr) << std::endl;
        std::cout << "GLFW error code: " << glfwGetError(nullptr) << std::endl;
        glfwTerminate();
    }

    // Make the window's context current
    glfwMakeContextCurrent(window_);

    // Initialize GLAD
    if (!gladLoadGLLoader((GLADloadproc)glfwGetProcAddress)) {
        glfwDestroyWindow(window_);
        glfwTerminate();
        throw std::runtime_error("Failed to initialize GLAD");
    }

    // Enable depth testing
    glEnable(GL_DEPTH_TEST);
    
    // Set grey background color
    glClearColor(0.2f, 0.2f, 0.2f, 1.0f);

    // Initialize shaders and axis lines
    initializeShaders();
    initializeAxisLines();
}

void Visualizer::initializeShaders() {
    // Read and compile shaders
    std::string vertexCode = readShaderFile("shaders/axis.vert");
    std::string fragmentCode = readShaderFile("shaders/axis.frag");
    
    GLuint vertexShader = compileShader(GL_VERTEX_SHADER, vertexCode.c_str());
    GLuint fragmentShader = compileShader(GL_FRAGMENT_SHADER, fragmentCode.c_str());

    // Create shader program
    shader_program_ = glCreateProgram();
    glAttachShader(shader_program_, vertexShader);
    glAttachShader(shader_program_, fragmentShader);
    glLinkProgram(shader_program_);

    // Check for linking errors
    GLint success;
    GLchar infoLog[512];
    glGetProgramiv(shader_program_, GL_LINK_STATUS, &success);
    if (!success) {
        glGetProgramInfoLog(shader_program_, 512, nullptr, infoLog);
        throw std::runtime_error("Shader program linking failed: " + std::string(infoLog));
    }

    // Delete shaders as they're linked into our program now and no longer necessary
    glDeleteShader(vertexShader);
    glDeleteShader(fragmentShader);
}

void Visualizer::initializeAxisLines() {
    // Axis line vertices (position and color)
    float vertices[] = {
        // positions        // colors
        0.0f, 0.0f, 0.0f,   1.0f, 0.0f, 0.0f,  // x-axis start (red)
        2.0f, 0.0f, 0.0f,   1.0f, 0.0f, 0.0f,  // x-axis end
        0.0f, 0.0f, 0.0f,   0.0f, 1.0f, 0.0f,  // y-axis start (green)
        0.0f, 2.0f, 0.0f,   0.0f, 1.0f, 0.0f,  // y-axis end
        0.0f, 0.0f, 0.0f,   0.0f, 0.0f, 1.0f,  // z-axis start (blue)
        0.0f, 0.0f, 2.0f,   0.0f, 0.0f, 1.0f   // z-axis end
    };

    // Create and bind VAO
    glGenVertexArrays(1, &axis_vao_);
    glGenBuffers(1, &axis_vbo_);
    
    glBindVertexArray(axis_vao_);
    glBindBuffer(GL_ARRAY_BUFFER, axis_vbo_);
    glBufferData(GL_ARRAY_BUFFER, sizeof(vertices), vertices, GL_STATIC_DRAW);

    // Position attribute
    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 6 * sizeof(float), (void*)0);
    glEnableVertexAttribArray(0);
    // Color attribute
    glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 6 * sizeof(float), (void*)(3 * sizeof(float)));
    glEnableVertexAttribArray(1);

    glBindBuffer(GL_ARRAY_BUFFER, 0);
    glBindVertexArray(0);
}

void Visualizer::renderAxisLines() {
    glUseProgram(shader_program_);

    // Calculate view and projection matrices
    Eigen::Matrix4f view = Eigen::Matrix4f::Identity();
    Eigen::Vector3f f = (camera_target_ - camera_position_).normalized();
    Eigen::Vector3f s = f.cross(camera_up_).normalized();
    Eigen::Vector3f u = s.cross(f);
    
    view.block<3,1>(0,0) = s;
    view.block<3,1>(0,1) = u;
    view.block<3,1>(0,2) = -f;
    view.block<3,1>(0,3) = -camera_position_;

    // Calculate perspective projection matrix
    float tanHalfFov = std::tan(fov_ * 0.5f * M_PI / 180.0f);
    Eigen::Matrix4f projection = Eigen::Matrix4f::Zero();
    projection(0,0) = 1.0f / (aspect_ratio_ * tanHalfFov);
    projection(1,1) = 1.0f / tanHalfFov;
    projection(2,2) = -(far_plane_ + near_plane_) / (far_plane_ - near_plane_);
    projection(2,3) = -1.0f;
    projection(3,2) = -(2.0f * far_plane_ * near_plane_) / (far_plane_ - near_plane_);

    Eigen::Matrix4f model = Eigen::Matrix4f::Identity();

    // Set uniforms
    GLint modelLoc = glGetUniformLocation(shader_program_, "model");
    GLint viewLoc = glGetUniformLocation(shader_program_, "view");
    GLint projLoc = glGetUniformLocation(shader_program_, "projection");

    if (modelLoc == -1 || viewLoc == -1 || projLoc == -1) {
        std::cerr << "Failed to get uniform locations" << std::endl;
        return;
    }

    glUniformMatrix4fv(modelLoc, 1, GL_FALSE, model.data());
    glUniformMatrix4fv(viewLoc, 1, GL_FALSE, view.data());
    glUniformMatrix4fv(projLoc, 1, GL_FALSE, projection.data());

    // Draw axis lines
    glBindVertexArray(axis_vao_);
    glDrawArrays(GL_LINES, 0, 6);
    glBindVertexArray(0);
}

void Visualizer::render() {
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);
    renderAxisLines();
}

void Visualizer::setCameraPosition(const Eigen::Vector3f& position) {
    camera_position_ = position;
}

void Visualizer::setCameraTarget(const Eigen::Vector3f& target) {
    camera_target_ = target;
}

void Visualizer::setCameraUp(const Eigen::Vector3f& up) {
    camera_up_ = up;
}

void Visualizer::setFOV(float fov) {
    fov_ = fov;
}

void Visualizer::setAspectRatio(float aspect) {
    aspect_ratio_ = aspect;
}

Visualizer::~Visualizer() {
    glDeleteVertexArrays(1, &axis_vao_);
    glDeleteBuffers(1, &axis_vbo_);
    glDeleteProgram(shader_program_);
    
    if (window_) {
        glfwDestroyWindow(window_);
    }
    glfwTerminate();
}

bool Visualizer::shouldClose() const {
    return glfwWindowShouldClose(window_);
}

void Visualizer::pollEvents() {
    glfwPollEvents();
}

void Visualizer::swapBuffers() {
    glfwSwapBuffers(window_);
} 
#include "Visualizer.h"
#include <iostream>
#include <vector>
#include <glm/gtc/type_ptr.hpp>
#include <random>

// Vertex shader for point sprites
const char *pointVertexShaderSource = R"(
    #version 330 core
    layout (location = 0) in vec3 aPos;
    
    uniform mat4 model;
    uniform mat4 view;
    uniform mat4 projection;
    
    void main() {
        gl_Position = projection * view * model * vec4(aPos, 1.0);
        gl_PointSize = 5.0;
    }
)";

// Fragment shader for point sprites
const char *pointFragmentShaderSource = R"(
    #version 330 core
    out vec4 FragColor;
    
    void main() {
        FragColor = vec4(1.0, 1.0, 1.0, 1.0);
    }
)";

// Vertex shader for axes
const char *axisVertexShaderSource = R"(
    #version 330 core
    layout (location = 0) in vec3 aPos;
    layout (location = 1) in vec3 aColor;
    
    uniform mat4 model;
    uniform mat4 view;
    uniform mat4 projection;
    
    out vec3 Color;
    
    void main() {
        gl_Position = projection * view * model * vec4(aPos, 1.0);
        Color = aColor;
    }
)";

// Fragment shader for axes
const char *axisFragmentShaderSource = R"(
    #version 330 core
    in vec3 Color;
    out vec4 FragColor;
    
    void main() {
        FragColor = vec4(Color, 1.0);
    }
)";

// Vertex shader for icosahedron
const char *icosVertexShaderSource = R"(
    #version 330 core
    layout (location = 0) in vec3 aPos;
    layout (location = 1) in vec4 aColor;
    
    uniform mat4 model;
    uniform mat4 view;
    uniform mat4 projection;
    
    out vec4 FragColor;
    
    void main() {
        gl_Position = projection * view * model * vec4(aPos, 1.0);
        FragColor = aColor;
    }
)";

// Fragment shader for icosahedron
const char *icosFragmentShaderSource = R"(
    #version 330 core
    in vec4 FragColor;
    out vec4 outColor;
    
    void main() {
        outColor = FragColor;
    }
)";

// Vertex shader for icosahedron wireframe
const char *icosWireframeVertexShaderSource = R"(
    #version 330 core
    layout (location = 0) in vec3 aPos;
    
    uniform mat4 model;
    uniform mat4 view;
    uniform mat4 projection;
    
    void main() {
        gl_Position = projection * view * model * vec4(aPos, 1.0);
    }
)";

// Fragment shader for icosahedron wireframe
const char *icosWireframeFragmentShaderSource = R"(
    #version 330 core
    out vec4 FragColor;
    
    void main() {
        FragColor = vec4(0.0, 0.0, 0.0, 1.0);
    }
)";

Visualizer::Visualizer(std::shared_ptr<PointProbabilityEngine> engine, int width, int height, const std::string &title)
    : engine(engine), width(width), height(height), title(title), window(nullptr),
      cameraPos(0.0f, 0.0f, 3.0f),
      cameraFront(0.0f, 0.0f, -1.0f),
      cameraUp(0.0f, 1.0f, 0.0f),
      fov(45.0f),
      pointVAO(0), pointVBO(0), axesVAO(0), axesVBO(0),
      pointShaderProgram(0), axesShaderProgram(0), icosShaderProgram(0), icosWireframeShaderProgram(0),
      icosVAO(0), icosVBO(0), icosEBO(0),
      icosWireframeVAO(0), icosWireframeVBO(0), icosWireframeEBO(0)
{
  if (!engine)
  {
    throw std::invalid_argument("Engine pointer cannot be null");
  }
}

Visualizer::~Visualizer()
{
  if (pointVAO)
    glDeleteVertexArrays(1, &pointVAO);
  if (pointVBO)
    glDeleteBuffers(1, &pointVBO);
  if (axesVAO)
    glDeleteVertexArrays(1, &axesVAO);
  if (axesVBO)
    glDeleteBuffers(1, &axesVBO);
  if (icosVAO)
    glDeleteVertexArrays(1, &icosVAO);
  if (icosVBO)
    glDeleteBuffers(1, &icosVBO);
  if (icosEBO)
    glDeleteBuffers(1, &icosEBO);
  if (icosWireframeVAO)
    glDeleteVertexArrays(1, &icosWireframeVAO);
  if (icosWireframeVBO)
    glDeleteBuffers(1, &icosWireframeVBO);
  if (icosWireframeEBO)
    glDeleteBuffers(1, &icosWireframeEBO);
  if (pointShaderProgram)
    glDeleteProgram(pointShaderProgram);
  if (axesShaderProgram)
    glDeleteProgram(axesShaderProgram);
  if (icosShaderProgram)
    glDeleteProgram(icosShaderProgram);
  if (icosWireframeShaderProgram)
    glDeleteProgram(icosWireframeShaderProgram);
  if (window)
    glfwDestroyWindow(window);
  glfwTerminate();
}

bool Visualizer::initialize()
{
  if (!glfwInit())
  {
    std::cerr << "Failed to initialize GLFW" << std::endl;
    return false;
  }

  glfwWindowHint(GLFW_CONTEXT_VERSION_MAJOR, 3);
  glfwWindowHint(GLFW_CONTEXT_VERSION_MINOR, 3);
  glfwWindowHint(GLFW_OPENGL_PROFILE, GLFW_OPENGL_CORE_PROFILE);

  window = glfwCreateWindow(width, height, title.c_str(), nullptr, nullptr);
  if (!window)
  {
    std::cerr << "Failed to create GLFW window" << std::endl;
    glfwTerminate();
    return false;
  }

  glfwMakeContextCurrent(window);
  glfwSetFramebufferSizeCallback(window, framebufferSizeCallback);

  if (!gladLoadGLLoader((GLADloadproc)glfwGetProcAddress))
  {
    std::cerr << "Failed to initialize GLAD" << std::endl;
    return false;
  }

  glViewport(0, 0, width, height);

  glEnable(GL_DEPTH_TEST);
  glEnable(GL_PROGRAM_POINT_SIZE);
  glEnable(GL_BLEND);
  glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA);
  glEnable(GL_CULL_FACE);
  glCullFace(GL_BACK);

  setupCamera();
  setupPointShaders();
  setupAxesShaders();
  setupIcosShaders();
  generateIcosahedron();
  generateRandomColors(20); // 20 faces for icosahedron
  setupBuffers();

  return true;
}

void Visualizer::setupCamera()
{
  cameraPos = glm::vec3(3.0f, 0.0f, 3.0f);           // Changed Y to 0 to put camera on XZ plane
  cameraFront = glm::vec3(-0.7071f, 0.0f, -0.7071f); // Normalized direction vector pointing to origin
  cameraUp = glm::vec3(0.0f, 1.0f, 0.0f);
}

void Visualizer::setupPointShaders()
{
  // Point shader program
  GLuint pointVertexShader = glCreateShader(GL_VERTEX_SHADER);
  glShaderSource(pointVertexShader, 1, &pointVertexShaderSource, NULL);
  glCompileShader(pointVertexShader);

  GLuint pointFragmentShader = glCreateShader(GL_FRAGMENT_SHADER);
  glShaderSource(pointFragmentShader, 1, &pointFragmentShaderSource, NULL);
  glCompileShader(pointFragmentShader);

  pointShaderProgram = glCreateProgram();
  glAttachShader(pointShaderProgram, pointVertexShader);
  glAttachShader(pointShaderProgram, pointFragmentShader);
  glLinkProgram(pointShaderProgram);

  glDeleteShader(pointVertexShader);
  glDeleteShader(pointFragmentShader);
}

void Visualizer::setupAxesShaders()
{
  // Axis shader program
  GLuint axisVertexShader = glCreateShader(GL_VERTEX_SHADER);
  glShaderSource(axisVertexShader, 1, &axisVertexShaderSource, NULL);
  glCompileShader(axisVertexShader);

  GLuint axisFragmentShader = glCreateShader(GL_FRAGMENT_SHADER);
  glShaderSource(axisFragmentShader, 1, &axisFragmentShaderSource, NULL);
  glCompileShader(axisFragmentShader);

  axesShaderProgram = glCreateProgram();
  glAttachShader(axesShaderProgram, axisVertexShader);
  glAttachShader(axesShaderProgram, axisFragmentShader);
  glLinkProgram(axesShaderProgram);

  glDeleteShader(axisVertexShader);
  glDeleteShader(axisFragmentShader);
}

void Visualizer::setupIcosShaders()
{
  // Setup face shader program
  GLuint vertexShader = glCreateShader(GL_VERTEX_SHADER);
  glShaderSource(vertexShader, 1, &icosVertexShaderSource, NULL);
  glCompileShader(vertexShader);

  GLuint fragmentShader = glCreateShader(GL_FRAGMENT_SHADER);
  glShaderSource(fragmentShader, 1, &icosFragmentShaderSource, NULL);
  glCompileShader(fragmentShader);

  icosShaderProgram = glCreateProgram();
  glAttachShader(icosShaderProgram, vertexShader);
  glAttachShader(icosShaderProgram, fragmentShader);
  glLinkProgram(icosShaderProgram);

  glDeleteShader(vertexShader);
  glDeleteShader(fragmentShader);

  // Setup wireframe shader program
  vertexShader = glCreateShader(GL_VERTEX_SHADER);
  glShaderSource(vertexShader, 1, &icosWireframeVertexShaderSource, NULL);
  glCompileShader(vertexShader);

  fragmentShader = glCreateShader(GL_FRAGMENT_SHADER);
  glShaderSource(fragmentShader, 1, &icosWireframeFragmentShaderSource, NULL);
  glCompileShader(fragmentShader);

  icosWireframeShaderProgram = glCreateProgram();
  glAttachShader(icosWireframeShaderProgram, vertexShader);
  glAttachShader(icosWireframeShaderProgram, fragmentShader);
  glLinkProgram(icosWireframeShaderProgram);

  glDeleteShader(vertexShader);
  glDeleteShader(fragmentShader);
}

void Visualizer::setupBuffers()
{
  // Setup point buffers
  glGenVertexArrays(1, &pointVAO);
  glGenBuffers(1, &pointVBO);

  // Setup axes buffers
  glGenVertexArrays(1, &axesVAO);
  glGenBuffers(1, &axesVBO);

  float axesVertices[] = {
      // Positions        // Colors
      0.0f, 0.0f, 0.0f, 1.0f, 0.0f, 0.0f, // X axis start
      1.0f, 0.0f, 0.0f, 1.0f, 0.0f, 0.0f, // X axis end
      0.0f, 0.0f, 0.0f, 0.0f, 1.0f, 0.0f, // Y axis start
      0.0f, 1.0f, 0.0f, 0.0f, 1.0f, 0.0f, // Y axis end
      0.0f, 0.0f, 0.0f, 0.0f, 0.0f, 1.0f, // Z axis start
      0.0f, 0.0f, 1.0f, 0.0f, 0.0f, 1.0f  // Z axis end
  };

  glBindVertexArray(axesVAO);
  glBindBuffer(GL_ARRAY_BUFFER, axesVBO);
  glBufferData(GL_ARRAY_BUFFER, sizeof(axesVertices), axesVertices, GL_STATIC_DRAW);

  glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 6 * sizeof(float), (void *)0);
  glEnableVertexAttribArray(0);
  glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 6 * sizeof(float), (void *)(3 * sizeof(float)));
  glEnableVertexAttribArray(1);

  // Setup icosahedron buffers
  glGenVertexArrays(1, &icosVAO);
  glGenBuffers(1, &icosVBO);
  glGenBuffers(1, &icosEBO);

  glBindVertexArray(icosVAO);
  glBindBuffer(GL_ARRAY_BUFFER, icosVBO);
  glBufferData(GL_ARRAY_BUFFER, icosVertices.size() * sizeof(float), icosVertices.data(), GL_STATIC_DRAW);
  glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, icosEBO);
  glBufferData(GL_ELEMENT_ARRAY_BUFFER, icosIndices.size() * sizeof(unsigned int), icosIndices.data(), GL_STATIC_DRAW);

  glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 3 * sizeof(float), (void *)0);
  glEnableVertexAttribArray(0);

  // Setup icosahedron wireframe buffers
  glGenVertexArrays(1, &icosWireframeVAO);
  glGenBuffers(1, &icosWireframeVBO);
  glGenBuffers(1, &icosWireframeEBO);

  glBindVertexArray(icosWireframeVAO);
  glBindBuffer(GL_ARRAY_BUFFER, icosWireframeVBO);
  glBufferData(GL_ARRAY_BUFFER, icosVertices.size() * sizeof(float), icosVertices.data(), GL_STATIC_DRAW);
  glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, icosWireframeEBO);
  glBufferData(GL_ELEMENT_ARRAY_BUFFER, icosWireframeIndices.size() * sizeof(unsigned int), icosWireframeIndices.data(), GL_STATIC_DRAW);

  glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 3 * sizeof(float), (void *)0);
  glEnableVertexAttribArray(0);
}

void Visualizer::generateIcosahedron()
{
  // Clear existing data
  icosVertices.clear();
  icosIndices.clear();
  icosWireframeIndices.clear();

  // Golden ratio
  const float t = (1.0f + std::sqrt(5.0f)) / 2.0f;
  const float s = 1.0f / std::sqrt(1.0f + t * t);

  // Generate 12 vertices
  for (int i = 0; i < 12; i++)
  {
    addIcosVertex(icos.vertices[i].x(), icos.vertices[i].y(), icos.vertices[i].z());
  }

  for (int i = 0; i < 20; i++)
  {
    addIcosFace(icos.faces[i][0], icos.faces[i][1], icos.faces[i][2]);
  }

  for (int i = 0; i < 30; i++)
  {
    addIcosWireframeEdge(icos.edges[i][0], icos.edges[i][1]);
  }
}

void Visualizer::generateRandomColors(size_t numFaces)
{
  std::random_device rd;
  std::mt19937 gen(rd());
  std::uniform_real_distribution<float> dis(0.2f, 0.8f);
  std::uniform_real_distribution<float> alpha_dis(0.3f, 0.7f);

  icosColors.clear();
  for (size_t i = 0; i < numFaces; ++i)
  {
    icosColors.push_back(dis(gen));       // R
    icosColors.push_back(dis(gen));       // G
    icosColors.push_back(dis(gen));       // B
    icosColors.push_back(alpha_dis(gen)); // A
  }
}

void Visualizer::render()
{
  glClearColor(0.2f, 0.2f, 0.2f, 1.0f);
  glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);

  glm::mat4 view = glm::lookAt(cameraPos, cameraPos + cameraFront, cameraUp);
  glm::mat4 projection = glm::perspective(glm::radians(fov), (float)width / (float)height, 0.1f, 100.0f);

  // Render coordinate axes
  glUseProgram(axesShaderProgram);
  glUniformMatrix4fv(glGetUniformLocation(axesShaderProgram, "view"), 1, GL_FALSE, glm::value_ptr(view));
  glUniformMatrix4fv(glGetUniformLocation(axesShaderProgram, "projection"), 1, GL_FALSE, glm::value_ptr(projection));
  glUniformMatrix4fv(glGetUniformLocation(axesShaderProgram, "model"), 1, GL_FALSE, glm::value_ptr(glm::mat4(1.0f)));

  glBindVertexArray(axesVAO);
  glDrawArrays(GL_LINES, 0, 6);

  // Get point data from engine and convert to vector for rendering
  const auto &pointMap = engine->getMap().getMapPoints();
  std::vector<float> pointVertices;
  pointVertices.reserve(pointMap.size() * 3);

  // for (const auto &[point, metadata] : pointMap)
  // {
  //   const auto &pos = point->getPose();
  //   pointVertices.push_back(pos.x());
  //   pointVertices.push_back(pos.y());
  //   pointVertices.push_back(pos.z());
  // }

  // Update point buffer
  glBindVertexArray(pointVAO);
  glBindBuffer(GL_ARRAY_BUFFER, pointVBO);
  glBufferData(GL_ARRAY_BUFFER, pointVertices.size() * sizeof(float), pointVertices.data(), GL_STATIC_DRAW);
  glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 3 * sizeof(float), (void *)0);
  glEnableVertexAttribArray(0);

  // Render points
  glUseProgram(pointShaderProgram);
  glUniformMatrix4fv(glGetUniformLocation(pointShaderProgram, "view"), 1, GL_FALSE, glm::value_ptr(view));
  glUniformMatrix4fv(glGetUniformLocation(pointShaderProgram, "projection"), 1, GL_FALSE, glm::value_ptr(projection));
  glUniformMatrix4fv(glGetUniformLocation(pointShaderProgram, "model"), 1, GL_FALSE, glm::value_ptr(glm::mat4(1.0f)));

  glBindVertexArray(pointVAO);
  glDrawArrays(GL_POINTS, 0, pointVertices.size() / 3);

  // Render icosahedra around each point
  glUseProgram(icosShaderProgram);
  glUniformMatrix4fv(glGetUniformLocation(icosShaderProgram, "view"), 1, GL_FALSE, glm::value_ptr(view));
  glUniformMatrix4fv(glGetUniformLocation(icosShaderProgram, "projection"), 1, GL_FALSE, glm::value_ptr(projection));

  // for (const auto &[point, metadata] : pointMap)
  // {
  //   const auto &pos = point->getPose();
  //   glm::mat4 model = glm::mat4(1.0f);
  //   model = glm::translate(model, glm::vec3(pos.x(), pos.y(), pos.z()));
  //   model = glm::scale(model, glm::vec3(0.1f)); // Scale down the icosahedron
  //   glUniformMatrix4fv(glGetUniformLocation(icosShaderProgram, "model"), 1, GL_FALSE, glm::value_ptr(model));

  //   // Render faces
  //   glBindVertexArray(icosVAO);
  //   for (size_t j = 0; j < icosIndices.size(); j += 3)
  //   {
  //     size_t colorIndex = (j / 3) * 4;
  //     glVertexAttrib4f(1, icosColors[colorIndex], icosColors[colorIndex + 1],
  //                      icosColors[colorIndex + 2], icosColors[colorIndex + 3]);
  //     glDrawElements(GL_TRIANGLES, 3, GL_UNSIGNED_INT, (void *)(j * sizeof(unsigned int)));
  //   }

  //   // Render wireframe
  //   glUseProgram(icosWireframeShaderProgram);
  //   glUniformMatrix4fv(glGetUniformLocation(icosWireframeShaderProgram, "model"), 1, GL_FALSE, glm::value_ptr(model));
  //   glUniformMatrix4fv(glGetUniformLocation(icosWireframeShaderProgram, "view"), 1, GL_FALSE, glm::value_ptr(view));
  //   glUniformMatrix4fv(glGetUniformLocation(icosWireframeShaderProgram, "projection"), 1, GL_FALSE, glm::value_ptr(projection));

  //   glPolygonMode(GL_FRONT_AND_BACK, GL_LINE);
  //   glBindVertexArray(icosWireframeVAO);
  //   glDrawElements(GL_LINES, icosWireframeIndices.size(), GL_UNSIGNED_INT, 0);
  //   glPolygonMode(GL_FRONT_AND_BACK, GL_FILL);
  // }

  glfwSwapBuffers(window);
}

void Visualizer::update(const glm::vec3 &cameraPos, const glm::vec3 &lookAtPoint)
{
  this->cameraPos = cameraPos;
  this->cameraFront = glm::normalize(lookAtPoint - cameraPos);
}

void Visualizer::pollEvents()
{
  glfwPollEvents();
}

bool Visualizer::shouldClose() const
{
  return glfwWindowShouldClose(window);
}

void Visualizer::framebufferSizeCallback(GLFWwindow *window, int width, int height)
{
  glViewport(0, 0, width, height);
}

void Visualizer::addIcosVertex(float x, float y, float z)
{
  icosVertices.push_back(x);
  icosVertices.push_back(y);
  icosVertices.push_back(z);
}

void Visualizer::addIcosFace(unsigned int a, unsigned int b, unsigned int c)
{
  icosIndices.push_back(a);
  icosIndices.push_back(b);
  icosIndices.push_back(c);
}

void Visualizer::addIcosWireframeEdge(unsigned int a, unsigned int b)
{
  icosWireframeIndices.push_back(a);
  icosWireframeIndices.push_back(b);
}
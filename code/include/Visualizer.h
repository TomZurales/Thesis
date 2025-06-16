#pragma once

#define GLFW_INCLUDE_NONE
#include <GLFW/glfw3.h>
#include <glad/glad.h>
#include <glm/glm.hpp>
#include <glm/gtc/matrix_transform.hpp>
#include <string>
#include <memory>
#include <vector>
#include "PointProbabilityEngine.h"
#include "Icosahedron.h"

class Visualizer
{
public:
  Visualizer(std::shared_ptr<PointProbabilityEngine> engine, int width = 800, int height = 600, const std::string &title = "Visualizer");
  ~Visualizer();

  // Delete copy constructor and assignment operator
  Visualizer(const Visualizer &) = delete;
  Visualizer &operator=(const Visualizer &) = delete;

  bool initialize();
  void render();
  bool shouldClose() const;
  void update(const glm::vec3 &cameraPos, const glm::vec3 &lookAtPoint);
  void pollEvents();

private:
  GLFWwindow *window;
  int width;
  int height;
  std::string title;
  std::shared_ptr<PointProbabilityEngine> engine;

  Icosahedron icos;

  // Camera properties
  glm::vec3 cameraPos;
  glm::vec3 cameraFront;
  glm::vec3 cameraUp;
  float fov;

  // OpenGL objects for points
  GLuint pointVAO, pointVBO;
  GLuint pointShaderProgram;

  // OpenGL objects for coordinate axes
  GLuint axesVAO, axesVBO;
  GLuint axesShaderProgram;

  // OpenGL objects for icosahedra
  GLuint icosVAO, icosVBO, icosEBO;
  GLuint icosWireframeVAO, icosWireframeVBO, icosWireframeEBO;
  GLuint icosShaderProgram;
  GLuint icosWireframeShaderProgram;
  std::vector<float> icosVertices;
  std::vector<unsigned int> icosIndices;
  std::vector<unsigned int> icosWireframeIndices;
  std::vector<float> icosColors;

  void setupCamera();
  void setupPointShaders();
  void setupAxesShaders();
  void setupIcosShaders();
  void setupBuffers();
  void generateIcosahedron();
  void generateRandomColors(size_t numFaces);
  static void framebufferSizeCallback(GLFWwindow *window, int width, int height);

  // Helper functions for icosahedron generation
  void addIcosVertex(float x, float y, float z);
  void addIcosFace(unsigned int a, unsigned int b, unsigned int c);
  void addIcosWireframeEdge(unsigned int a, unsigned int b);
};
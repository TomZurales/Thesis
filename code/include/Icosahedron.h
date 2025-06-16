#pragma once

#include <Eigen/Core>
#include <vector>

#define ICOS_SHORT sqrt(2 / (5 + sqrt(5)))
#define ICOS_LONG ((1 + sqrt(5)) / 2) * ICOS_SHORT

class Icosahedron
{
public:
  Icosahedron();
  ~Icosahedron() = default;

  int getNearestFace(Eigen::Vector3f in);

  std::vector<Eigen::Vector3f> vertices = {
      Eigen::Vector3f(0, ICOS_LONG, ICOS_SHORT).normalized(),   // 1
      Eigen::Vector3f(0, ICOS_LONG, -ICOS_SHORT).normalized(),  // 2
      Eigen::Vector3f(ICOS_LONG, ICOS_SHORT, 0).normalized(),   // 3
      Eigen::Vector3f(ICOS_SHORT, 0, -ICOS_LONG).normalized(),  // 4
      Eigen::Vector3f(-ICOS_SHORT, 0, -ICOS_LONG).normalized(), // 5
      Eigen::Vector3f(-ICOS_LONG, ICOS_SHORT, 0).normalized(),  // 6
      Eigen::Vector3f(-ICOS_SHORT, 0, ICOS_LONG).normalized(),  // 7
      Eigen::Vector3f(ICOS_SHORT, 0, ICOS_LONG).normalized(),   // 8
      Eigen::Vector3f(ICOS_LONG, -ICOS_SHORT, 0).normalized(),  // 9
      Eigen::Vector3f(0, -ICOS_LONG, -ICOS_SHORT).normalized(), // 10
      Eigen::Vector3f(-ICOS_LONG, -ICOS_SHORT, 0).normalized(), // 11
      Eigen::Vector3f(0, -ICOS_LONG, ICOS_SHORT).normalized()   // 12
  };

  std::vector<std::vector<int>>
      faces = {
          {0, 1, 2},   // 1
          {1, 2, 3},   // 2
          {1, 3, 4},   // 3
          {1, 4, 5},   // 4
          {0, 1, 5},   // 5
          {0, 5, 6},   // 6
          {0, 6, 7},   // 7
          {0, 2, 7},   // 8
          {2, 7, 8},   // 9
          {2, 3, 8},   // 10
          {3, 8, 9},   // 11
          {3, 4, 9},   // 12
          {4, 9, 10},  // 13
          {4, 5, 10},  // 14
          {5, 6, 10},  // 15
          {6, 10, 11}, // 16
          {6, 7, 11},  // 17
          {7, 8, 11},  // 18
          {8, 9, 11},  // 19
          {8, 10, 11}  // 20
  };
  std::vector<Eigen::Vector3f> face_centers;
  std::vector<std::vector<int>> edges = {
      {0, 1},
      {1, 2},
      {0, 2},
      {1, 3},
      {2, 3},
      {1, 4},
      {3, 4},
      {1, 5},
      {4, 5},
      {5, 0},
      {0, 7},
      {2, 7},
      {2, 8},
      {7, 8},
      {3, 8},
      {3, 9},
      {8, 9},
      {4, 9},
      {4, 10},
      {9, 10},
      {5, 10},
      {5, 6},
      {6, 10},
      {0, 6},
      {6, 7},
      {7, 11},
      {8, 11},
      {9, 11},
      {10, 11},
      {6, 11}};
};
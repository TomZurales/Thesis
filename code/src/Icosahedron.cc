#include "Icosahedron.h"

Icosahedron::Icosahedron()
{
  // Initialize face centers
  for (auto face_vertices : faces)
  {
    float avg_x = 0;
    float avg_y = 0;
    float avg_z = 0;
    avg_x += vertices[face_vertices[0]].x();
    avg_x += vertices[face_vertices[1]].x();
    avg_x += vertices[face_vertices[2]].x();

    avg_y += vertices[face_vertices[0]].y();
    avg_y += vertices[face_vertices[1]].y();
    avg_y += vertices[face_vertices[2]].y();

    avg_z += vertices[face_vertices[0]].z();
    avg_z += vertices[face_vertices[1]].z();
    avg_z += vertices[face_vertices[2]].z();

    avg_x /= 3;
    avg_y /= 3;
    avg_z /= 3;

    face_centers.push_back(Eigen::Vector3f(avg_x, avg_y, avg_z).normalized());
  }
}

int Icosahedron::getNearestFace(Eigen::Vector3f in)
{
  auto in_norm = in.normalized();
  int nearest_index = 0;
  float max_dot = face_centers[0].dot(in_norm);

  for (size_t i = 1; i < face_centers.size(); ++i)
  {
    float dot = face_centers[i].dot(in_norm);
    if (dot > max_dot)
    {
      max_dot = dot;
      nearest_index = static_cast<int>(i);
    }
  }
  return nearest_index;
}
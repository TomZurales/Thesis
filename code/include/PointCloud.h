#pragma once

#include <GL/glew.h>
#include <glm/glm.hpp>
#include <glm/gtc/matrix_transform.hpp>
#include <glm/gtc/type_ptr.hpp>
#include <vector>
#include <Point.h>

#include "ShaderManager.h"
#include "Shader.h"
#include "Camera.h"

class PointCloud
{
    GLuint pointCloudVAO = 0;
    GLuint pointCloudVBO = 0;
    glm::mat4 modelPose = glm::mat4(1.0f); // Point cloud is always at the origin

public:
    PointCloud();
    void draw(std::vector<Point *> points, Camera *camera) const;
};
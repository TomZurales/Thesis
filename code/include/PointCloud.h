#pragma once

#include <glad/glad.h>
#include <glm/glm.hpp>
#include <glm/gtc/matrix_transform.hpp>
#include <glm/gtc/type_ptr.hpp>
#include <vector>
#include <Point.h>

#include "Shader.h"

class IcosModel
{
    Shader *shader;
    GLuint icosVAO = 0;
    glm::mat4 modelPose = glm::mat4(1.0f); // Point cloud is always at the origin

public:
    IcosModel() = delete;
    IcosModel(Shader *shader);
    void draw(std::vector<Point *> points) const;
};
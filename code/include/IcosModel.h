#pragma once

#include <glad/glad.h>
#include <glm/glm.hpp>
#include <glm/gtc/matrix_transform.hpp>
#include <glm/gtc/type_ptr.hpp>
#include <vector>
#include <Point.h>
#include <Icosahedron.h>

#include "Shader.h"

class IcosModel
{
    Shader *shader;
    GLuint icosVAO = 0;
    GLuint icosEBO = 0;

public:
    IcosModel() = delete;
    IcosModel(Shader *shader);
    void draw(Point *point, Icosahedron *icos) const;
};
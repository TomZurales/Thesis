#pragma once

#include <GL/glew.h>
#include <glm/glm.hpp>
#include <glm/gtc/matrix_transform.hpp>
#include <glm/gtc/type_ptr.hpp>
#include <vector>
#include <Point.h>
#include <Icosahedron.h>
#include <set>

#include "ShaderManager.h"
#include "Shader.h"

class IcosModel
{
    GLuint icosVAO = 0;
    GLuint icosEBO = 0;

public:
    IcosModel();
    void draw(Point *point, Icosahedron *icos) const;
};
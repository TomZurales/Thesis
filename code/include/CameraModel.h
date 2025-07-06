#pragma once

#include <GL/glew.h>
#include <glm/glm.hpp>
#include <glm/gtc/matrix_transform.hpp>
#include <glm/gtc/type_ptr.hpp>
#include <vector>
#include <memory>

#include "ShaderManager.h"
#include "Camera.h"
#include "Utility.h"

class CameraModel
{
    GLuint cameraModelVAO = 0;
    Camera *camera;

public:
    CameraModel(Camera *);
    void draw() const;
};
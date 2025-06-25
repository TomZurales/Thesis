#include "Graphics.h"

#include <glm/glm.hpp>
#include <glm/gtc/matrix_transform.hpp>
#include <glm/gtc/type_ptr.hpp>

void Graphics::initCenteredPoint()
{
    float point_vertices[] = {
        0.0f, 0.0f, 0.0f};

    unsigned int pointVBO;

    glGenVertexArrays(1, &pointVAO);
    glGenBuffers(1, &pointVBO);

    glBindVertexArray(pointVAO);

    glBindBuffer(GL_ARRAY_BUFFER, pointVBO);
    glBufferData(GL_ARRAY_BUFFER, sizeof(point_vertices), point_vertices, GL_STATIC_DRAW);

    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 3 * sizeof(float), (void *)0);
    glEnableVertexAttribArray(0);

    glBindBuffer(GL_ARRAY_BUFFER, 0);
    glBindVertexArray(0);
    centeredPointInitialized = true;

    solidColor3DShader = new Shader("/home/tom/workspace/thesis/code/src/Graphics/shaders/vertex/solid_color_3d.glsl", "/home/tom/workspace/thesis/code/src/Graphics/shaders/fragment/solid_color_3d.glsl");
}

void Graphics::drawCenteredPoint() const
{
    glm::mat4 proj = glm::identity<glm::mat4>(); // Orthographic projection
    glm::mat4 view = glm::identity<glm::mat4>();
    // note that we're translating the scene in the reverse direction of where we want to move
    glm::mat4 model = glm::identity<glm::mat4>();
    solidColor3DShader->setMatrix4fv("projection", proj);
    solidColor3DShader->setMatrix4fv("view", view);
    solidColor3DShader->setMatrix4fv("model", model);
    solidColor3DShader->use();
    glBindVertexArray(pointVAO);
    glDrawArrays(GL_POINTS, 0, 1);
    glBindVertexArray(0);
}
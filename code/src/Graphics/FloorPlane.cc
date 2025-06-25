#include "FloorPlane.h"

FloorPlane::FloorPlane(Shader *shader) : shader(shader)
{
    float plane_vertices[] = {
        -10.0f, 0.0f, -10.0f,
        10.0f, 0.0f, -10.0f,
        10.0f, 0.0f, 10.0f,
        -10.0f, 0.0f, 10.0f};

    unsigned int plane_indices[] = {
        0, 1, 2,
        0, 2, 3};

    std::vector<float> line_vertices;
    std::vector<unsigned int> line_indices;

    for (int i = -10; i <= 10; i++)
    {
        // Vertical lines
        line_vertices.push_back(i);
        line_vertices.push_back(0.0f);
        line_vertices.push_back(-10.0f);
        line_vertices.push_back(i);
        line_vertices.push_back(0.0f);
        line_vertices.push_back(10.0f);

        // Horizontal lines
        line_vertices.push_back(-10.0f);
        line_vertices.push_back(0.0f);
        line_vertices.push_back(i);
        line_vertices.push_back(10.0f);
        line_vertices.push_back(0.0f);
        line_vertices.push_back(i);
    }

    for (int i = 0; i < 21; i++)
    {
        // Vertical lines indices
        line_indices.push_back(i * 2);
        line_indices.push_back(i * 2 + 1);

        // Horizontal lines indices
        line_indices.push_back(42 + i * 2);
        line_indices.push_back(42 + i * 2 + 1);
    }

    unsigned int planeVBO, planeEBO, lineVBO, lineEBO;

    glGenVertexArrays(1, &planeVAO);
    glGenBuffers(1, &planeVBO);
    glGenBuffers(1, &planeEBO);

    glBindVertexArray(planeVAO);

    glBindBuffer(GL_ARRAY_BUFFER, planeVBO);
    glBufferData(GL_ARRAY_BUFFER, sizeof(plane_vertices), plane_vertices, GL_STATIC_DRAW);

    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, planeEBO);
    glBufferData(GL_ELEMENT_ARRAY_BUFFER, sizeof(plane_indices), plane_indices, GL_STATIC_DRAW);

    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 3 * sizeof(float), (void *)0);
    glEnableVertexAttribArray(0);

    glGenVertexArrays(1, &linesVAO);
    glGenBuffers(1, &lineVBO);
    glGenBuffers(1, &lineEBO);

    glBindVertexArray(linesVAO);

    glBindBuffer(GL_ARRAY_BUFFER, lineVBO);
    glBufferData(GL_ARRAY_BUFFER, line_vertices.size() * sizeof(float), line_vertices.data(), GL_STATIC_DRAW);

    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, lineEBO);
    glBufferData(GL_ELEMENT_ARRAY_BUFFER, line_indices.size() * sizeof(unsigned int), line_indices.data(), GL_STATIC_DRAW);

    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 3 * sizeof(float), (void *)0);
    glEnableVertexAttribArray(0);

    glBindBuffer(GL_ARRAY_BUFFER, 0);
    glBindVertexArray(0);
    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, 0); // Unbind EBO
}

void FloorPlane::draw() const
{
    shader->use();
    shader->setMatrix4fv("model", modelPose);
    glEnable(GL_DEPTH_TEST);
    glEnable(GL_BLEND);
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA);
    glBindVertexArray(planeVAO);
    shader->setVector4f("color", glm::vec4(0.5f, 0.5f, 0.5f, 0.25f)); // Set a gray color for the floor plane
    glDrawElements(GL_TRIANGLES, 6, GL_UNSIGNED_INT, 0);
    glBindVertexArray(linesVAO);
    glDisable(GL_DEPTH_TEST);                                         // Disable depth test for lines
    shader->setVector4f("color", glm::vec4(0.3f, 0.3f, 0.3f, 0.25f)); // Set a gray color for the floor plane
    glDrawElements(GL_LINES, 80, GL_UNSIGNED_INT, 0);                 // Draw the grid lines
    glBindVertexArray(0);
}
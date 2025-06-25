#include "IcosModel.h"

IcosModel::IcosModel(Shader *shader) : shader(shader)
{

    unsigned int icosModelVBO;

    glGenVertexArrays(1, &icosVAO);
    glGenBuffers(1, &icosModelVBO);
    glGenBuffers(1, &icosEBO);

    glBindVertexArray(icosVAO);

    Icosahedron icos;
    std::vector<float> pointData;
    for (const auto &point : icos.vertices)
    {
        pointData.push_back(point.x());
        pointData.push_back(point.y());
        pointData.push_back(point.z());
    }
    std::vector<unsigned int> indices;
    for (const auto &face : icos.faces)
    {
        indices.push_back(face[0]);
        indices.push_back(face[1]);
        indices.push_back(face[2]);
    }

    glBindBuffer(GL_ARRAY_BUFFER, icosModelVBO);
    glBufferData(GL_ARRAY_BUFFER, pointData.size() * sizeof(float), pointData.data(), GL_STATIC_DRAW);

    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, icosEBO);
    glBufferData(GL_ELEMENT_ARRAY_BUFFER, indices.size() * sizeof(unsigned int), indices.data(), GL_STATIC_DRAW);

    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 3 * sizeof(float), (void *)0);
    glEnableVertexAttribArray(0);

    glBindBuffer(GL_ARRAY_BUFFER, 0);
    glBindVertexArray(0);
    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, 0); // Unbind EBO
}

void IcosModel::draw(Point *point, Icosahedron *icos) const
{
    if (!icos)
        return;

    shader->use();

    shader->setMatrix4fv("model", glm::translate(glm::mat4(1.0f), glm::vec3(point->getPose().x(), point->getPose().y(), point->getPose().z())));
    glEnable(GL_DEPTH_TEST);
    glBindVertexArray(icosVAO);
    shader->setVector4f("color", glm::vec4(0.0f, 0.0f, 0.0f, 1.0f));
    glDrawElements(GL_TRIANGLES, icos->faces.size() * 3, GL_UNSIGNED_INT, 0);
    glBindVertexArray(0);
    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, 0); // Unbind EBO
}
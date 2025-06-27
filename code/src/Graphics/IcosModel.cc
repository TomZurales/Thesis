#include "IcosModel.h"

IcosModel::IcosModel(Shader *shader, Shader *solidShader) : shader(shader), solidShader(solidShader)
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

    // --- Draw faces with heatmap colors ---
    shader->use();
    shader->setMatrix4fv("model", glm::translate(glm::mat4(1.0f), glm::vec3(point->getPose().x(), point->getPose().y(), point->getPose().z())));

    std::vector<float> intensities;
    for (int i = 0; i < 20; i++)
        intensities.push_back(icos->getNormalizedValue("dists", i));
    shader->setFloatArray("heatmapValues", intensities);

    glEnable(GL_DEPTH_TEST);
    glEnable(GL_CULL_FACE);
    glCullFace(GL_BACK);
    glFrontFace(GL_CCW);
    glBindVertexArray(icosVAO);
    glDrawElements(GL_TRIANGLES, icos->faces.size() * 3, GL_UNSIGNED_INT, 0);

    // --- Draw edges in black ---
    // Build edge index buffer on the fly (or cache it in the class for efficiency)
    std::vector<unsigned int> edge_indices;
    std::set<std::pair<unsigned int, unsigned int>> unique_edges;
    for (const auto &face : icos->faces)
    {
        for (int i = 0; i < 3; ++i)
        {
            unsigned int a = face[i];
            unsigned int b = face[(i + 1) % 3];
            if (a > b)
                std::swap(a, b);
            if (unique_edges.insert({a, b}).second)
            {
                edge_indices.push_back(a);
                edge_indices.push_back(b);
            }
        }
    }
    glBindVertexArray(0); // Unbind VAO before binding edge EBO

    GLuint edgeEBO;
    glGenBuffers(1, &edgeEBO);
    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, edgeEBO);
    glBufferData(GL_ELEMENT_ARRAY_BUFFER, edge_indices.size() * sizeof(unsigned int), edge_indices.data(), GL_STATIC_DRAW);

    solidShader->use();
    // solidShader->setMatrix4fv("model", glm::translate(glm::mat4(1.0f), glm::vec3(point->getPose().x(), point->getPose().y(), point->getPose().z())));
    solidShader->setVector4f("color", glm::vec4(0, 0, 0, 1));
    glDisable(GL_CULL_FACE);
    glPolygonMode(GL_FRONT_AND_BACK, GL_LINE);
    // You may need to re-bind your vertex VBO and set up attrib pointers here if not using VAO
    glBindVertexArray(icosVAO); // If your VAO has the correct vertex attrib pointers
    glDrawElements(GL_LINES, edge_indices.size(), GL_UNSIGNED_INT, 0);
    glBindVertexArray(0);
    glPolygonMode(GL_FRONT_AND_BACK, GL_FILL);
    glEnable(GL_CULL_FACE);

    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, 0);
    glDeleteBuffers(1, &edgeEBO);
}
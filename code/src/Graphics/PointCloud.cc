#include "PointCloud.h"

IcosModel::IcosModel(Shader *shader) : shader(shader)
{

    unsigned int pointCloudVBO;

    glGenVertexArrays(1, &icosVAO);
    glGenBuffers(1, &pointCloudVBO);

    glBindVertexArray(icosVAO);

    glBindBuffer(GL_ARRAY_BUFFER, pointCloudVBO);

    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 3 * sizeof(float), (void *)0);
    glEnableVertexAttribArray(0);

    glBindBuffer(GL_ARRAY_BUFFER, 0);
    glBindVertexArray(0);
    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, 0); // Unbind EBO
}

void IcosModel::draw(std::vector<Point *> points) const
{
    if (points.empty())
        return;
    std::vector<float> pointData;
    for (const auto &point : points)
    {
        Eigen::Vector3f pose = point->getPose();
        pointData.push_back(pose.x());
        pointData.push_back(pose.y());
        pointData.push_back(pose.z());
    }
    glBufferData(GL_ARRAY_BUFFER, pointData.size() * sizeof(float), pointData.data(), GL_STREAM_DRAW);

    shader->use();
    shader->setMatrix4fv("model", modelPose);
    glEnable(GL_DEPTH_TEST);
    glBindVertexArray(icosVAO);
    glPointSize(8.0f);
    shader->setVector4f("color", glm::vec4(0.0f, 0.0f, 0.0f, 1.0f));
    glDrawArrays(GL_POINTS, 0, points.size());
    glBindVertexArray(0);
}
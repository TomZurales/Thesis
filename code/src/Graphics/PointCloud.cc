#include "PointCloud.h"
#include <iostream>

PointCloud::PointCloud()
{
    glGenVertexArrays(1, &pointCloudVAO);
    glBindVertexArray(pointCloudVAO);

    glGenBuffers(1, &pointCloudVBO);
    glBindBuffer(GL_ARRAY_BUFFER, pointCloudVBO);

    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 3 * sizeof(float), (void *)0);
    glEnableVertexAttribArray(0);

    glBindVertexArray(0);
}

void PointCloud::draw(std::vector<Point *> points, Camera *camera) const
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

    pointData.push_back(camera->getPose()(0, 3)); // Camera position x
    pointData.push_back(camera->getPose()(1, 3)); // Camera position y
    pointData.push_back(camera->getPose()(2, 3)); // Camera position z

    glBindVertexArray(pointCloudVAO);

    ShaderManager *sm = ShaderManager::getInstance();
    sm->useShader("solid_color_3d");
    sm->setModelMatrix(modelPose);
    sm->setColor(glm::vec4(0.0f, 0.0f, 0.0f, 1.0f)); // Set color to black

    glBindBuffer(GL_ARRAY_BUFFER, pointCloudVBO);
    glBufferData(GL_ARRAY_BUFFER, pointData.size() * sizeof(GLfloat), pointData.data(), GL_STREAM_DRAW);

    glEnable(GL_DEPTH_TEST);
    glPointSize(2.0f);
    glDrawArrays(GL_POINTS, 0, points.size());

    glBindVertexArray(0);
}
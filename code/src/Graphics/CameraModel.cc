#include "CameraModel.h"

CameraModel::CameraModel(Camera *camera) : camera(camera)
{
    GLuint cameraModelVBO, cameraModelEBO = 0;

    glGenVertexArrays(1, &cameraModelVAO);
    glBindVertexArray(cameraModelVAO);

    glGenBuffers(1, &cameraModelVBO);
    glGenBuffers(1, &cameraModelEBO);

    std::vector<float> pointData =
        {
            0.0f, 0.0f, 0.0f,    // Camera center
            1.0f, 1.0f, -1.0f,   // Top right corner
            -1.0f, 1.0f, -1.0f,  // Top left corner
            -1.0f, -1.0f, -1.0f, // Bottom left corner
            1.0f, -1.0f, -1.0f   // Bottom right corner
        };
    std::vector<unsigned int> indices =
        {
            0, 1,
            0, 2,
            0, 3,
            0, 4,
            1, 2,
            2, 3,
            3, 4,
            4, 1};
    glBindBuffer(GL_ARRAY_BUFFER, cameraModelVBO);
    glBufferData(GL_ARRAY_BUFFER, pointData.size() * sizeof(float), pointData.data(), GL_STATIC_DRAW);

    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, cameraModelEBO);
    glBufferData(GL_ELEMENT_ARRAY_BUFFER, indices.size() * sizeof(unsigned int), indices.data(), GL_STATIC_DRAW);

    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 3 * sizeof(float), (void *)0);
    glEnableVertexAttribArray(0);

    glBindVertexArray(0);
    glBindBuffer(GL_ARRAY_BUFFER, 0);
    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, 0); // Unbind EBO
}

void CameraModel::draw() const
{
    glBindVertexArray(cameraModelVAO);

    ShaderManager *sm = ShaderManager::getInstance();
    sm->useShader("solid_color_3d");
    sm->setColor(glm::vec4(0.0f, 0.0f, 0.0f, 1.0f)); // Black color
    // auto modelMat = glm::lookAt(
    //     glm::vec3(camera->getPose()(0, 3), camera->getPose()(1, 3), camera->getPose()(2, 3)), // Camera position
    //     glm::vec3(0.0f, 0.0f, 0.0f),                                                          // Look at point
    //     glm::vec3(0.0f, 1.0f, 0.0f)                                                           // Up vector
    // );

    // modelMat = eigenToGlm(glmToEigen(modelMat).inverse());
    // // set pose to origin, leave rotation alone
    // // modelMat.block<3, 1>(0, 3) = Eigen::Vector3f(0.0f, 0.0f, 0.0f); // Set translation to origin
    sm->setModelMatrix(eigenToGlm(camera->getPose())); // Camera model is always at the origin

    glDrawElements(GL_LINES, 16, GL_UNSIGNED_INT, 0);
    glBindVertexArray(0); // Unbind VAO before binding edge EBO
}
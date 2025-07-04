#include "PointProbabilityEngine.h"

#include <glad/glad.h>

void PointProbabilityEngine::init3DView()
{
    // Generate framebuffer
    glGenFramebuffers(1, &fbo);
    glBindFramebuffer(GL_FRAMEBUFFER, fbo);
    glObjectLabel(GL_FRAMEBUFFER, fbo, -1, "3D View FBO");
    // Generate texture to render to
    glGenTextures(1, &texture);
    glBindTexture(GL_TEXTURE_2D, texture);
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, 1000, 1000, 0, GL_RGBA, GL_UNSIGNED_BYTE, nullptr);
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR);
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR);
    glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_2D, texture, 0);

    // Create and attach a renderbuffer for depth and stencil
    glGenRenderbuffers(1, &rbo);
    glBindRenderbuffer(GL_RENDERBUFFER, rbo);
    glRenderbufferStorage(GL_RENDERBUFFER, GL_DEPTH24_STENCIL8, 1000, 1000);
    glFramebufferRenderbuffer(GL_FRAMEBUFFER, GL_DEPTH_STENCIL_ATTACHMENT, GL_RENDERBUFFER, rbo);

    // Check framebuffer completeness
    if (glCheckFramebufferStatus(GL_FRAMEBUFFER) != GL_FRAMEBUFFER_COMPLETE)
    {
        std::cerr << "Error: Framebuffer is not complete!" << std::endl;
        glBindFramebuffer(GL_FRAMEBUFFER, 0);
        return;
    }

    // Unbind framebuffer
    glBindFramebuffer(GL_FRAMEBUFFER, 0);

    ShaderManager *sm = ShaderManager::getInstance();
    sm->addShader("solid_color_3d",
                  "/home/tom/workspace/thesis/code/src/Graphics/shaders/vertex/solid_color_3d.glsl",
                  "/home/tom/workspace/thesis/code/src/Graphics/shaders/fragment/solid_color_3d.glsl");
    sm->addShader("heatmap_3d",
                  "/home/tom/workspace/thesis/code/src/Graphics/shaders/vertex/solid_color_3d.glsl",
                  "/home/tom/workspace/thesis/code/src/Graphics/shaders/fragment/heatmap_3d.glsl");

    sm->setProjectionMatrix(glm::perspective(glm::radians(45.0f), 1.0f, 0.01f, 100.0f));
    // sm->setChangeOfBasis(glm::scale(glm::mat4(1.0f), glm::vec3(1.0f, -1.0f, 1.0f)));
    sm->setChangeOfBasis(glm::mat4(1.0f));

    floorPlane = new FloorPlane();
    pointCloud = new PointCloud();
    icosModel = new IcosModel();
}

void PointProbabilityEngine::show3DView() const
{
    ImGui::Begin("3D View");
    ImVec2 windowSize = ImGui::GetContentRegionAvail();
    glBindFramebuffer(GL_FRAMEBUFFER, fbo);
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, windowSize.x, windowSize.y, 0, GL_RGBA, GL_UNSIGNED_BYTE, nullptr);
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR);
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR);
    glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_2D, texture, 0);
    glBindRenderbuffer(GL_RENDERBUFFER, rbo);
    glRenderbufferStorage(GL_RENDERBUFFER, GL_DEPTH24_STENCIL8, windowSize.x, windowSize.y);
    glFramebufferRenderbuffer(GL_FRAMEBUFFER, GL_DEPTH_STENCIL_ATTACHMENT, GL_RENDERBUFFER, rbo);

    glViewport(0, 0, windowSize.x, windowSize.y);
    glClearColor(1.0f, 1.0f, 1.0f, 1.0f);
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);
    ShaderManager::getInstance()->setViewMatrix(eigenToGlm(camera.getPose().inverse()));

    // Draw the point cloud first (opaque objects)
    std::vector<Point *> visiblePoints;
    for (const auto &point : map.getMapPoints())
    {
        if (point->isInView() && point->isVisible())
            visiblePoints.push_back(point);
    }
    pointCloud->draw(visiblePoints);

    // Draw the floor plane last (transparent objects)
    floorPlane->draw();

    icosModel->draw(backend->getActivePoint(), ((IcosahedronBackend *)backend)->getActiveIcosahedron()); // Draw the icosahedron model at the origin
    glBindFramebuffer(GL_FRAMEBUFFER, 0);
    ImGui::Image((ImTextureID)texture, windowSize); // Placeholder for 3D rendering
    ImGui::End();
}
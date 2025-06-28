#include "ShaderManager.h"
#include <iostream>

// Initialize static member
ShaderManager *ShaderManager::instance = nullptr;

ShaderManager::~ShaderManager()
{
    // Delete all shaders
    for (auto &pair : shaders)
    {
        delete pair.second;
    }
    shaders.clear();
}

ShaderManager *ShaderManager::getInstance()
{
    if (instance == nullptr)
    {
        instance = new ShaderManager();
    }
    return instance;
}

void ShaderManager::addShader(const std::string &name, const char *vertexPath, const char *fragmentPath)
{
    if (shaders.find(name) != shaders.end())
    {
        std::cerr << "Warning: Shader with name '" << name << "' already exists. Overwriting." << std::endl;
        delete shaders[name];
    }

    shaders[name] = new Shader(vertexPath, fragmentPath);
}

void ShaderManager::useShader(const std::string &name)
{
    auto it = shaders.find(name);
    if (it != shaders.end())
    {
        it->second->use();
    }
    else
    {
        std::cerr << "Error: Shader '" << name << "' not found!" << std::endl;
    }
}

void ShaderManager::setModelMatrix(const glm::mat4 &matrix)
{
    for (auto &pair : shaders)
    {
        pair.second->use();
        pair.second->setMatrix4fv("model", matrix);
    }
}

void ShaderManager::setViewMatrix(const glm::mat4 &matrix)
{
    for (auto &pair : shaders)
    {
        pair.second->use();
        pair.second->setMatrix4fv("view", matrix);
    }
}

void ShaderManager::setProjectionMatrix(const glm::mat4 &matrix)
{
    for (auto &pair : shaders)
    {
        pair.second->use();
        pair.second->setMatrix4fv("projection", matrix);
    }
}

void ShaderManager::setColor(const glm::vec4 &color)
{
    for (auto &pair : shaders)
    {
        pair.second->use();
        pair.second->setVector4f("color", color);
    }
}

void ShaderManager::setFaceValues(const std::vector<float> &values)
{
    for (auto &pair : shaders)
    {
        pair.second->use();
        pair.second->setFloatArray("heatmapValues", values);
    }
}

void ShaderManager::setChangeOfBasis(const glm::mat4 &matrix)
{
    for (auto &pair : shaders)
    {
        pair.second->use();
        pair.second->setMatrix4fv("changeOfBasis", matrix);
    }
}
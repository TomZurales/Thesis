#version 330 core
layout (location = 0) in vec3 aPos;

uniform mat4 model;
uniform mat4 view;
uniform mat4 projection;
uniform mat4 changeOfBasis;

void main()
{
    gl_Position = changeOfBasis * projection * view * model * vec4(aPos, 1.0);
}
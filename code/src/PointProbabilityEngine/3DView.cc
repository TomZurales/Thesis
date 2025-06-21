#include "PointProbabilityEngine.h"

void PointProbabilityEngine::show3DView() const
{
    ImGui::Begin("3D View");
    ImVec2 windowSize = ImGui::GetContentRegionAvail();
    ImGui::Image((ImTextureID)0, windowSize); // Placeholder for 3D rendering
    ImGui::End();
}
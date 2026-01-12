#include "observability_scenario.h"

ObservabilityScenario::ObservabilityScenario(int n_blockers, float goal_blocked_rate)
{
  if(n_blockers < 0) {
    valid = false;
    return;
  }
  // if(n_blockers == 0 && goal_blocked_rate != 0.0f) {
  //   valid = false;
  //   return;
  // } 
  // if(n_blockers == 0) {
  //   valid = true;
  //   return;
  // }
  if(n_blockers > 4) {
    valid = false;
    return;
  }
  // if(goal_blocked_rate < 0.0f || goal_blocked_rate < (0.5f / n_blockers)) {
  //   valid = false;
  //   return;
  // }

  std::vector<Eigen::Vector3f> testing_viewpoints;
  for(int i = 0; i < 10000; i++) {
    testing_viewpoints.push_back(randomPosition());
  }

  // while(true) {
    blockers.clear();
    for(int i = 0; i < n_blockers; i++) {
      blockers.push_back(randomPosition());
    }

    // int n_blocked = 0;
    // for(const auto& viewpoint : testing_viewpoints) {
    //   if(!isSeen(viewpoint)) {
    //     n_blocked++;
    //   }
    // }

    // float blocked_rate = static_cast<float>(n_blocked) / testing_viewpoints.size();

    // if(fabs(blocked_rate - goal_blocked_rate) < 0.02f) {
    //   valid = true;
    //   return;
    // }
  // }
}

bool ObservabilityScenario::isSeen(Eigen::Vector3f point) const
{
    Eigen::Vector3f origin(0.0f, 0.0f, 0.0f);
    
    for(const auto& blocker_point : blockers) {
        // Normal vector pointing towards origin
        Eigen::Vector3f normal = (origin - blocker_point).normalized();
        
        // Vector from blocker point to test point
        Eigen::Vector3f to_point = point - blocker_point;
        
        // If dot product is negative, point is on opposite side of blocker from origin
        if(to_point.dot(normal) < 0.0f) {
            return false;  // Point is blocked
        }
    }
    
    return true;  // Point is visible (not blocked by any blocker)
}
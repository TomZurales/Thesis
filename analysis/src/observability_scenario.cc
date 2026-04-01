#include "observability_scenario.h"

Eigen::Vector3f genRandomBlockerFavorCenter()
{
  float dist = static_cast<float>(rand()) / static_cast<float>(RAND_MAX);
  Eigen::Vector3f pos = randomPosition();

  return pos.normalized() * dist;
}

Eigen::Vector3f genRandomBlockerFavorRandomness()
{
  return randomPosition();
}

ObservabilityScenario::ObservabilityScenario(float goal_blocked_rate)
{
  int min_blockers = 1;
  int max_blockers = 4;
  if(goal_blocked_rate > 0.5)
  {
    min_blockers = 2;
  }

  std::vector<Eigen::Vector3f> random_viewpoints;
  for(int i = 0; i < 5000; i++)
  {
    random_viewpoints.push_back(randomPosition());
  }

  std::vector<Eigen::Vector3f> bestBlockers;
  float bestError = 1000000;
  float desired_seen_count = (1 - goal_blocked_rate) * 5000;
  bool done = false;

  for(int num_blockers = min_blockers; num_blockers <= max_blockers; num_blockers++)
  {
    if(done)
      break;
    for(int j = 0; j < 500; j++)
    {
      blockers.clear();
      for(int k = 0; k < num_blockers; k++)
      {
        blockers.push_back(randomPosition());
      }

      int seen_count = 0;
      for(int k = 0; k < random_viewpoints.size(); k++)
      {
        if(isSeen(random_viewpoints[k]))
        {
          seen_count++;
        }
      }

      float error = std::abs(seen_count - desired_seen_count);
      if(error < bestError)
      {
        bestError = error;
        bestBlockers = blockers;
      }

      if((error / 5000) < 0.02)
      {
        done = true;
        break;
      }
    }
  }

  blockers = bestBlockers;
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
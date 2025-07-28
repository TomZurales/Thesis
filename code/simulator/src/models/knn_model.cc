#include "models/knn_model.h"
#include <algorithm>

void KNNModel::initialize(std::vector<float> parameters)
{
    k = static_cast<int>(parameters[0]);
    numObservations = static_cast<int>(parameters[1]);
    distanceThreshold = parameters[2];
    feedbackThreshold = parameters[3];
}

float KNNModel::predict(Viewpoint vp)
{
    // Calculate distances to all observations
    distances.clear();

    for (const auto &obs : observations)
    {
        if (std::max(obs.getViewpoint().theta, vp.theta) - std::min(obs.getViewpoint().theta, vp.theta) > distanceThreshold)
            continue; // Skip observations that are too far apart in angle
        if (std::max(obs.getViewpoint().phi, vp.phi) - std::min(obs.getViewpoint().phi, vp.phi) > distanceThreshold)
            continue; // Skip observations that are too far apart in angle
        distances.emplace_back(obs.getViewpoint().distanceTo(vp), obs);
    }

    // Sort by distance
    std::sort(distances.begin(), distances.end(),
              [](const std::pair<float, Observation> &a, const std::pair<float, Observation> &b)
              {
                  return a.first < b.first;
              });

    if (distances.empty())
    {
        return 0.5f; // No valid observations, return default value
    }

    int sumSize = std::min(k, static_cast<int>(distances.size()));
    float sum = 0.0f;
    for (int i = 0; i < sumSize; i++)
    {
        sum += distances[i].second.getStatus();
    }
    return sum / sumSize; // Return average status of neighbors
}

void KNNModel::integrateObservation(Observation observation)
{
    bool nearestSameSet = false;
    bool nearestOppositeSet = false;
    nearestSame = Observation();
    nearestOpposite = Observation();
    for (auto dist : distances)
    {
        if (dist.second.getStatus() == observation.getStatus() && !nearestSameSet)
        {
            nearestSame = dist.second;
            nearestSameSet = true;
        }
        else if (dist.second.getStatus() != observation.getStatus() && !nearestOppositeSet)
        {
            nearestOpposite = dist.second;
            nearestOppositeSet = true;
        }
        if (nearestSameSet && nearestOppositeSet)
        {
            break; // Both nearest observations found
        }
    }
    observations.push_back(observation);
}

void KNNModel::feedback(float value)
{
    if (observations.size() <= numObservations)
    {
        return;
    }

    if (value > feedbackThreshold)
    {
        // Delete the nearest opposite observation if it exists, otherwise the nearest same, otherwise the oldest observation
        if (nearestOpposite.getStatus() != INVALID)
        {
            auto it = std::find_if(observations.begin(), observations.end(),
                                   [&](const Observation &obs)
                                   {
                                       const Viewpoint &vp1 = obs.getViewpoint();
                                       const Viewpoint &vp2 = nearestOpposite.getViewpoint();
                                       return vp1.theta == vp2.theta && vp1.phi == vp2.phi &&
                                              vp1.d == vp2.d && obs.getStatus() == nearestOpposite.getStatus();
                                   });
            if (it != observations.end())
            {
                observations.erase(it);
            }
        }
        else if (nearestSame.getStatus() != INVALID)
        {
            auto it = std::find_if(observations.begin(), observations.end(),
                                   [&](const Observation &obs)
                                   {
                                       const Viewpoint &vp1 = obs.getViewpoint();
                                       const Viewpoint &vp2 = nearestSame.getViewpoint();
                                       return vp1.theta == vp2.theta && vp1.phi == vp2.phi &&
                                              vp1.d == vp2.d && obs.getStatus() == nearestSame.getStatus();
                                   });
            if (it != observations.end())
            {
                observations.erase(it);
            }
        }
        else
        { // Delete the oldest observation
            observations.erase(observations.begin());
        }
    }
    else
    {
        // Delete the newest observation, it didn't change much
        observations.pop_back();
    }
}
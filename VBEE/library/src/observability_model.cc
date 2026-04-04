#include "observability_model.h"
#include "observation.h"
#include "vbee.h"
#include <cstdlib>

#define feature_size 6.0f

extern VBEESettings global_vbee_settings;

float gaussianKernel(float distance, float bandwidth = 0.5f) {
  return expf(-(distance * distance) / (2 * bandwidth * bandwidth));
}

std::vector<std::pair<Observation, float>>
computeWeights(const Viewpoint &viewpoint,
               const std::vector<Observation> &observations) {
  std::vector<std::pair<Observation, float>> weighted_observations;

  for (const auto &observation : observations) {
    float distance = (observation.v - viewpoint).norm();
    weighted_observations.push_back(
        std::make_pair(observation, gaussianKernel(distance)));
  }
  return weighted_observations;
}

float weightedSum(
    const std::vector<std::pair<Observation, float>> &weighted_observations) {
  float sum = 0.0f;
  float weight_sum = 0.0f;

  for (const auto &weighted_observation : weighted_observations) {
    sum += weighted_observation.first.s * weighted_observation.second;
    weight_sum += weighted_observation.second;
  }

  if (weight_sum == 0.0f) {
    return 0.0f;
  }

  return sum / weight_sum;
}

float ObservabilityModel::Estimateish(const Observation &observation) {
  float psge = 0.5f;

  std::vector<Observation> same_hemisphere =
      pastObservationsInSameHemisphere(observation.v);

  same_hemisphere.erase(
      std::remove(same_hemisphere.begin(), same_hemisphere.end(), observation),
      same_hemisphere.end());

  if (same_hemisphere.size() > 0) {
    std::vector<std::pair<Observation, float>> weightedObservations =
        computeWeights(observation.v, same_hemisphere);

    if (weightedObservations.size() > global_vbee_settings.k) {
      std::partial_sort(weightedObservations.begin(),
                        weightedObservations.begin() + global_vbee_settings.k,
                        weightedObservations.end(),
                        [](const std::pair<Observation, float> &a,
                           const std::pair<Observation, float> &b) {
                          return a.second > b.second;
                        });
      weightedObservations.resize(global_vbee_settings.k);
    }
    psge = weightedSum(weightedObservations);
  }

  return std::abs(observation.s - psge);
}

float ObservabilityModel::Estimate(const Observation &observation,
                                   bool doUpdate) {
  float psge = global_vbee_settings.unknown_psge_value;

  std::vector<Observation> same_hemisphere =
      pastObservationsInSameHemisphere(observation.v);

  if (same_hemisphere.size() > 0) {
    std::vector<std::pair<Observation, float>> weightedObservations =
        computeWeights(observation.v, same_hemisphere);
    if (weightedObservations.size() > global_vbee_settings.k) {
      std::partial_sort(weightedObservations.begin(),
                        weightedObservations.begin() + global_vbee_settings.k,
                        weightedObservations.end(),
                        [](const std::pair<Observation, float> &a,
                           const std::pair<Observation, float> &b) {
                          return a.second > b.second;
                        });
      weightedObservations.resize(global_vbee_settings.k);
    }
    psge = weightedSum(weightedObservations);
  }

  if (doUpdate) {
    if (past_observations.size() < global_vbee_settings.n) {
      past_observations.push_back(observation);
    } else {
      std::vector<Observation> influenced_observations =
          pastObservationsInInflucencedArea(observation.v);
      float totalInfluence = 0.0f;
      for (Observation influenced_observation : influenced_observations) {
        bool inner = influenced_observation.v.norm() < observation.v.norm();
        bool old_o = influenced_observation.s == 1.0f;
        bool new_o = observation.s == 1.0f;

        if (inner && old_o && new_o) {
          totalInfluence += influenced_observation.bigPlus();
        } else if (inner && old_o && !new_o) {
          totalInfluence += influenced_observation.smallMinus();
        } else if (inner && !old_o && new_o) {
          totalInfluence += influenced_observation.bigMinus();
        } else if (inner && !old_o && !new_o) {
          totalInfluence += influenced_observation.smallPlus();
        } else if (!inner && old_o && new_o) {
          totalInfluence += influenced_observation.smallPlus();
        } else if (!inner && old_o && !new_o) {
          totalInfluence += influenced_observation.bigMinus();
        } else if (!inner && !old_o && new_o) {
          totalInfluence += influenced_observation.smallMinus();
        } else if (!inner && !old_o && !new_o) {
          totalInfluence += influenced_observation.bigPlus();
        }
      }

      float prob_replace = 1.0f;
      if (influenced_observations.size() > 0)
        prob_replace = totalInfluence / (5 * influenced_observations.size());

      if ((static_cast<float>(rand()) / static_cast<float>(RAND_MAX)) <
          prob_replace) {
        float inv_neededness = 1.0f;
        int least_needed_idx = 0;
        for (int i = 0; i < past_observations.size(); i++) {
          float new_inv_neededness = Estimateish(past_observations[i]);
          if (new_inv_neededness < inv_neededness) {
            inv_neededness = new_inv_neededness;
            least_needed_idx = i;
          }
        }

        past_observations[least_needed_idx] = observation;
      }
    }
  }
  return clampNearZeroOne(psge);
}

void ObservabilityModel::Update(const Observation &observation) {}

std::vector<Observation> ObservabilityModel::pastObservationsInSameHemisphere(
    const Viewpoint &viewpoint) {
  std::vector<Observation> same_hemisphere;

  for (const Observation &past_observation : past_observations) {
    float angle =
        std::acos(viewpoint.normalized().dot(past_observation.v.normalized()));
    if (angle < M_PI / 2.0f) {
      same_hemisphere.push_back(past_observation);
    }
  }

  return same_hemisphere;
}

std::vector<Observation> ObservabilityModel::pastObservationsInInflucencedArea(
    const Viewpoint &viewpoint) {
  std::vector<Observation> influenced_observations;

  float angle_threshold = std::atan((feature_size / 2) / viewpoint.norm());

  for (const Observation &past_observation : past_observations) {
    float angle =
        std::acos(viewpoint.normalized().dot(past_observation.v.normalized()));
    if (angle < angle_threshold) {
      influenced_observations.push_back(past_observation);
    }
  }
  return influenced_observations;
}
#include "vbee.h"

#define OBSERVABILITY_MIN 0.001f
#define OBSERVABILITY_MAX 0.75f

extern VBEESettings global_vbee_settings;

VBEE::VBEE(int mpID) : mpID(mpID) {

  model = ObservabilityModel();

  epe = ExistenceProbabilityEstimator();
  p_e = global_vbee_settings.init_p_e;
};

float VBEE::Update(Observation observation) {
  if (!global_vbee_settings.in_use)
    return 1.0f;

  if (observation.s == 0.0f) {
    seenStatus = NOT_SEEN;
  } else {
    seenStatus = SEEN;
  }

  // If this is a first-time VBEE observation, and it's negative, just return
  if (!beenSeen && observation.s == 0.0f)
    return p_e;

  // // Ensure the observation is from a sufficiently different viewpoint
  // // Note that !beenSeen is sufficient to bypass this check for the first observation
  // if(beenSeen)
  // {
  //   if((last_observer_position - observation.v).norm() <= 0.1f) {
  //     return p_e;
  //   }
  // }

  last_observer_position = observation.v;

  beenSeen = true;

  n_observations++;

  float prior = p_e;

  float model_estimate = std::min(0.999f, std::max(0.001f, model.Estimate(observation)));

  float posterior = epe.Update(observation, prior, model_estimate);

  // float weight = (1.0f - observability) *
  //                global_vbee_settings.observability_damping_coeff *
  //                Sigmoid(n_observations);

  p_e = std::max(global_vbee_settings.p_e_notch, std::min(1 - global_vbee_settings.p_e_notch, posterior));
  // std::min(
  //     0.999f, std::max(0.001f, prior * (1.0f - weight) + posterior * weight));

  // p_e = posterior;

  model.Update(observation);

  return p_e;
}

std::pair<float, float> VBEE::GetPSeenGivenExists(Viewpoint v) {
  // return model.Estimate(v);
  return std::pair<float, float>(0.0f, 0.0f);
}

// float VBEE::Update(Eigen::Vector3f v, bool seen) {
//   float s = seen ? 1.0f : 0.0f;
//   return Update(Observation{.v = v, .s = s}, true);
// }

// float VBEE::Update(Eigen::Vector3f observerPose, Eigen::Vector3f mapPointPose,
//                    bool seen) {
//   return Update((mapPointPose - observerPose).normalized(), seen);
// }

float VBEE::Query(bool ransac) const {
  if (!global_vbee_settings.in_use)
    return 1.0f;
  if (ransac && !global_vbee_settings.weight_ransac)
    return 1.0f;
  return p_e;
}

void VBEE::Merge(VBEE &other) {
  if (!global_vbee_settings.in_use)
    return;

  this->set_observability(std::max(this->observability, other.observability));
  this->set_pe(std::max(this->p_e, other.p_e));
  this->n_observations += other.n_observations;
}

void VBEE::Reset() { p_e = global_vbee_settings.init_p_e; }

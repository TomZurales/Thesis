#pragma once

#include "observation.h"
class ObservabilityModel {

  std::vector<Observation> past_observations;

  std::vector<Observation> pastObservationsInSameHemisphere(const Viewpoint&);
  std::vector<Observation> pastObservationsInInflucencedArea(const Viewpoint&);

public:
  float Estimate(const Observation &observation, bool doUpdate = true);
  float Estimateish(const Observation &observation);

  void Update(const Observation &observation);
};
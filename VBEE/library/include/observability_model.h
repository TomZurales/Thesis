#pragma once

#include "observation.h"
class ObservabilityModel {

public:
  float Estimate(const Observation &observation);

  void Update(const Observation &observation);
};
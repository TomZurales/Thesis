#include "observability_model.h"
#include "vbee.h"

#define feature_size 3.0f

extern VBEESettings global_vbee_settings;

float 
ObservabilityModel::Estimate(const Observation &observation) {
  return 0.5f;
}

void ObservabilityModel::Update(const Observation &observation) {
}
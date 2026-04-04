#include "existence_probability_estimator.h"
#include "vbee.h"

extern VBEESettings global_vbee_settings;

ExistenceProbabilityEstimator::ExistenceProbabilityEstimator() {
  fn = global_vbee_settings.falseNegativeRate; //0.1;
  fp = global_vbee_settings.falsePositiveRate; //0.0001;
}

float ExistenceProbabilityEstimator::Update(Observation o, float prior,
                                            float model_estimate) {
  float posterior;
  if (o.s == 1.0f) {
    float numerator = model_estimate * (1 - global_vbee_settings.falseNegativeRate) * prior;
    float denominator = numerator + (global_vbee_settings.falsePositiveRate * (1 - prior));
    posterior = numerator / denominator;
  } else {
    float numerator = (1 - model_estimate * (1 - global_vbee_settings.falseNegativeRate)) * prior;
    float denominator = numerator + ((1 - global_vbee_settings.falsePositiveRate) * (1 - prior));
    posterior = numerator / denominator;
  }
  return posterior;
}
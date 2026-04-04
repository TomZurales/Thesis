#pragma once

#include "viewpoint.h"

#include <boost/serialization/access.hpp>
#include <boost/serialization/array.hpp>

static float sigmoid(float x) {
  return 1.0f / (1.0f + exp(-0.125 * x));
}
typedef struct Observation_t {
  Viewpoint v;
  float s;
  int step = 0;
  float confidence = sigmoid(step);

  friend class boost::serialization::access;
  template <class Archive>
  void serialize(Archive &ar, const unsigned int /*version*/) {
    ar &boost::serialization::make_array(v.data(), v.size());
    ar & s;
    ar & confidence;
    ar & step;
  }

  float smallPlus() {
    step += 1;
    confidence = sigmoid(step);
    return 0;
  }

  float bigPlus() {
    step += 5;
    confidence = sigmoid(step);
    return 0;
  }

  float smallMinus() {
    step -= 1;
    confidence = sigmoid(step);
    return 1;
  }

  float bigMinus() {
    step -= 5;
    confidence = sigmoid(step);
    return 5;
  }

  bool operator==(const Observation_t& other) const {
    return v == other.v && s == other.s && step == other.step && confidence == other.confidence;
  }

} Observation;
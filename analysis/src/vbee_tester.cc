#include "observability_model.h"
#include "observability_scenario.h"
#include <Eigen/src/Core/Matrix.h>
#include <cstdlib>
#include <ctime>
#include <iostream>
#include "vbee.h"

#define N_TRAIN 10000
#define N_TEST 10000

VBEESettings global_vbee_settings;

const std::string SCENARIOS_FILE = "data/scenarios.bin";

struct TestPoint {
  int id;
  ObservabilityScenario scenario;
  Eigen::Vector3f position;
  ObservabilityModel model;
  ObservabilityModel model_updating;
  std::vector<Eigen::Vector3f> positive_observations;
  std::vector<Eigen::Vector3f> negative_observations;

  float point_prevalence = 0;

  std::vector<float> ground_truth;

  std::vector<float>
      om_predictions; // Predictions generated from the observability model
  std::vector<float> omu_predictions; // Predictions generated from the updating
                                      // observability model
  std::vector<float> pp_predictions;
  std::vector<float> gp_predictions;
  std::vector<std::vector<float>>
      knn_predictions; // Predictions generated from the KNN models
  std::vector<float>
      r_predictions; // "Predictions" generated from the random model

  TestPoint() {
    knn_predictions =
        std::vector<std::vector<float>>(5); // k = {1, 3, 5, 20, 50}
  }

  float getPrevalence() {
    return static_cast<float>(positive_observations.size()) /
           (positive_observations.size() + negative_observations.size());
  }
};

float log_loss(std::vector<float> estimates, std::vector<float> ground_truth) {
  if (estimates.size() != ground_truth.size()) {
    std::cerr << "Estimates and ground truth lengths do not match. Can't "
                 "calculate log loss."
              << std::endl;
    return -1;
  }

  int N = estimates.size();

  float sum = 0;
  for (int i = 0; i < N; i++) {
    float est = std::min(0.99f, std::max(0.01f, estimates[i]));
    sum += (ground_truth[i] * std::log(est)) +
           ((1 - ground_truth[i]) * std::log(1 - est));
  }
  return -1 * (sum / N);
}

float breir(std::vector<float> estimates, std::vector<float> ground_truth) {
  if (estimates.size() != ground_truth.size()) {
    std::cerr << "Estimates and ground truth lengths do not match. Can't "
                 "calculate Breir score."
              << std::endl;
    return -1;
  }

  int N = estimates.size();

  float sum = 0;
  for (int i = 0; i < N; i++) {
    float error = (ground_truth[i] - estimates[i]);
    sum += error * error;
  }
  return sum / N;
}

// Eigen::Vector3f randomPosition() {
//   return Eigen::Vector3f(
//       -5.0f + static_cast<float>(rand()) / static_cast<float>(RAND_MAX) * 10.0f,
//       -5.0f + static_cast<float>(rand()) / static_cast<float>(RAND_MAX) * 10.0f,
//       -5.0f +
//           static_cast<float>(rand()) / static_cast<float>(RAND_MAX) * 10.0f);
// }

int main(int argc, char **argv) {
  global_vbee_settings.n = 5000;
  global_vbee_settings.k = 1;

  srand(static_cast<unsigned int>(time(nullptr)));

  chdir("/home/tom/workspace/Thesis/analysis");

  std::vector<ObservabilityScenario> scenarios;

  for(float blocked_rate = 0.05; blocked_rate < 1.0f; blocked_rate += 0.05)
  {
    scenarios.push_back(ObservabilityScenario(blocked_rate));
  }

  std::cout << "Scenario Creation Done" << std::endl;
  // Set up for the training portion of the experiment
  std::vector<TestPoint> test_points;
  for (int i = 0; i < scenarios.size(); i++) {
    TestPoint tp;
    tp.id = i + 1;
    tp.position = randomPosition();
    tp.scenario = scenarios[i];

    test_points.push_back(tp);
  }

  for (int i = 0; i < N_TRAIN; i++) {
    Eigen::Vector3f test_pos = randomPosition();

    for (auto &test_point : test_points) {
      Eigen::Vector3f viewpoint = test_pos - test_point.position;
      if (test_point.scenario.isInKeepout(viewpoint)) {
        continue;
      }

      Observation obs = {viewpoint,
                         test_point.scenario.isSeen(viewpoint) ? 1.0f : 0.0f};
      test_point.model.Estimate(obs);

      if (test_point.scenario.isSeen(viewpoint)) {
        test_point.positive_observations.push_back(test_pos);
      } else {
        test_point.negative_observations.push_back(test_pos);
      }
    }
  }

  std::cout << "Training Done" << std::endl;

  float global_positive = 0;
  float global_negative = 0;
  for (auto &test_point : test_points) {
    global_positive += test_point.positive_observations.size();
    global_negative += test_point.negative_observations.size();

    if (test_point.positive_observations.size() +
            test_point.negative_observations.size() >
        0) {
      test_point.point_prevalence =
          static_cast<float>(test_point.positive_observations.size()) /
          (test_point.positive_observations.size() +
           test_point.negative_observations.size());
    } else {
      test_point.point_prevalence = 0;
    }
  }
  float global_prevalence =
      global_positive / (global_positive + global_negative);

  // Training portion complete. Set up for the testing portion of the experiment

  for (int i = 0; i < N_TEST; i++) {
    Eigen::Vector3f test_pos = randomPosition();

    for (auto &test_point : test_points) {
      Eigen::Vector3f viewpoint = test_pos - test_point.position;
      if (test_point.scenario.isInKeepout(viewpoint)) {
        continue;
      }

      Observation obs = {viewpoint,
                         test_point.scenario.isSeen(viewpoint) ? 1.0f : 0.0f};

      test_point.ground_truth.push_back(obs.s);

      test_point.om_predictions.push_back(
          test_point.model.Estimate(obs, false));
      test_point.r_predictions.push_back(
          (static_cast<float>(rand()) / static_cast<float>(RAND_MAX)));
      test_point.pp_predictions.push_back(test_point.point_prevalence);
      test_point.gp_predictions.push_back(global_prevalence);
    }
  }

  std::vector<float> all_ground_truth;
  std::vector<float> all_random;
  std::vector<float> all_om;
  std::vector<float> all_omu;
  std::vector<float> all_pp;
  std::vector<float> all_gp;

  for (auto &test_point : test_points) {
    all_ground_truth.insert(all_ground_truth.end(),
                            test_point.ground_truth.begin(),
                            test_point.ground_truth.end());
    all_random.insert(all_random.end(), test_point.r_predictions.begin(),
                      test_point.r_predictions.end());
    all_om.insert(all_om.end(), test_point.om_predictions.begin(),
                  test_point.om_predictions.end());
    all_omu.insert(all_omu.end(), test_point.omu_predictions.begin(),
                   test_point.omu_predictions.end());
    all_pp.insert(all_pp.end(), test_point.pp_predictions.begin(),
                  test_point.pp_predictions.end());
    all_gp.insert(all_gp.end(), test_point.gp_predictions.begin(),
                  test_point.gp_predictions.end());
  }

  std::cout << "Log Losses:" << std::endl;
  std::cout << "  Random: " << log_loss(all_random, all_ground_truth)
            << std::endl;
  std::cout << "  Global Prevalence: " << log_loss(all_gp, all_ground_truth)
            << std::endl;
  std::cout << "  Point Prevalence: " << log_loss(all_pp, all_ground_truth)
            << std::endl;
  std::cout << "  Observability Model: " << log_loss(all_om, all_ground_truth)
            << std::endl;

    std::cout << "Breir Scores:" << std::endl;
  std::cout << "  Random: " << breir(all_random, all_ground_truth)
            << std::endl;
  std::cout << "  Global Prevalence: " << breir(all_gp, all_ground_truth)
            << std::endl;
  std::cout << "  Point Prevalence: " << breir(all_pp, all_ground_truth)
            << std::endl;
  std::cout << "  Observability Model: " << breir(all_om, all_ground_truth)
            << std::endl;

  return 0;
}
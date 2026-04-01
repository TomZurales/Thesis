// Project headers
#include "observability_model.h"
#include "observation.h"
#include "vbee.h"
#include "observability_scenario.h"

// Boost serialization
#include <boost/archive/binary_iarchive.hpp>
#include <boost/archive/binary_oarchive.hpp>
#include <boost/serialization/map.hpp>
#include <boost/serialization/serialization.hpp>
#include <boost/serialization/string.hpp>
#include <boost/serialization/vector.hpp>

// Standard library
#include <fstream>
#include <iostream>
#include <map>
#include <mutex>
#include <set>
#include <thread>
#include <time.h>
#include <utility>

VBEESettings global_vbee_settings;

// Serialization support for Eigen::Vector3f
namespace boost {
namespace serialization {
template <class Archive>
void serialize(Archive &ar, Eigen::Vector3f &v, const unsigned int version) {
  ar & v.x();
  ar & v.y();
  ar & v.z();
}
} // namespace serialization
} // namespace boost

/**
 * Returns the current thread's CPU time in seconds
 */
double getCurrentThreadCpuTime() {
  struct timespec ts;
  clock_gettime(CLOCK_THREAD_CPUTIME_ID, &ts);
  return ts.tv_sec + ts.tv_nsec / 1e9;
}

std::vector<Eigen::Vector3f> viewpoints;

/**
 * Calculate the average error and confidence for a given scenario and model
 * Returns pair of (average_error, average_confidence)
 */
float calculateModelError(const ObservabilityScenario& scenario, ObservabilityModel model) {
  float total_error = 0.0f;

  for (const auto& viewpoint : viewpoints) {
    float seen = scenario.isSeen(viewpoint) ? 1.0f : 0.0f;
    auto estimate = model.Estimate(Observation{viewpoint, seen}, false);

    float error = estimate - seen;
    total_error += (error * error);
  }

  return total_error;
}

constexpr int EXPECTED_ARGC_WITH_PARAMS = 18;

int main(int argc, char **argv) {
  chdir("/home/tom/workspace/Thesis/optimization");
  // Validate command line arguments
  if (argc != 1 && argc != EXPECTED_ARGC_WITH_PARAMS) {
    std::cout << "Incorrect number of arguments." << std::endl;
    return -1;
  }

  // Parse VBEE settings from command line
  global_vbee_settings.in_use = true;
  global_vbee_settings.weight_ransac = false;
  global_vbee_settings.random_sparsification = false;
  global_vbee_settings.fake_eliminations = false;

  if (argc == EXPECTED_ARGC_WITH_PARAMS) {
    global_vbee_settings.n = std::stoi(argv[1]);
    global_vbee_settings.k = std::stoi(argv[2]);
    global_vbee_settings.distance_threshold = std::stof(argv[3]);
    global_vbee_settings.unknown_psge_value = std::stof(argv[4]);
    global_vbee_settings.min_confidence_threshold = std::stof(argv[5]);
    global_vbee_settings.max_error_threshold = std::stof(argv[6]);
    global_vbee_settings.init_p_e = std::stof(argv[7]);
    global_vbee_settings.bad_threshold = std::stof(argv[8]);
    global_vbee_settings.damping_coeff = std::stof(argv[9]);
    global_vbee_settings.init_observability = std::stof(argv[10]);
    global_vbee_settings.observability_damping_coeff = std::stof(argv[11]);
    global_vbee_settings.sigmoid_midpoint = std::stof(argv[12]);
    global_vbee_settings.sigmoid_steepness = std::stof(argv[13]);
    global_vbee_settings.falseNegativeRate = std::stof(argv[14]);
    global_vbee_settings.falsePositiveRate = std::stof(argv[15]);
    global_vbee_settings.p_e_notch = std::stof(argv[16]);
  } else {
    std::cout << "Using default VBEE parameters." << std::endl;
  }
  
  std::string output_filename(argv[17]);
  if(argc == 1)
  {
    output_filename = "test_file";
  }
  
  // Initialize scenario data structures
  std::vector<ObservabilityScenario> scenarios;

  // Load existing scenarios from binary file if available
  std::ifstream scenarios_file("data/scenarios.bin");
  if (scenarios_file.good()) {
    scenarios_file.close();
    std::cout << "Loading scenarios from 'data/scenarios.bin'..." << std::endl;
    
    try {
      std::ifstream ifs("data/scenarios.bin", std::ios::binary);
      boost::archive::binary_iarchive ia(ifs);
      std::vector<ObservabilityScenario> loaded_scenarios;
      ia >> loaded_scenarios;
      
      std::cout << "Successfully loaded " << loaded_scenarios.size()
                << " scenarios from file." << std::endl;

      // Store loaded scenarios and track their rate pairs
      for (const auto &scenario : loaded_scenarios) {
        scenarios.push_back(scenario);
      }
    } catch (const std::exception &e) {
      std::cerr << "Error loading scenarios: " << e.what() << std::endl;
      exit(-1);
    }
  } else {
    std::cout << "Generating Scenarios File" << std::endl;
    for(float blocked_rate = 0.05f; blocked_rate < 1.0f; blocked_rate += 0.05f)
    {
      for(int i = 0; i < 20; i++)
      {
        scenarios.push_back(ObservabilityScenario(blocked_rate));
      }
    }

    std::cout << "Scenarios created. Saving to file." << std::endl;
    try {
      std::ofstream ofs("data/scenarios.bin", std::ios::binary);
      boost::archive::binary_oarchive oa(ofs);
      oa << scenarios;
    } catch (const std::exception &e) {
      std::cerr << "Error saving scenarios: " << e.what() << std::endl;
      exit(-1);
    }
  }

  // Load or generate viewpoints
  std::ifstream viewpoints_file("data/viewpoints.bin");
  if (viewpoints_file.good()) {
    viewpoints_file.close();
    std::cout << "Loading viewpoints from 'data/viewpoints.bin'..." << std::endl;
    
    try {
      std::ifstream ifs("data/viewpoints.bin", std::ios::binary);
      boost::archive::binary_iarchive ia(ifs);
      ia >> viewpoints;
      
      std::cout << "Successfully loaded "
                << viewpoints.size() << "viewpoints from file." << std::endl;
    } catch (const std::exception &e) {
      std::cerr << "Error loading viewpoints: " << e.what() << std::endl;
      exit(-1);
    }
  } else {
    std::cerr << "No viewpoints file found. Creating file" << std::endl;
    for(int i = 0; i < 5000; i++)
    {
      viewpoints.push_back(randomPosition());
    }

    try {
      std::ofstream ofs("data/viewpoints.bin", std::ios::binary);
      boost::archive::binary_oarchive oa(ofs);
      oa << scenarios;
    } catch (const std::exception &e) {
      std::cerr << "Error saving viewpoints: " << e.what() << std::endl;
      exit(-1);
    }
  }


  // Initialize threading and data structures for scenario processing
  std::vector<std::thread> worker_threads;
  std::ofstream results_file(output_filename);

  // Thread-safe data structures for collecting results
  std::mutex scenario_stats_mutex;
  std::mutex stdout_mutex;

  std::vector<float> p_e_error_by_scenario(scenarios.size(), 0.0f);
  std::vector<float> observability_error_by_scenario(scenarios.size(), 0.0f);

  std::atomic<float> p_e_error(0.0f);
  std::atomic<float> observability_error(0.0f);

  // Process each scenario in separate threads
  for (size_t scenario_idx = 0; scenario_idx < scenarios.size(); ++scenario_idx) {
    worker_threads.emplace_back([&scenarios, scenario_idx, &scenario_stats_mutex, 
                                &stdout_mutex, &p_e_error_by_scenario, &observability_error_by_scenario]() {
      const ObservabilityScenario& scenario = scenarios[scenario_idx];
      float this_p_e_error = 0.0f;
      float this_observability_error = 0.0f;
      VBEE vbee(scenario_idx);

      // 1000 observations while the point exists
      for(int i = 0; i < 1000; i++)
      {
        Eigen::Vector3f viewpoint = randomPosition();
        Observation o;
        o.v = viewpoint;
        o.s = scenario.isSeen(viewpoint) ? 1.0f : 0.0f;
        float p_e = vbee.Update(o);
        if(p_e < global_vbee_settings.bad_threshold)
          this_p_e_error += 5.0f;
        else
          this_p_e_error += ((1 - global_vbee_settings.p_e_notch) - p_e) * ((1 - global_vbee_settings.p_e_notch) - p_e);
      }

      this_observability_error = calculateModelError(scenario, vbee.GetObservabilityModel());

      // 1000 observations while the point does not exist
      for(int i = 0; i < 1000; i++)
      {
        Eigen::Vector3f viewpoint = randomPosition();
        Observation o;
        o.v = viewpoint;
        o.s = 0.0f;
        float p_e = vbee.Update(o);
        this_p_e_error += (global_vbee_settings.p_e_notch - p_e) * (global_vbee_settings.p_e_notch - p_e);
        if(p_e < global_vbee_settings.bad_threshold)
        {
          break;
        }
      }

      {
        std::lock_guard<std::mutex> lock(scenario_stats_mutex);
        p_e_error_by_scenario[scenario_idx] = this_p_e_error;
        observability_error_by_scenario[scenario_idx] = this_observability_error;
      }
    });
  }

  // Wait for all threads to complete
  for (auto &thread : worker_threads) {
    thread.join();
  }

  float total_p_e_error = 0.0f;
  float total_observability_error = 0.0f;
  std::ofstream results_by_scenario(output_filename + "_by_scenario.csv");
  for (size_t i = 0; i < scenarios.size(); ++i) {
    total_p_e_error += p_e_error_by_scenario[i];
    total_observability_error += observability_error_by_scenario[i];
    results_by_scenario << p_e_error_by_scenario[i] << ", " << observability_error_by_scenario[i] << std::endl;
  }
  results_by_scenario.close();

  std::ofstream results_output_file(output_filename);
  results_output_file << total_p_e_error << ", " << total_observability_error << std::endl;
  results_output_file.close();
  
  return 0;
}

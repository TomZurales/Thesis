// Project headers
#include "observability_model.h"
#include "observation.h"
#include "vbee.h"
#include "world.h"

// Boost serialization
#include <boost/archive/binary_iarchive.hpp>
#include <boost/archive/binary_oarchive.hpp>
#include <boost/serialization/map.hpp>
#include <boost/serialization/serialization.hpp>
#include <boost/serialization/string.hpp>
#include <boost/serialization/vector.hpp>

// Standard library
#include <chrono>
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

std::map<std::string, std::vector<Observation>> observation_cache;

/**
 * Calculate the average error and confidence for a given world and model
 * Returns pair of (average_error, average_confidence)
 */
float calculateModelError(const World& world, ObservabilityModel model) {
  float total_error = 0.0f;
  
  const std::string world_name = world.getName();
  const auto& observations = observation_cache[world_name];
  const float num_observations = static_cast<float>(observations.size());

  for (const auto& observation : observations) {
    auto estimate = model.Estimate(observation.v);

    float error = std::abs(estimate.first - observation.s);
    total_error += error;
  }

  return total_error;
}

constexpr int EXPECTED_ARGC_WITH_PARAMS = 17;

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
  } else {
    std::cout << "Using default VBEE parameters." << std::endl;
  }
  
  const std::string output_filename(argv[16]);
  
  // Initialize world data structures
  std::vector<World> worlds;
  std::set<std::pair<float, float>> existing_rate_pairs;

  // Load existing worlds from binary file if available
  std::ifstream worlds_file("data/worlds.bin");
  if (worlds_file.good()) {
    worlds_file.close();
    std::cout << "Loading worlds from 'data/worlds.bin'..." << std::endl;
    
    try {
      std::ifstream ifs("data/worlds.bin", std::ios::binary);
      boost::archive::binary_iarchive ia(ifs);
      std::vector<World> loaded_worlds;
      ia >> loaded_worlds;
      
      std::cout << "Successfully loaded " << loaded_worlds.size()
                << " worlds from file." << std::endl;

      // Store loaded worlds and track their rate pairs
      for (const auto &world : loaded_worlds) {
        worlds.push_back(world);
        existing_rate_pairs.insert(world.getRatePair());
      }
    } catch (const std::exception &e) {
      std::cerr << "Error loading worlds: " << e.what() << std::endl;
      exit(-1);
    }
  } else {
    std::cerr << "No worlds file found. Cannot proceed." << std::endl;
    exit(-1);
  }

  // Load or generate world observations
  std::ifstream observations_file("data/world_observations.bin");
  if (observations_file.good()) {
    observations_file.close();
    std::cout << "Loading world observations from 'data/world_observations.bin'..." << std::endl;
    
    try {
      std::ifstream ifs("data/world_observations.bin", std::ios::binary);
      boost::archive::binary_iarchive ia(ifs);
      ia >> observation_cache;
      
      std::cout << "Successfully loaded observations for "
                << observation_cache.size() << " worlds from file." << std::endl;
    } catch (const std::exception &e) {
      std::cerr << "Error loading world observations: " << e.what() << std::endl;
      exit(-1);
    }
  } else {
    std::cerr << "No world observations file found. Cannot proceed." << std::endl;
    exit(-1);
  }


  // Initialize threading and data structures for world processing
  std::vector<std::thread> worker_threads;
  std::ofstream results_file(output_filename);

  // Thread-safe data structures for collecting results
  std::mutex world_stats_mutex;
  std::mutex stdout_mutex;

  std::vector<float> p_e_error_by_world(worlds.size(), 0.0f);
  std::vector<float> observability_error_by_world(worlds.size(), 0.0f);

  std::atomic<float> p_e_error(0.0f);
  std::atomic<float> observability_error(0.0f);

  // Process each world in separate threads
  for (size_t world_idx = 0; world_idx < worlds.size(); ++world_idx) {
    worker_threads.emplace_back([&worlds, world_idx, &world_stats_mutex, 
                                &stdout_mutex, &p_e_error_by_world, &observability_error_by_world]() {
      const World& world = worlds[world_idx];
      float this_p_e_error = 0.0f;
      float this_observability_error = 0.0f;
      VBEE vbee(world_idx);

      // 1000 observations while the point exists
      for(int i = 0; i < 1000; i++)
      {
        Eigen::Vector3f viewpoint = world.getRandomValidViewpoint();
        bool seen = world.isSeen(viewpoint);
        float p_e = vbee.Update(Observation{viewpoint, seen ? 1.0f : 0.0f}, true);
        this_p_e_error += std::abs(1 - p_e);
      }

      this_observability_error = calculateModelError(world, vbee.GetObservabilityModel());

      // 1000 observations while the point does not exist
      for(int i = 0; i < 1000; i++)
      {
        Eigen::Vector3f viewpoint = world.getRandomValidViewpoint();
        float p_e = vbee.Update(Observation{viewpoint, 0.0f}, true);
        this_p_e_error += std::abs(0 - p_e);
      }

      {
        std::lock_guard<std::mutex> lock(world_stats_mutex);
        p_e_error_by_world[world_idx] = this_p_e_error;
        observability_error_by_world[world_idx] = this_observability_error;
      }
    });
  }

  // Wait for all threads to complete
  for (auto &thread : worker_threads) {
    thread.join();
  }

  float total_p_e_error = 0.0f;
  float total_observability_error = 0.0f;
  std::ofstream results_by_world(output_filename + "_by_world.csv");
  for (size_t i = 0; i < worlds.size(); ++i) {
    total_p_e_error += p_e_error_by_world[i];
    total_observability_error += observability_error_by_world[i];
    results_by_world << p_e_error_by_world[i] << ", " << observability_error_by_world[i] << std::endl;
  }
  results_by_world.close();

  std::ofstream results_output_file(output_filename);
  results_output_file << total_p_e_error << ", " << total_observability_error << std::endl;
  results_output_file.close();
  
  return 0;
}

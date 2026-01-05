#include <chrono>
#include <cstdlib>
#include <fcntl.h>
#include <fstream>
#include <iostream>
#include <ostream>
#include <unistd.h>
#include <vector>
#include <yaml-cpp/yaml.h>

#include <opencv2/core/core.hpp>

#include "System.h"

#include "MapPoint.h"
#include "TrackedStats.h"
#include "vbee.h"

using namespace std;

char* _thesis_root = getenv("THESIS_ROOT");
char* _thesis_runtime_root = getenv("THESIS_RUNTIME_ROOT");

void LoadImages(const string &strPathLeft, const string &strPathRight,
                const string &strPathTimes, vector<string> &vstrImageLeft,
                vector<string> &vstrImageRight, vector<double> &vTimeStamps);

VBEESettings global_vbee_settings;
TrackedStats global_tracked_stats;

int main(int argc, char **argv) {
  if (argc != 2) {
    std::cerr
        << "This program should be run through the run_tests script. Exiting."
        << std::endl;
    exit(1);
  }

  if(!_thesis_root || !_thesis_runtime_root) {
    std::cerr << "Please set THESIS_ROOT and THESIS_RUNTIME_ROOT "
                 "environment variables."
              << std::endl;
    exit(1);
  }

  std::string thesis_root = std::string(_thesis_root);
  std::string thesis_runtime_root = std::string(_thesis_runtime_root);

  bool use_viewer = false;
  std::ifstream viewer_file("use_viewer");
  if (viewer_file.good()) {
    use_viewer = true;
  }
  viewer_file.close();

  // Override to always use viewer for debugging
  use_viewer = true;

  {
    int fd = open("heartbeat.txt", O_WRONLY | O_CREAT | O_TRUNC, 0644);
    write(fd, "-1", 2);
    close(fd);
  }

  std::string dataset;
  std::string mode;

  try {
    YAML::Node config = YAML::LoadFile(argv[1]);

    dataset = config["dataset"].as<std::string>();
    mode = config["mode"].as<std::string>();

    global_vbee_settings.in_use = (mode != "baseline");
    global_vbee_settings.weight_ransac = (mode == "vbee_ransac");
    global_vbee_settings.random_sparsification =
        (mode == "random_cull" || mode == "random_cull_fake");
    global_vbee_settings.fake_eliminations =
        (mode == "vbee_fake" || mode == "random_cull_fake");

    global_vbee_settings.n = config["n"].as<int>();
    global_vbee_settings.k = config["k"].as<int>();
    global_vbee_settings.distance_threshold =
        config["distance_threshold"].as<float>();
    global_vbee_settings.unknown_psge_value =
        config["unknown_psge_value"].as<float>();
    global_vbee_settings.min_confidence_threshold =
        config["min_confidence_threshold"].as<float>();
    global_vbee_settings.max_error_threshold =
        config["max_error_threshold"].as<float>();
    global_vbee_settings.init_p_e = config["init_p_e"].as<float>();
    global_vbee_settings.bad_threshold = config["bad_threshold"].as<float>();
    global_vbee_settings.damping_coeff = config["damping_coeff"].as<float>();
    global_vbee_settings.init_observability =
        config["init_observability"].as<float>();
    global_vbee_settings.observability_damping_coeff =
        config["observability_damping_coeff"].as<float>();
    global_vbee_settings.sigmoid_midpoint =
        config["sigmoid_midpoint"].as<double>();
    global_vbee_settings.sigmoid_steepness =
        config["sigmoid_steepness"].as<double>();
    global_vbee_settings.falseNegativeRate =
        config["falseNegativeRate"].as<double>();
    global_vbee_settings.falsePositiveRate =
        config["falsePositiveRate"].as<double>();

  } catch (const YAML::Exception &e) {
    std::cerr << "Failed to parse YAML file: " << e.what() << std::endl;
    exit(1);
  }

  std::cout << "Loaded Configuration" << std::endl;
  std::cout << "Dataset: " << dataset << std::endl;
  std::cout << "Mode: " << mode << std::endl;
  std::cout << "VBEE in use: " << (global_vbee_settings.in_use ? "Yes" : "No")
            << std::endl;
  std::cout << "VBEE with RANSAC: "
            << (global_vbee_settings.weight_ransac ? "Yes" : "No") << std::endl;
  std::cout << "Random Sparsification: "
            << (global_vbee_settings.random_sparsification ? "Yes" : "No")
            << std::endl;
  std::cout << "Fake Eliminations: "
            << (global_vbee_settings.fake_eliminations ? "Yes" : "No")
            << std::endl
            << std::endl;

  if (global_vbee_settings.in_use) {
    std::cout << "VBEE Settings:" << std::endl;
    std::cout << "n: " << global_vbee_settings.n << std::endl;
    std::cout << "k: " << global_vbee_settings.k << std::endl;
    std::cout << "distance_threshold: "
              << global_vbee_settings.distance_threshold << std::endl;
    std::cout << "unknown_psge_value: "
              << global_vbee_settings.unknown_psge_value << std::endl;
    std::cout << "min_confidence_threshold: "
              << global_vbee_settings.min_confidence_threshold << std::endl;
    std::cout << "max_error_threshold: "
              << global_vbee_settings.max_error_threshold << std::endl;
    std::cout << "init_p_e: " << global_vbee_settings.init_p_e << std::endl;
    std::cout << "bad_threshold: " << global_vbee_settings.bad_threshold
              << std::endl;
    std::cout << "damping_coeff: " << global_vbee_settings.damping_coeff
              << std::endl;
    std::cout << "init_observability: "
              << global_vbee_settings.init_observability << std::endl;
    std::cout << "observability_damping_coeff: "
              << global_vbee_settings.observability_damping_coeff << std::endl;
    std::cout << "sigmoid_midpoint: " << global_vbee_settings.sigmoid_midpoint
              << std::endl;
    std::cout << "sigmoid_steepness: " << global_vbee_settings.sigmoid_steepness
              << std::endl;
    std::cout << "falseNegativeRate: " << global_vbee_settings.falseNegativeRate
              << std::endl;
    std::cout << "falsePositiveRate: " << global_vbee_settings.falsePositiveRate
              << std::endl;
    std::cout << std::endl;
  }

  // Load all sequences:
  int seq;
  vector<vector<string>> vstrImageLeft;
  vector<vector<string>> vstrImageRight;
  vector<vector<double>> vTimestampsCam;
  vector<int> nImages;

  vstrImageLeft.resize(1);
  vstrImageRight.resize(1);
  vTimestampsCam.resize(1);
  nImages.resize(1);

  std::vector<double> split_stamps;

  int tot_images = 0;
  for (seq = 0; seq < 1; seq++) {
    string pathCam0 = thesis_root + "/datasets/" + dataset + "/mav0/cam0/data";
    string pathCam1 = thesis_root + "/datasets/" + dataset + "/mav0/cam1/data";

    string pathTimeStamps =
        thesis_root + "/datasets/" + dataset + "/timestamps.txt";

    LoadImages(pathCam0, pathCam1, pathTimeStamps, vstrImageLeft[seq],
               vstrImageRight[seq], vTimestampsCam[seq]);

    nImages[seq] = vstrImageLeft[seq].size();
    tot_images += nImages[seq];

    string pathSplits = thesis_root + "/datasets/" + dataset + "/splits.txt";
    ifstream fSplits(pathSplits);
    if (fSplits.is_open()) {
      string line;
      while (getline(fSplits, line)) {
        if (!line.empty()) {
          try {
            double stamp = stod(line) / 1e9;
            split_stamps.push_back(stamp);
          } catch (const std::exception &) {
            // Skip lines that cannot be converted to long
          }
        }
      }
      fSplits.close();
    }
  }

  // Vector for tracking time statistics
  vector<float> vTimesTrack;
  vTimesTrack.resize(tot_images);

  std::string settings_file = thesis_runtime_root + "/.aux/EuRoC.yaml";

  if (dataset == "all_days" || dataset == "small_skips" ||
      dataset == "big_skip")
    settings_file = thesis_runtime_root + "/.aux/VBEE.yaml";

  // Create SLAM system. It initializes all system threads and gets ready to
  // process frames.
  ORB_SLAM3::System SLAM(thesis_runtime_root + "/.aux/ORBvoc.txt",
                         settings_file, ORB_SLAM3::System::STEREO, true,
                         false, false);

  cv::Mat imLeft, imRight;
  for (seq = 0; seq < 1; seq++) {

    // Seq loop
    double t_resize = 0;
    double t_rect = 0;
    double t_track = 0;
    int num_rect = 0;
    int proccIm = 0;
    for (int ni = 0; ni < nImages[seq]; ni++, proccIm++) {
      if (proccIm % 20 == 0) {
        int fd = open("heartbeat.txt", O_WRONLY | O_CREAT | O_TRUNC, 0644);
        write(fd, "1", 1);
        close(fd);
      }

      // Read left and right images from file
      imLeft = cv::imread(vstrImageLeft[seq][ni],
                          cv::IMREAD_UNCHANGED); //,cv::IMREAD_UNCHANGED);
      imRight = cv::imread(vstrImageRight[seq][ni],
                           cv::IMREAD_UNCHANGED); //,cv::IMREAD_UNCHANGED);

      if (imLeft.empty()) {
        cerr << endl
             << "Failed to load image at: " << string(vstrImageLeft[seq][ni])
             << endl;
        return 1;
      }

      if (imRight.empty()) {
        cerr << endl
             << "Failed to load image at: " << string(vstrImageRight[seq][ni])
             << endl;
        return 1;
      }

      double tframe = vTimestampsCam[seq][ni];

#ifdef COMPILEDWITHC11
      std::chrono::steady_clock::time_point t1 =
          std::chrono::steady_clock::now();
#else
      std::chrono::steady_clock::time_point t1 =
          std::chrono::steady_clock::now();
#endif

      // Pass the images to the SLAM system
      SLAM.TrackStereo(imLeft, imRight, tframe, vector<ORB_SLAM3::IMU::Point>(),
                       vstrImageLeft[seq][ni]);

      if (std::find(split_stamps.begin(), split_stamps.end(), tframe) !=
          split_stamps.end()) {

        double cull_count = 0.0;
        double total_mps = 0.0;
        std::vector<ORB_SLAM3::Map *> vpMaps = SLAM.mpAtlas->GetAllMaps();
        for (ORB_SLAM3::Map *pMap : vpMaps) {
          for (ORB_SLAM3::MapPoint *pMP : pMap->GetAllMapPoints()) {
            if (pMP->isBad() || pMP->IsFakeBad())
              continue;

            total_mps = total_mps + 1.0;
            // If the point is from a previous map, and we're below the bad
            // threshold, eliminate it
            if (pMP->vbee.Query() < global_vbee_settings.bad_threshold) {

              // If we're doing random sparsification, just count it towards the
              // cull count. Otherwise, do a proper elimination.
              if (global_vbee_settings.random_sparsification) {
                cull_count = cull_count + 1.0;
              } else {
                global_tracked_stats.AddElimination(pMP->mnId);
                // Decide whether to do a fake elimination or a real one
                if (global_vbee_settings.fake_eliminations) {
                  pMP->SetFakeBadFlag();
                } else {
                  pMP->SetBadFlag();
                }
                pMP->SetVBEEEliminated();
              }
            }
          }
        }

        if (global_vbee_settings.random_sparsification && cull_count > 0.1) {
          double elimination_ratio = cull_count / total_mps;

          std::cout << "Random Sparsification culling " << cull_count
                    << " out of " << total_mps << " map points ("
                    << elimination_ratio * 100.0 << "%) at time " << tframe
                    << std::endl;

          std::vector<ORB_SLAM3::Map *> vpMaps = SLAM.mpAtlas->GetAllMaps();
          for (ORB_SLAM3::Map *pMap : vpMaps) {
            for (ORB_SLAM3::MapPoint *pMP : pMap->GetAllMapPoints()) {
              if (pMP->isBad() || pMP->IsFakeBad())
                continue;

              double rand_val = static_cast<double>(rand()) / RAND_MAX;
              if (rand_val < elimination_ratio) {
                global_tracked_stats.AddElimination(pMP->mnId);
                if (global_vbee_settings.fake_eliminations) {
                  pMP->SetFakeBadFlag();
                } else {
                  pMP->SetBadFlag();
                }
                pMP->SetVBEEEliminated();
              }
            }
          }
        }
      }

#ifdef COMPILEDWITHC11
      std::chrono::steady_clock::time_point t2 =
          std::chrono::steady_clock::now();
#else
      std::chrono::steady_clock::time_point t2 =
          std::chrono::steady_clock::now();
#endif

#ifdef REGISTER_TIMES
      t_track =
          t_resize + t_rect +
          std::chrono::duration_cast<std::chrono::duration<double, std::milli>>(
              t2 - t1)
              .count();
      SLAM.InsertTrackTime(t_track);
#endif

      double ttrack =
          std::chrono::duration_cast<std::chrono::duration<double>>(t2 - t1)
              .count();

      vTimesTrack[ni] = ttrack;

      // Wait to load the next frame
      double T = 0;
      if (ni < nImages[seq] - 1)
        T = vTimestampsCam[seq][ni + 1] - tframe;
      else if (ni > 0)
        T = tframe - vTimestampsCam[seq][ni - 1];

      if (ttrack < T)
        usleep((T - ttrack) * 1e6); // 1e6
    }

    if (seq < 1 - 1) {
      cout << "Changing the dataset" << endl;

      SLAM.ChangeDataset();
    }
  }

  global_tracked_stats.setNumMaps(SLAM.mpAtlas->GetAllMaps().size());
  global_tracked_stats.setNumKeyFrames(
      SLAM.mpAtlas->GetCurrentMap()->KeyFramesInMap());
  global_tracked_stats.setNumMapPoints(
      SLAM.mpAtlas->GetCurrentMap()->MapPointsInMap());

  // Stop all threads
  SLAM.Shutdown();

  // Save camera trajectory
  SLAM.SaveTrajectoryEuRoC("CameraTrajectory.txt");
  SLAM.SaveKeyFrameTrajectoryEuRoC("KeyFrameTrajectory.txt");
  global_tracked_stats.writeToFile("TrackedStats.csv");

  return 0;
}

void LoadImages(const string &strPathLeft, const string &strPathRight,
                const string &strPathTimes, vector<string> &vstrImageLeft,
                vector<string> &vstrImageRight, vector<double> &vTimeStamps) {
  ifstream fTimes;
  fTimes.open(strPathTimes.c_str());
  vTimeStamps.reserve(5000);
  vstrImageLeft.reserve(5000);
  vstrImageRight.reserve(5000);
  while (!fTimes.eof()) {
    string s;
    getline(fTimes, s);
    if (!s.empty()) {
      stringstream ss;
      ss << s;
      vstrImageLeft.push_back(strPathLeft + "/" + ss.str() + ".png");
      vstrImageRight.push_back(strPathRight + "/" + ss.str() + ".png");
      double t;
      ss >> t;
      vTimeStamps.push_back(t / 1e9);
    }
  }
}

#pragma once

#include <atomic>
#include <fstream>
#include <mutex>
#include <set>

class TrackedStats {
    std::atomic<double> track_times_sec_sum{0.0};
    std::atomic<int> n_track{0};

    std::atomic<double> relocalization_times_sec_sum{0.0};
    std::atomic<int> n_relocalization{0};

    std::atomic<double> loop_closure_times_sec_sum{0.0};
    std::atomic<int> n_loop_closure{0};

    std::atomic<int> n_eliminations{0};
    std::atomic<int> n_bad_eliminations{0};

    std::mutex mtx_eliminations;
    std::set<unsigned long> eliminated_mappoint_ids;

    std::mutex mtx_bad_eliminations;
    std::set<unsigned long> bad_eliminated_mappoint_ids;

    std::mutex mtx_cull_count;
    std::set<unsigned long> cull_count_ids;
    std::atomic<int> cull_count{0};

    std::atomic<int> num_maps{0};
    std::atomic<int> num_keyframes{0};
    std::atomic<int> num_mappoints{0};

public:
    void setNumMaps(int num) {
        num_maps = num;
    }

    void setNumKeyFrames(int num) {
        num_keyframes = num;
    }

    void setNumMapPoints(int num) {
        num_mappoints = num;
    }

    void AddTrackTime(double time_sec) {
        track_times_sec_sum = track_times_sec_sum + time_sec;
        n_track++;
    }

    void AddRelocalizationTime(double time_sec) {
        relocalization_times_sec_sum = relocalization_times_sec_sum + time_sec;
        n_relocalization++;
    }

    void AddLoopClosureTime(double time_sec) {
        loop_closure_times_sec_sum = loop_closure_times_sec_sum + time_sec;
        n_loop_closure++;
    }

    void AddElimination(unsigned long mappoint_id) {
        {
            std::lock_guard<std::mutex> lock(mtx_eliminations);
            if (eliminated_mappoint_ids.find(mappoint_id) != eliminated_mappoint_ids.end()) {
                return; // Already counted
            }
            eliminated_mappoint_ids.insert(mappoint_id);
        }
        n_eliminations++;
    }

    void AddPointToCullCount(unsigned long mappoint_id) {
        {
            std::lock_guard<std::mutex> lock(mtx_cull_count);
            if (cull_count_ids.find(mappoint_id) != cull_count_ids.end()) {
                return; // Already counted
            }
            cull_count_ids.insert(mappoint_id);
        }
        cull_count++;
    }
    
    int GetCullCount() {
        return cull_count.load();
    }

    void ResetCullCount() {
        cull_count = 0;
    }

    void AddBadElimination(unsigned long mappoint_id) {
        {
            std::lock_guard<std::mutex> lock(mtx_bad_eliminations);
            if (bad_eliminated_mappoint_ids.find(mappoint_id) != bad_eliminated_mappoint_ids.end()) {
                return; // Already counted
            }
            bad_eliminated_mappoint_ids.insert(mappoint_id);
        }
        n_bad_eliminations++;
    }

    void writeToFile(std::string filename) const {
        std::ofstream file(filename);
        if(!file.is_open()) {
            throw std::runtime_error("Could not open file to write TrackedStats");
        }
        file << "avg_track_time_sec,n_track,avg_relocalization_time_sec,n_relocalization,avg_loop_closure_time_sec,n_loop_closure,n_good_eliminations,n_bad_eliminations,num_maps,num_keyframes,num_mappoints\n";
        double avg_track_time = n_track > 0 ? track_times_sec_sum / n_track : 0.0;
        double avg_relocalization_time = n_relocalization > 0 ? relocalization_times_sec_sum / n_relocalization : 0.0;
        double avg_loop_closure_time = n_loop_closure > 0 ? loop_closure_times_sec_sum / n_loop_closure : 0.0;
        file << avg_track_time << ","
            << n_track << ","
            << avg_relocalization_time << ","
            << n_relocalization << ","
            << avg_loop_closure_time << ","
            << n_loop_closure << ","
            << n_eliminations.load() - n_bad_eliminations.load() << ","
            << n_bad_eliminations.load() << ","
            << num_maps.load() << ","
            << num_keyframes.load() << ","
            << num_mappoints.load() << "\n";
    }
};
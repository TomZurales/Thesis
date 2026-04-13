#include <algorithm>
#include <gtest/gtest.h>
#include <iostream>
#include <random>

#include "observation.h"
#include "vbee.h"

VBEESettings global_vbee_settings;

TEST(VBEE, Initialization) {
    global_vbee_settings.in_use = true;
    VBEE vbee(1);
    EXPECT_DOUBLE_EQ(vbee.Query(), global_vbee_settings.init_p_e);
}

TEST(VBEE, PositiveObservations) {
    global_vbee_settings.in_use = true;
    VBEE vbee(1);
    Observation obs;
    obs.v = Eigen::Vector3f::Random();
    obs.s = 1.0f;
    vbee.Update(obs);
    double p_e = vbee.Query();
    std::cout << "p_e after positive observation: " << p_e << std::endl;
    EXPECT_GT(p_e, global_vbee_settings.init_p_e);
}

TEST(VBEE, NegativeObservations) {
    global_vbee_settings.in_use = true;
    VBEE vbee(1);
    Observation obs;
    obs.v = Eigen::Vector3f::Random();
    obs.s = -1.0f;
    vbee.Update(obs);
    double p_e = vbee.Query();
    std::cout << "p_e after negative observation: " << p_e << std::endl;
    EXPECT_LT(p_e, global_vbee_settings.init_p_e);
}

TEST(VBEE, MixedObservations) {
    global_vbee_settings.in_use = true;
    VBEE vbee(1);

    std::vector<Observation> observations;
    for (int i = 0; i < 5; i++) {
        Observation obs;
        obs.v = Eigen::Vector3f(0, 5, 0) + (Eigen::Vector3f::Random().normalized() * 0.1f);
        obs.s = 1.0f;
        observations.push_back(obs);
    }
    for (int i = 0; i < 10; i++) {
        Observation obs;
        obs.v = Eigen::Vector3f(0, -5, 0) + (Eigen::Vector3f::Random().normalized() * 0.1f);
        obs.s = -1.0f;
        observations.push_back(obs);
    }

    std::shuffle(observations.begin(), observations.end(), std::mt19937{std::random_device{}()});
    for (const auto& obs : observations) {
        vbee.Update(obs);
    }

    double p_e = vbee.Query();
    std::cout << "p_e after mixed observations: " << p_e << std::endl;

    vbee.Update({Eigen::Vector3f(0, 5, 0) + (Eigen::Vector3f::Random().normalized() * 0.1f), -1.0f});
    vbee.Update({Eigen::Vector3f(0, 5, 0) + (Eigen::Vector3f::Random().normalized() * 0.1f), -1.0f});
    vbee.Update({Eigen::Vector3f(0, 5, 0) + (Eigen::Vector3f::Random().normalized() * 0.1f), -1.0f});
    vbee.Update({Eigen::Vector3f(0, 5, 0) + (Eigen::Vector3f::Random().normalized() * 0.1f), -1.0f});
    vbee.Update({Eigen::Vector3f(0, 5, 0) + (Eigen::Vector3f::Random().normalized() * 0.1f), -1.0f});
    vbee.Update({Eigen::Vector3f(0, 5, 0) + (Eigen::Vector3f::Random().normalized() * 0.1f), -1.0f});
    vbee.Update({Eigen::Vector3f(0, 5, 0) + (Eigen::Vector3f::Random().normalized() * 0.1f), -1.0f});
    vbee.Update({Eigen::Vector3f(0, 5, 0) + (Eigen::Vector3f::Random().normalized() * 0.1f), -1.0f});
    vbee.Update({Eigen::Vector3f(0, 5, 0) + (Eigen::Vector3f::Random().normalized() * 0.1f), -1.0f});
    vbee.Update({Eigen::Vector3f(0, 5, 0) + (Eigen::Vector3f::Random().normalized() * 0.1f), -1.0f});
    vbee.Update({Eigen::Vector3f(0, 5, 0) + (Eigen::Vector3f::Random().normalized() * 0.1f), -1.0f});
    vbee.Update({Eigen::Vector3f(0, 5, 0) + (Eigen::Vector3f::Random().normalized() * 0.1f), -1.0f});
    vbee.Update({Eigen::Vector3f(0, 5, 0) + (Eigen::Vector3f::Random().normalized() * 0.1f), -1.0f});
    vbee.Update({Eigen::Vector3f(0, 5, 0) + (Eigen::Vector3f::Random().normalized() * 0.1f), -1.0f});
    vbee.Update({Eigen::Vector3f(0, 5, 0) + (Eigen::Vector3f::Random().normalized() * 0.1f), -1.0f});
    vbee.Update({Eigen::Vector3f(0, 5, 0) + (Eigen::Vector3f::Random().normalized() * 0.1f), -1.0f});
    vbee.Update({Eigen::Vector3f(0, 5, 0) + (Eigen::Vector3f::Random().normalized() * 0.1f), -1.0f});
    vbee.Update({Eigen::Vector3f(0, 5, 0) + (Eigen::Vector3f::Random().normalized() * 0.1f), -1.0f});
    vbee.Update({Eigen::Vector3f(0, 5, 0) + (Eigen::Vector3f::Random().normalized() * 0.1f), -1.0f});
    vbee.Update({Eigen::Vector3f(0, 5, 0) + (Eigen::Vector3f::Random().normalized() * 0.1f), -1.0f});
    vbee.Update({Eigen::Vector3f(0, 5, 0) + (Eigen::Vector3f::Random().normalized() * 0.1f), -1.0f});
    vbee.Update({Eigen::Vector3f(0, 5, 0) + (Eigen::Vector3f::Random().normalized() * 0.1f), -1.0f});
    vbee.Update({Eigen::Vector3f(0, 5, 0) + (Eigen::Vector3f::Random().normalized() * 0.1f), -1.0f});
    vbee.Update({Eigen::Vector3f(0, 5, 0) + (Eigen::Vector3f::Random().normalized() * 0.1f), -1.0f});
    vbee.Update({Eigen::Vector3f(0, 5, 0) + (Eigen::Vector3f::Random().normalized() * 0.1f), -1.0f});
    vbee.Update({Eigen::Vector3f(0, 5, 0) + (Eigen::Vector3f::Random().normalized() * 0.1f), -1.0f});
    vbee.Update({Eigen::Vector3f(0, 5, 0) + (Eigen::Vector3f::Random().normalized() * 0.1f), -1.0f});
    vbee.Update({Eigen::Vector3f(0, 5, 0) + (Eigen::Vector3f::Random().normalized() * 0.1f), -1.0f});
    vbee.Update({Eigen::Vector3f(0, 5, 0) + (Eigen::Vector3f::Random().normalized() * 0.1f), -1.0f});
    vbee.Update({Eigen::Vector3f(0, 5, 0) + (Eigen::Vector3f::Random().normalized() * 0.1f), -1.0f});
    vbee.Update({Eigen::Vector3f(0, 5, 0) + (Eigen::Vector3f::Random().normalized() * 0.1f), -1.0f});
    vbee.Update({Eigen::Vector3f(0, 5, 0) + (Eigen::Vector3f::Random().normalized() * 0.1f), -1.0f});
    vbee.Update({Eigen::Vector3f(0, 5, 0) + (Eigen::Vector3f::Random().normalized() * 0.1f), -1.0f});
    vbee.Update({Eigen::Vector3f(0, 5, 0) + (Eigen::Vector3f::Random().normalized() * 0.1f), -1.0f});
    vbee.Update({Eigen::Vector3f(0, 5, 0) + (Eigen::Vector3f::Random().normalized() * 0.1f), -1.0f});
    vbee.Update({Eigen::Vector3f(0, 5, 0) + (Eigen::Vector3f::Random().normalized() * 0.1f), -1.0f});
    vbee.Update({Eigen::Vector3f(0, 5, 0) + (Eigen::Vector3f::Random().normalized() * 0.1f), -1.0f});
    vbee.Update({Eigen::Vector3f(0, 5, 0) + (Eigen::Vector3f::Random().normalized() * 0.1f), -1.0f});
    vbee.Update({Eigen::Vector3f(0, 5, 0) + (Eigen::Vector3f::Random().normalized() * 0.1f), -1.0f});
    vbee.Update({Eigen::Vector3f(0, 5, 0) + (Eigen::Vector3f::Random().normalized() * 0.1f), -1.0f});
    vbee.Update({Eigen::Vector3f(0, 5, 0) + (Eigen::Vector3f::Random().normalized() * 0.1f), -1.0f});
    vbee.Update({Eigen::Vector3f(0, 5, 0) + (Eigen::Vector3f::Random().normalized() * 0.1f), -1.0f});
    vbee.Update({Eigen::Vector3f(0, 5, 0) + (Eigen::Vector3f::Random().normalized() * 0.1f), -1.0f});
    p_e = vbee.Query();
    std::cout << "p_e after negative observation: " << p_e << std::endl;

    EXPECT_LT(p_e, global_vbee_settings.init_p_e);
}
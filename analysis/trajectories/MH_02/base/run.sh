#!/bin/bash

SYSTEM_DIR=../../../../slam_systems/ORB_SLAM3_Base
BIN_DIR=$SYSTEM_DIR/Examples/Stereo
DATASETS_DIR=../../../../datasets

SLAM=$BIN_DIR/stereo_euroc
VOCAB=$SYSTEM_DIR/Vocabulary/ORBvoc.txt
SETTINGS=$BIN_DIR/EuRoC.yaml
DATASET=$DATASETS_DIR/EuRoC/MH_02
STAMPS=$DATASETS_DIR/EuRoC/MH_02/timestamps.txt

$SLAM $VOCAB $SETTINGS $DATASET $STAMPS

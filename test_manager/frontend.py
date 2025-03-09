import os
import streamlit as st
from backend import *

slam_system = st.selectbox("Select SLAM System", get_all_slam_systems(), placeholder="Select SLAM System")

if verify_slam_system(slam_system):
    config = 
else:
    print("Invalid SLAM System")

st.selectbox("Select Configuration", get_slam_system_configs(slam_system))


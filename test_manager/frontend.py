# from typing import List
# import dearpygui.dearpygui as dpg
# import dearpygui.demo as demo
# import os

# def get_slam_systems() -> List[str]:
#     # return all top level directories in the slam_systems directory
#     slam_systems = []
#     slam_systems_dir = os.path.join(os.path.dirname(__file__), "../slam_systems")
#     for item in os.listdir(slam_systems_dir):
#         if os.path.isdir(os.path.join(slam_systems_dir, item)):
#             slam_systems.append(item)
#     return slam_systems
    
# page = 0

# def save_callback():
#     global page
#     print("Save Clicked")
#     page = page + 1

# dpg.create_context()
# dpg.create_viewport(title="Test Manager", width=800, height=600)
# dpg.setup_dearpygui()
# demo.show_demo()


# with dpg.window(label="Test Manager", tag="Primary Window"):
#     if page == 0:
#         dpg.add_combo(label="SLAM System", items=get_slam_systems(), tag="slam_system_combo")
#     if page == 1:
#         dpg.add_input_text(label="Config Name", tag="config_name_input")
#     dpg.add_button(label="Save", callback=save_callback)

# dpg.show_viewport()

# dpg.set_primary_window("Primary Window", True)

# dpg.start_dearpygui()
# dpg.destroy_context()

import os
import streamlit as st
from backend import *

slam_system = st.selectbox("Select SLAM System", get_all_slam_systems(), placeholder="Select SLAM System")

if verify_slam_system(slam_system):
    print("Valid SLAM System")
else:
    print("Invalid SLAM System")

st.selectbox("Select Configuration", get_slam_system_configs(slam_system))


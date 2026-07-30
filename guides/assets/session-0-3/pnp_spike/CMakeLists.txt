cmake_minimum_required(VERSION 3.8)
project(pnp_spike)

if(CMAKE_CXX_COMPILER_ID MATCHES "GNU|Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

find_package(ament_cmake REQUIRED)
find_package(geometry_msgs REQUIRED)
find_package(moveit_ros_planning_interface REQUIRED)
find_package(rclcpp REQUIRED)
find_package(tf2 REQUIRED)
find_package(tf2_geometry_msgs REQUIRED)

add_executable(pose_goal_spike src/pose_goal_spike.cpp)
target_compile_features(pose_goal_spike PUBLIC cxx_std_17)
ament_target_dependencies(
  pose_goal_spike
  geometry_msgs
  moveit_ros_planning_interface
  rclcpp
  tf2
  tf2_geometry_msgs
)

install(TARGETS pose_goal_spike DESTINATION lib/${PROJECT_NAME})
install(DIRECTORY launch DESTINATION share/${PROJECT_NAME})

ament_package()

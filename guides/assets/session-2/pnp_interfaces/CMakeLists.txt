cmake_minimum_required(VERSION 3.8)
project(pnp_interfaces)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

find_package(ament_cmake REQUIRED)
find_package(action_msgs REQUIRED)
find_package(builtin_interfaces REQUIRED)
find_package(geometry_msgs REQUIRED)
find_package(rosidl_default_generators REQUIRED)

rosidl_generate_interfaces(${PROJECT_NAME}
  "action/PickPlace.action"
  "action/RunTrial.action"
  "msg/ErrorCode.msg"
  "msg/StageStatus.msg"
  "msg/TaskStatus.msg"
  DEPENDENCIES action_msgs builtin_interfaces geometry_msgs
)

rosidl_get_typesupport_target(cpp_typesupport_target
  ${PROJECT_NAME} rosidl_typesupport_cpp
)
add_executable(interface_constants_check test/interface_constants_check.cpp)
target_link_libraries(interface_constants_check "${cpp_typesupport_target}")
install(TARGETS interface_constants_check
  DESTINATION lib/${PROJECT_NAME}
)

ament_export_dependencies(rosidl_default_runtime)
ament_package()

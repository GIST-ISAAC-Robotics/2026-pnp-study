#include <algorithm>
#include <array>
#include <chrono>
#include <cmath>
#include <map>
#include <memory>
#include <string>
#include <thread>

#include <geometry_msgs/msg/pose.hpp>
#include <moveit/move_group_interface/move_group_interface.hpp>
#include <rclcpp/rclcpp.hpp>
#include <tf2/LinearMath/Matrix3x3.h>
#include <tf2/LinearMath/Quaternion.h>
#include <tf2_geometry_msgs/tf2_geometry_msgs.hpp>

namespace
{
constexpr double kPi = 3.14159265358979323846;
constexpr double kJoint1OriginX = 0.012;

geometry_msgs::msg::Quaternion top_down_quaternion(double base_yaw)
{
  const double c = std::cos(base_yaw);
  const double s = std::sin(base_yaw);

  // Rotation columns are the tool axes expressed in the planning frame:
  // +X_tool = -Z_world (approach), +Y_tool = tangential, +Z_tool = radial.
  tf2::Matrix3x3 rotation(
    0.0, -s, c,
    0.0, c, s,
    -1.0, 0.0, 0.0);
  tf2::Quaternion quaternion;
  rotation.getRotation(quaternion);
  quaternion.normalize();
  return tf2::toMsg(quaternion);
}

double position_error_mm(
  const geometry_msgs::msg::Pose & target,
  const geometry_msgs::msg::Pose & actual)
{
  const double dx = target.position.x - actual.position.x;
  const double dy = target.position.y - actual.position.y;
  const double dz = target.position.z - actual.position.z;
  return 1000.0 * std::sqrt(dx * dx + dy * dy + dz * dz);
}

double orientation_error_deg(
  const geometry_msgs::msg::Quaternion & target,
  const geometry_msgs::msg::Quaternion & actual)
{
  tf2::Quaternion q_target;
  tf2::Quaternion q_actual;
  tf2::fromMsg(target, q_target);
  tf2::fromMsg(actual, q_actual);
  q_target.normalize();
  q_actual.normalize();
  const double dot = std::clamp(
    std::abs(q_target.dot(q_actual)), 0.0, 1.0);
  return 2.0 * std::acos(dot) * 180.0 / kPi;
}

double tool_tilt_deg(
  const geometry_msgs::msg::Quaternion & orientation)
{
  tf2::Quaternion quaternion;
  tf2::fromMsg(orientation, quaternion);
  quaternion.normalize();
  const tf2::Matrix3x3 rotation(quaternion);

  // URDF: end_effector_joint extends +X from link5; fingers move +/-Y.
  const tf2::Vector3 approach(
    rotation[0][0], rotation[1][0], rotation[2][0]);
  const double cosine = std::clamp(-approach.z(), -1.0, 1.0);
  return std::acos(cosine) * 180.0 / kPi;
}
}  // namespace

int main(int argc, char ** argv)
{
  rclcpp::init(argc, argv);
  auto node = std::make_shared<rclcpp::Node>(
    "pose_goal_spike",
    rclcpp::NodeOptions()
    .automatically_declare_parameters_from_overrides(true));

  if (!node->has_parameter("mode")) {
    node->declare_parameter<std::string>("mode", "position_only");
  }
  if (!node->has_parameter("tool_yaw_offset_rad")) {
    node->declare_parameter<double>("tool_yaw_offset_rad", 0.0);
  }
  if (!node->has_parameter("tilt_limit_deg")) {
    node->declare_parameter<double>("tilt_limit_deg", 10.0);
  }

  const std::string mode = node->get_parameter("mode").as_string();
  const double tool_yaw_offset =
    node->get_parameter("tool_yaw_offset_rad").as_double();
  const double tilt_limit =
    node->get_parameter("tilt_limit_deg").as_double();
  if (mode != "position_only" && mode != "full_pose") {
    RCLCPP_FATAL(
      node->get_logger(), "mode must be position_only or full_pose");
    rclcpp::shutdown();
    return 2;
  }

  rclcpp::executors::SingleThreadedExecutor executor;
  executor.add_node(node);
  std::thread spinner([&executor]() {executor.spin();});

  int failed_points = 0;
  {
    using moveit::planning_interface::MoveGroupInterface;
    MoveGroupInterface arm(node, "arm");
    arm.setPlanningTime(5.0);
    arm.setNumPlanningAttempts(5);
    arm.setMaxVelocityScalingFactor(0.1);
    arm.setMaxAccelerationScalingFactor(0.1);
    arm.setGoalPositionTolerance(0.005);
    arm.setGoalOrientationTolerance(0.02);

    RCLCPP_INFO(node->get_logger(), "mode=%s", mode.c_str());
    RCLCPP_INFO(
      node->get_logger(), "planning_frame=%s",
      arm.getPlanningFrame().c_str());
    RCLCPP_INFO(
      node->get_logger(), "end_effector_link=%s",
      arm.getEndEffectorLink().c_str());
    RCLCPP_INFO(
      node->get_logger(), "approach_axis=+X_tool tilt_limit_deg=%.3f",
      tilt_limit);

    const std::array<std::array<double, 3>, 3> points = {{
      {{0.16, 0.00, 0.12}},
      {{0.17, 0.05, 0.12}},
      {{0.17, -0.05, 0.12}},
    }};

    for (std::size_t index = 0; index < points.size(); ++index) {
      const auto & point = points[index];
      const double base_yaw =
        std::atan2(point[1], point[0] - kJoint1OriginX)
        + tool_yaw_offset;

      // A known near-top-down seed: joint2 + joint3 + joint4 ~= pi/2.
      const std::map<std::string, double> seed = {
        {"joint1", base_yaw},
        {"joint2", 0.0},
        {"joint3", -0.39},
        {"joint4", 1.96},
      };
      arm.clearPoseTargets();
      arm.setStartStateToCurrentState();
      if (!arm.setJointValueTarget(seed)) {
        RCLCPP_ERROR(
          node->get_logger(), "point=%zu seed_target=REJECTED",
          index + 1);
        ++failed_points;
        continue;
      }

      MoveGroupInterface::Plan seed_plan;
      const auto seed_plan_code = arm.plan(seed_plan);
      if (!static_cast<bool>(seed_plan_code)) {
        RCLCPP_ERROR(
          node->get_logger(), "point=%zu seed_plan=FAIL code=%d",
          index + 1, seed_plan_code.val);
        ++failed_points;
        continue;
      }
      const auto seed_execute_code = arm.execute(seed_plan);
      if (!static_cast<bool>(seed_execute_code)) {
        RCLCPP_ERROR(
          node->get_logger(), "point=%zu seed_execute=FAIL code=%d",
          index + 1, seed_execute_code.val);
        ++failed_points;
        continue;
      }

      geometry_msgs::msg::Pose target;
      target.position.x = point[0];
      target.position.y = point[1];
      target.position.z = point[2];
      target.orientation = top_down_quaternion(base_yaw);

      arm.clearPoseTargets();
      arm.setStartStateToCurrentState();
      bool target_accepted = false;
      if (mode == "position_only") {
        target_accepted = arm.setPositionTarget(
          point[0], point[1], point[2], arm.getEndEffectorLink());
      } else {
        target_accepted = arm.setPoseTarget(
          target, arm.getEndEffectorLink());
      }
      if (!target_accepted) {
        RCLCPP_ERROR(
          node->get_logger(), "point=%zu target=REJECTED", index + 1);
        ++failed_points;
        continue;
      }

      MoveGroupInterface::Plan plan;
      const auto plan_code = arm.plan(plan);
      if (!static_cast<bool>(plan_code)) {
        RCLCPP_ERROR(
          node->get_logger(), "point=%zu plan=FAIL code=%d",
          index + 1, plan_code.val);
        ++failed_points;
        continue;
      }

      const auto execute_code = arm.execute(plan);
      if (!static_cast<bool>(execute_code)) {
        RCLCPP_ERROR(
          node->get_logger(),
          "point=%zu plan=OK execute=FAIL code=%d",
          index + 1, execute_code.val);
        ++failed_points;
        continue;
      }

      std::this_thread::sleep_for(std::chrono::milliseconds(250));
      const auto actual =
        arm.getCurrentPose(arm.getEndEffectorLink()).pose;
      const double position_mm = position_error_mm(target, actual);
      const double orientation_deg =
        orientation_error_deg(target.orientation, actual.orientation);
      const double tilt_deg = tool_tilt_deg(actual.orientation);
      RCLCPP_INFO(
        node->get_logger(),
        "RESULT point=%zu mode=%s plan=OK execute=OK "
        "position_error_mm=%.3f orientation_error_deg=%.3f "
        "actual_tool_tilt_deg=%.3f tilt_pass=%s",
        index + 1, mode.c_str(), position_mm, orientation_deg, tilt_deg,
        tilt_deg <= tilt_limit ? "true" : "false");
    }

    arm.clearPoseTargets();
    arm.setStartStateToCurrentState();
    geometry_msgs::msg::Pose unreachable;
    unreachable.position.x = 1.50;
    unreachable.position.y = 0.0;
    unreachable.position.z = 0.50;
    unreachable.orientation = top_down_quaternion(0.0);
    if (mode == "position_only") {
      arm.setPositionTarget(
        unreachable.position.x,
        unreachable.position.y,
        unreachable.position.z,
        arm.getEndEffectorLink());
    } else {
      arm.setPoseTarget(unreachable, arm.getEndEffectorLink());
    }
    MoveGroupInterface::Plan unreachable_plan;
    const auto unreachable_code = arm.plan(unreachable_plan);
    RCLCPP_INFO(
      node->get_logger(), "UNREACHABLE expected_fail=%s code=%d",
      static_cast<bool>(unreachable_code) ? "false" : "true",
      unreachable_code.val);
  }

  executor.cancel();
  spinner.join();
  rclcpp::shutdown();
  return failed_points == 0 ? 0 : 1;
}

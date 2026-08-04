#include "pnp_interfaces/msg/error_code.hpp"
#include "pnp_interfaces/msg/stage_status.hpp"

static_assert(pnp_interfaces::msg::ErrorCode::OK == 0);
static_assert(pnp_interfaces::msg::ErrorCode::TASK_CANCELED == 403);
static_assert(pnp_interfaces::msg::StageStatus::PLACE == 32);
static_assert(pnp_interfaces::msg::StageStatus::CLEANUP == 64);

int main()
{
  return 0;
}

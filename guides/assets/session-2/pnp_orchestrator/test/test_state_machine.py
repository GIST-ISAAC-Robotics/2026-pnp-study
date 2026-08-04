from pnp_orchestrator.state_machine import (
    EVALUATION_TRANSITIONS,
    EvaluationState,
    ExplicitStateMachine,
    MANIPULATION_TRANSITIONS,
    ManipulationState,
    ORCHESTRATOR_TRANSITIONS,
    OrchestratorState,
    TransitionError,
)
import pytest


def test_evaluation_success_path():
    machine = ExplicitStateMachine(
        EvaluationState.VALIDATE_PROFILE,
        EVALUATION_TRANSITIONS,
    )
    for state in (
        EvaluationState.ALLOCATE_ATTEMPT,
        EvaluationState.RESET,
        EvaluationState.CALL_RUN_TRIAL,
        EvaluationState.COLLECT,
        EvaluationState.SCORE,
        EvaluationState.RECORD,
        EvaluationState.VALIDATE_PROFILE,
    ):
        machine.move(state)
    assert machine.state == EvaluationState.VALIDATE_PROFILE


def test_orchestrator_fixed_path():
    machine = ExplicitStateMachine(
        OrchestratorState.IDLE,
        ORCHESTRATOR_TRANSITIONS,
    )
    for state in (
        OrchestratorState.SELECT_TARGET,
        OrchestratorState.LOAD_FIXED_TARGET,
        OrchestratorState.VALIDATE,
        OrchestratorState.CALL_MANIPULATION,
        OrchestratorState.COMPLETE,
        OrchestratorState.IDLE,
    ):
        machine.move(state)
    assert machine.state == OrchestratorState.IDLE


def test_illegal_orchestrator_transition_is_rejected():
    machine = ExplicitStateMachine(
        OrchestratorState.IDLE,
        ORCHESTRATOR_TRANSITIONS,
    )
    with pytest.raises(TransitionError, match='IDLE -> VALIDATE'):
        machine.move(OrchestratorState.VALIDATE)


def test_manipulation_lift_only_path_skips_place():
    machine = ExplicitStateMachine(
        ManipulationState.IDLE,
        MANIPULATION_TRANSITIONS,
    )
    for state in (
        ManipulationState.SETUP_SCENE,
        ManipulationState.PLAN_PICK,
        ManipulationState.EXECUTE_PICK,
        ManipulationState.PREPARE_TRANSPORT,
        ManipulationState.ATTACH_OBJECT,
        ManipulationState.LIFT,
        ManipulationState.VERIFY_PICK,
        ManipulationState.CLEANUP,
        ManipulationState.RETURN_RESULT,
        ManipulationState.IDLE,
    ):
        machine.move(state)
    assert machine.state == ManipulationState.IDLE

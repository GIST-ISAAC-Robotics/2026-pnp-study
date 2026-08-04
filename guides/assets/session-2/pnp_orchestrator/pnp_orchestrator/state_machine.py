from enum import Enum


class OrchestratorState(str, Enum):
    IDLE = 'IDLE'
    SELECT_TARGET = 'SELECT_TARGET'
    TRANSFORM = 'TRANSFORM'
    CALL_PICK_PLACE = 'CALL_PICK_PLACE'
    DONE = 'DONE'
    FAILED = 'FAILED'


class ManipulationState(str, Enum):
    IDLE = 'IDLE'
    SETUP_SCENE = 'SETUP_SCENE'
    APPROACH = 'APPROACH'
    GRASP = 'GRASP'
    LIFT = 'LIFT'
    TRANSPORT = 'TRANSPORT'
    PLACE = 'PLACE'
    CLEANUP = 'CLEANUP'
    DONE = 'DONE'
    FAILED = 'FAILED'


ORCHESTRATOR_TRANSITIONS = {
    OrchestratorState.IDLE: {OrchestratorState.SELECT_TARGET},
    OrchestratorState.SELECT_TARGET: {
        OrchestratorState.TRANSFORM,
        OrchestratorState.FAILED,
    },
    OrchestratorState.TRANSFORM: {
        OrchestratorState.CALL_PICK_PLACE,
        OrchestratorState.FAILED,
    },
    OrchestratorState.CALL_PICK_PLACE: {
        OrchestratorState.DONE,
        OrchestratorState.FAILED,
    },
    OrchestratorState.DONE: {OrchestratorState.IDLE},
    OrchestratorState.FAILED: {OrchestratorState.IDLE},
}


MANIPULATION_TRANSITIONS = {
    ManipulationState.IDLE: {ManipulationState.SETUP_SCENE},
    ManipulationState.SETUP_SCENE: {
        ManipulationState.APPROACH,
        ManipulationState.CLEANUP,
    },
    ManipulationState.APPROACH: {
        ManipulationState.GRASP,
        ManipulationState.CLEANUP,
    },
    ManipulationState.GRASP: {
        ManipulationState.LIFT,
        ManipulationState.CLEANUP,
    },
    ManipulationState.LIFT: {
        ManipulationState.TRANSPORT,
        ManipulationState.CLEANUP,
    },
    ManipulationState.TRANSPORT: {
        ManipulationState.PLACE,
        ManipulationState.CLEANUP,
    },
    ManipulationState.PLACE: {ManipulationState.CLEANUP},
    ManipulationState.CLEANUP: {
        ManipulationState.DONE,
        ManipulationState.FAILED,
    },
    ManipulationState.DONE: {ManipulationState.IDLE},
    ManipulationState.FAILED: {ManipulationState.IDLE},
}


class TransitionError(RuntimeError):
    pass


class ExplicitStateMachine:
    def __init__(self, initial_state, transitions):
        self._state = initial_state
        self._transitions = transitions

    @property
    def state(self):
        return self._state

    def move(self, next_state):
        allowed = self._transitions.get(self._state, set())
        if next_state not in allowed:
            raise TransitionError(
                f'illegal transition: {self._state.value} -> {next_state.value}'
            )
        self._state = next_state
        return self._state

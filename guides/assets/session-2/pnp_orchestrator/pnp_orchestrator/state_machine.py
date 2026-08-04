from enum import Enum


class EvaluationState(str, Enum):
    VALIDATE_PROFILE = 'VALIDATE_PROFILE'
    ALLOCATE_ATTEMPT = 'ALLOCATE_ATTEMPT'
    RESET = 'RESET'
    RECORD_RESET_FAILURE = 'RECORD_RESET_FAILURE'
    CALL_RUN_TRIAL = 'CALL_RUN_TRIAL'
    COLLECT = 'COLLECT'
    SCORE = 'SCORE'
    RECORD = 'RECORD'
    SAFE_STOP = 'SAFE_STOP'


class OrchestratorState(str, Enum):
    IDLE = 'IDLE'
    SELECT_TARGET = 'SELECT_TARGET'
    LOAD_FIXED_TARGET = 'LOAD_FIXED_TARGET'
    DETECT = 'DETECT'
    TRANSFORM = 'TRANSFORM'
    VALIDATE = 'VALIDATE'
    CALL_MANIPULATION = 'CALL_MANIPULATION'
    COMPLETE = 'COMPLETE'
    SAFE_STOP = 'SAFE_STOP'


class ManipulationState(str, Enum):
    IDLE = 'IDLE'
    SETUP_SCENE = 'SETUP_SCENE'
    PLAN_PICK = 'PLAN_PICK'
    EXECUTE_PICK = 'EXECUTE_PICK'
    PREPARE_TRANSPORT = 'PREPARE_TRANSPORT'
    ATTACH_OBJECT = 'ATTACH_OBJECT'
    LIFT = 'LIFT'
    VERIFY_PICK = 'VERIFY_PICK'
    PLAN_PLACE = 'PLAN_PLACE'
    EXECUTE_PLACE = 'EXECUTE_PLACE'
    CLEANUP = 'CLEANUP'
    RETURN_RESULT = 'RETURN_RESULT'
    SAFE_STOP = 'SAFE_STOP'


EVALUATION_TRANSITIONS = {
    EvaluationState.VALIDATE_PROFILE: {
        EvaluationState.ALLOCATE_ATTEMPT,
        EvaluationState.SAFE_STOP,
    },
    EvaluationState.ALLOCATE_ATTEMPT: {EvaluationState.RESET},
    EvaluationState.RESET: {
        EvaluationState.RECORD_RESET_FAILURE,
        EvaluationState.CALL_RUN_TRIAL,
    },
    EvaluationState.RECORD_RESET_FAILURE: {EvaluationState.RECORD},
    EvaluationState.CALL_RUN_TRIAL: {
        EvaluationState.COLLECT,
        EvaluationState.SAFE_STOP,
    },
    EvaluationState.COLLECT: {
        EvaluationState.SCORE,
        EvaluationState.SAFE_STOP,
    },
    EvaluationState.SCORE: {EvaluationState.RECORD},
    EvaluationState.RECORD: {
        EvaluationState.ALLOCATE_ATTEMPT,
        EvaluationState.VALIDATE_PROFILE,
    },
    EvaluationState.SAFE_STOP: set(),
}


ORCHESTRATOR_TRANSITIONS = {
    OrchestratorState.IDLE: {OrchestratorState.SELECT_TARGET},
    OrchestratorState.SELECT_TARGET: {
        OrchestratorState.LOAD_FIXED_TARGET,
        OrchestratorState.DETECT,
        OrchestratorState.COMPLETE,
    },
    OrchestratorState.LOAD_FIXED_TARGET: {
        OrchestratorState.VALIDATE,
        OrchestratorState.COMPLETE,
    },
    OrchestratorState.DETECT: {
        OrchestratorState.TRANSFORM,
        OrchestratorState.COMPLETE,
    },
    OrchestratorState.TRANSFORM: {
        OrchestratorState.VALIDATE,
        OrchestratorState.COMPLETE,
    },
    OrchestratorState.VALIDATE: {
        OrchestratorState.CALL_MANIPULATION,
        OrchestratorState.COMPLETE,
    },
    OrchestratorState.CALL_MANIPULATION: {
        OrchestratorState.COMPLETE,
        OrchestratorState.SAFE_STOP,
    },
    OrchestratorState.COMPLETE: {OrchestratorState.IDLE},
    OrchestratorState.SAFE_STOP: set(),
}


MANIPULATION_TRANSITIONS = {
    ManipulationState.IDLE: {ManipulationState.SETUP_SCENE},
    ManipulationState.SETUP_SCENE: {
        ManipulationState.PLAN_PICK,
        ManipulationState.CLEANUP,
    },
    ManipulationState.PLAN_PICK: {
        ManipulationState.EXECUTE_PICK,
        ManipulationState.CLEANUP,
    },
    ManipulationState.EXECUTE_PICK: {
        ManipulationState.PREPARE_TRANSPORT,
        ManipulationState.CLEANUP,
    },
    ManipulationState.PREPARE_TRANSPORT: {
        ManipulationState.ATTACH_OBJECT,
        ManipulationState.CLEANUP,
    },
    ManipulationState.ATTACH_OBJECT: {
        ManipulationState.LIFT,
        ManipulationState.CLEANUP,
    },
    ManipulationState.LIFT: {
        ManipulationState.VERIFY_PICK,
        ManipulationState.CLEANUP,
    },
    ManipulationState.VERIFY_PICK: {
        ManipulationState.PLAN_PLACE,
        ManipulationState.CLEANUP,
    },
    ManipulationState.PLAN_PLACE: {
        ManipulationState.EXECUTE_PLACE,
        ManipulationState.CLEANUP,
    },
    ManipulationState.EXECUTE_PLACE: {ManipulationState.CLEANUP},
    ManipulationState.CLEANUP: {
        ManipulationState.RETURN_RESULT,
        ManipulationState.SAFE_STOP,
    },
    ManipulationState.RETURN_RESULT: {ManipulationState.IDLE},
    ManipulationState.SAFE_STOP: set(),
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

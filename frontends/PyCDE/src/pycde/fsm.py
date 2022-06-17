from pycde import System, Input, Output, module, generator
from pycde.module import _SpecializedModule, Generator, _GeneratorPortAccess
from pycde.dialects import fsm
from pycde.pycde_types import types
from typing import Callable

from mlir.ir import InsertionPoint
from collections import defaultdict
from functools import lru_cache


class _Transition:

  __slots__ = ['from_state', 'to_state', 'condition']

  def __init__(self,
               from_state: str,
               to_state: str,
               condition: Callable = None):
    if from_state is None or to_state is None:
      raise ValueError("State and next state must be specified")

    self.from_state = from_state
    self.to_state = to_state
    self.condition = condition

  def emit(self, state_op, ports):
    # Create transition ops for all outgoing transitions.
    with InsertionPoint(state_op.transitions):
      op = fsm.TransitionOp(self.to_state)

      # If a condition function was specified, execute it on the ports and
      # assign the result as the guard of this transition.
      if self.condition:
        op.set_guard(lambda: self.condition(ports))


def create_fsm_machine_op(sys, mod: _SpecializedModule, symbol):
  """Creation callback for creating a MSFTModuleOp."""
  return fsm.MachineOp(symbol,
                       mod.modcls.fsm_initial_state,
                       mod.input_ports,
                       mod.output_ports,
                       loc=mod.loc,
                       ip=sys._get_ip())


def generate_fsm_machine_op(generate_obj: Generator,
                            spec_mod: _SpecializedModule):
  """ Generator callback for generating an FSM op. """
  entry_block = spec_mod.circt_mod.body.blocks[0]
  ports = _GeneratorPortAccess(spec_mod)

  # Cache true/false values in machine scope to avoid IR spam.
  @lru_cache
  def get_cached_bool(v):
    with InsertionPoint(entry_block):
      return types.i1(v)

  get_cached_bool(False)
  get_cached_bool(True)

  with InsertionPoint(entry_block), generate_obj.loc:
    for state, state_transitions in spec_mod.modcls.transitions.items():
      # Create state op and assert the current state in its output vector.
      state_op = fsm.StateOp(state)
      with InsertionPoint(state_op.output):
        outputs = []
        for state_it in spec_mod.modcls.states:
          outputs.append(get_cached_bool(state_it == state))
        fsm.OutputOp(*outputs)

      # Emit outgoing transitions from this state.
      for transition in state_transitions:
        transition.emit(state_op, ports)


def machine(to_be_wrapped):
  """
  Wrap a class as a FSM machine.
  """

  states = None
  transition_dict = None
  initial_state = None
  for attr_name in dir(to_be_wrapped):
    if attr_name.startswith("_"):
      continue

    if attr_name == "fsm_initial_state":
      if states is not None:
        raise ValueError("fsm_initial_state can only be defined once.")
      initial_state = getattr(to_be_wrapped, attr_name)
    elif attr_name == "fsm_transitions":
      if transition_dict is not None:
        raise ValueError("fsm_transitions can only be defined once.")
      transition_dict = getattr(to_be_wrapped, attr_name)

  if transition_dict is None:
    raise ValueError("fsm_transitions must be defined.")

  # Ensure states are unique
  states = list(transition_dict.keys())
  states = [state.lower() for state in states]
  if len(set(states)) != len(states):
    raise ValueError("fsm_states must be unique.")

  if len(states) == 0:
    raise ValueError("fsm_states must be non-empty.")

  # Add output ports for each state.
  for state in states:
    setattr(to_be_wrapped, 'is_' + state, Output(types.i1))

  # Create and transitions.
  transitions = defaultdict(lambda: [])
  for from_state, transitionargs in transition_dict.items():
    if isinstance(transitionargs, list):
      for transition in transitionargs:
        transitions[from_state].append(_Transition(from_state, *transition))
    else:
      transitions[from_state].append(_Transition(from_state, *transitionargs))

  for _, to_states in transitions.items():
    for transition in to_states:
      if transition.from_state not in states:
        raise ValueError("Invalid transition from state {}".format(
            transition.from_state))
      if transition.to_state not in states:
        raise ValueError("Invalid transition to state {}".format(
            transition.to_state))

  to_be_wrapped.transitions = transitions
  to_be_wrapped.states = states

  # Set module creation and generation callbacks.
  setattr(to_be_wrapped, 'create_cb', create_fsm_machine_op)
  setattr(to_be_wrapped, 'generator_cb', generate_fsm_machine_op)

  # Create a dummy Generator function to generate the machine internals.
  # This function doesn't do anything, since all generation logic is embedded
  # within generate_fsm_machine_op. In the future, we may allow an actual
  # @generator function specified by the user if they want to do something
  # specific.
  setattr(to_be_wrapped, 'dummy_generator_f', generator(lambda x: None))

  # Treat the remainder of the class as a module.
  return module(to_be_wrapped)

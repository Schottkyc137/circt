from pycde import System, Input, Output, module, generator
from pycde.module import _SpecializedModule, Generator, _GeneratorPortAccess
from pycde.dialects import fsm
from pycde.pycde_types import types
from typing import Callable

from mlir.ir import InsertionPoint
from collections import defaultdict
from functools import lru_cache

from pycde.support import _obj_to_attribute


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


def _index_of_first(lst, pred):
  for i, v in enumerate(lst):
    if pred(v):
      return i
  return None


def create_fsm_machine_op(sys, mod: _SpecializedModule, symbol):
  """Creation callback for creating a MSFTModuleOp."""

  # Add attributes for in- and outputs.
  attributes = {}
  attributes["in_names"] = _obj_to_attribute(
      [port_name for port_name, _ in mod.input_ports])
  attributes["out_names"] = _obj_to_attribute(
      [port_name for port_name, _ in mod.input_ports])

  # Add attributes to indicate whether the FSM has explicit clock and reset
  # signals. This attribute indicates the input port index of the signal.
  attributes['has_clock'] = _obj_to_attribute(
      _index_of_first(mod.input_ports, lambda p: p[0] == mod.modcls.clock_name))

  if mod.modcls.reset_name is not None:
    attributes['has_reset'] = _obj_to_attribute(
        _index_of_first(mod.input_ports,
                        lambda p: p[0] == mod.modcls.reset_name))

  return fsm.MachineOp(symbol,
                       mod.modcls.fsm_initial_state,
                       mod.input_ports,
                       mod.output_ports,
                       attributes=attributes,
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


def machine(clock: str = 'clk', reset: str = None):
  """top-level FSM decorator which gives the user the option specify port
  names for the clock and (optional) reset signal."""

  def machine_clocked(to_be_wrapped):
    """
    Wrap a class as an FSM machine.

    An FSM PyCDE module is expected to implement:

    - A set of input ports:
        These can be of any type, and are used to drive the FSM.
    - An `fsm_initial_state` variable:
        A string denoting the name of the initial state of the FSM.
    - An `fsm_transitions` variable:
        A dictionary containing states and state transitions.
        The dictionary is keyed by state names, and the values are lists of
        transitions.

        Transitions can be specified either as a tuple of (next_state, condition)
        or as a single `next_state` string (unconditionally taken).
        a `condition` function is a function which takes a single input representing
        the `ports` of a component, similar to the `@generator` decorator used
        elsewhere in PyCDE.
    """
    states = None
    transition_dict = None
    initial_state = None

    attr_dict = dir(to_be_wrapped)

    if 'fsm_initial_state' not in attr_dict:
      raise ValueError("fsm_initial_state must be defined")

    if 'fsm_transitions' not in attr_dict:
      raise ValueError("fsm_transitions must be defined")
    transition_dict = to_be_wrapped.fsm_transitions

    # Ensure state uniqueness.
    states = list(transition_dict.keys())
    states = [state.lower() for state in states]
    if len(set(states)) != len(states):
      raise ValueError("fsm_states must be unique.")

    if len(states) == 0:
      raise ValueError("fsm_states must be non-empty.")

    # Add an output port for each state.
    for state in states:
      setattr(to_be_wrapped, 'is_' + state, Output(types.i1))

    to_be_wrapped.clock_name = clock
    to_be_wrapped.reset_name = reset

    # Create clock and optional reset signals
    setattr(to_be_wrapped, clock, Input(types.i1))
    if reset is not None:
      setattr(to_be_wrapped, reset, Input(types.i1))

    # Create Transition objects.
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

  return machine_clocked
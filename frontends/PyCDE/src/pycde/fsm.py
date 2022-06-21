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
  """Creation callback for creating a FSM MachineOp."""

  # Add attributes for in- and output names.
  attributes = {}
  attributes["in_names"] = _obj_to_attribute(
      [port_name for port_name, _ in mod.input_ports])
  attributes["out_names"] = _obj_to_attribute(
      [port_name for port_name, _ in mod.output_ports])

  # Add attributes for clock and reset names.
  attributes["clock_name"] = _obj_to_attribute(mod.modcls.clock_name)
  if mod.modcls.reset_name:
    attributes["reset_name"] = _obj_to_attribute(mod.modcls.reset_name)

  return fsm.MachineOp(symbol,
                       mod.modcls.fsm_initial_state,
                       mod.input_ports,
                       mod.output_ports,
                       attributes=attributes,
                       loc=mod.loc,
                       ip=sys._get_ip())


class FSMPortAccess:
  """Get the ports of an FSM machine."""


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

  # Prime the cache. This is a super minor nit, but being explicit about the
  # ordering here ensures that %0 = False and %1 = True in the IR as well as
  # constants being emitted before the FSM ops.
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


"""
FSM wrapping example:  


Given a simple FSM like below:
```
@fsm.machine()
class MyFSM:
  a = Input(types.i1)
  b = Input(types.i1)
  fsm_transitions = {
    a:(b, lambda ports : ports.a),b:a
  }
```

This will, via. the @fsm.machine() decorator, be elaborated to:
```
@module
class MyFSM:

  a = Input(types.i1)
  b = Input(types.i1)
  clk = Input(types.i1)

  is_a = Output(types.i1)
  is_b = Output(types.i1)

  @fsm.machine()
  class _MyFSM:
    a = Input(types.i1)
    b = Input(types.i1)
    fsm_transitions = {
        "a": ("b", lambda ports: ports.a),
        "b": ("a", lambda ports: ports.b)
    }

  @generator
  def construct(ports):
    # fsm.hw_instance operation
    myfsm = MyFSM(clk=ports.clk, a=ports.a, b=ports.b)
    ports.is_a = myfsm.is_a
    ports.is_b = myfsm.is_b
```

The reason for this wrapper is to have a method of exposing the as-of-yet
unmaterialized clock and reset (CR) ports of an FSM to the instantiater of MyFSM.
If we instead added CR ports directly to _MyFSM, we would have to do a lot of
special-case logic for eliding these in the PyCDE module helper functions
(e.g. specializing GeneratorPortAccess, module.input_port_lookup, ...).

Through the wrapper, we control the instantiation of MyFSM, and can automatically
hook up the CR ports to the correct inputs of the fsm.hw_instance operation.


  """


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

    # Store requested clock and reset names.
    to_be_wrapped.clock_name = clock
    to_be_wrapped.reset_name = reset

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

    # Create an __init__ function that allows clk and reset signals to pass through
    # legally.
    def init_cr_passthrough(*args, **kwargs):
      cr_names = [clock]
      if reset is not None:
        cr_names.append(reset)
      for k, _ in kwargs.items():
        if k not in cr_names:
          raise ValueError("Input which doesn't have a port: {}".format(k))
      return

    setattr(to_be_wrapped, '__init__', init_cr_passthrough)

    # Treat the remainder of the class as a module.
    return module(to_be_wrapped)

  return machine_clocked
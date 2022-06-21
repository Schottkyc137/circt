# RUN: py-split-input-file.py %s

from re import A
from pycde import System, Input, Output, module, generator, externmodule

from pycde.dialects import comb
from pycde import fsm
from pycde.pycde_types import types, dim

from circt.support import connect


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
    dd = Input(types.i1)
    fsm_initial_state = "a"
    fsm_transitions = {
        "a": ("b", lambda ports: ports.a),
        "b": ("a", lambda ports: ports.dd)
    }

  @generator
  def construct(ports):
    myfsm = MyFSM._MyFSM(a=ports.a, dd=ports.b)
    # Attach clock and optional reset. This seems a bit janky...
    connect(myfsm._instantiation.operands[len(myfsm._pycde_mod.input_ports)],
            ports.clk)
    print(len(myfsm._instantiation.operands))

    myfsm._instantiation._clock_backedge = ports.clk
    ports.is_a = myfsm.is_a
    ports.is_b = myfsm.is_b


system = System([MyFSM])
system.generate()
system.print()

# @module
# class M0:

#   # Create an FSM.
#   # 'clock' name is mandatory, 'reset' name is optional.
#   @fsm.machine(clock="clock")
#   class F0:
#     a = Input(types.i1)
#     b = Input(types.i1)
#     c = Input(types.i1)

#     def maj3(ports):

#       def nand(*args):
#         return comb.XorOp(comb.AndOp(*args), types.i1(1))

#       c1 = nand(ports.a, ports.b)
#       c2 = nand(ports.b, ports.c)
#       c3 = nand(ports.a, ports.c)
#       return nand(c1, c2, c3)

#     fsm_initial_state = 'idle'
#     fsm_transitions = {
#         # Transition using inline function
#         'idle': [('a', lambda ports: ports.a)],
#         # Always taken transition
#         'a':
#             'b',
#         # Transition using outline function
#         'b': ('c', maj3),
#         # Multiple transitions
#         'c': [('idle', lambda ports: ports.c),
#               ('a', lambda ports: comb.XorOp(ports.b, types.i1(1)))],
#     }

#   clock = Input(types.i1)
#   a = Input(types.i1)
#   b = Input(types.i1)
#   c = Input(types.i1)

#   is_idle = Output(types.i1)
#   is_a = Output(types.i1)
#   is_b = Output(types.i1)
#   is_c = Output(types.i1)

#   @generator
#   def build(ports):
#     fsm = M0.F0(a=ports.a, b=ports.b, c=ports.c)

#     ports.is_a = fsm.is_a
#     ports.is_b = fsm.is_b
#     ports.is_c = fsm.is_c
#     ports.is_idle = fsm.is_idle

# system = System([M0])
# system.generate()
# system.print()

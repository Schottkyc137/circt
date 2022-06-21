# RUN: py-split-input-file.py %s

from re import A
from pycde import System, Input, module, generator, externmodule

from pycde.dialects import comb
from pycde import fsm
from pycde.pycde_types import types, dim


# Create an FSM.
# 'clock' name is mandatory, 'reset' name is optional.
@fsm.machine(clock="clock")
class F0:
  a = Input(types.i1)
  c = Input(types.i1)
  d = Input(types.i1)

  def maj3(ports):

    def nand(*args):
      return comb.XorOp(comb.AndOp(*args), types.i1(1))

    c1 = nand(ports.a, ports.c)
    c2 = nand(ports.c, ports.d)
    c3 = nand(ports.a, ports.d)
    return nand(c1, c2, c3)

  fsm_initial_state = 'idle'
  fsm_transitions = {
      # Transition using inline function
      'idle': [('a', lambda ports: ports.a)],
      # Always taken transition
      'a':
          'b',
      # Transition using outline function
      'b': ('c', maj3),
      # Multiple transitions
      'c': [('idle', lambda ports: ports.d),
            ('idle', lambda ports: comb.XorOp(ports.d, types.i1(1)))],
  }


m1 = System([F0])
m1.generate()
m1.print()

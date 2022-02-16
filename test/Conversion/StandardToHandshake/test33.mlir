// NOTE: Assertions have been autogenerated by utils/update_mlir_test_checks.py
// RUN: circt-opt -lower-std-to-handshake %s | FileCheck %s
// CHECK-LABEL:   handshake.func @test(
// CHECK-SAME:                         %[[VAL_0:.*]]: none, ...) -> none attributes {argNames = ["inCtrl"], resNames = ["outCtrl"]} {
// CHECK:           %[[VAL_1:.*]]:5 = memory[ld = 2, st = 1] (%[[VAL_2:.*]], %[[VAL_3:.*]], %[[VAL_4:.*]], %[[VAL_5:.*]]) {id = 0 : i32, lsq = false} : memref<10xf32>, (f32, index, index, index) -> (f32, f32, none, none, none)
// CHECK:           %[[VAL_6:.*]]:2 = fork [2] %[[VAL_1]]#4 : none
// CHECK:           %[[VAL_7:.*]]:2 = fork [2] %[[VAL_1]]#3 : none
// CHECK:           %[[VAL_8:.*]]:3 = fork [3] %[[VAL_0]] : none
// CHECK:           %[[VAL_9:.*]] = constant %[[VAL_8]]#1 {value = 0 : index} : index
// CHECK:           %[[VAL_10:.*]] = constant %[[VAL_8]]#0 {value = 10 : index} : index
// CHECK:           %[[VAL_11:.*]] = cf.br %[[VAL_8]]#2 : none
// CHECK:           %[[VAL_12:.*]] = cf.br %[[VAL_9]] : index
// CHECK:           %[[VAL_13:.*]] = cf.br %[[VAL_10]] : index
// CHECK:           %[[VAL_14:.*]], %[[VAL_15:.*]] = control_merge %[[VAL_11]] : none
// CHECK:           %[[VAL_16:.*]]:2 = fork [2] %[[VAL_15]] : index
// CHECK:           %[[VAL_17:.*]] = buffer [1] %[[VAL_18:.*]] {initValues = [0], sequential = true} : i1
// CHECK:           %[[VAL_19:.*]]:3 = fork [3] %[[VAL_17]] : i1
// CHECK:           %[[VAL_20:.*]] = mux %[[VAL_19]]#2 {{\[}}%[[VAL_14]], %[[VAL_21:.*]]] : i1, none
// CHECK:           %[[VAL_22:.*]] = mux %[[VAL_16]]#1 {{\[}}%[[VAL_13]]] : index, index
// CHECK:           %[[VAL_23:.*]] = mux %[[VAL_19]]#1 {{\[}}%[[VAL_22]], %[[VAL_24:.*]]] : i1, index
// CHECK:           %[[VAL_25:.*]]:2 = fork [2] %[[VAL_23]] : index
// CHECK:           %[[VAL_26:.*]] = mux %[[VAL_16]]#0 {{\[}}%[[VAL_12]]] : index, index
// CHECK:           %[[VAL_27:.*]] = mux %[[VAL_19]]#0 {{\[}}%[[VAL_26]], %[[VAL_28:.*]]] : i1, index
// CHECK:           %[[VAL_29:.*]]:2 = fork [2] %[[VAL_27]] : index
// CHECK:           %[[VAL_18]] = merge %[[VAL_30:.*]]#0 : i1
// CHECK:           %[[VAL_31:.*]] = arith.cmpi slt, %[[VAL_29]]#0, %[[VAL_25]]#0 : index
// CHECK:           %[[VAL_30]]:4 = fork [4] %[[VAL_31]] : i1
// CHECK:           %[[VAL_32:.*]], %[[VAL_33:.*]] = cf.cond_br %[[VAL_30]]#3, %[[VAL_25]]#1 : index
// CHECK:           sink %[[VAL_33]] : index
// CHECK:           %[[VAL_34:.*]], %[[VAL_35:.*]] = cf.cond_br %[[VAL_30]]#2, %[[VAL_20]] : none
// CHECK:           %[[VAL_36:.*]], %[[VAL_37:.*]] = cf.cond_br %[[VAL_30]]#1, %[[VAL_29]]#1 : index
// CHECK:           sink %[[VAL_37]] : index
// CHECK:           %[[VAL_38:.*]] = merge %[[VAL_36]] : index
// CHECK:           %[[VAL_39:.*]] = merge %[[VAL_32]] : index
// CHECK:           %[[VAL_40:.*]], %[[VAL_41:.*]] = control_merge %[[VAL_34]] : none
// CHECK:           %[[VAL_42:.*]]:4 = fork [4] %[[VAL_40]] : none
// CHECK:           %[[VAL_43:.*]]:2 = fork [2] %[[VAL_42]]#3 : none
// CHECK:           %[[VAL_44:.*]] = join %[[VAL_43]]#1, %[[VAL_7]]#1, %[[VAL_6]]#1, %[[VAL_1]]#2 : none
// CHECK:           sink %[[VAL_41]] : index
// CHECK:           %[[VAL_45:.*]] = constant %[[VAL_43]]#0 {value = 1 : index} : index
// CHECK:           %[[VAL_46:.*]]:2 = fork [2] %[[VAL_45]] : index
// CHECK:           %[[VAL_47:.*]], %[[VAL_4]] = load {{\[}}%[[VAL_46]]#1] %[[VAL_1]]#0, %[[VAL_42]]#2 : index, f32
// CHECK:           %[[VAL_48:.*]] = arith.addi %[[VAL_38]], %[[VAL_46]]#0 : index
// CHECK:           %[[VAL_49:.*]]:3 = fork [3] %[[VAL_48]] : index
// CHECK:           %[[VAL_50:.*]], %[[VAL_5]] = load {{\[}}%[[VAL_49]]#2] %[[VAL_1]]#1, %[[VAL_42]]#1 : index, f32
// CHECK:           %[[VAL_51:.*]] = arith.addf %[[VAL_47]], %[[VAL_50]] : f32
// CHECK:           %[[VAL_52:.*]] = join %[[VAL_42]]#0, %[[VAL_7]]#0, %[[VAL_6]]#0 : none
// CHECK:           %[[VAL_2]], %[[VAL_3]] = store {{\[}}%[[VAL_49]]#1] %[[VAL_51]], %[[VAL_52]] : index, f32
// CHECK:           %[[VAL_24]] = cf.br %[[VAL_39]] : index
// CHECK:           %[[VAL_21]] = cf.br %[[VAL_44]] : none
// CHECK:           %[[VAL_28]] = cf.br %[[VAL_49]]#0 : index
// CHECK:           %[[VAL_53:.*]], %[[VAL_54:.*]] = control_merge %[[VAL_35]] : none
// CHECK:           sink %[[VAL_54]] : index
// CHECK:           return %[[VAL_53]] : none
// CHECK:         }
func @test() {
  %10 = memref.alloc() : memref<10xf32>
  %c0 = arith.constant 0 : index
  %c10 = arith.constant 10 : index
  cf.br ^bb1(%c0 : index)
^bb1(%1: index):      // 2 preds: ^bb0, ^bb2
  %2 = arith.cmpi slt, %1, %c10 : index
  cf.cond_br %2, ^bb2, ^bb3
^bb2: // pred: ^bb1
  %c1 = arith.constant 1 : index
  %5 = memref.load %10[%c1] : memref<10xf32>
  %3 = arith.addi %1, %c1 : index
  %7 = memref.load %10[%3] : memref<10xf32>
  %8 = arith.addf %5, %7 : f32
  memref.store %8, %10[%3] : memref<10xf32>
  cf.br ^bb1(%3 : index)
^bb3: // pred: ^bb1
  return
}

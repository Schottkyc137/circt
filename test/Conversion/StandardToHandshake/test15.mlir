// NOTE: Assertions have been autogenerated by utils/update_mlir_test_checks.py
// RUN: circt-opt -lower-std-to-handshake %s | FileCheck %s
// CHECK-LABEL:   handshake.func @affine_load(
// CHECK-SAME:                                %[[VAL_0:.*]]: index,
// CHECK-SAME:                                %[[VAL_1:.*]]: none, ...) -> none attributes {argNames = ["in0", "inCtrl"], resNames = ["outCtrl"]} {
// CHECK:           %[[VAL_2:.*]]:2 = memory[ld = 1, st = 0] (%[[VAL_3:.*]]) {id = 0 : i32, lsq = false} : memref<10xf32>, (index) -> (f32, none)
// CHECK:           %[[VAL_4:.*]] = merge %[[VAL_0]] : index
// CHECK:           %[[VAL_5:.*]]:4 = fork [4] %[[VAL_1]] : none
// CHECK:           %[[VAL_6:.*]] = constant %[[VAL_5]]#2 {value = 0 : index} : index
// CHECK:           %[[VAL_7:.*]] = constant %[[VAL_5]]#1 {value = 10 : index} : index
// CHECK:           %[[VAL_8:.*]] = constant %[[VAL_5]]#0 {value = 1 : index} : index
// CHECK:           %[[VAL_9:.*]] = cf.br %[[VAL_4]] : index
// CHECK:           %[[VAL_10:.*]] = cf.br %[[VAL_5]]#3 : none
// CHECK:           %[[VAL_11:.*]] = cf.br %[[VAL_6]] : index
// CHECK:           %[[VAL_12:.*]] = cf.br %[[VAL_7]] : index
// CHECK:           %[[VAL_13:.*]] = cf.br %[[VAL_8]] : index
// CHECK:           %[[VAL_14:.*]], %[[VAL_15:.*]] = control_merge %[[VAL_10]] : none
// CHECK:           %[[VAL_16:.*]]:4 = fork [4] %[[VAL_15]] : index
// CHECK:           %[[VAL_17:.*]] = buffer [1] %[[VAL_18:.*]] {initValues = [0], sequential = true} : i1
// CHECK:           %[[VAL_19:.*]]:5 = fork [5] %[[VAL_17]] : i1
// CHECK:           %[[VAL_20:.*]] = mux %[[VAL_19]]#4 {{\[}}%[[VAL_14]], %[[VAL_21:.*]]] : i1, none
// CHECK:           %[[VAL_22:.*]] = mux %[[VAL_16]]#3 {{\[}}%[[VAL_12]]] : index, index
// CHECK:           %[[VAL_23:.*]] = mux %[[VAL_19]]#3 {{\[}}%[[VAL_22]], %[[VAL_24:.*]]] : i1, index
// CHECK:           %[[VAL_25:.*]]:2 = fork [2] %[[VAL_23]] : index
// CHECK:           %[[VAL_26:.*]] = mux %[[VAL_16]]#2 {{\[}}%[[VAL_9]]] : index, index
// CHECK:           %[[VAL_27:.*]] = mux %[[VAL_19]]#2 {{\[}}%[[VAL_26]], %[[VAL_28:.*]]] : i1, index
// CHECK:           %[[VAL_29:.*]] = mux %[[VAL_16]]#1 {{\[}}%[[VAL_13]]] : index, index
// CHECK:           %[[VAL_30:.*]] = mux %[[VAL_19]]#1 {{\[}}%[[VAL_29]], %[[VAL_31:.*]]] : i1, index
// CHECK:           %[[VAL_32:.*]] = mux %[[VAL_16]]#0 {{\[}}%[[VAL_11]]] : index, index
// CHECK:           %[[VAL_33:.*]] = mux %[[VAL_19]]#0 {{\[}}%[[VAL_32]], %[[VAL_34:.*]]] : i1, index
// CHECK:           %[[VAL_35:.*]]:2 = fork [2] %[[VAL_33]] : index
// CHECK:           %[[VAL_18]] = merge %[[VAL_36:.*]]#0 : i1
// CHECK:           %[[VAL_37:.*]] = arith.cmpi slt, %[[VAL_35]]#0, %[[VAL_25]]#0 : index
// CHECK:           %[[VAL_36]]:6 = fork [6] %[[VAL_37]] : i1
// CHECK:           %[[VAL_38:.*]], %[[VAL_39:.*]] = cf.cond_br %[[VAL_36]]#5, %[[VAL_25]]#1 : index
// CHECK:           sink %[[VAL_39]] : index
// CHECK:           %[[VAL_40:.*]], %[[VAL_41:.*]] = cf.cond_br %[[VAL_36]]#4, %[[VAL_27]] : index
// CHECK:           sink %[[VAL_41]] : index
// CHECK:           %[[VAL_42:.*]], %[[VAL_43:.*]] = cf.cond_br %[[VAL_36]]#3, %[[VAL_30]] : index
// CHECK:           sink %[[VAL_43]] : index
// CHECK:           %[[VAL_44:.*]], %[[VAL_45:.*]] = cf.cond_br %[[VAL_36]]#2, %[[VAL_20]] : none
// CHECK:           %[[VAL_46:.*]], %[[VAL_47:.*]] = cf.cond_br %[[VAL_36]]#1, %[[VAL_35]]#1 : index
// CHECK:           sink %[[VAL_47]] : index
// CHECK:           %[[VAL_48:.*]] = merge %[[VAL_46]] : index
// CHECK:           %[[VAL_49:.*]]:2 = fork [2] %[[VAL_48]] : index
// CHECK:           %[[VAL_50:.*]] = merge %[[VAL_40]] : index
// CHECK:           %[[VAL_51:.*]]:2 = fork [2] %[[VAL_50]] : index
// CHECK:           %[[VAL_52:.*]] = merge %[[VAL_42]] : index
// CHECK:           %[[VAL_53:.*]]:2 = fork [2] %[[VAL_52]] : index
// CHECK:           %[[VAL_54:.*]] = merge %[[VAL_38]] : index
// CHECK:           %[[VAL_55:.*]], %[[VAL_56:.*]] = control_merge %[[VAL_44]] : none
// CHECK:           %[[VAL_57:.*]]:2 = fork [2] %[[VAL_55]] : none
// CHECK:           %[[VAL_58:.*]]:2 = fork [2] %[[VAL_57]]#1 : none
// CHECK:           %[[VAL_59:.*]] = join %[[VAL_58]]#1, %[[VAL_2]]#1 : none
// CHECK:           sink %[[VAL_56]] : index
// CHECK:           %[[VAL_60:.*]] = arith.addi %[[VAL_49]]#1, %[[VAL_51]]#1 : index
// CHECK:           %[[VAL_61:.*]] = constant %[[VAL_58]]#0 {value = 7 : index} : index
// CHECK:           %[[VAL_62:.*]] = arith.addi %[[VAL_60]], %[[VAL_61]] : index
// CHECK:           %[[VAL_63:.*]], %[[VAL_3]] = load {{\[}}%[[VAL_62]]] %[[VAL_2]]#0, %[[VAL_57]]#0 : index, f32
// CHECK:           sink %[[VAL_63]] : f32
// CHECK:           %[[VAL_64:.*]] = arith.addi %[[VAL_49]]#0, %[[VAL_53]]#1 : index
// CHECK:           %[[VAL_28]] = cf.br %[[VAL_51]]#0 : index
// CHECK:           %[[VAL_31]] = cf.br %[[VAL_53]]#0 : index
// CHECK:           %[[VAL_24]] = cf.br %[[VAL_54]] : index
// CHECK:           %[[VAL_21]] = cf.br %[[VAL_59]] : none
// CHECK:           %[[VAL_34]] = cf.br %[[VAL_64]] : index
// CHECK:           %[[VAL_65:.*]], %[[VAL_66:.*]] = control_merge %[[VAL_45]] : none
// CHECK:           sink %[[VAL_66]] : index
// CHECK:           return %[[VAL_65]] : none
// CHECK:         }
func @affine_load(%arg0: index) {
  %0 = memref.alloc() : memref<10xf32>
  %c0 = arith.constant 0 : index
  %c10 = arith.constant 10 : index
  %c1 = arith.constant 1 : index
  cf.br ^bb1(%c0 : index)
^bb1(%1: index):      // 2 preds: ^bb0, ^bb2
  %2 = arith.cmpi slt, %1, %c10 : index
  cf.cond_br %2, ^bb2, ^bb3
^bb2: // pred: ^bb1
  %3 = arith.addi %1, %arg0 : index
  %c7 = arith.constant 7 : index
  %4 = arith.addi %3, %c7 : index
  %5 = memref.load %0[%4] : memref<10xf32>
  %6 = arith.addi %1, %c1 : index
  cf.br ^bb1(%6 : index)
^bb3: // pred: ^bb1
  return
}

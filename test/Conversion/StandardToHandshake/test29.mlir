// NOTE: Assertions have been autogenerated by utils/update_mlir_test_checks.py
// RUN: circt-opt -lower-std-to-handshake %s | FileCheck %s

// CHECK-LABEL:   handshake.func @load_store(
// CHECK-SAME:                               %[[VAL_0:.*]]: memref<4xi32>,
// CHECK-SAME:                               %[[VAL_1:.*]]: index,
// CHECK-SAME:                               %[[VAL_2:.*]]: none, ...) -> none
// CHECK:           %[[VAL_3:.*]]:3 = extmemory[ld = 1, st = 1] (%[[VAL_0]] : memref<4xi32>) (%[[VAL_4:.*]], %[[VAL_5:.*]], %[[VAL_6:.*]]) {id = 0 : i32} : (i32, index, index) -> (i32, none, none)
// CHECK:           %[[VAL_7:.*]]:2 = fork [2] %[[VAL_3]]#1 : none
// CHECK:           %[[VAL_8:.*]] = merge %[[VAL_1]] : index
// CHECK:           %[[VAL_9:.*]]:2 = fork [2] %[[VAL_8]] : index
// CHECK:           %[[VAL_10:.*]]:3 = fork [3] %[[VAL_2]] : none
// CHECK:           %[[VAL_11:.*]]:2 = fork [2] %[[VAL_10]]#2 : none
// CHECK:           %[[VAL_12:.*]] = join %[[VAL_11]]#1, %[[VAL_7]]#1, %[[VAL_3]]#2 : none
// CHECK:           %[[VAL_13:.*]] = constant %[[VAL_11]]#0 {value = 11 : i32} : i32
// CHECK:           %[[VAL_4]], %[[VAL_5]] = store {{\[}}%[[VAL_9]]#1] %[[VAL_13]], %[[VAL_10]]#1 : index, i32
// CHECK:           %[[VAL_14:.*]] = join %[[VAL_10]]#0, %[[VAL_7]]#0 : none
// CHECK:           %[[VAL_15:.*]], %[[VAL_6]] = load {{\[}}%[[VAL_9]]#0] %[[VAL_3]]#0, %[[VAL_14]] : index, i32
// CHECK:           sink %[[VAL_15]] : i32
// CHECK:           return %[[VAL_12]] : none
// CHECK:         }
func.func @load_store(%0 : memref<4xi32>, %1 : index) {
  %c1 = arith.constant 11 : i32
  memref.store %c1, %0[%1] : memref<4xi32>
  %3 = memref.load %0[%1] : memref<4xi32>
  return
}

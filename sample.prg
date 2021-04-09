namespace System {
    namespace lang {
        class Object {
            native def Object;
            native def toString;
        }
        class Unit extends Object;
        class Byte extends Object;
        class Integer extends Object {
            native def + (v: Integer);
            native def - (v: Integer);
            native def * (v: Integer);
            native def / (v: Integer);
            native def ** (v: Integer);
            native def toFloat;
            native def toString;
        }
        class Float extends Object {
            native def + (v: Float);
            native def - (v: Float);
            native def * (v: Float);
            native def / (v: Float);
            native def ** (v: Float);
            native def toInteger;
            native def toString;
        }
        class Char extends Object;
        class String extends Object {
            native def length;
            native def toCharArray(): Array[Char];
        }
        class Array[T] extends Object {
            native def length;
        }
        class List[T] extends Object {
            native def length;
        }
        class HashMap[A, B] extends Object;
        class LinkedList[T] extends Object;
    }
}

// 함수 이름에 대한 encoding기능이 현재 미구현
def add(a: int): int = a + 4;
//def sum(from:int, to:int):int {
//  var r = 0, i = 0;
//  // i에 대한 type예측을 compiler가 해주어야 한다.
//  for i <= from ... to:  
//    r += i;
//  return r;
//}

def add(a: int, b: int): int = a + b;

//def main(args:string[]) {
//  System.out.println("Hello, Bear World!");
//  return 0;
//}

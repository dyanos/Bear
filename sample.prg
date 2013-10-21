def add(a:int, b:int):int = a + b;
def sum(from:int, to:int):int {
  var r = 0, i = 0;
  // i에 대한 type예측을 compiler가 해주어야 한다.
  for i <= from ... to:
    r += i;
  return r;
}
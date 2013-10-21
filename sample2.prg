/*namespace System.lang {
native class Object {
public:
  def Object();
  def ~Object();
  
  def toString():System.lang.String;
}

native class Integer : public System.lang.Object {
public:
  def Integer();
  def ~Integer();
  
  def +(right:int);
  def -(right:int);
}
}

def makeRandomList(to:int):List<int> = 
  [1 ... to].random_shuffle;

def sort(lst:List<int>):List<int> {
  val length:int = lst.get_length();
  for i <= [1 ... length]:
    for j <= [1 ... length]:
      if lst[i] > lst[j]:
        (lst[i], lst[j]) = (lst[j], lst[i]);
}

def sum(to:int):int {
  (t < 1) ? true => 1; 
  return reduce(def _(a:int, b:int):int = a + b, [1 ... to]);
}

def factorial(v:int):int {
  // variable ? pattern => <expr> or { <exprs> }, ..., <pattern> => <expr> or { <exprs> };
  return v ?
    0 => 1,
    _ => v*factorial(v-1);
}

def main():_ {
  System.out.println("%d", factorial(10));
  System.out.println("%d", sum(10));
}*/

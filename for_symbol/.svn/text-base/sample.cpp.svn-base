#include <vector>

//template <class T>
class List {
public:
  List() {}
//  List(T a) {}
};

template <class T>
class List1 {
public:
  List1() {}
};

template <class T, class A>
class List2 {
public:
  List2() {}
  List2(T a, A b) {}
};

int x;
List y;
List2<int, float> z_;
List2<List, float> z;

namespace System {
  namespace out {
    void println(char* fmt, ...);
    void print_vector(int val, int val2, std::vector<int>* sample);
    int sum(List* lst);
    int c;
    
    template<class T>
    class List3 {
    public:
      List3() {}
      List3(T a) {}
    };
  };
};

void print_vector(int val, int val2, System::out::List3<int>* sample);

std::vector<int>* shuffle(int length, int** hello);

int main() {
  std::vector<int> sample;
  List* hello;
  System::out::List3<int>* hello2;
  shuffle(10, 0);
  System::out::println("hello");
  System::out::print_vector(6, 5, &sample);
  print_vector(6, 5, hello2);
  System::out::sum(hello);
  System::out::sum(&y);
  x=10;
  List2<int, float> dummy1 = z_;
  List2<List, float> dummy2 = z;
  System::out::c = 10;

  return 0;
}

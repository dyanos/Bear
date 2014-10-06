#include <iostream>

namespace System {
  namespace out {
    void println(char* format) {
      std::cout << format << std::endl;       
    }
  };
};

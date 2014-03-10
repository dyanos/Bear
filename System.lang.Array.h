#include "System.lang.Object.h"

namespace System {
  namespace lang {
    class Array : public Object {
    public:
      Array();
      Array(const Array & right);

      static Array toRange(int a, int b) {
        
      }

    private:
      std::vector<Object> values;
    };
  };
};

#include <iostream>

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

namespace System {
  namespace lang {
    class String {
    public:
      String() : string(nullptr) {}
      String(const char * str) {
        if (str == nullptr || strlen(str) == 0) 
          return;
        
        int len = strlen(str);
        string = new char [len+1];
        memset(string, 0, sizeof(char)*(len + 1));
        strncpy(string, str, len);    
      }
      ~String() {
        if (string != nullptr || strlen(string) == 0)
          delete string;
      }

      // conversion function
      operator char * () {
        return string;
      }

    private:
      char* string;
    };
  };
};

int main() {
  System::lang::String string;
  return 0;
}

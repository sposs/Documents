#include "parent.h"

class MyObject: public parent {
public:
  MyObject(int arg){parent(arg);}
  ~MyObject();
  
  int my_function(int a);
  void  my_other_func();
};

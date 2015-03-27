#include "parent.h"

class MyObject: public Parent {
public:
  MyObject(int arg){Parent(arg);}
  ~MyObject();
  
  int my_function(int a);
  void  my_other_func();
};

#include <vector>
#include <string>
#include <iostream>
#include <stdio.h>

#include "test.h"

//g++ inheritance.cc  -std=c++11 && ./a.exe

using namespace std;

Derived TestClass::func(){
    // this->
    return {};
}


void foo(Base a)
{
    /* code */
    cout<<"size= "<<sizeof(Derived)<<endl;
    cout<<"size= "<<sizeof(a)<<endl;
    // Base *x = &a;
    a.foo();
}

void foo2(Base& a)
{
    /* code */
    a.foo();
    a.
}
//-----------------------------------------------------------------------------------
int main(int argc, char const *argv[])
{
    Derived x;// = new Derived();
    x.foo();

    TestClass ttt;
    ttt.func();

    std::vector<Derived> v;
    v[1].foo();
    v.

    // ((Base*)x)->f();

    foo(x);
    // cout<<"--------"<<endl;
    // foo2(x);
}


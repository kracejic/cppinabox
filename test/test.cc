#include <vector>
#include <string>
#include <iostream>
#include <stdio.h>

#include "test.h"

//g++ inheritance.cc  -std=c++11 && ./a.exe

using namespace std;

Derived TestClass::func(){
    this->cislo
    return {};
}


void foo(Base a)
{
    /* code */
    cout<<"size= "<<sizeof(Derived)<<endl;
    cout<<"size= "<<sizeof(a)<<endl;
    // Base *x = &a;
    a.f();
}

void foo2(Base& a)
{
    /* code */
    a.f();
}
//-----------------------------------------------------------------------------------

int main(int argc, char const *argv[])
{
    Derived x;// = new Derived();
    x.f();

    std::vector<Derived> v;

    // ((Base*)x)->f();

    foo(x);
    // cout<<"--------"<<endl;
    // foo2(x);
}


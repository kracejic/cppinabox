#include <vector>
#include <string>
#include <iostream>
#include <stdio.h>

//g++ inheritance.cc  -std=c++11 && ./a.exe

using namespace std;


class Base {
    int a, b;
  public:
    Base() { cout << "Base()" << endl; };
    virtual ~Base() { cout << "~Base()" << endl; };

    virtual void f(){cout<<"base"<<endl;}
};

class Derived : public Base {
    int c;
  public:
    Derived() { cout << "Derived()" << endl; };
    ~Derived() override { cout << "~Derived()" << endl; };
    void f() override {cout<<"derived"<<endl;}
};

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
    a.
}
//-----------------------------------------------------------------------------------



int main(int argc, char const *argv[])
{
    Derived x;// = new Derived();

    std::vector<Derived> v;
    v.

    // ((Base*)x)->f();

    foo(x);
    // cout<<"--------"<<endl;
    // foo2(x);
}


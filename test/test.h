

#include <vector>
#include <string>
#include <iostream>
#include <stdio.h>


using namespace std;


class Base {
    int a, b;
  public:
    Base() { cout << "Base()" << endl; };
    virtual ~Base() { cout << "~Base()" << endl; };

    virtual void foo(){cout<<"base"<<endl;}
};

class Derived : public Base {
    int c;
  public:
    Derived() { cout << "Derived()" << endl; };
    ~Derived() override { cout << "~Derived()" << endl; };
    void foo() override {cout<<"derived"<<endl;}
};


class TestClass
{
public:
    Derived x;
    int cislo {5};
    TestClass();
    ~TestClass();

    Derived func();

    
};
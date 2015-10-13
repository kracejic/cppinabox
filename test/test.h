

#include <vector>
#include <string>
#include <iostream>
#include <stdio.h>


using namespace std;

/**
 * This is Base class documentation
 */
class Base {
    int a, b;
  public:
    Base() { cout << "Base()" << endl; };
    virtual ~Base() { cout << "~Base()" << endl; };

    /**
     * [foo description]
     */
    virtual void foo(){cout<<"base"<<endl;}
};


/**
 * Derived class doc
 */
class Derived : public Base {
    int c;
  public:
    Derived() { cout << "Derived()" << endl; };
    ~Derived() override { cout << "~Derived()" << endl; };
    /**
     * foo is derived
     */
    void foo() override {cout<<"derived"<<endl;}
};

/**
 * TestClass doc
 */
class TestClass
{
public:
    Derived x;
    int cislo {5};
    TestClass();
    ~TestClass();

    /**
     * [func description] Derived func();
     * @return [description]
     */
    Derived func();

    
};
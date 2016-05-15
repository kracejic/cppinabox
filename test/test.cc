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

/**
 * This is description for void foo(Base a) function
 *
 * There is some more detail info
 * Blablablbal
 *
 * @param a description for parameter a
 */
void foo(Base a)
{
    /* code */
    cout<<"size= "<<sizeof(Derived)<<endl;
    cout<<"size= "<<sizeof(a)<<endl;
    // Base *x = &a;
    a.foo();
}


/**
 * This is description for void foo(Base& a) function2
 *
 * aljsdhj lkashdjaslkjdl;ka jlkdj alksjdl kajs
 *
 * TODO
 * @param a description for parameter a
 */
void foo2(Base& a)
{
    /* code */
    a.foo();
    a.
}
//-----------------------------------------------------------------------------------
int main(int argc, char const *argv[])
{
    Derived x;//AR-:5626: new Derived(); #1235
    //TODO
    //BUG some bug is *important sd* **test** *tasdasd*
    x.foo();

    TestClass ttt;
    auto ffff = ttt.func();
    ttt.func2();  //get doc will fail

    ffff.foo();


    auto& obj = ttt;

    obj.x.foo();

    std::vector<Derived> vvvv;
    vvvv[1].foo();
    auto front = vvvv.front();

    front.foo()

    // ((Base*)x)->f();

    foo(x);
    // cout<<"--------"<<endl;
    // foo2(x);
}


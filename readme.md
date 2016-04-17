# cppinabox

Cppinabox is plugin for C++. It targets on providing almost complete IDE-like experience for developers in C++. This plugin is right now in heavy development.


## Features

* Smart autocompletion (based on YCMD)
* GOTO definition, declaration, definition/declaration, imprecise
* Default sublime text GOTO as a fallback for GOTOs from YCMD
* Get Type (to check if *auto* is deduced correctly), Get parent
* Get Doc - tries to get doxygen documentation via YCMD (fallback: displays surrounding lines of get definition/declaration result)
* Ctrl + Shift + click for GOTO definition/declaration
* Better open header (searches two directories up for common header directy names)
* auto restart of YCMD server in case of server being down


## Features (planned)

* Snippets


## Keyboard shortcuts

| Key           | Function           | 
| ------------- | ------------------ |
| alt+o         | open header        |
| alt+o         | open header        |
| alt+d         | goto def/dec       |
| alt+w         | goto declaration   |
| alt+r         | get doc            |
| alt+c         | get type           |

* Ctrl + Shift + click for GOTO definition/declaration
* Ctrl+shift+P + type cppinabox to see what other function are available


## Instalation of YCMD

### Linux


### Windows + MSYS2

#### Prerequisites

* Python2 
    * download and install python2

* MSYS2
    * Download and install [msys2](https://msys2.github.io/)
    * ```pacman --needed -Sy bash pacman pacman-mirrors msys2-runtime```
    * *restart msys2*
    * ```pacman -Su```
    * ```pacman -S mingw32/mingw-w64-i686-boost mingw32/mingw-w64-i686-clang mingw32/mingw-w64-i686-clang-analyzer mingw32/mingw-w64-i686-clang-tools-extra mingw32/mingw-w64-i686-cmake mingw32/mingw-w64-i686-gcc mingw32/mingw-w64-i686-gdb mingw32/mingw-w64-i686-make mingw32/mingw-w64-i686-ninja mingw32/mingw-w64-i686-python2 mingw32/mingw-w64-i686-python3 msys/git```

    * If you have proxy do not forget to: ```export http_proxy='http://127.0.0.1:6666' ; export ftp_proxy='http://127.0.0.1:6666'```



#### Building YCMD

git clone https://github.com/Valloric/ycmd.git
cd ycmd
mkdir build
cd build
cmake -G "Ninja" -Dgtest_disable_pthreads=TRUE -DUSE_SYSTEM_LIBCLANG=TRUE -DPATH_TO_LLVM_ROOT="/mingw32/bin/" -DUSE_CLANG_COMPLETER=TRUE ../cpp/
ninja  ycm_core

#### Configuring

You can use these commands to get path for standard library:
```
g++ -E -x c++ - -v < /dev/null 
clang++ -E -x c++ - -v < /dev/null
```


And you can add them to your .ycm_extra_conf.py:
```
 "-isystemC:/path_to_msys64/mingw32/include/c++/5.2.0",
 "-isystemC:/path_to_msys64/mingw32/include/c++/5.2.0/i686-w64-mingw32",
 "-isystemC:/path_to_msys64/mingw32/include/c++/5.2.0/backward",
 "-isystemC:/path_to_msys64/mingw32/bin/../lib/clang/3.7.0/include",
 "-isystemC:/path_to_msys64/mingw32/lib/gcc/i686-w64-mingw32/5.2.0/include",
 "-isystemC:/path_to_msys64/mingw32/lib/gcc/i686-w64-mingw32/5.2.0/include-fixed",
 "-isystemC:/path_to_msys64/mingw32/i686-w64-mingw32/include",
 "-isystemC:/path_to_msys64/mingw32/include",
```

Or you can adapt conf file in this plugin.


## Available snippets

|      trigger       |        snippet description           |
| ------------------ | ------------------------------------ |
|  sd     |  std::   |
|  un     |  using namespace std;   |
|  up     |  std::unique_ptr    |
|  mu     |  std::make_unique   |
|  sp     |  std::shared_ptr     |
|  ms     |  std::make_shared     |
|  i8 - ui64     |   uint64_t     |


## C++inabox syntax

Little better syntax highliting straight from github.

paste this into Packages/User/C++inabox.sublime-settings
```.json
{
    "auto_complete_triggers":
    [
        {
            "characters": ".:>",
            "selector": "source.c++ - string - comment - constant.numeric"
        }
    ],
    "extensions":
    [
        "cpp",
        "cc",
        "cxx",
        "c++",
        "c",
        "h",
        "hpp",
        "hxx",
        "h++",
        "inl",
        "ipp"
    ]
}
```


#include "lulesh-wrap.h"

#include <string>
#include <sstream>

// create stubs
namespace std {
void exit_stub(int exit_code)
{
  std::ostringstream what;
  what << "ExitStubError: exit(" << exit_code << ") called\n";
  throw ExitStubError(what.str());
}
} // end of namespace std
using std::exit_stub;

//void exit_stub(int exit_code) { std::exit_stub(exit_code); }

#include <climits>
#include <vector>
#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>
#include <time.h>
#include <sys/time.h>
#include <iostream>
#include <unistd.h>
#include <cstdlib>

#if _OPENMP
# include <omp.h>
#endif

#define main lulesh_main
#define exit exit_stub
#define static
#define inline
#include "lulesh.cc"
#undef inline
#undef static
#undef exit
#undef main


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

#define main lulesh_main
#include <cstdlib>
#define exit exit_stub
#include "lulesh.cc"
#undef exit
#undef maiin


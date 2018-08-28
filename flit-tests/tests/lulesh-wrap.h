#ifndef LULESH_WRAP_H
#define LULESH_WRAP_H

#include <stdexcept>

// exception thrown by the exit_stub()
struct ExitStubError : public std::runtime_error {
  using std::runtime_error::runtime_error;
};

// The main() function from lulesh
int lulesh_main(int argc, char* argv[]);

#endif // LULESH_WRAP_H

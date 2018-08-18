# This file is included by the generated Makefile.  If you have some things you
# want to change about the Makefile, it is best to do it here.

# additional source files to compile other than what is in '.' and 'tests/'
# since those directories are added by a wildcard.
SOURCE         +=

# required compiler flags
# for example, include directories
#   CC_REQUIRED += -I<path>
# or defines
#   CC_REQUIRED += -DDEBUG_ENABLED=1
CC_REQUIRED    += -I..
CC_REQUIRED    += -DUSE_MPI=0
CC_REQUIRED    += -Wno-unknown-pragmas
CC_REQUIRED    += -Wno-unused-parameter

# required linker flags
# for example, link libraries
#   LD_REQUIRED += -L<library-path> -l<library-name>
# or rpath
#   LD_REQUIRED += -Wl,-rpath=<abs-path-to-library-dir>
LD_REQUIRED    +=

# compiler and linker flags respectively - specifically for a dev build
# - DEV_CFLAGS:   non-recorded compiler flags (such as includes)
# - DEV_LDFLAGS:  linker flags (also not under test)
DEV_CFLAGS     +=
DEV_LDFLAGS    +=

# wrapper around the running of the test executable when run through the
# Makefile.
# For example, to run a test incorporating MPI, you could use
#   RUN_WRAPPER := srun --nodes 1
RUN_WRAPPER    :=


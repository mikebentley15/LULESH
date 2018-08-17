#define main main_old
#include "../laghos.cc"
#undef main

#include <flit.h>

#include <string>

namespace {
// RAII wrapper around tmpfile()
struct FileCloser {
  FILE* file;
  int fd;
  TmpFile(FILE* _file) file(_file) {
    if (file == nullptr) {
      throw std::ios_base::failure("Could not open temporary file");
    }
    fd = fileno(tmp);
    if (fd < 0) {
      throw std::ios_base::failure("Could not get file descriptor of"
                                   " the temporary file");
    }
  }
  ~TmpFile() {
    fclose(file);
  }
};

struct FdReplace {
  int old_fd;
  int replace_fd;
  int old_fd_copy;
  FILE* old_file;
  FILE* replace_file;
  FdReplace (FILE* old_file, FILE* replace_file)
    : old_file(_old_file)
    , replace_file(_replace_file)
  {
    old_fd = fileno(old_file);
    if (old_fd < 0)
      throw std::ios_base::failure("Could not get fileno of old_file");
    replace_fd = fileno(replace_file);
    if (replace_fd < 0)
      throw std::ios_base::failure("Could not get fileno of replace_file");
    fflush(old_file);
    old_fd_copy = dup(old_fd);
    if (old_fd_copy < 0)
      throw std::ios_base::failure("Could not dup old_fd");
    if (dup2(replace_fd, old_fd) < 0)
      throw std::ios_base::failure("Could not replace old_fd");
  }
  ~FdReplace () {
    fflush(old_file);
    dup2(old_fd_copy, old_fd);
    close(old_fd_copy);
  }
};

std::string read_file(FILE* file) {
  fseek(file, 0, SEEK_END);
  auto size = ftell(file);
  rewind(file);
  std::string contents(size + 1, '\0');
  auto read_size = fread(contents.data(), size, 1, file);
  if (read_size != size) {
    throw std::ios_base::failure("Did not read in one go");
  }
  return contents;
}
} // end of unnamed namespace

template <typename T>
class LuleshTest : public flit::TestBase<T> {
public:
  LuleshTest(std::string id) : flit::TestBase<T>(std::move(id)) {}
  virtual size_t getInputsPerRun() override { return 0; }
  virtual std::vector<T> getDefaultInput() override { return { }; }

  virtual long double compare(long double ground_truth,
                              long double test_results) const override {
    // absolute error
    return test_results - ground_truth;
  }

  virtual long double compare(const std::string &ground_truth,
                              const std::string &test_results) const override {
    FLIT_UNUSED(ground_truth);
    FLIT_UNUSED(test_results);
    return 0.0;
  }

protected:
  virtual flit::Variant run_impl(const std::vector<T> &ti) override {
    FLIT_UNUSED(ti);
    const char** argv = {"laghos2.0", "-i", "10"};
    const int argc = 3;
    
    FileCloser temporary_file(tmpfile());
    FdReplace replacer(stdout, temporary_file.file);
    FLIT_UNUSED(replacer);

    main_old(argc, argv);

    return read_file(temporary_file.file);
  }

protected:
  using flit::TestBase<T>::id;
};

REGISTER_TYPE(LuleshTest)

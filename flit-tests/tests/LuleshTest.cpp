#include "lulesh-wrap.h"

#include <flit.h>

#include <cstdlib>
#include <stdexcept>
#include <string>
#include <sstream>

#include <unistd.h>

namespace {
// RAII wrapper around tmpfile()
struct FileCloser {
  FILE* file;
  int fd;
  FileCloser(FILE* _file) : file(_file) {
    if (file == nullptr) {
      throw std::ios_base::failure("Could not open temporary file");
    }
    fd = fileno(file);
    if (fd < 0) {
      throw std::ios_base::failure("Could not get file descriptor of"
                                   " the temporary file");
    }
  }
  ~FileCloser() {
    fclose(file);
  }
};

struct FdReplace {
  int old_fd;
  int replace_fd;
  int old_fd_copy;
  FILE* old_file;
  FILE* replace_file;
  FdReplace (FILE* _old_file, FILE* _replace_file)
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
  char* data = const_cast<char*>(contents.data());
  long read_size = fread(data, 1, size, file);
  if (read_size != size) {
    throw std::ios_base::failure(
        "Did not read in one go (" + std::to_string(size) + ", "
        + std::to_string(read_size) + ")");
  }
  return contents;
}

double get_val(const std::string contents, const std::string label) {
  auto label_pos = contents.find(label);
  auto number_pos = contents.find_first_of("0123456789", label_pos);
  auto end_pos = contents.find_first_of("\n \t\r", number_pos);
  return std::stod(contents.substr(number_pos, end_pos - number_pos));
}
} // end of unnamed namespace

template <typename T>
class LuleshTest : public flit::TestBase<T> {
public:
  LuleshTest(std::string id) : flit::TestBase<T>(std::move(id)) {}
  virtual size_t getInputsPerRun() override { return 0; }
  virtual std::vector<T> getDefaultInput() override { return { }; }

  virtual long double compare(const std::string &ground_truth,
                              const std::string &test_results) const override
  {
    auto gt_max_abs_diff   = get_val(ground_truth, "MaxAbsDiff");
    auto gt_total_abs_diff = get_val(ground_truth, "TotalAbsDiff");
    auto gt_max_rel_diff   = get_val(ground_truth, "MaxRelDiff");
    auto tr_max_abs_diff   = get_val(test_results, "MaxAbsDiff");
    auto tr_total_abs_diff = get_val(test_results, "TotalAbsDiff");
    auto tr_max_rel_diff   = get_val(test_results, "MaxRelDiff");

    return std::abs(gt_max_abs_diff - tr_max_abs_diff)
         + std::abs(gt_total_abs_diff - tr_total_abs_diff)
         + std::abs(gt_max_rel_diff - tr_max_rel_diff);
  }

protected:
  virtual flit::Variant run_impl(const std::vector<T> &ti) override {
    FLIT_UNUSED(ti);
    return flit::Variant();
  }

protected:
  using flit::TestBase<T>::id;
};

template <>
flit::Variant LuleshTest<double>::run_impl(const std::vector<double> &ti) {
    FLIT_UNUSED(ti);
    const int argc = 3;
    char arg1[] = "laghos2.0";
    char arg2[] = "-i";
    char arg3[] = "10";
    char* argv[] = {arg1, arg2, arg3};

    FileCloser temporary_file(tmpfile());
    try {
      FdReplace replacer(stdout, temporary_file.file);
      FLIT_UNUSED(replacer);
      lulesh_main(argc, argv);
    } catch (ExitStubError &ex) {
      flit::info_stream << id << ": LULESH errored out\n";
      std::cout << "LULESH errored out, returning rediculous values\n";
      std::cout << "  " << ex.what() << std::endl;
      return
        "Run Error:\n"
        "  MaxAbsDiff   = 5e5\n"
        "  TotalAbsDiff = 5e5\n"
        "  MaxRelDiff   = 5e5\n"
        ;  // some obsurd value
    }
    std::string contents = read_file(temporary_file.file);

    auto max_abs_diff = get_val(contents, "MaxAbsDiff");
    auto total_abs_diff = get_val(contents, "TotalAbsDiff");
    auto max_rel_diff = get_val(contents, "MaxRelDiff");

    flit::info_stream << id << ": ("
      << max_abs_diff
      << total_abs_diff
      << max_rel_diff
      << std::endl;
    std::cout << contents;
    
    return contents;
  }

REGISTER_TYPE(LuleshTest)

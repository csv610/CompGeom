#include <CGAL/Exact_predicates_inexact_constructions_kernel.h>

#include <algorithm>
#include <cstdint>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <random>
#include <stdexcept>
#include <string>

using Kernel = CGAL::Exact_predicates_inexact_constructions_kernel;

static void usage(const char* program) {
  std::cerr << "usage:\n"
            << "  " << program << " square count output.txt [side]\n"
            << "  " << program << " rectangle count output.txt width height\n"
            << "  " << program << " box count output.txt width height depth\n"
            << "  " << program << " cube count output.txt [side]\n"
            << "  " << program << " sphere count output.txt [radius]\n";
}

static std::size_t parse_count(const char* text) {
  const auto value = std::stoull(text);
  if (value == 0) throw std::invalid_argument("count must be positive");
  return static_cast<std::size_t>(value);
}

static double parse_positive(const char* text, const char* name) {
  const double value = std::stod(text);
  if (!(value > 0.0)) throw std::invalid_argument(std::string(name) + " must be positive");
  return value;
}

int main(int argc, char** argv) {
  if (argc < 4) {
    usage(argv[0]);
    return 2;
  }

  try {
    const std::string domain = argv[1];
    const std::size_t count = parse_count(argv[2]);
    const std::string output_path = argv[3];
    const std::uint64_t seed = std::random_device{}();
    std::mt19937_64 generator(seed);
    std::ofstream output(output_path);
    if (!output) throw std::runtime_error("cannot open output file: " + output_path);
    output << count << '\n' << std::setprecision(17);

    if (domain == "square") {
      if (argc > 5) throw std::invalid_argument("square accepts at most one side argument");
      const double side = argc == 5 ? parse_positive(argv[4], "side") : 1.0;
      std::uniform_real_distribution<double> x(0.0, side), y(0.0, side);
      for (std::size_t i = 0; i < count; ++i) output << x(generator) << ' ' << y(generator) << '\n';
    } else if (domain == "rectangle") {
      if (argc != 6) throw std::invalid_argument("rectangle requires width and height");
      const double width = parse_positive(argv[4], "width");
      const double height = parse_positive(argv[5], "height");
      std::uniform_real_distribution<double> x(0.0, width), y(0.0, height);
      for (std::size_t i = 0; i < count; ++i) output << x(generator) << ' ' << y(generator) << '\n';
    } else if (domain == "box") {
      if (argc != 7) throw std::invalid_argument("box requires width, height, and depth");
      const double width = parse_positive(argv[4], "width");
      const double height = parse_positive(argv[5], "height");
      const double depth = parse_positive(argv[6], "depth");
      std::uniform_real_distribution<double> x(0.0, width), y(0.0, height), z(0.0, depth);
      for (std::size_t i = 0; i < count; ++i)
        output << x(generator) << ' ' << y(generator) << ' ' << z(generator) << '\n';
    } else if (domain == "cube") {
      if (argc > 5) throw std::invalid_argument("cube accepts at most one side argument");
      const double side = argc == 5 ? parse_positive(argv[4], "side") : 1.0;
      std::uniform_real_distribution<double> coordinate(0.0, side);
      for (std::size_t i = 0; i < count; ++i)
        output << coordinate(generator) << ' ' << coordinate(generator) << ' '
               << coordinate(generator) << '\n';
    } else if (domain == "sphere") {
      if (argc > 5) throw std::invalid_argument("sphere accepts at most one radius argument");
      const double radius = argc == 5 ? parse_positive(argv[4], "radius") : 1.0;
      std::uniform_real_distribution<double> coordinate(-radius, radius);
      std::size_t generated = 0;
      while (generated < count) {
        const double x = coordinate(generator);
        const double y = coordinate(generator);
        const double z = coordinate(generator);
        if (x * x + y * y + z * z <= radius * radius) {
          output << x << ' ' << y << ' ' << z << '\n';
          ++generated;
        }
      }
    } else {
      throw std::invalid_argument("unknown domain: " + domain);
    }

    std::cout << "generated " << count << " points in a " << domain
              << " and wrote " << output_path << "\n";
  } catch (const std::exception& error) {
    std::cerr << "error: " << error.what() << '\n';
    usage(argv[0]);
    return 1;
  }
}

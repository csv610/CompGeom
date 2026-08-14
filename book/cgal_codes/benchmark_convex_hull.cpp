#include <CGAL/Exact_predicates_inexact_constructions_kernel.h>
#include <CGAL/Surface_mesh.h>
#include <CGAL/convex_hull_2.h>
#include <CGAL/convex_hull_3.h>

#include <chrono>
#include <cstdint>
#include <iomanip>
#include <iostream>
#include <random>
#include <string>
#include <vector>

using Kernel = CGAL::Exact_predicates_inexact_constructions_kernel;
using Clock = std::chrono::steady_clock;

static void usage(const char* program) {
  std::cerr << "usage: " << program << " --dimension 2|3 [--seed number]\n";
}

static std::uint64_t parse_seed(int argc, char** argv) {
  std::uint64_t seed = 42;
  for (int i = 1; i < argc; ++i) {
    const std::string option = argv[i];
    if (option == "--seed" && i + 1 < argc) seed = std::stoull(argv[++i]);
  }
  return seed;
}

static int parse_dimension(int argc, char** argv) {
  for (int i = 1; i + 1 < argc; ++i) {
    if (std::string(argv[i]) == "--dimension") return std::stoi(argv[i + 1]);
  }
  return 0;
}

static void benchmark_2d(std::uint64_t seed) {
  std::mt19937_64 generator(seed);
  std::uniform_real_distribution<double> coordinate(0.0, 1.0);
  std::cout << "dimension,points,hull_vertices,seconds\n";
  for (const std::size_t count : {10ULL, 100ULL, 1000ULL, 10000ULL, 100000ULL, 1000000ULL}) {
    std::vector<Kernel::Point_2> points;
    points.reserve(count);
    for (std::size_t i = 0; i < count; ++i)
      points.emplace_back(coordinate(generator), coordinate(generator));
    std::vector<Kernel::Point_2> hull;
    const auto start = Clock::now();
    CGAL::convex_hull_2(points.begin(), points.end(), std::back_inserter(hull));
    const double seconds = std::chrono::duration<double>(Clock::now() - start).count();
    std::cout << "2," << count << ',' << hull.size() << ','
              << std::setprecision(10) << seconds << '\n';
  }
}

static void benchmark_3d(std::uint64_t seed) {
  std::mt19937_64 generator(seed);
  std::uniform_real_distribution<double> coordinate(0.0, 1.0);
  std::cout << "dimension,points,hull_vertices,hull_faces,seconds\n";
  for (const std::size_t count : {10ULL, 100ULL, 1000ULL, 10000ULL, 100000ULL, 1000000ULL}) {
    std::vector<Kernel::Point_3> points;
    points.reserve(count);
    for (std::size_t i = 0; i < count; ++i)
      points.emplace_back(coordinate(generator), coordinate(generator), coordinate(generator));
    CGAL::Surface_mesh<Kernel::Point_3> hull;
    const auto start = Clock::now();
    CGAL::convex_hull_3(points.begin(), points.end(), hull);
    const double seconds = std::chrono::duration<double>(Clock::now() - start).count();
    std::cout << "3," << count << ',' << num_vertices(hull) << ',' << num_faces(hull) << ','
              << std::setprecision(10) << seconds << '\n';
  }
}

int main(int argc, char** argv) {
  const int dimension = parse_dimension(argc, argv);
  if (dimension != 2 && dimension != 3) {
    usage(argv[0]);
    return 2;
  }
  try {
    if (dimension == 2) benchmark_2d(parse_seed(argc, argv));
    else benchmark_3d(parse_seed(argc, argv));
  } catch (const std::exception& error) {
    std::cerr << "error: " << error.what() << '\n';
    return 1;
  }
}

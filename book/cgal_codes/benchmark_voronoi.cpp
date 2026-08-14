#include <CGAL/Delaunay_triangulation_2.h>
#include <CGAL/Delaunay_triangulation_3.h>
#include <CGAL/Exact_predicates_inexact_constructions_kernel.h>
#include <CGAL/Object.h>

#include <chrono>
#include <cstdint>
#include <iomanip>
#include <iostream>
#include <random>
#include <stdexcept>
#include <string>

using Kernel = CGAL::Exact_predicates_inexact_constructions_kernel;
using Clock = std::chrono::steady_clock;

static void usage(const char* program) {
  std::cerr << "usage: " << program << " --dimension 2|3 [--seed number]\n";
}

static int dimension(int argc, char** argv) {
  for (int i = 1; i + 1 < argc; ++i)
    if (std::string(argv[i]) == "--dimension") return std::stoi(argv[i + 1]);
  return 0;
}

static std::uint64_t seed(int argc, char** argv) {
  for (int i = 1; i + 1 < argc; ++i)
    if (std::string(argv[i]) == "--seed") return std::stoull(argv[i + 1]);
  return 42;
}

static void benchmark_2d(std::uint64_t random_seed) {
  std::mt19937_64 generator(random_seed);
  std::uniform_real_distribution<double> coordinate(0.0, 1.0);
  std::cout << "dimension,sites,finite_delaunay_edges,voronoi_segments,voronoi_rays,"
               "voronoi_lines,seconds\n";
  for (const std::size_t count : {10ULL, 100ULL, 1000ULL, 10000ULL, 100000ULL, 1000000ULL}) {
    CGAL::Delaunay_triangulation_2<Kernel> triangulation;
    const auto start = Clock::now();
    for (std::size_t i = 0; i < count; ++i)
      triangulation.insert(Kernel::Point_2(coordinate(generator), coordinate(generator)));
    std::size_t edges = 0, segments = 0, rays = 0, lines = 0;
    for (auto edge = triangulation.finite_edges_begin();
         edge != triangulation.finite_edges_end(); ++edge) {
      ++edges;
      const CGAL::Object dual = triangulation.dual(*edge);
      if (CGAL::object_cast<Kernel::Segment_2>(&dual)) ++segments;
      else if (CGAL::object_cast<Kernel::Ray_2>(&dual)) ++rays;
      else if (CGAL::object_cast<Kernel::Line_2>(&dual)) ++lines;
    }
    const double seconds = std::chrono::duration<double>(Clock::now() - start).count();
    std::cout << "2," << count << ',' << edges << ',' << segments << ',' << rays << ',' << lines
              << ',' << std::setprecision(10) << seconds << '\n';
  }
}

static void benchmark_3d(std::uint64_t random_seed) {
  std::mt19937_64 generator(random_seed);
  std::uniform_real_distribution<double> coordinate(0.0, 1.0);
  std::cout << "dimension,sites,finite_delaunay_facets,voronoi_segments,voronoi_rays,"
               "voronoi_lines,seconds\n";
  for (const std::size_t count : {10ULL, 100ULL, 1000ULL, 10000ULL, 100000ULL, 1000000ULL}) {
    CGAL::Delaunay_triangulation_3<Kernel> triangulation;
    const auto start = Clock::now();
    for (std::size_t i = 0; i < count; ++i)
      triangulation.insert(Kernel::Point_3(coordinate(generator), coordinate(generator),
                                           coordinate(generator)));
    std::size_t facets = 0, segments = 0, rays = 0, lines = 0;
    for (auto facet = triangulation.finite_facets_begin();
         facet != triangulation.finite_facets_end(); ++facet) {
      ++facets;
      const CGAL::Object dual = triangulation.dual(*facet);
      if (CGAL::object_cast<Kernel::Segment_3>(&dual)) ++segments;
      else if (CGAL::object_cast<Kernel::Ray_3>(&dual)) ++rays;
      else if (CGAL::object_cast<Kernel::Line_3>(&dual)) ++lines;
    }
    const double seconds = std::chrono::duration<double>(Clock::now() - start).count();
    std::cout << "3," << count << ',' << facets << ',' << segments << ',' << rays << ',' << lines
              << ',' << std::setprecision(10) << seconds << '\n';
  }
}

int main(int argc, char** argv) {
  const int requested_dimension = dimension(argc, argv);
  if (requested_dimension != 2 && requested_dimension != 3) {
    usage(argv[0]);
    return 2;
  }
  try {
    if (requested_dimension == 2) benchmark_2d(seed(argc, argv));
    else benchmark_3d(seed(argc, argv));
  } catch (const std::exception& error) {
    std::cerr << "error: " << error.what() << '\n';
    return 1;
  }
}

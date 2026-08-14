#include <CGAL/Constrained_Delaunay_triangulation_2.h>
#include <CGAL/Delaunay_mesh_face_base_2.h>
#include <CGAL/Delaunay_mesh_size_criteria_2.h>
#include <CGAL/Delaunay_mesh_vertex_base_2.h>
#include <CGAL/Delaunay_mesher_2.h>
#include <CGAL/Delaunay_triangulation_3.h>
#include <CGAL/Exact_predicates_inexact_constructions_kernel.h>
#include <CGAL/Triangulation_data_structure_2.h>

#include <chrono>
#include <cstdint>
#include <iomanip>
#include <iostream>
#include <random>
#include <stdexcept>
#include <string>
#include <vector>

using Kernel = CGAL::Exact_predicates_inexact_constructions_kernel;
using Clock = std::chrono::steady_clock;

static void usage(const char* program) {
  std::cerr << "usage: " << program
            << " --dimension 2|3 [--seed number] [--refine-max-edge value]\n";
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

static double refine_max_edge(int argc, char** argv) {
  for (int i = 1; i + 1 < argc; ++i)
    if (std::string(argv[i]) == "--refine-max-edge") return std::stod(argv[i + 1]);
  return 0.0;
}

static void benchmark_2d(std::uint64_t random_seed, double max_edge) {
  using Vertex_base = CGAL::Delaunay_mesh_vertex_base_2<Kernel>;
  using Face_base = CGAL::Delaunay_mesh_face_base_2<Kernel>;
  using Tds = CGAL::Triangulation_data_structure_2<Vertex_base, Face_base>;
  using Triangulation = CGAL::Constrained_Delaunay_triangulation_2<Kernel, Tds>;
  using Criteria = CGAL::Delaunay_mesh_size_criteria_2<Triangulation>;
  std::mt19937_64 generator(random_seed);
  std::uniform_real_distribution<double> coordinate(0.0, 1.0);
  std::cout << "dimension,points,vertices,finite_faces,refined,seconds\n";
  for (const std::size_t count : {10ULL, 100ULL, 1000ULL, 10000ULL, 100000ULL, 1000000ULL}) {
    Triangulation triangulation;
    const auto start = Clock::now();
    for (std::size_t i = 0; i < count; ++i)
      triangulation.insert(Kernel::Point_2(coordinate(generator), coordinate(generator)));
    const bool refine = max_edge > 0.0;
    if (refine) {
      CGAL::Delaunay_mesher_2<Triangulation, Criteria> mesher(
          triangulation, Criteria(0.125, max_edge));
      mesher.init(false);
      mesher.refine_mesh();
    }
    const double seconds = std::chrono::duration<double>(Clock::now() - start).count();
    std::cout << "2," << count << ',' << triangulation.number_of_vertices() << ','
              << triangulation.number_of_faces() << ',' << (refine ? "true" : "false")
              << ',' << std::setprecision(10) << seconds << '\n';
  }
}

static void benchmark_3d(std::uint64_t random_seed) {
  std::mt19937_64 generator(random_seed);
  std::uniform_real_distribution<double> coordinate(0.0, 1.0);
  std::cout << "dimension,points,vertices,finite_cells,refined,seconds\n";
  for (const std::size_t count : {10ULL, 100ULL, 1000ULL, 10000ULL, 100000ULL, 1000000ULL}) {
    CGAL::Delaunay_triangulation_3<Kernel> triangulation;
    const auto start = Clock::now();
    for (std::size_t i = 0; i < count; ++i)
      triangulation.insert(Kernel::Point_3(coordinate(generator), coordinate(generator),
                                           coordinate(generator)));
    const double seconds = std::chrono::duration<double>(Clock::now() - start).count();
    std::cout << "3," << count << ',' << triangulation.number_of_vertices() << ','
              << triangulation.number_of_finite_cells() << ",false," << std::setprecision(10)
              << seconds << '\n';
  }
}

int main(int argc, char** argv) {
  const int requested_dimension = dimension(argc, argv);
  if (requested_dimension != 2 && requested_dimension != 3) {
    usage(argv[0]);
    return 2;
  }
  try {
    const double max_edge = refine_max_edge(argc, argv);
    if (max_edge < 0.0) throw std::invalid_argument("refine-max-edge must be nonnegative");
    if (requested_dimension == 3 && max_edge > 0.0)
      throw std::invalid_argument("3D quality refinement is not enabled in this benchmark");
    if (requested_dimension == 2) benchmark_2d(seed(argc, argv), max_edge);
    else benchmark_3d(seed(argc, argv));
  } catch (const std::exception& error) {
    std::cerr << "error: " << error.what() << '\n';
    return 1;
  }
}

#include <CGAL/Constrained_Delaunay_triangulation_2.h>
#include <CGAL/Delaunay_mesh_face_base_2.h>
#include <CGAL/Delaunay_mesh_vertex_base_2.h>
#include <CGAL/Delaunay_triangulation_3.h>
#include <CGAL/Exact_predicates_inexact_constructions_kernel.h>
#include <CGAL/IO/polygon_mesh_io.h>
#include <CGAL/Side_of_triangle_mesh.h>
#include <CGAL/Surface_mesh.h>
#include <CGAL/Triangulation_data_structure_2.h>

#include <array>
#include <fstream>
#include <iostream>
#include <sstream>
#include <stdexcept>
#include <string>
#include <vector>

using Kernel = CGAL::Exact_predicates_inexact_constructions_kernel;

static std::vector<std::array<double, 4>> read_constraints(const std::string& path) {
  std::ifstream input(path);
  if (!input) throw std::runtime_error("cannot open 2D constraint file: " + path);
  std::vector<std::array<double, 4>> constraints;
  std::string line;
  while (std::getline(input, line)) {
    const auto comment = line.find('#');
    if (comment != std::string::npos) line.resize(comment);
    std::istringstream parser(line);
    std::array<double, 4> values{};
    if (!(parser >> values[0])) continue;
    if (!(parser >> values[1] >> values[2] >> values[3]))
      throw std::runtime_error("2D constraints require x1 y1 x2 y2");
    constraints.push_back(values);
  }
  return constraints;
}

static int voronoi_2d(const std::string& path) {
  using Vb = CGAL::Delaunay_mesh_vertex_base_2<Kernel>;
  using Fb = CGAL::Delaunay_mesh_face_base_2<Kernel>;
  using Tds = CGAL::Triangulation_data_structure_2<Vb, Fb>;
  using Triangulation = CGAL::Constrained_Delaunay_triangulation_2<Kernel, Tds>;
  const auto constraints = read_constraints(path);
  Triangulation triangulation;
  for (const auto& segment : constraints)
    triangulation.insert_constraint(Kernel::Point_2(segment[0], segment[1]),
                                    Kernel::Point_2(segment[2], segment[3]));
  std::size_t edges = 0, segments = 0, rays = 0;
  for (auto edge = triangulation.finite_edges_begin();
       edge != triangulation.finite_edges_end(); ++edge) {
    ++edges;
    const auto face = edge->first;
    const auto neighbor = face->neighbor(edge->second);
    if (triangulation.is_infinite(neighbor)) ++rays;
    else ++segments;
  }
  std::cout << "dimension: 2\nconstraints: " << constraints.size()
            << "\nfinite constrained-Delaunay edges: " << edges
            << "\nVoronoi segments: " << segments << "\nVoronoi rays: " << rays << '\n';
  return 0;
}

static int voronoi_3d(const std::string& path) {
  using Surface = CGAL::Surface_mesh<Kernel::Point_3>;
  Surface surface;
  if (!CGAL::IO::read_polygon_mesh(path, surface) || surface.is_empty())
    throw std::runtime_error("cannot read non-empty OBJ/OFF surface: " + path);
  CGAL::Delaunay_triangulation_3<Kernel> triangulation;
  for (auto vertex : surface.vertices()) triangulation.insert(surface.point(vertex));
  CGAL::Side_of_triangle_mesh<Surface, Kernel> inside(surface);
  std::size_t facets = 0, restricted_segments = 0, rays = 0, lines = 0;
  for (auto facet = triangulation.finite_facets_begin();
       facet != triangulation.finite_facets_end(); ++facet) {
    const CGAL::Object dual = triangulation.dual(*facet);
    if (const auto* segment = CGAL::object_cast<Kernel::Segment_3>(&dual)) {
      ++facets;
      const Kernel::Point_3 midpoint = CGAL::midpoint(segment->source(), segment->target());
      if (inside(midpoint) != CGAL::ON_UNBOUNDED_SIDE) ++restricted_segments;
    } else if (CGAL::object_cast<Kernel::Ray_3>(&dual)) {
      ++rays;
    } else if (CGAL::object_cast<Kernel::Line_3>(&dual)) {
      ++lines;
    }
  }
  std::cout << "dimension: 3\nconstraint surface vertices: " << num_vertices(surface)
            << "\nconstraint surface faces: " << num_faces(surface)
            << "\nVoronoi segments inside domain: " << restricted_segments
            << "\nboundary rays: " << rays << "\nlines: " << lines << '\n';
  return 0;
}

int main(int argc, char** argv) {
  if (argc != 4 || std::string(argv[1]) != "--dimension") {
    std::cerr << "usage: constrained_voronoi --dimension 2|3 constraints.{txt,obj,off}\n";
    return 2;
  }
  try {
    const int dimension = std::stoi(argv[2]);
    if (dimension == 2) return voronoi_2d(argv[3]);
    if (dimension == 3) return voronoi_3d(argv[3]);
    throw std::invalid_argument("dimension must be 2 or 3");
  } catch (const std::exception& error) {
    std::cerr << "error: " << error.what() << '\n';
    return 1;
  }
}

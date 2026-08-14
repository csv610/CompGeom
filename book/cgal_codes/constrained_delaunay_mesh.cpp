#include <CGAL/Constrained_Delaunay_triangulation_2.h>
#include <CGAL/Delaunay_mesh_face_base_2.h>
#include <CGAL/Delaunay_mesh_size_criteria_2.h>
#include <CGAL/Delaunay_mesh_vertex_base_2.h>
#include <CGAL/Delaunay_mesher_2.h>
#include <CGAL/Exact_predicates_inexact_constructions_kernel.h>
#include <CGAL/IO/polygon_mesh_io.h>
#include <CGAL/Mesh_complex_3_in_triangulation_3.h>
#include <CGAL/Mesh_criteria_3.h>
#include <CGAL/Mesh_triangulation_3.h>
#include <CGAL/Polyhedral_mesh_domain_3.h>
#include <CGAL/Surface_mesh.h>
#include <CGAL/Triangulation_data_structure_2.h>
#include <CGAL/make_mesh_3.h>

#include <array>
#include <fstream>
#include <iostream>
#include <sstream>
#include <stdexcept>
#include <string>
#include <vector>

using Kernel = CGAL::Exact_predicates_inexact_constructions_kernel;

static std::vector<std::array<double, 4>> read_2d_constraints(const std::string& path) {
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

static int mesh_2d(const std::string& path) {
  using Vb = CGAL::Delaunay_mesh_vertex_base_2<Kernel>;
  using Fb = CGAL::Delaunay_mesh_face_base_2<Kernel>;
  using Tds = CGAL::Triangulation_data_structure_2<Vb, Fb>;
  using Tr = CGAL::Constrained_Delaunay_triangulation_2<Kernel, Tds>;
  using Criteria = CGAL::Delaunay_mesh_size_criteria_2<Tr>;
  const auto constraints = read_2d_constraints(path);
  Tr triangulation;
  for (const auto& constraint : constraints)
    triangulation.insert_constraint(Kernel::Point_2(constraint[0], constraint[1]),
                                    Kernel::Point_2(constraint[2], constraint[3]));
  CGAL::Delaunay_mesher_2<Tr, Criteria> mesher(triangulation, Criteria(0.125, 0.0));
  mesher.init(true);
  mesher.refine_mesh();
  std::cout << "dimension: 2\nconstraints: " << constraints.size()
            << "\nvertices: " << triangulation.number_of_vertices()
            << "\nfinite faces: " << triangulation.number_of_faces() << '\n';
  return 0;
}

static int mesh_3d(const std::string& path) {
  using Surface = CGAL::Surface_mesh<Kernel::Point_3>;
  using Domain = CGAL::Polyhedral_mesh_domain_3<Surface, Kernel>;
  using Tr = typename CGAL::Mesh_triangulation_3<Domain>::type;
  using C3t3 = CGAL::Mesh_complex_3_in_triangulation_3<Tr>;
  using Criteria = CGAL::Mesh_criteria_3<Tr>;
  Surface surface;
  if (!CGAL::IO::read_polygon_mesh(path, surface) || surface.is_empty())
    throw std::runtime_error("cannot read non-empty OBJ/OFF surface: " + path);
  Domain domain(surface);
  Criteria criteria(CGAL::parameters::facet_angle = 30,
                    CGAL::parameters::facet_size = 0.2,
                    CGAL::parameters::cell_radius_edge_ratio = 2,
                    CGAL::parameters::cell_size = 0.2);
  C3t3 mesh = CGAL::make_mesh_3<C3t3>(domain, criteria);
  std::cout << "dimension: 3\ninput surface vertices: " << num_vertices(surface)
            << "\ninput surface faces: " << num_faces(surface)
            << "\nmesh cells: " << mesh.number_of_cells_in_complex() << '\n';
  return 0;
}

int main(int argc, char** argv) {
  if (argc != 4 || std::string(argv[1]) != "--dimension") {
    std::cerr << "usage: constrained_delaunay_mesh --dimension 2|3 constraints.{txt,obj,off}\n";
    return 2;
  }
  try {
    const int dimension = std::stoi(argv[2]);
    const std::string path = argv[3];
    if (dimension == 2) return mesh_2d(path);
    if (dimension == 3) return mesh_3d(path);
    throw std::invalid_argument("dimension must be 2 or 3");
  } catch (const std::exception& error) {
    std::cerr << "error: " << error.what() << '\n';
    return 1;
  }
}

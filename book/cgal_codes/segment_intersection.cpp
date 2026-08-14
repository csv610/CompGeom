#include <CGAL/Exact_predicates_exact_constructions_kernel.h>
#include <CGAL/intersections.h>

#include <fstream>
#include <iostream>
#include <sstream>
#include <stdexcept>
#include <string>
#include <variant>
#include <vector>

using Kernel = CGAL::Exact_predicates_exact_constructions_kernel;

static std::vector<std::vector<double>> read_segments(const std::string& path) {
  std::ifstream input(path);
  if (!input) throw std::runtime_error("cannot open segment file: " + path);
  std::vector<std::vector<double>> rows;
  std::string line;
  std::size_t expected = 0;
  bool first = true;
  std::size_t dimension = 0;
  while (std::getline(input, line)) {
    const auto comment = line.find('#');
    if (comment != std::string::npos) line.resize(comment);
    std::istringstream parser(line);
    std::vector<double> row;
    double value;
    while (parser >> value) row.push_back(value);
    if (row.empty()) continue;
    if (first && row.size() == 1) {
      expected = static_cast<std::size_t>(row.front());
      first = false;
      continue;
    }
    first = false;
    if (row.size() != 4 && row.size() != 6)
      throw std::runtime_error("each segment must have 4 or 6 coordinates");
    const std::size_t row_dimension = row.size() == 4 ? 2 : 3;
    if (dimension == 0) dimension = row_dimension;
    if (row_dimension != dimension)
      throw std::runtime_error("mixed 2D and 3D segments are not supported");
    rows.push_back(std::move(row));
  }
  if (expected != 0 && expected != rows.size())
    throw std::runtime_error("segment-count header does not match input");
  return rows;
}

template <typename Point, typename Segment>
static void print_intersections(const std::vector<Segment>& segments) {
  using Intersection = std::variant<Point, Segment>;
  for (std::size_t first = 0; first < segments.size(); ++first) {
    for (std::size_t second = first + 1; second < segments.size(); ++second) {
      const auto result = CGAL::intersection(segments[first], segments[second]);
      std::cout << "segments " << first << "," << second << ": ";
      if (!result) {
        std::cout << "disjoint\n";
        continue;
      }
      const Intersection& value = *result;
      if (const auto* point = std::get_if<Point>(&value))
        std::cout << "point intersection: " << *point << '\n';
      else
        std::cout << "overlap: " << std::get<Segment>(value) << '\n';
    }
  }
}

int main(int argc, char** argv) {
  if (argc != 2) {
    std::cerr << "usage: segment_intersection segments.txt\n"
              << "format: x1 y1 x2 y2 (2D) or x1 y1 z1 x2 y2 z2 (3D)\n";
    return 2;
  }
  try {
    const auto rows = read_segments(argv[1]);
    if (rows.empty()) throw std::runtime_error("input file contains no segments");
    if (rows.front().size() == 4) {
      std::vector<Kernel::Segment_2> segments;
      for (const auto& row : rows)
        segments.emplace_back(Kernel::Point_2(row[0], row[1]),
                              Kernel::Point_2(row[2], row[3]));
      std::cout << "dimension: 2\nsegments: " << segments.size() << '\n';
      print_intersections<Kernel::Point_2>(segments);
    } else {
      std::vector<Kernel::Segment_3> segments;
      for (const auto& row : rows)
        segments.emplace_back(Kernel::Point_3(row[0], row[1], row[2]),
                              Kernel::Point_3(row[3], row[4], row[5]));
      std::cout << "dimension: 3\nsegments: " << segments.size() << '\n';
      print_intersections<Kernel::Point_3>(segments);
    }
  } catch (const std::exception& error) {
    std::cerr << "error: " << error.what() << '\n';
    return 1;
  }
}

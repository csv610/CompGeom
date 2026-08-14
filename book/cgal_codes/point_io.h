#pragma once

#include <cstddef>
#include <cctype>
#include <fstream>
#include <sstream>
#include <stdexcept>
#include <string>
#include <vector>

namespace compgeom {

inline std::string extension(const std::string& path) {
  const auto dot = path.find_last_of('.');
  if (dot == std::string::npos) return {};
  std::string result = path.substr(dot + 1);
  for (char& character : result)
    character = static_cast<char>(std::tolower(static_cast<unsigned char>(character)));
  return result;
}

inline std::vector<std::vector<double>> read_mesh_rows(const std::string& path,
                                                        std::size_t dimension) {
  std::ifstream input(path);
  if (!input) throw std::runtime_error("cannot open point file: " + path);
  const std::string format = extension(path);
  std::vector<std::vector<double>> rows;
  std::string line;
  std::size_t expected = 0;
  if (format == "off") {
    if (!(input >> line) || line != "OFF")
      throw std::runtime_error("OFF file must begin with OFF: " + path);
    std::size_t face_count = 0, edge_count = 0;
    if (!(input >> expected >> face_count >> edge_count))
      throw std::runtime_error("invalid OFF counts: " + path);
    rows.reserve(expected);
    for (std::size_t i = 0; i < expected; ++i) {
      double x, y, z;
      if (!(input >> x >> y >> z)) throw std::runtime_error("invalid OFF vertex: " + path);
      rows.push_back(dimension == 2 ? std::vector<double>{x, y}
                                    : std::vector<double>{x, y, z});
    }
    return rows;
  }
  while (std::getline(input, line)) {
    if (format == "obj") {
      std::istringstream in(line);
      std::string tag;
      double x, y, z;
      if (in >> tag && tag == "v" && in >> x >> y >> z)
        rows.push_back(dimension == 2 ? std::vector<double>{x, y}
                                      : std::vector<double>{x, y, z});
    }
  }
  if (format == "obj" && rows.empty()) throw std::runtime_error("OBJ contains no vertices: " + path);
  return rows;
}

inline std::vector<std::vector<double>> read_rows(const std::string& path,
                                                   std::size_t dimension) {
  const std::string format = extension(path);
  if (format == "obj" || format == "off") return read_mesh_rows(path, dimension);
  std::ifstream input(path);
  if (!input) throw std::runtime_error("cannot open point file: " + path);
  std::vector<std::vector<double>> rows;
  std::string line;
  std::size_t expected = 0;
  bool first = true;
  while (std::getline(input, line)) {
    const auto comment = line.find('#');
    if (comment != std::string::npos) line.resize(comment);
    std::istringstream in(line);
    std::vector<double> row;
    double value;
    while (in >> value) row.push_back(value);
    if (row.empty()) continue;
    if (first && row.size() == 1) {
      expected = static_cast<std::size_t>(row.front());
      first = false;
      rows.reserve(expected);
      continue;
    }
    first = false;
    if (row.size() != dimension)
      throw std::runtime_error("expected " + std::to_string(dimension) +
                               " coordinates per point in " + path);
    rows.push_back(std::move(row));
  }
  if (expected != 0 && rows.size() != expected)
    throw std::runtime_error("point-count header does not match " + path);
  return rows;
}

inline std::vector<std::vector<double>> read_rows_auto(const std::string& path) {
  const std::string format = extension(path);
  if (format == "obj" || format == "off") return read_mesh_rows(path, 3);
  std::ifstream input(path);
  if (!input) throw std::runtime_error("cannot open point file: " + path);
  std::vector<std::vector<double>> rows;
  std::string line;
  std::size_t expected = 0;
  bool first = true;
  std::size_t dimension = 0;
  while (std::getline(input, line)) {
    const auto comment = line.find('#');
    if (comment != std::string::npos) line.resize(comment);
    std::istringstream in(line);
    std::vector<double> row;
    double value;
    while (in >> value) row.push_back(value);
    if (row.empty()) continue;
    if (first && row.size() == 1) {
      expected = static_cast<std::size_t>(row.front());
      first = false;
      continue;
    }
    first = false;
    if (row.size() != 2 && row.size() != 3)
      throw std::runtime_error("each point must have 2 or 3 coordinates in " + path);
    if (dimension == 0) dimension = row.size();
    if (row.size() != dimension)
      throw std::runtime_error("mixed 2D and 3D points in " + path);
    rows.push_back(std::move(row));
  }
  if (expected != 0 && rows.size() != expected)
    throw std::runtime_error("point-count header does not match " + path);
  return rows;
}

template <typename Point>
inline std::vector<Point> read_points_2d(const std::string& path) {
  const auto rows = read_rows(path, 2);
  std::vector<Point> points;
  points.reserve(rows.size());
  for (const auto& row : rows) points.emplace_back(row[0], row[1]);
  return points;
}

template <typename Point>
inline std::vector<Point> read_points_3d(const std::string& path) {
  const auto rows = read_rows(path, 3);
  std::vector<Point> points;
  points.reserve(rows.size());
  for (const auto& row : rows) points.emplace_back(row[0], row[1], row[2]);
  return points;
}

} // namespace compgeom

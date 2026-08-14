#include <CGAL/Exact_predicates_exact_constructions_kernel.h>
#include <CGAL/Polygon_2.h>
#include <CGAL/Polygon_set_2.h>

#include <iostream>
#include <list>

using Kernel = CGAL::Exact_predicates_exact_constructions_kernel;
using Point = Kernel::Point_2;
using Polygon = CGAL::Polygon_2<Kernel>;
using PolygonSet = CGAL::Polygon_set_2<Kernel>;
using PolygonWithHoles = CGAL::Polygon_with_holes_2<Kernel>;

static Polygon make_rectangle(int left, int bottom, int right, int top) {
  Polygon polygon;
  polygon.push_back(Point(left, bottom));
  polygon.push_back(Point(right, bottom));
  polygon.push_back(Point(right, top));
  polygon.push_back(Point(left, top));
  return polygon;
}

int main() {
  const Polygon first = make_rectangle(0, 0, 4, 3);
  const Polygon second = make_rectangle(2, 1, 6, 4);

  PolygonSet intersection;
  intersection.insert(first);
  intersection.intersection(second);

  std::list<PolygonWithHoles> output;
  intersection.polygons_with_holes(std::back_inserter(output));

  std::cout << "intersection components: " << output.size() << '\n';
  for (const PolygonWithHoles& polygon : output) {
    std::cout << "outer boundary area: " << polygon.outer_boundary().area()
              << '\n';
  }
  return 0;
}


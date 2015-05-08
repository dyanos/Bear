#ifndef _UTILITY_H_
#define _UTILITY_H_

#include <cmath>

const double PI = 3.141592653589793238463;
const float  PI_F = 3.14159265358979f;

double getDistance(double lat1, double long1, double lat2, double long2) {
  double degrees_to_radians = ::PI / 180.0;

  double phi1 = (90.0 - lat1) * degrees_to_radians;
  double phi2 = (90.0 - lat2) * degrees_to_radians;

  double theta1 = long1 * degrees_to_radians;
  double theta2 = long2 * degrees_to_radians;

  double v = std::sin(phi1) * std::sin(phi2) * std::cos(theta1 - theta2) + std::cos(phi1) * std::cos(phi2);

  if (v > 1.0) 
    v = 1.0;
  else if (v < -1.0) 
    v = -1.0;

  return std::acos(v) * 6373.0;
}

#endif


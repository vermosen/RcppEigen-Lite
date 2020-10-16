#pragma once
#ifndef RCPPUTILS_NANOTIME_H
#define RCPPUTILS_NANOTIME_H

#include <Rcpp.h>

#include <vector>

// TODO: it seems impossible to return a const reference here
// maybe migrating to https://github.com/r-lib/cpp11 at some point
inline std::vector<std::int64_t> nanotime_to_int64(const Rcpp::NumericVector& v) {

  std::vector<double> in = Rcpp::as<std::vector<double>>(v);
  std::vector<std::int64_t> rv =
    *reinterpret_cast<std::vector<std::int64_t>*>(&in);
  return rv;
}

inline Rcpp::NumericVector int64_to_nanotime(std::vector<std::int64_t>&& in) {
  const std::vector<double>& vec =
    *reinterpret_cast<const std::vector<double>*>(&in);
  Rcpp::NumericVector rv = Rcpp::wrap(vec);
  return rv;
}

inline std::int64_t nanotime_to_int64(double v) {
  std::int64_t rv = *reinterpret_cast<std::int64_t*>(&v);
  return rv;
}

inline double int64_to_nanotime(std::int64_t in) {
  double rv = *reinterpret_cast<double*>(&in);
  return rv;
}

#endif // RCPPUTILS_NANOTIME_H
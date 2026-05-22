// wtmm.cpp  –  Wavelet-Transform Modulus-Maxima multi-fractal spectrum
// g++ -O2 wtmm.cpp -lgsl -lgslcblas -lm -o wtmm
// ./wtmm attractor.txt  -> width

#include <iostream>
#include <vector>
#include <cmath>
#include <gsl/gsl_wavelet.h>
#include <gsl/gsl_sort.h>
#include <algorithm>

static double width(const std::vector<double>& x);

int main(int argc, char* argv[])
{
    if (argc != 2) { std::cerr << "usage: wtmm file.txt\n"; return 1; }
    FILE* f = fopen(argv[1], "r");
    if (!f) { std::perror("fopen"); return 1; }
    double v;
    std::vector<double> sig;
    while (fscanf(f, "%lf", &v) == 1) sig.push_back(v);
    fclose(f);
    if (sig.size() < 64) { std::cerr << "need >=64 samples\n"; return 1; }
    size_t n = 1;
    while ((n << 1) <= sig.size()) n <<= 1;
    sig.resize(n);
    std::cout << width(sig) << '\n';
    return 0;
}

static double width(const std::vector<double>& x)
{
    const size_t n = x.size();
    gsl_wavelet* w = gsl_wavelet_alloc(gsl_wavelet_daubechies, 4);
    gsl_wavelet_workspace* work = gsl_wavelet_workspace_alloc(n);
    std::vector<double> y = x;
    gsl_wavelet_transform_forward(w, y.data(), 1, n, work);
    gsl_wavelet_workspace_free(work);
    gsl_wavelet_free(w);

    // modulus maxima line histogram -> Hölder exponents
    std::vector<double> h;
    for (size_t i = 1; i + 1 < n; ++i)
        if (std::fabs(y[i]) > std::fabs(y[i-1]) && std::fabs(y[i]) > std::fabs(y[i+1]))
            h.push_back(std::log2(std::fabs(y[i])));
    if (h.size() < 8) return 0.0;
    gsl_sort(h.data(), 1, h.size());
    return h[static_cast<size_t>(h.size()*0.84)] - h[static_cast<size_t>(h.size()*0.16)];
}

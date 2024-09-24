#include <bits/stdc++.h>
using namespace std;

const double PI = 3.141592653589793238;

double sqr(double x)
{
	return x * x;
}

double getProb(int id)
{
	double mu = 24.0;
	double sigma = 6.0;
	return 200.0 / (sqrt(PI * 2.0) * sigma) * exp(-sqr(double(id) - mu) / (sqr(sigma) * 2));
}

int main()
{
	freopen("manual_dump.txt", "w", stdout);

	return 0;
}
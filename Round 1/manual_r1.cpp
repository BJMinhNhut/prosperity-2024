#include <bits/stdc++.h>
using namespace std;

const double a = 0.0002;
const double b = -0.18;

double P(double upper)
{ // P(x < upper)
	double ans = 0.0;
	for (int x = 900; x < upper; ++x)
		ans += a * double(x) + b;
	return ans;
}

int main()
{
	freopen("manual_dump.txt", "w", stdout);
	int x, y;
	double best = -1e18;
	for (int i = 900; i <= 1000; ++i)
		for (int j = i + 1; j <= 1000; ++j)
		{
			double ans = double(1000 - i) * P(i) + double(1000 - j) * (P(j) - P(i));
			cout << ans << "= " << double(1000 - i) * P(i) << " + " << double(1000 - j) * (P(j) - P(i)) << " => " << i << ' ' << j << '\n';
			if (best < ans)
			{
				best = ans;
				x = i, y = j;
			}
		}
	cout << P(1000) << '\n';
	cout << best << ' ' << x << ' ' << y;
}
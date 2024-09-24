#include <bits/stdc++.h>
using namespace std;

vector<string> label = {"Pizza", "Wasabi", "Snowball", "Shells"};
vector<vector<double>> proportion = {
	{1, 0.48, 1.52, 0.71},
	{2.05, 1, 3.26, 1.56},
	{0.64, 0.3, 1, 0.46},
	{1.41, 0.61, 2.08, 1}};

vector<string> trades;
vector<string> best;
double best_proportion = 0.0;
const double eps = 1e-6;

void backtrack(int lastObj, int cnt, double cur_proportion)
{
	if (cnt == 5 || trades.back() == "Shells")
	{
		if (trades.back() == "Shells" && cur_proportion > 2000000.0 + eps)
		{
			for (string &obj : trades)
				cout << obj << ' ';
			cout << setprecision(5) << fixed << cur_proportion << ' ' << (cur_proportion - 2000000.0) / 2000000.0 * 100.0 << "%\n";
		}
		if (trades.back() == "Shells")
		{
			if (best_proportion + eps < cur_proportion || (best_proportion - cur_proportion <= eps && trades.size() < best.size()))
			{
				best_proportion = cur_proportion;
				best = trades;
			}
		}
	}
	if (cnt == 5)
		return;
	for (int i = 0; i < 4; ++i)
	{
		trades.push_back(label[i]);
		backtrack(i, cnt + 1, cur_proportion * proportion[lastObj][i]);
		trades.pop_back();
	}
}

int main()
{
	freopen("manual_r2_dump.txt", "w", stdout);
	trades = {"Shells"};
	backtrack(3, 0, 2'000'000.0);
	cout << "--------------------\n";
	cout << "Best results: " << setprecision(5) << fixed << best_proportion << ' ' << (best_proportion - 2000000.0) / 2000000.0 * 100.0 << "%\n";
	for (string &obj : best)
		cout << obj << ' ';
}
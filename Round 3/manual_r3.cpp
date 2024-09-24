#include <bits/stdc++.h>
using namespace std;

const double UNIT = 7500;
struct Block
{
	int mult;
	int percent;
	int hunt;
	string pos;

	Block(int m, int h, string p) : mult(m), hunt(h), percent(0), pos(p) {}

	bool operator<(const Block &other) const
	{
		// mult/hunt < other.mult/other.hunt
		return 1ll * mult * other.hunt < 1ll * other.mult * hunt;
	}

	string str() const
	{
		return "(" + to_string(mult) + ", " + to_string(hunt) + ", " + pos + ") ";
	}

	double getCost()
	{
		return double(UNIT * mult) / double(hunt + percent);
	}
};

vector<Block> blocks = {
	Block(24, 2, "G26"),
	Block(70, 4, "G27"),
	Block(41, 3, "G28"),
	Block(21, 2, "G29"),
	Block(60, 4, "G30"),

	Block(47, 3, "H26"),
	Block(82, 5, "H27"),
	Block(87, 5, "H28"),
	Block(80, 5, "H29"),
	Block(35, 3, "H30"),

	Block(73, 4, "I26"),
	Block(89, 5, "I27"),
	Block(100, 8, "I28"),
	Block(90, 7, "I29"),
	Block(17, 2, "I30"),

	Block(77, 5, "J26"),
	Block(83, 5, "J27"),
	Block(85, 5, "J28"),
	Block(79, 5, "J29"),
	Block(55, 4, "J30"),

	Block(12, 2, "K26"),
	Block(27, 3, "K27"),
	Block(52, 4, "K28"),
	Block(15, 2, "K29"),
	Block(30, 3, "K30"),
};

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

	sort(blocks.begin(), blocks.end());
	double sum = 0.0;
	for (int i = 0; i < blocks.size(); ++i)
	{
		cout << blocks[i].str() << ' ' << setprecision(4) << fixed << (blocks[i].mult) / float(blocks[i].hunt) << '\n';
		cout << "Prob: " << setprecision(4) << fixed << getProb(i) << '\n';
		sum += floor(getProb(i));
		blocks[i].percent = floor(getProb(i));
	}
	cout << "Sum prob: " << setprecision(6) << fixed << sum << '\n';

	double best = 0.0;
	string best_sol;
	const double eps = 1e-5;
	for (int i = 0; i < blocks.size(); ++i)
	{
		double cost = blocks[i].getCost();
		if (cost > best + eps)
		{
			best = cost;
			best_sol = blocks[i].str();
		}
		for (int j = i + 1; j < blocks.size(); ++j)
		{
			double cost2 = cost + blocks[j].getCost() - 25'000.0;
			cout << cost2 << ' ' << blocks[i].str() + blocks[j].str() << '\n';
			if (cost2 > best + eps)
			{
				best = cost2;
				best_sol = blocks[i].str() + blocks[j].str();
			}
			for (int k = j + 1; k < blocks.size(); ++k)
			{
				double cost3 = cost2 + blocks[k].getCost() - 75'000.0;
				if (cost3 > best + eps)
				{
					best = cost3;
					best_sol = blocks[i].str() + blocks[j].str() + blocks[k].str();
				}
			}
		}
	}
	cout << "Best: " << setprecision(4) << fixed << best << " Sol: " << best_sol;
	return 0;
}
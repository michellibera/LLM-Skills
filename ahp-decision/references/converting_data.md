# Converting hard data into AHP weights

When a criterion has an objective numeric value (price, weight, time, salary, battery capacity, test score), don't bore the user with 9 pairwise comparisons. Just ask for the values and convert them automatically.

## Two types of criteria

### Benefit (more is better)
Examples: salary, performance, capacity, rating, battery hours, disk space.

Algorithm: normalize proportionally.

```python
weights = [v / sum(values) for v in values]
```

Example: salaries of job offers A=10000, B=12000, C=8000
- A: 10000/30000 = 0.333
- B: 12000/30000 = 0.400
- C: 8000/30000 = 0.267

### Cost (less is better)
Examples: price, weight, commute time, calorie count, wait time.

Algorithm: normalize reciprocals.

```python
inv = [1/v for v in values]
weights = [x / sum(inv) for x in inv]
```

Example: laptop prices A=1000, B=1500, C=2000
- 1/A = 0.001, 1/B = 0.000667, 1/C = 0.0005
- sum = 0.002167
- A: 0.461, B: 0.308, C: 0.231

So laptop A gets a weight of 46% on the price criterion - because it's the cheapest.

## Function in the script

`scripts/ahp_solver.py` has a function `normalize_hard_data(values, benefit=True)`. Use it:

```python
from ahp_solver import normalize_hard_data

# price (cost)
prices = [1000, 1500, 2000]
price_weights = normalize_hard_data(prices, benefit=False)

# battery in hours (benefit)
battery = [8, 12, 6]
battery_weights = normalize_hard_data(battery, benefit=True)
```

## Pitfalls

1. **Nonlinear scale.** Sometimes the user doesn't perceive price linearly - the difference between 1000 and 2000 hurts more than between 9000 and 10000. If you sense this, prefer pairwise comparisons over normalization.

2. **Threshold values.** "Everything under 5000 is equally good to me". In such cases hard values won't work - go back to pairwise comparisons, or apply a threshold function before normalization.

3. **Negative and zero values.** The script guards against division by zero, but if you have negative values (e.g. ROI), shift them by a constant so they become positive.

4. **Different units within a group of criteria.** Not a problem - normalization brings everything to a 0-1 scale.

## When to use pairwise comparisons anyway

- When the user doesn't know exact values ("I don't know exactly how much it costs, but I know X is more expensive").
- When perception is strongly nonlinear (luxury, prestige).
- When "a small price difference is meaningless to me" (threshold effect).
- When the user wants to "feel into" the decision rather than just optimize numbers.

from data import prepare_data
from math_engine import run_calculations

df, err = prepare_data()
results = run_calculations(df, err)

print(results.keys())

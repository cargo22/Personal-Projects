import os
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error

data_path = os.path.join(os.path.dirname(__file__), "training_data.csv")
df = pd.read_csv(data_path)

# 1 if the player also played yesterday (a back-to-back), else 0
df["is_back_to_back"] = (df["days_rest"] == 1).astype(int)


X = df[["rolling_avg", "home_away", "opp_def_rating", "is_back_to_back"]]

y = df["points"]

print(X.head())
print(y.head())

# TEMPORARY: training_data.csv only has 2015-16 to 2021-22,
# so 2021-22 stands in as validation for now.
# REAL PLAN: train 2015-16 to 2021-22, validate on 2022-23,
# test on 2023-24 / 24-25 / 25-26 (rebuild the CSV on the PC first)
is_test = df["season"] == "2021-22"

X_train, y_train = X[~is_test], y[~is_test]
X_test, y_test = X[is_test], y[is_test]

print("train rows:", len(X_train))
print("test rows:", len(X_test))

model = LinearRegression()
model.fit(X_train, y_train)

for feature, weight in zip(X.columns, model.coef_):
    print(f"{feature}: {weight:.3f}")

predictions = model.predict(X_test)

baseline_mae = mean_absolute_error(y_test, X_test["rolling_avg"])
model_mae = mean_absolute_error(y_test, predictions)

print(f"baseline MAE: {baseline_mae:.4f}")
print(f"model MAE:    {model_mae:.4f}")
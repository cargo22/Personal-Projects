import os
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error

data_path = os.path.join(os.path.dirname(__file__), "training_data.csv")
df = pd.read_csv(data_path)

# 1 if the player also played yesterday (a back-to-back), else 0
df["is_back_to_back"] = (df["days_rest"] == 1).astype(int)


X = df[["rolling_avg", "home_away", "opp_def_rating", "is_back_to_back", "rolling_minutes"]]

y = df["points"]

print(X.head())
print(y.head())

# chronological split: train on the past, validate on the next season,
# test on the seasons after that — never let the model see the future
train_seasons = ["2015-16", "2016-17", "2017-18", "2018-19", "2019-20", "2020-21", "2021-22"]
val_seasons = ["2022-23"]
test_seasons = ["2023-24", "2024-25", "2025-26"]

is_train = df["season"].isin(train_seasons)
is_val = df["season"].isin(val_seasons)
is_test = df["season"].isin(test_seasons)

X_train, y_train = X[is_train], y[is_train]
X_val, y_val = X[is_val], y[is_val]
X_test, y_test = X[is_test], y[is_test]

print("train rows:", len(X_train))
print("val rows:  ", len(X_val))
print("test rows: ", len(X_test))

model = RandomForestRegressor(n_estimators=100, random_state=42, max_depth=10, min_samples_leaf=50)
model.fit(X_train, y_train)

for feature, weight in zip(X.columns, model.feature_importances_):
    print(f"{feature}: {weight:.3f}")

val_predictions = model.predict(X_val)
val_baseline_mae = mean_absolute_error(y_val, X_val["rolling_avg"])
val_model_mae = mean_absolute_error(y_val, val_predictions)

print(f"\nvalidation (2022-23):")
print(f"baseline MAE: {val_baseline_mae:.4f}")
print(f"model MAE:    {val_model_mae:.4f}")

test_predictions = model.predict(X_test)
test_baseline_mae = mean_absolute_error(y_test, X_test["rolling_avg"])
test_model_mae = mean_absolute_error(y_test, test_predictions)

print(f"\ntest (2023-24 / 24-25 / 25-26):")
print(f"baseline MAE: {test_baseline_mae:.4f}")
print(f"model MAE:    {test_model_mae:.4f}")
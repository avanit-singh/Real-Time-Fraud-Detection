import pandas as pd
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix, precision_score
from sqlalchemy import create_engine

print("1. Loading processed data...")
df = pd.read_parquet("data/processed/model_ready_data.parquet")
df.fillna(0, inplace=True)

print("2. Simulating Rule-Based Engine...")
# Rule: If txn count > 3 in an hour AND amount > 50,000 INR -> Flag as Fraud 
df['rule_pred'] = ((df['txn_count_1hr'] > 3) & (df['amount_inr'] > 50000)).astype(int)

print("3. Training Machine Learning Model (XGBoost)...")
features = ['amount_inr', 'txn_count_1hr', 'amt_spent_1hr', 'amount_z_score', 'account_age_days']
X = df[features]
y = df['is_fraud']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

# Calculate ratio of negative to positive classes for scale_pos_weight
ratio = float(y_train.value_counts()[0]) / y_train.value_counts()[1]

# Initialize XGBoost
clf = xgb.XGBClassifier(
    n_estimators=150, 
    max_depth=5, 
    learning_rate=0.1, 
    scale_pos_weight=ratio, # Handles the 2% fraud imbalance natively
    random_state=42, 
    n_jobs=-1
)
clf.fit(X_train, y_train)

print("4. Generating predictions...")
df['ml_pred'] = clf.predict(X)

def calculate_metrics(y_true, y_pred, name):
    tn, fp, fn, tp = confusion_matrix(y_true, y_pred).ravel()
    fpr = fp / (fp + tn)
    detection_rate = tp / (tp + fn)
    print(f"\n--- {name} Metrics ---")
    print(f"Detection Rate (Recall): {detection_rate:.2%}")
    print(f"False Positive Rate (FPR): {fpr:.2%}")
    print(f"Precision: {precision_score(y_true, y_pred, zero_division=0):.2%}")

calculate_metrics(df['is_fraud'], df['rule_pred'], "Rule-Based Engine")
calculate_metrics(df['is_fraud'], df['ml_pred'], "XGBoost ML")

print("\n5. Pushing XGBoost predictions to SQL Server...")
df_predictions = df[['txn_id', 'rule_pred', 'ml_pred']]
server = r'HARIOM\SQLEXPRESS'
database = 'master'
driver = 'ODBC Driver 17 for SQL Server' 
connection_string = f"mssql+pyodbc://@{server}/{database}?driver={driver}&trusted_connection=yes"
engine = create_engine(connection_string)

df_predictions.to_sql('fact_ml_predictions', con=engine, if_exists='replace', index=False)
print("Success! ML Predictions saved.")
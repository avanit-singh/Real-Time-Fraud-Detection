import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import confusion_matrix, precision_score, recall_score, classification_report

df = pd.read_parquet("data/processed/model_ready_data.parquet")
df.fillna(0, inplace=True)

# 1. Rule-Based Engine Simulation
# Rule: If txn count > 3 in an hour AND amount > 50,000 INR -> Flag as Fraud
df['rule_pred'] = ((df['txn_count_1hr'] > 3) & (df['amount_inr'] > 50000)).astype(int)

# 2. Machine Learning Approach
features = ['amount_inr', 'txn_count_1hr', 'amt_spent_1hr', 'amount_z_score', 'account_age_days']
X = df[features]
y = df['is_fraud']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

clf = RandomForestClassifier(n_estimators=100, class_weight='balanced', random_state=42)
clf.fit(X_train, y_train)

y_pred_ml = clf.predict(X_test)

def calculate_metrics(y_true, y_pred, name):
    tn, fp, fn, tp = confusion_matrix(y_true, y_pred).ravel()
    fpr = fp / (fp + tn)
    detection_rate = tp / (tp + fn) # Recall
    print(f"--- {name} Metrics ---")
    print(f"Detection Rate (Recall): {detection_rate:.2%}")
    print(f"False Positive Rate (FPR): {fpr:.2%}")
    print(f"Precision: {precision_score(y_true, y_pred):.2%}\n")

calculate_metrics(df['is_fraud'], df['rule_pred'], "Rule-Based Engine")
calculate_metrics(y_test, y_pred_ml, "Random Forest ML")
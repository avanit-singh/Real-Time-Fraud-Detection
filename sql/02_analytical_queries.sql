-- Calculate Overall Fraud Metrics by Payment Method
SELECT 
    payment_method,
    COUNT(*) as total_txns,
    SUM(is_fraud) as total_fraud_txns,
    SUM(CASE WHEN is_fraud = 1 THEN amount_inr ELSE 0 END) as fraud_loss_inr,
    ROUND((SUM(is_fraud) * 100.0) / COUNT(*), 2) as fraud_rate_pct
FROM fact_transaction
GROUP BY payment_method
ORDER BY fraud_loss_inr DESC;
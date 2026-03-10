import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score, classification_report, roc_auc_score
from imblearn.over_sampling import SMOTE
import joblib
import xgboost as xgb
import lightgbm as lgb
from sklearn.preprocessing import StandardScaler

def load_and_prepare_data():
    """Load and prepare the dataset"""
    # Load the dataset
    data = pd.read_csv("transfusion.csv")
    
    # Rename columns for clarity
    data.columns = ['Recency', 'Frequency', 'Monetary', 'Time', 'Donated']
    
    # Split into features (X) and target (y)
    X = data.drop('Donated', axis=1)
    y = data['Donated']
    
    # Handle class imbalance using SMOTE
    smote = SMOTE(random_state=42)
    X_resampled, y_resampled = smote.fit_resample(X, y)
    
    # Split into training and testing sets
    X_train, X_test, y_train, y_test = train_test_split(X_resampled, y_resampled, test_size=0.2, random_state=42)
    
    return X_train, X_test, y_train, y_test

def train_random_forest(X_train, y_train):
    """Train Random Forest model"""
    model = RandomForestClassifier(random_state=42, class_weight={0: 1, 1: 3})
    model.fit(X_train, y_train)
    return model

def train_xgboost(X_train, y_train):
    """Train XGBoost model"""
    model = xgb.XGBClassifier(random_state=42, scale_pos_weight=3)
    model.fit(X_train, y_train)
    return model

def train_lightgbm(X_train, y_train):
    """Train LightGBM model"""
    model = lgb.LGBMClassifier(random_state=42, class_weight={0: 1, 1: 3})
    model.fit(X_train, y_train)
    return model

def train_svm(X_train, y_train):
    """Train SVM model"""
    # Scale the features for SVM
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    
    model = SVC(kernel='rbf', probability=True, class_weight={0: 1, 1: 3})
    model.fit(X_train_scaled, y_train)
    return model, scaler

def evaluate_model(model, X_test, y_test, model_name, scaler=None):
    """Evaluate model performance"""
    if scaler is not None:
        X_test_scaled = scaler.transform(X_test)
        y_pred = model.predict(X_test_scaled)
        y_pred_proba = model.predict_proba(X_test_scaled)[:, 1]
    else:
        y_pred = model.predict(X_test)
        y_pred_proba = model.predict_proba(X_test)[:, 1]
    
    accuracy = accuracy_score(y_test, y_pred)
    roc_auc = roc_auc_score(y_test, y_pred_proba)
    
    print(f"\n{model_name} Results:")
    print("-" * 20)
    print(f"Accuracy: {accuracy:.4f}")
    print(f"ROC-AUC Score: {roc_auc:.4f}")
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred))
    
    return accuracy, roc_auc

def main():
    print("Training Multiple ML Models")
    print("=" * 30)
    
    # Load and prepare data
    X_train, X_test, y_train, y_test = load_and_prepare_data()
    
    # Dictionary to store model results
    results = {}
    
    # Train and evaluate Random Forest
    print("\nTraining Random Forest...")
    rf_model = train_random_forest(X_train, y_train)
    rf_acc, rf_auc = evaluate_model(rf_model, X_test, y_test, "Random Forest")
    results['Random Forest'] = {'accuracy': rf_acc, 'roc_auc': rf_auc}
    joblib.dump(rf_model, 'models/random_forest_model.pkl')
    
    # Train and evaluate XGBoost
    print("\nTraining XGBoost...")
    xgb_model = train_xgboost(X_train, y_train)
    xgb_acc, xgb_auc = evaluate_model(xgb_model, X_test, y_test, "XGBoost")
    results['XGBoost'] = {'accuracy': xgb_acc, 'roc_auc': xgb_auc}
    joblib.dump(xgb_model, 'models/xgboost_model.pkl')
    
    # Train and evaluate LightGBM
    print("\nTraining LightGBM...")
    lgb_model = train_lightgbm(X_train, y_train)
    lgb_acc, lgb_auc = evaluate_model(lgb_model, X_test, y_test, "LightGBM")
    results['LightGBM'] = {'accuracy': lgb_acc, 'roc_auc': lgb_auc}
    joblib.dump(lgb_model, 'models/lightgbm_model.pkl')
    
    # Train and evaluate SVM
    print("\nTraining SVM...")
    svm_model, scaler = train_svm(X_train, y_train)
    svm_acc, svm_auc = evaluate_model(svm_model, X_test, y_test, "SVM", scaler)
    results['SVM'] = {'accuracy': svm_acc, 'roc_auc': svm_auc}
    joblib.dump((svm_model, scaler), 'models/svm_model.pkl')
    
    # Print comparison of all models
    print("\nModel Comparison:")
    print("=" * 30)
    print(f"{'Model':<15} {'Accuracy':<10} {'ROC-AUC':<10}")
    print("-" * 30)
    for model_name, metrics in results.items():
        print(f"{model_name:<15} {metrics['accuracy']:<10.4f} {metrics['roc_auc']:<10.4f}")

if __name__ == "__main__":
    # Create models directory if it doesn't exist
    import os
    os.makedirs('models', exist_ok=True)
    
    main() 
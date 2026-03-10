import joblib
import pandas as pd
import numpy as np

def load_model_by_name(model_name):
    """Load the specified model"""
    try:
        model_data = joblib.load(f'models/{model_name.lower().replace(" ", "_")}_model.pkl')
        if isinstance(model_data, tuple):
            model, scaler = model_data
        else:
            model, scaler = model_data, None
        return model, scaler
    except Exception as e:
        print(f"Error loading {model_name} model: {str(e)}")
        return None, None

def predict_blood_donation(model, recency, frequency, monetary, time, model_name, scaler=None):
    """
    Predict if a person will donate blood based on their donation history.
    
    Parameters:
    - model: The trained model
    - recency: Months since last donation
    - frequency: Total number of donations
    - monetary: Total blood donated in c.c.
    - time: Months since first donation
    - model_name: Name of the model being used
    - scaler: Optional scaler for feature scaling
    
    Returns:
    - prediction: 1 if likely to donate, 0 if not
    - probability: Probability of donation (0-1)
    """
    try:
        # Create a DataFrame with the input features
        features = pd.DataFrame({
            'Recency': [recency],
            'Frequency': [frequency],
            'Monetary': [monetary],
            'Time': [time]
        })
        
        # Scale features if needed
        if scaler is not None:
            features_scaled = scaler.transform(features)
        else:
            features_scaled = features
        
        # Make prediction
        prediction = model.predict(features_scaled)[0]
        probability = model.predict_proba(features_scaled)[0][1]
        
        return prediction, probability
        
    except Exception as e:
        print(f"Error making prediction: {str(e)}")
        return None, None

def get_user_input():
    """Get donation history from user input"""
    print("\nPlease enter the donor's information:")
    print("-" * 40)
    
    while True:
        try:
            recency = float(input("How many months since last donation? "))
            frequency = int(input("How many times have they donated in total? "))
            monetary = float(input("How much blood have they donated in total (in c.c.)? "))
            time = float(input("How many months since their first donation? "))
            
            # Validate inputs
            if recency < 0 or frequency < 0 or monetary < 0 or time < 0:
                print("Please enter non-negative values.")
                continue
                
            if recency > time:
                print("Months since last donation cannot be greater than months since first donation.")
                continue
                
            if monetary < frequency * 250:  # Assuming minimum 250cc per donation
                print("Total blood donated seems too low for the number of donations.")
                continue
                
            return recency, frequency, monetary, time
            
        except ValueError:
            print("Please enter valid numbers.")
            continue

def main():
    print("Blood Donation Prediction System")
    print("=" * 30)
    
    # Available models
    models = ["Random Forest", "XGBoost", "LightGBM", "SVM"]
    
    while True:
        # Get user input
        recency, frequency, monetary, time = get_user_input()
        
        # Get predictions from all models
        print("\nPredictions from all models:")
        print("=" * 50)
        print(f"{'Model':<15} {'Prediction':<10} {'Probability':<10}")
        print("-" * 50)
        
        for model_name in models:
            model, scaler = load_model_by_name(model_name)
            if model is not None:
                prediction, probability = predict_blood_donation(
                    model, recency, frequency, monetary, time, model_name, scaler
                )
                if prediction is not None:
                    print(f"{model_name:<15} {'Yes' if prediction == 1 else 'No':<10} {probability:.2%}")
        
        # Ask if user wants to make another prediction
        while True:
            try:
                again = input("\nWould you like to make another prediction? (yes/no): ").lower()
                if again in ['yes', 'no']:
                    break
                print("Please enter 'yes' or 'no'")
            except:
                print("Please enter 'yes' or 'no'")
        
        if again == 'no':
            break
    
    print("\nThank you for using the Blood Donation Prediction System!")

if __name__ == "__main__":
    main() 
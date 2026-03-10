import joblib
import pandas as pd
import numpy as np

def predict_blood_donation(recency, frequency, monetary, time):
    """
    Predict if a person will donate blood based on their donation history.
    
    Parameters:
    - recency: Months since last donation
    - frequency: Total number of donations
    - monetary: Total blood donated in c.c.
    - time: Months since first donation
    
    Returns:
    - prediction: 1 if likely to donate, 0 if not
    - probability: Probability of donation (0-1)
    """
    try:
        # Load the trained model
        model = joblib.load('transfusion_model.pkl')
        
        # Create a DataFrame with the input features
        features = pd.DataFrame({
            'Recency': [recency],
            'Frequency': [frequency],
            'Monetary': [monetary],
            'Time': [time]
        })
        
        # Make prediction
        prediction = model.predict(features)[0]
        probability = model.predict_proba(features)[0][1]
        
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

if __name__ == "__main__":
    print("Blood Donation Prediction System")
    print("=" * 30)
    
    while True:
        # Get user input
        recency, frequency, monetary, time = get_user_input()
        
        # Make prediction
        prediction, probability = predict_blood_donation(recency, frequency, monetary, time)
        
        if prediction is not None:
            print("\nPrediction Results:")
            print("-" * 20)
            print(f"Will donate: {'Yes' if prediction == 1 else 'No'}")
            print(f"Probability of donation: {probability:.2%}")
            print("\nInput Features:")
            print("-" * 20)
            print(f"Months since last donation: {recency}")
            print(f"Total number of donations: {frequency}")
            print(f"Total blood donated (c.c.): {monetary}")
            print(f"Months since first donation: {time}")
        
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
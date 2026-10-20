import streamlit as st
from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import pickle


# Add cache resources for pickled aspects of the model
@st.cache_resource
def pull_model():
    with open('models/dt_model.pkl', 'rb') as f:
        model = pickle.load(f)
    return model


@st.cache_resource
def pull_features():
    with open('models/features.pkl', 'rb') as f:
        features = pickle.load(f)
    return features


@st.cache_resource
def pull_scaler():
    with open('models/scaler.pkl', 'rb') as f:
        scaler = pickle.load(f)
    return scaler


model = pull_model()
features = pull_features()
scaler = pull_scaler()

st.title("F1 Podium Predictor 🏎️")
st.write("Model: Decision Tree (AUC: 0.946)")


def populate_streamlit(df):
    # Extract the 11 features the model needs
    X = df[features]
    # Predict probabilities
    probabilities = model.predict_proba(X)[:, 1]
    # Predict class (0 or 1)
    predictions = model.predict(X)
    # Add to dataframe
    df['Predicted_Podium'] = predictions
    df['Podium_Probability'] = probabilities

    # Confusion Matrix
    st.subheader("Model Performance")
    cm = confusion_matrix(df['is_podium'], df['Predicted_Podium'])
    fig, ax = plt.subplots()
    cm_normalized = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]  # Row percentages
    disp = ConfusionMatrixDisplay(confusion_matrix=cm_normalized, display_labels=['No Podium', 'Podium'])
    disp.plot(ax=ax, cmap='Blues', values_format='.2%')
    st.pyplot(fig)

    # Display results
    st.subheader("Predicted Top 3 Finishers by Race")

    def colour_coding(row):
        if row["Predicted_Podium"] == row["is_podium"]:
            return ['background-color: lightgreen'] * len(row)  # Correct prediction
        else:
            return ['background-color: lightcoral'] * len(row)  # Wrong prediction

    # Group by race
    for race_name in df['name'].unique():
        race_df = df[df['name'] == race_name].copy()

        # Sort by probability (highest first)
        race_df = race_df.sort_values('Podium_Probability', ascending=False)

        # Top 3
        top3 = race_df.head(3)

        st.write(f"**{race_name}**")
        result_cols = ['driver_name', 'Podium_Probability', 'Predicted_Podium', 'is_podium']
        top3_results = top3[result_cols]
        top3_styled = top3_results.style.apply(colour_coding, axis=1)
        st.dataframe(top3_styled, hide_index=True)
        st.write("")  # Spacing


use_default = st.checkbox("Use data provided: ", value=True)

if use_default:
    df = pd.read_csv('data/processed/race_driver_records_test_fe.csv')
    st.success(f"✓ Loaded 2023 test data: {len(df)} records")
    populate_streamlit(df)
else:
    uploaded_file = st.file_uploader("Upload CSV", type=['csv'])
    if uploaded_file:
        df = pd.read_csv(uploaded_file)
        populate_streamlit(df)

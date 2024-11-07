#!/usr/bin/env python
# coding: utf-8

# In[3]:


import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# Load the expanded dataset from Excel
try:
    df = pd.read_excel("Expanded_AM_DSS_Dataset.xlsx")
except FileNotFoundError:
    st.write("Error: Dataset file 'Expanded_AM_DSS_Dataset.xlsx' not found. Please ensure it is in the same directory as this script.")
    st.stop()

# Title and Introduction
st.title("Decision Support System for Additive Manufacturing in Supply Chain")
st.write("This DSS guides you through selecting objectives, decisions, KPIs, and integration levels for optimized supply chain management.")

# Step 1: Select Industry Sector and Objectives
st.header("Step 1: Select Your Industry Sector and Objectives")
sector = st.selectbox("Select your industry sector:", ["Food", "Military", "Retail", "Automotive"])

objectives = []
if sector == "Food":
    objectives = ["Freshness", "Traceability", "Cost Efficiency", "Waste Reduction"]
elif sector == "Military":
    objectives = ["Resilience", "Durability", "Logistics Optimization", "Security"]
elif sector == "Retail":
    objectives = ["Agility", "Customer Satisfaction", "Cost Reduction", "Inventory Management"]
elif sector == "Automotive":
    objectives = ["Customization", "Sustainability", "Cost Efficiency", "Production Flexibility"]

chosen_objectives = st.multiselect("Select objectives for your sector:", objectives)

# Step 2: Select Decisions by Levels
st.header("Step 2: Select Decisions by Level")

# Strategic Decisions
st.subheader("Strategic Decisions")
strategic_decisions = st.multiselect("Select strategic decisions:", 
                                     ["AM Technology Selection", "AM Integration Strategy",
                                      "Inventory Policy Selection", "AM Business Case", 
                                      "Make-or-Buy", "Centralised vs. Decentralised SC Configuration",
                                      "AM Facility Location"])

# Tactical Decisions
st.subheader("Tactical Decisions")
tactical_decisions = st.multiselect("Select tactical decisions:", 
                                    ["Production Method Allocation", "AM Equipment Allocation", 
                                     "Inventory Control", "Transportation Routes Strategy",
                                     "AM Materials Selection", "Supplier Selection for AM Raw Materials"])

# Operational Decisions
st.subheader("Operational Decisions")
operational_decisions = st.multiselect("Select operational decisions:", 
                                       ["Part-to-Printer Assignment", "AM Production Scheduling", 
                                        "Post-Processing Requirements", "AM Process Parameter Adjustment"])

# Step 3: Select KPIs Based on Objectives
st.header("Step 3: Select KPIs")
kpi_categories = {
    "Reliability": ["Quality_Consistency", "Customer_Satisfaction", "Demand_Fulfillment_Rate"],
    "Responsiveness": ["Cycle_Time", "Lead_Time", "On_Time_Delivery"],
    "Sustainability": ["Carbon_Emission_Cost", "Waste_Reduction", "Energy_Consumption"],
    "Agility": ["Manufacturing_Flexibility", "Demand_Volatility_Management", "Resource_Allocation_Flexibility"],
    "Cost": ["Production_Cost", "Transportation_Cost", "Inventory_Holding_Cost"],
    "Asset Management Efficiency": ["Capacity_Utilisation", "Inventory_Levels", "Facility_Utilisation"]
}

selected_kpis = {}
for category, kpis in kpi_categories.items():
    st.subheader(f"{category} KPIs")
    selected_kpis[category] = st.multiselect(f"Select KPIs under {category}:", kpis)

# Flatten selected KPIs for easy access
chosen_kpis = [kpi for kpis in selected_kpis.values() for kpi in kpis]

# Step 4: Select Level of Integration
st.header("Step 4: Select Level of Integration")
integration_level = st.radio("Choose your integration level:", ["Fully AM", "Hybrid AM and TM", "Fully TM"])

# Debugging: Display selected KPIs and integration level
st.write("### Debugging Information")
st.write("Selected KPIs:", chosen_kpis)
st.write("Integration Level:", integration_level)

# Step 5: Displaying Outcomes Based on Selections with Simulation and Visualization
st.header("Step 5: Outcomes and Results")

try:
    # Filter dataset based on selected integration level
    filtered_data = df[df["Integration_Level"] == integration_level]

    # Debugging: Display a sample of filtered data
    st.write("Filtered Data Sample:", filtered_data.head())

    # Validate if selected KPIs are in the dataset columns
    missing_kpis = [kpi for kpi in chosen_kpis if kpi not in filtered_data.columns]
    if missing_kpis:
        st.write(f"**Error**: The following KPIs are not available in the dataset: {', '.join(missing_kpis)}")
    else:
        # Run Monte Carlo simulation for selected KPIs if available
        if chosen_kpis:
            num_simulations = 1000
            simulated_results = []

            for _ in range(num_simulations):
                sample = filtered_data.sample(1)
                noise = np.random.normal(0, 0.05, len(chosen_kpis))  # Introduce variability
                result = sample[chosen_kpis].values[0] + noise
                simulated_results.append(result)

            simulated_df = pd.DataFrame(simulated_results, columns=chosen_kpis)

            # Calculate main KPI categories by averaging sub-KPIs
            main_kpi_results = {}
            for category, sub_kpis in selected_kpis.items():
                if sub_kpis:
                    main_kpi_results[category] = simulated_df[sub_kpis].mean().mean()

            # Display simulated KPI results
            st.write("### Simulated KPI Results for Selected Integration Level")
            st.write(pd.Series(main_kpi_results))

            # Visualize with Plotly
            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=list(main_kpi_results.keys()),
                y=list(main_kpi_results.values()),
                marker=dict(color="royalblue"),
                name="Main KPI Values"
            ))
            fig.update_layout(
                title=f"KPI Performance for Integration Level: {integration_level}",
                xaxis_title="Main KPI",
                yaxis_title="Value",
                showlegend=False
            )
            st.plotly_chart(fig, use_container_width=True)

            # Interactive Dashboard - Correlation Matrix for Sub-KPIs
            correlation_matrix = simulated_df.corr()
            st.write("### KPI Correlation Matrix")
            fig_corr = px.imshow(correlation_matrix, text_auto=True, title="Correlation Matrix of Selected Sub-KPIs")
            st.plotly_chart(fig_corr)

            # Additional insights
            st.write("### Scenario Insights")
            st.write(f"At the {integration_level} integration level, the DSS suggests optimized KPI performance based on selected decisions and objectives with variability considered.")
        else:
            st.write("Please select at least one KPI to display simulation results.")

except Exception as e:
    st.write("An error occurred:", str(e))


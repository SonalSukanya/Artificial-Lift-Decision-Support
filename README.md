# Artificial Lift Decision Support System

An engineering-based decision-support dashboard for screening and comparing artificial lift methods for oil wells using well, reservoir, and production data.

The system evaluates four commonly used artificial lift methods:

- Electric Submersible Pump (ESP)
- Gas Lift
- Progressive Cavity Pump (PCP)
- Sucker Rod Pump (SRP)

The dashboard combines petroleum engineering principles with data analysis to provide a transparent preliminary screening of artificial lift suitability.

---

## Project Objective

Artificial lift selection depends on multiple well and reservoir characteristics such as production rate, fluid viscosity, GOR, water cut, reservoir pressure, temperature, and well geometry.

The objective of this project is to develop an interactive tool that:

- Accepts a well-level dataset as input
- Allows users to select a basin, field, and individual well
- Analyzes available well, reservoir, and production parameters
- Identifies missing engineering inputs
- Allows users to enter additional information when required
- Compares ESP, Gas Lift, PCP, and SRP
- Provides transparent screening scores
- Explains the engineering factors influencing each method
- Displays the calculations used in the analysis
- Clearly communicates data limitations and uncertainty

The system is intended as a **preliminary engineering screening tool**, rather than a final artificial lift design system.

---

## Dashboard Workflow

```text
Upload Well Dataset
        ↓
Select Basin
        ↓
Select Field
        ↓
Select Well
        ↓
Analyze Available Data
        ↓
Identify Missing Inputs
        ↓
Enter Additional Engineering Data
        ↓
Compare ESP / Gas Lift / PCP / SRP
        ↓
View Engineering Mechanism
        ↓
View Factors & Calculations
        ↓
Review Data Quality & Limitations

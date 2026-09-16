import streamlit as st
import pandas as pd
import numpy as np
import os


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Artificial Lift Decision Support",
    page_icon="🛢️",
    layout="wide"
)

st.title("Artificial Lift Decision Support System")
st.caption(
    "Engineering-based screening of ESP, Gas Lift, PCP and SRP "
    "using well, reservoir and production data."
)


# ============================================================
# 1. DATA UPLOAD
# ============================================================

st.sidebar.header("1. Dataset")

uploaded_file = st.sidebar.file_uploader(
    "Upload well dataset (CSV)",
    type=["csv"]
)

default_paths = [
    r"C:\Users\Sonal Sukanya\Documents\AL PROJECT\artificial_lift_decision_data_v2.csv",
    r"C:\Users\Sonal Sukanya\Documents\AL PROJECT\artificial_lift_decision_data.csv"
]

df = None

if uploaded_file is not None:

    df = pd.read_csv(uploaded_file)

    st.sidebar.success("Dataset uploaded successfully.")

else:

    for path in default_paths:
        if os.path.exists(path):
            df = pd.read_csv(path)
            st.sidebar.info(
                f"Using local dataset: {os.path.basename(path)}"
            )
            break


if df is None:

    st.warning(
        "Please upload your well dataset using the sidebar."
    )

    st.stop()


# ============================================================
# 2. REQUIRED COLUMNS
# ============================================================

required_columns = [
    "well_id",
    "field_id",
    "basin",
    "fluid_type",
    "completion_type",
    "lateral_length_ft",
    "n_perforation_stages",
    "workover_count",
    "initial_reservoir_pressure_psia",
    "reservoir_temperature_degF",
    "permeability_md",
    "porosity_pct",
    "net_pay_ft",
    "api_gravity",
    "bubble_point_pressure_psia",
    "oil_viscosity_cp",
    "formation_volume_factor_bo",
    "reservoir_drive_type",
    "aquifer_strength_index",
    "avg_oil_rate_bopd",
    "avg_gas_rate_mcfd",
    "avg_water_rate_bwpd",
    "avg_gor_scf_bbl",
    "avg_water_cut_pct",
    "production_days"
]

missing_columns = [
    col for col in required_columns
    if col not in df.columns
]

if missing_columns:

    st.error("The uploaded dataset is missing required columns:")

    for col in missing_columns:
        st.write(f"- `{col}`")

    st.stop()


# ============================================================
# 3. DERIVED VARIABLES
# ============================================================

# Production availability

df["production_data_available"] = (
    df["avg_oil_rate_bopd"].notna()
)


# Liquid rate

df["avg_liquid_rate_blpd"] = (
    df["avg_oil_rate_bopd"] +
    df["avg_water_rate_bwpd"]
)


# Pressure / bubble-point ratio

df["pressure_to_bubble_point_ratio"] = (
    df["initial_reservoir_pressure_psia"] /
    df["bubble_point_pressure_psia"]
)


# Production status

df["production_data_status"] = np.where(
    df["production_data_available"],
    "Production Data Available",
    "Insufficient Production Data"
)


# ============================================================
# 4. SIDEBAR WELL SELECTION
# ============================================================

st.sidebar.header("2. Select Well")

basin_options = sorted(
    df["basin"].dropna().unique().tolist()
)

selected_basin = st.sidebar.selectbox(
    "Basin",
    basin_options
)

basin_df = df[
    df["basin"] == selected_basin
]


field_options = sorted(
    basin_df["field_id"].dropna().unique().tolist()
)

selected_field = st.sidebar.selectbox(
    "Field",
    field_options
)

field_df = basin_df[
    basin_df["field_id"] == selected_field
]


# Formation is optional because your current CSV
# does not contain formation_name.

if "formation_name" in field_df.columns:

    formation_options = sorted(
        field_df["formation_name"]
        .dropna()
        .unique()
        .tolist()
    )

    selected_formation = st.sidebar.selectbox(
        "Formation",
        ["All"] + formation_options
    )

    if selected_formation != "All":

        field_df = field_df[
            field_df["formation_name"] ==
            selected_formation
        ]


well_options = sorted(
    field_df["well_id"].dropna().unique().tolist()
)

selected_well = st.sidebar.selectbox(
    "Well",
    well_options
)


well = df[
    df["well_id"] == selected_well
].iloc[0]


# ============================================================
# 5. WELL OVERVIEW
# ============================================================

st.header("Selected Well")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Well",
        str(well["well_id"])
    )

with col2:
    st.metric(
        "Field",
        str(well["field_id"])
    )

with col3:
    st.metric(
        "Basin",
        str(well["basin"])
    )

with col4:

    if "formation_name" in df.columns:
        st.metric(
            "Formation",
            str(well["formation_name"])
        )
    else:
        st.metric(
            "Formation",
            "Not available"
        )


# ============================================================
# 6. BASIC WELL INFORMATION
# ============================================================

st.subheader("Well & Reservoir Information")

info_col1, info_col2, info_col3 = st.columns(3)

with info_col1:

    st.write("**Fluid type:**", well["fluid_type"])
    st.write("**Completion:**", well["completion_type"])
    st.write(
        "**Lateral length:**",
        f"{well['lateral_length_ft']:,.0f} ft"
    )
    st.write(
        "**Perforation stages:**",
        int(well["n_perforation_stages"])
    )
    st.write(
        "**Workovers:**",
        int(well["workover_count"])
    )

with info_col2:

    st.write(
        "**Reservoir pressure:**",
        f"{well['initial_reservoir_pressure_psia']:,.0f} psi"
    )

    st.write(
        "**Bubble point:**",
        f"{well['bubble_point_pressure_psia']:,.0f} psi"
    )

    st.write(
        "**Pᵢ / Pᵦ:**",
        f"{well['pressure_to_bubble_point_ratio']:.2f}"
    )

    st.write(
        "**Temperature:**",
        f"{well['reservoir_temperature_degF']:.1f} °F"
    )

    st.write(
        "**Viscosity:**",
        f"{well['oil_viscosity_cp']:.2f} cP"
    )

with info_col3:

    st.write(
        "**API gravity:**",
        f"{well['api_gravity']:.1f}"
    )

    st.write(
        "**Permeability:**",
        f"{well['permeability_md']:.4g} md"
    )

    st.write(
        "**Porosity:**",
        f"{well['porosity_pct']:.2f}%"
    )

    st.write(
        "**Net pay:**",
        f"{well['net_pay_ft']:.1f} ft"
    )

    st.write(
        "**Reservoir drive:**",
        well["reservoir_drive_type"]
    )


# ============================================================
# 7. PRODUCTION DATA
# ============================================================

st.subheader("Production Information")

p1, p2, p3, p4, p5 = st.columns(5)

with p1:
    value = well["avg_oil_rate_bopd"]

    st.metric(
        "Oil Rate",
        "N/A" if pd.isna(value)
        else f"{value:,.0f} BOPD"
    )

with p2:
    value = well["avg_water_rate_bwpd"]

    st.metric(
        "Water Rate",
        "N/A" if pd.isna(value)
        else f"{value:,.0f} BWPD"
    )

with p3:
    value = well["avg_liquid_rate_blpd"]

    st.metric(
        "Liquid Rate",
        "N/A" if pd.isna(value)
        else f"{value:,.0f} BLPD"
    )

with p4:
    value = well["avg_gor_scf_bbl"]

    st.metric(
        "GOR",
        "N/A" if pd.isna(value)
        else f"{value:,.0f} scf/bbl"
    )

with p5:
    value = well["avg_water_cut_pct"]

    st.metric(
        "Water Cut",
        "N/A" if pd.isna(value)
        else f"{value:.1f}%"
    )


# ============================================================
# 8. MISSING DATA / USER INPUT
# ============================================================

st.header("Complete Missing Engineering Inputs")

st.info(
    "Only parameters that are not available in the dataset need to be "
    "entered. User-entered values are used only for the current analysis "
    "and are not added to the original dataset."
)


# ------------------------------------------------------------
# Inputs
# ------------------------------------------------------------

input_col1, input_col2, input_col3 = st.columns(3)

with input_col1:

    well_depth = st.number_input(
        "Well depth (ft)",
        min_value=0.0,
        value=None,
        placeholder="Enter if available"
    )

    pump_setting_depth = st.number_input(
        "Pump setting depth (ft)",
        min_value=0.0,
        value=None,
        placeholder="Enter if available"
    )

with input_col2:

    gas_availability = st.selectbox(
        "Gas available for Gas Lift?",
        ["Unknown", "Yes", "No"]
    )

    electrical_power = st.selectbox(
        "Electrical power available?",
        ["Unknown", "Yes", "No"]
    )

with input_col3:

    sand_production = st.selectbox(
        "Significant sand production?",
        ["Unknown", "Yes", "No"]
    )

    surface_pressure = st.number_input(
        "Surface pressure (psi)",
        min_value=0.0,
        value=None,
        placeholder="Enter if available"
    )


# ============================================================
# 9. DATA COMPLETENESS
# ============================================================

st.header("Data Quality")

critical_parameters = {
    "Well depth": well_depth,
    "Pump setting depth": pump_setting_depth,
    "Production rate": well["avg_oil_rate_bopd"],
    "Reservoir pressure": well["initial_reservoir_pressure_psia"],
    "Oil viscosity": well["oil_viscosity_cp"],
    "GOR": well["avg_gor_scf_bbl"],
    "Water cut": well["avg_water_cut_pct"],
    "Reservoir temperature": well["reservoir_temperature_degF"]
}

quality_rows = []

for parameter, value in critical_parameters.items():

    available = not pd.isna(value)

    quality_rows.append({
        "Parameter": parameter,
        "Value": value if available else "Unavailable",
        "Source": "Dataset" if available and parameter != "Well depth"
        and parameter != "Pump setting depth"
        else (
            "User entered"
            if available
            else "Unavailable"
        ),
        "Status": "Available" if available else "Missing"
    })

quality_df = pd.DataFrame(quality_rows)

st.dataframe(
    quality_df,
    use_container_width=True,
    hide_index=True
)


# ============================================================
# 10. ENGINEERING SCREENING FUNCTIONS
# ============================================================

def score_liquid_rate(rate):

    if pd.isna(rate):
        return None

    if rate < 300:
        return 2

    elif rate < 1000:
        return 3

    elif rate < 3000:
        return 4

    else:
        return 5


def score_viscosity_for_pcp(viscosity):

    if pd.isna(viscosity):
        return None

    if viscosity < 2:
        return 2

    elif viscosity < 5:
        return 3

    elif viscosity < 10:
        return 4

    else:
        return 5


def score_viscosity_for_esp(viscosity):

    if pd.isna(viscosity):
        return None

    if viscosity < 2:
        return 5

    elif viscosity < 5:
        return 4

    elif viscosity < 10:
        return 3

    else:
        return 2


def score_gor_for_gaslift(gor):

    if pd.isna(gor):
        return None

    if gor < 500:
        return 2

    elif gor < 1000:
        return 3

    elif gor < 2000:
        return 4

    else:
        return 5


def score_gor_for_esp(gor):

    if pd.isna(gor):
        return None

    if gor < 500:
        return 5

    elif gor < 1000:
        return 4

    elif gor < 2000:
        return 3

    else:
        return 2


def score_api_for_pcp(api):

    if pd.isna(api):
        return None

    if api < 30:
        return 5

    elif api < 35:
        return 4

    elif api < 40:
        return 3

    else:
        return 2


def score_pressure_ratio(ratio):

    if pd.isna(ratio):
        return None

    if ratio < 0.8:
        return 2

    elif ratio < 1.0:
        return 3

    elif ratio < 1.5:
        return 4

    else:
        return 5


def score_water_cut(wc):

    if pd.isna(wc):
        return None

    if wc < 20:
        return 4

    elif wc < 50:
        return 4

    elif wc < 70:
        return 3

    else:
        return 2


def score_temperature(temp):

    if pd.isna(temp):
        return None

    if temp < 150:
        return 5

    elif temp < 200:
        return 4

    elif temp < 250:
        return 3

    else:
        return 2


# ============================================================
# 11. CALCULATE METHOD SCORES
# ============================================================

liquid = well["avg_liquid_rate_blpd"]
viscosity = well["oil_viscosity_cp"]
gor = well["avg_gor_scf_bbl"]
api = well["api_gravity"]
pressure_ratio = well["pressure_to_bubble_point_ratio"]
water_cut = well["avg_water_cut_pct"]
temperature = well["reservoir_temperature_degF"]


# ------------------------------------------------------------
# ESP
# ------------------------------------------------------------

esp_components = {

    "Liquid rate":
        score_liquid_rate(liquid),

    "Viscosity":
        score_viscosity_for_esp(viscosity),

    "GOR":
        score_gor_for_esp(gor),

    "Water cut":
        score_water_cut(water_cut),

    "Pressure relative to bubble point":
        score_pressure_ratio(pressure_ratio),

    "Temperature":
        score_temperature(temperature)
}


# ------------------------------------------------------------
# GAS LIFT
# ------------------------------------------------------------

gaslift_components = {

    "GOR":
        score_gor_for_gaslift(gor),

    "Liquid rate":
        score_liquid_rate(liquid),

    "Pressure relative to bubble point":
        score_pressure_ratio(pressure_ratio),

    "Viscosity":
        score_viscosity_for_esp(viscosity)
}


# ------------------------------------------------------------
# PCP
# ------------------------------------------------------------

pcp_components = {

    "Viscosity":
        score_viscosity_for_pcp(viscosity),

    "API gravity":
        score_api_for_pcp(api),

    "Liquid rate":
        score_liquid_rate(liquid),

    "Water cut":
        score_water_cut(water_cut),

    "Temperature":
        score_temperature(temperature)
}


# ------------------------------------------------------------
# SRP
# ------------------------------------------------------------

srp_components = {

    "Liquid rate":
        score_liquid_rate(liquid),

    "Viscosity":
        score_viscosity_for_esp(viscosity),

    "Water cut":
        score_water_cut(water_cut),

    "Temperature":
        score_temperature(temperature)
}


# ============================================================
# 12. SCORE CALCULATION
# ============================================================

def calculate_score(component_dict):

    available_scores = [
        value
        for value in component_dict.values()
        if value is not None
    ]

    if len(available_scores) == 0:
        return np.nan

    return (
        sum(available_scores) /
        len(available_scores)
    )


scores = {

    "ESP": calculate_score(
        esp_components
    ),

    "Gas Lift": calculate_score(
        gaslift_components
    ),

    "PCP": calculate_score(
        pcp_components
    ),

    "SRP": calculate_score(
        srp_components
    )
}


# ============================================================
# 13. DATA COMPLETENESS BY METHOD
# ============================================================

method_parameters = {

    "ESP": [
        liquid,
        viscosity,
        gor,
        water_cut,
        pressure_ratio,
        temperature
    ],

    "Gas Lift": [
        gor,
        liquid,
        pressure_ratio,
        viscosity,
        gas_availability
        if gas_availability != "Unknown"
        else None
    ],

    "PCP": [
        viscosity,
        api,
        liquid,
        water_cut,
        temperature,
        sand_production
        if sand_production != "Unknown"
        else None
    ],

    "SRP": [
        liquid,
        viscosity,
        water_cut,
        temperature,
        well_depth
    ]
}


completeness = {}

for method, parameters in method_parameters.items():

    available = 0

    for value in parameters:

        if value is not None and not pd.isna(value):
            available += 1

    completeness[method] = (
        available /
        len(parameters)
    ) * 100


# ============================================================
# 14. COMPARISON TABLE
# ============================================================

st.header("Artificial Lift Comparison")

comparison_data = []

for method in [
    "ESP",
    "Gas Lift",
    "PCP",
    "SRP"
]:

    comparison_data.append({

        "Artificial Lift":
            method,

        "Screening Score / 5":
            round(scores[method], 2),

        "Data Completeness":
            f"{completeness[method]:.0f}%"
    })


comparison_df = pd.DataFrame(
    comparison_data
)

st.dataframe(
    comparison_df,
    use_container_width=True,
    hide_index=True
)


# ============================================================
# 15. ENGINEERING MECHANISM
# ============================================================

st.header("How Each Artificial Lift Method Works")


mechanisms = {

    "ESP": """
**Electric Submersible Pump (ESP)**

An ESP uses a downhole electric motor to drive a centrifugal pump.

The pump adds energy to the produced fluid and increases its pressure
so that the fluid can reach the surface.

ESP is generally associated with wells requiring relatively high liquid
production rates.

Important considerations include:

- Liquid production rate
- Free gas / high GOR
- Fluid viscosity
- Temperature
- Water production
- Electrical power availability
- Pump setting depth
- Well geometry

High free gas can reduce pump performance because centrifugal pumps are
sensitive to gas interference. GOR in this dashboard is therefore only
used as a screening indicator and is not a direct measurement of free
gas at the pump.
""",

    "Gas Lift": """
**Gas Lift**

Gas lift injects high-pressure gas into the production tubing through
gas-lift valves.

The injected gas mixes with the produced fluids and reduces the
effective density of the fluid column.

This reduces the hydrostatic pressure required to lift the fluids to
surface.

Important considerations include:

- Well depth
- Injection-gas availability
- Reservoir pressure
- GOR
- Production rate
- Tubing/completion geometry
- Surface compression facilities

Gas lift can be particularly useful where injection gas and compression
facilities are available.
""",

    "PCP": """
**Progressive Cavity Pump (PCP)**

A PCP consists primarily of a helical rotor rotating inside an
elastomeric stator.

Rotation creates progressing cavities that transport fluid from the
wellbore to the surface.

PCPs are commonly considered for viscous fluids and applications where
solids handling is important.

Important considerations include:

- Oil viscosity
- Fluid properties
- Sand/solids production
- Temperature
- Production rate
- Elastomer compatibility
- Gas handling
- Power availability
""",

    "SRP": """
**Sucker Rod Pump (SRP)**

An SRP uses a surface pumping unit and a string of sucker rods to
reciprocate a downhole plunger.

The reciprocating motion allows the pump to lift produced fluid to the
surface.

SRPs are commonly used for conventional oil wells with low-to-moderate
production requirements.

Important considerations include:

- Well depth
- Production rate
- Fluid viscosity
- Well geometry
- Rod loading
- Gas interference
- Sand production
- Pumping speed
"""
}


tabs = st.tabs([
    "ESP",
    "Gas Lift",
    "PCP",
    "SRP"
])


for tab, method in zip(
    tabs,
    ["ESP", "Gas Lift", "PCP", "SRP"]
):

    with tab:

        st.subheader(method)

        st.markdown(
            mechanisms[method]
        )

        st.write(
            f"**Screening score:** "
            f"{scores[method]:.2f} / 5"
        )

        st.write(
            f"**Data completeness:** "
            f"{completeness[method]:.0f}%"
        )


# ============================================================
# 16. WHY SECTION
# ============================================================

st.header("Why Does the Screening Score Look Like This?")

st.write(
    "The following factors are currently influencing each method's "
    "screening score."
)


def display_factors(component_dict):

    rows = []

    for parameter, score in component_dict.items():

        if score is None:

            rows.append({
                "Parameter": parameter,
                "Screening Rating": "Unavailable",
                "Interpretation": "Data not available"
            })

        else:

            if score >= 4:
                interpretation = "Positive screening factor"

            elif score >= 3:
                interpretation = "Moderate / neutral factor"

            else:
                interpretation = "Potential limiting factor"

            rows.append({
                "Parameter": parameter,
                "Screening Rating": f"{score}/5",
                "Interpretation": interpretation
            })

    return pd.DataFrame(rows)


factor_tabs = st.tabs([
    "ESP Factors",
    "Gas Lift Factors",
    "PCP Factors",
    "SRP Factors"
])


factor_dicts = [
    esp_components,
    gaslift_components,
    pcp_components,
    srp_components
]


for tab, components in zip(
    factor_tabs,
    factor_dicts
):

    with tab:

        st.dataframe(
            display_factors(components),
            use_container_width=True,
            hide_index=True
        )


# ============================================================
# 17. CALCULATIONS
# ============================================================

st.header("Engineering Calculations Used")

st.subheader("1. Average Liquid Rate")

st.latex(
    r"q_L = q_o + q_w"
)

st.write(
    "where:"
)

st.write(
    "- qₗ = total liquid rate\n"
    "- qₒ = oil rate\n"
    "- qᵥ = water rate"
)

if not pd.isna(well["avg_liquid_rate_blpd"]):

    st.code(
        f"qL = {well['avg_oil_rate_bopd']:.2f} "
        f"+ {well['avg_water_rate_bwpd']:.2f}\n"
        f"qL = {well['avg_liquid_rate_blpd']:.2f} BLPD"
    )


st.subheader("2. Pressure Relative to Bubble Point")

st.latex(
    r"\frac{P_i}{P_b}"
)

if not pd.isna(
    well["pressure_to_bubble_point_ratio"]
):

    st.code(
        f"Pi/Pb = "
        f"{well['initial_reservoir_pressure_psia']:.2f} / "
        f"{well['bubble_point_pressure_psia']:.2f}\n"
        f"Pi/Pb = "
        f"{well['pressure_to_bubble_point_ratio']:.3f}"
    )


st.subheader("3. Screening Score")

st.latex(
    r"""
    Score =
    \frac{\sum R_i}{N_{available}}
    """
)

st.write(
    "Each available engineering factor receives a transparent "
    "screening rating from 1 to 5. Missing parameters are excluded "
    "rather than being assigned assumed values."
)


# ============================================================
# 18. DATA SOURCES
# ============================================================

st.header("Parameter Sources")

source_rows = []

parameter_source = {

    "Well depth":
        "User input / unavailable",

    "Pump setting depth":
        "User input / unavailable",

    "Production rate":
        "Dataset",

    "Reservoir pressure":
        "Dataset",

    "Oil viscosity":
        "Dataset",

    "GOR":
        "Dataset",

    "Water cut":
        "Dataset",

    "Temperature":
        "Dataset",

    "Liquid rate":
        "Calculated from dataset",

    "Pi/Pb":
        "Calculated from dataset"
}


for parameter, source in parameter_source.items():

    source_rows.append({
        "Parameter": parameter,
        "Source": source
    })


st.dataframe(
    pd.DataFrame(source_rows),
    use_container_width=True,
    hide_index=True
)


# ============================================================
# 19. IMPORTANT LIMITATIONS
# ============================================================

st.header("Data Quality & Limitations")

st.warning(
    """
This dashboard provides an engineering screening analysis, not a final
field design.

The current dataset does not contain several method-specific parameters,
including:

- Well depth
- Pump setting depth
- Tubing/casing dimensions
- Gas injection availability
- Surface compression details
- Electrical power availability
- Detailed sand production
- Pump performance curves
- Detailed PVT
- Downhole flowing pressure
- Equipment-specific operating limits

Therefore, the result should be interpreted as a preliminary
artificial-lift screening.

A detailed artificial-lift design would require well-specific
nodal analysis, equipment constraints, operating envelopes and economic
evaluation.
"""
)


# ============================================================
# 20. FOOTER
# ============================================================

st.divider()

st.caption(
    "Artificial Lift Decision Support System | "
    "ESP • Gas Lift • PCP • SRP"
)
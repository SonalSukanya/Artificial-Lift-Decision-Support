
import os
import streamlit as st
import pandas as pd
import numpy as np


# ============================================================
# 1. PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Artificial Lift Decision Support",
    page_icon="🛢️",
    layout="wide"
)

st.title("Artificial Lift Decision Support System")
st.caption(
    "Preliminary technical screening of ESP, Gas Lift, PCP and SRP"
)


# ============================================================
# 2. SESSION STATE AND DATA LOADING
# ============================================================

if "well_dataset" not in st.session_state:
    st.session_state["well_dataset"] = None

if "dataset_name" not in st.session_state:
    st.session_state["dataset_name"] = None


DEFAULT_PATHS = [
    r"C:\Users\Sonal Sukanya\Documents\AL PROJECT\artificial_lift_decision_data_v2.csv",
    r"C:\Users\Sonal Sukanya\Documents\AL PROJECT\artificial_lift_decision_data.csv"
]


# ============================================================
# 3. PAGE NAVIGATION
# ============================================================

page = st.sidebar.radio(
    "Navigate",
    [
        "1. Data Upload & Instructions",
        "2. Recommendation Criteria",
        "3. Well-Specific Recommendation"
    ]
)


# ============================================================
# 4. DATA UPLOAD PAGE
# ============================================================

if page == "1. Data Upload & Instructions":

    st.header("Dataset Requirements & Upload Instructions")

    st.write(
        "Upload a CSV file containing one row per well. "
        "Use the exact column names listed below."
    )

    st.info(
        "Required means the column must exist in the CSV. "
        "Individual production values may be blank when unavailable. "
        "Do not replace missing values with zero."
    )

    well_columns = [
        ("well_id", "Unique well identifier", "Text", "Required"),
        ("field_id", "Field identifier", "Text", "Required"),
        ("basin", "Basin name", "Text", "Required"),
        ("fluid_type", "Produced fluid type", "Text", "Required"),
        ("completion_type", "Completion type", "Text", "Required"),
        ("lateral_length_ft", "Lateral length", "ft", "Required"),
        ("n_perforation_stages", "Number of perforation stages", "Count", "Required"),
        ("workover_count", "Number of workovers", "Count", "Required")
    ]

    reservoir_columns = [
        ("initial_reservoir_pressure_psia", "Initial reservoir pressure", "psia", "Required"),
        ("reservoir_temperature_degF", "Reservoir temperature", "°F", "Required"),
        ("permeability_md", "Permeability", "mD", "Required"),
        ("porosity_pct", "Porosity", "%", "Required"),
        ("net_pay_ft", "Net pay thickness", "ft", "Required"),
        ("bubble_point_pressure_psia", "Bubble-point pressure", "psia", "Required"),
        ("formation_volume_factor_bo", "Oil formation volume factor", "RB/STB", "Required"),
        ("reservoir_drive_type", "Reservoir drive mechanism", "Text", "Required"),
        ("aquifer_strength_index", "Aquifer strength index", "Dataset scale", "Required")
    ]

    fluid_columns = [
        ("api_gravity", "Oil API gravity", "°API", "Required"),
        ("oil_viscosity_cp", "Oil viscosity", "cP", "Required"),
        ("sulfur_content_pct", "Sulfur content", "%", "Optional")
    ]

    production_columns = [
        ("avg_oil_rate_bopd", "Average oil production rate", "BOPD", "Required; values may be blank"),
        ("avg_gas_rate_mcfd", "Average gas production rate", "Mscf/day", "Required; values may be blank"),
        ("avg_water_rate_bwpd", "Average water production rate", "BWPD", "Required; values may be blank"),
        ("avg_gor_scf_bbl", "Average gas-oil ratio", "scf/STB", "Required; values may be blank"),
        ("avg_water_cut_pct", "Average water cut", "%", "Required; values may be blank"),
        ("production_days", "Producing days in reporting period", "Days", "Optional")
    ]

    derived_columns = [
        ("production_data_available", "Derived from oil-rate availability", "True/False"),
        ("avg_liquid_rate_blpd", "Oil rate + water rate", "BLPD"),
        ("pressure_to_bubble_point_ratio", "Initial pressure / bubble-point pressure", "Dimensionless"),
        ("production_data_status", "Generated production-data status", "Text")
    ]

    def show_schema_table(rows, headings):
        table = pd.DataFrame(rows, columns=headings)
        st.dataframe(
            table,
            use_container_width=True,
            hide_index=True
        )

    with st.expander("A. Well and completion information", expanded=True):
        show_schema_table(
            well_columns,
            ["CSV column name", "Meaning", "Unit / format", "Requirement"]
        )

    with st.expander("B. Reservoir information"):
        show_schema_table(
            reservoir_columns,
            ["CSV column name", "Meaning", "Unit / format", "Requirement"]
        )

    with st.expander("C. Fluid properties"):
        show_schema_table(
            fluid_columns,
            ["CSV column name", "Meaning", "Unit / format", "Requirement"]
        )

    with st.expander("D. Production information"):
        show_schema_table(
            production_columns,
            ["CSV column name", "Meaning", "Unit / format", "Requirement"]
        )

    with st.expander("E. Automatically generated columns"):
        st.write(
            "Do not add these columns manually. "
            "The dashboard calculates or generates them."
        )

        # FIX: derived_columns has THREE values per row,
        # so this table must have THREE column headings.
        show_schema_table(
            derived_columns,
            ["Generated column", "How it is obtained", "Unit / format"]
        )

    st.subheader("CSV header template")

    csv_header = (
        "well_id,field_id,basin,fluid_type,completion_type,"
        "lateral_length_ft,n_perforation_stages,workover_count,"
        "initial_reservoir_pressure_psia,reservoir_temperature_degF,"
        "permeability_md,porosity_pct,net_pay_ft,api_gravity,"
        "sulfur_content_pct,bubble_point_pressure_psia,oil_viscosity_cp,"
        "formation_volume_factor_bo,reservoir_drive_type,"
        "aquifer_strength_index,avg_oil_rate_bopd,avg_gas_rate_mcfd,"
        "avg_water_rate_bwpd,avg_gor_scf_bbl,avg_water_cut_pct,"
        "production_days"
    )

    st.code(csv_header, language="text")

    st.markdown(
        """
        **Important dataset instructions**

        - Use numeric values for numerical columns.
        - Do not include units inside individual cells.
        - Use consistent names for basins, fields and completion types.
        - Leave unavailable production values blank, not zero.
        - Do not include `lift_type`; it is excluded to avoid biasing the screening.
        - `formation_name` is optional.
        - Well depth and pump setting depth are not available in the current dataset.
          They can be entered separately when known.
        - Gas availability, electrical power and sand production are also
          entered separately.
        """
    )

    st.divider()

    st.subheader("Upload your dataset")

    uploaded_file = st.file_uploader(
        "Choose a CSV file",
        type=["csv"],
        key="main_dataset_uploader"
    )

    if uploaded_file is not None:

        try:
            uploaded_df = pd.read_csv(uploaded_file)

            st.session_state["well_dataset"] = uploaded_df
            st.session_state["dataset_name"] = uploaded_file.name

            st.success("Dataset uploaded successfully.")

        except Exception as error:
            st.error(f"Could not read the CSV file: {error}")

    elif st.session_state["well_dataset"] is None:

        for path in DEFAULT_PATHS:

            if os.path.exists(path):

                try:
                    st.session_state["well_dataset"] = pd.read_csv(path)
                    st.session_state["dataset_name"] = os.path.basename(path)

                    st.info(
                        "Using local dataset: "
                        + os.path.basename(path)
                    )

                    break

                except Exception as error:
                    st.error(f"Could not read local CSV: {error}")

    if st.session_state["well_dataset"] is not None:

        st.subheader("Dataset preview")

        st.write(
            f"File: **{st.session_state['dataset_name']}**"
        )

        st.write(
            f"Rows: **{len(st.session_state['well_dataset'])}** | "
            f"Columns: **{len(st.session_state['well_dataset'].columns)}**"
        )

        st.dataframe(
            st.session_state["well_dataset"].head(10),
            use_container_width=True,
            hide_index=True
        )

        st.success(
            "Dataset is stored for the other dashboard pages. "
            "You can now open Recommendation Criteria or "
            "Well-Specific Recommendation."
        )

    else:
        st.warning(
            "Upload a CSV file to use the recommendation pages."
        )


# ============================================================
# 5. RECOMMENDATION CRITERIA PAGE
# ============================================================

elif page == "2. Recommendation Criteria":

    st.header("Artificial Lift Recommendation Criteria")

    st.write(
        "This page explains the engineering considerations behind "
        "the preliminary screening of each artificial lift method."
    )

    st.info(
        "The dashboard evaluates technical suitability using available "
        "reservoir, fluid and production properties. Economics are excluded."
    )

    st.subheader("1. Electric Submersible Pump (ESP)")

    st.markdown(
        """
        ESP uses a downhole electric motor to drive a multistage
        centrifugal pump.

        **Selection considerations**

        - **Liquid rate:** ESPs are commonly used for relatively high
          liquid-production requirements. The required rate must fall
          within the selected pump's operating range.
        - **Viscosity:** Increasing viscosity increases hydraulic losses
          and can reduce pump performance.
        - **GOR/free gas:** Free gas entering the pump can cause gas
          interference, reducing pump head and efficiency.
        - **Water cut:** Influences the produced-fluid mixture and
          fluid properties used in pump design.
        - **Temperature:** Affects motor, cable, seal and equipment
          temperature limits.
        - **Electrical power:** A suitable power supply is required.
        """
    )

    st.divider()

    st.subheader("2. Gas Lift")

    st.markdown(
        """
        Gas lift injects high-pressure gas into the production tubing.
        The injected gas reduces the average density of the flowing
        fluid column, reducing the hydrostatic pressure required to
        lift fluids to the surface.

        **Selection considerations**

        - **Injection-gas availability:** A reliable gas supply is essential.
        - **GOR:** Provides information about produced gas relative to oil,
          but is not the same as free-gas fraction at the injection point.
        - **Reservoir pressure:** Influences the well's inflow and the
          pressure conditions under which gas lift operates.
        - **Liquid rate:** Must be evaluated against the expected gas
          injection rate and unloading/operating design.
        - **Well depth and completion:** Influence valve placement,
          injection depth and gas-lift design.
        - **Compression facilities:** Required to supply injection gas
          at the necessary pressure.
        """
    )

    st.divider()

    st.subheader("3. Progressive Cavity Pump (PCP)")

    st.markdown(
        """
        PCP uses a helical rotor rotating inside an elastomeric stator.
        The progressing cavities transport fluid to the surface.

        **Selection considerations**

        - **Viscosity:** PCPs are positive-displacement pumps and are
          often considered for viscous-fluid applications.
        - **Liquid rate:** Must be within the selected pump's displacement
          and operating-speed range.
        - **Gas:** Free gas can reduce volumetric efficiency and affect
          pump operation.
        - **Sand/solids:** Some PCP designs can handle solids, but abrasive
          solids can cause rotor and stator wear.
        - **Temperature:** Must be compatible with the elastomer.
        - **Fluid chemistry:** Produced-fluid composition must be
          compatible with the selected elastomer.
        - **Well geometry:** Rod-driven PCP systems require checks for
          rod/tubing contact and mechanical loading.
        """
    )

    st.divider()

    st.subheader("4. Sucker Rod Pump (SRP)")

    st.markdown(
        """
        SRP uses a surface pumping unit and sucker-rod string to
        reciprocate a downhole plunger.

        **Selection considerations**

        - **Production rate:** SRP is commonly applied to low-to-moderate
          production requirements.
        - **Well depth:** Influences rod loading and pumping-unit design.
        - **Viscosity:** Higher viscosity increases friction and
          affects pump performance.
        - **Gas:** Gas interference can reduce pump fillage and efficiency.
        - **Sand:** Solids can cause wear or sticking of pump components.
        - **Deviation/dogleg:** Can increase rod/tubing contact and wear.
        """
    )

    st.divider()

    st.subheader("How the dashboard calculates the screening score")

    st.latex(
        r"Score = \frac{\sum R_i}{N_{\mathrm{available}}}"
    )

    st.write(
        "Each method receives a rating for the factors included in its "
        "screening function. The final score is the arithmetic mean of "
        "the available factor ratings."
    )

    st.warning(
        "These ratings are preliminary screening heuristics. "
        "They are not universal operating limits, pump-performance curves "
        "or a substitute for detailed artificial-lift design."
    )

    st.subheader("What is excluded from the recommendation?")

    st.markdown(
        """
        **Economics are deliberately excluded.** The dashboard does not
        compare:

        - Initial installation cost
        - Energy or gas-compression cost
        - Maintenance and workover cost
        - Downtime cost
        - Production value or profitability

        The recommendation is therefore a preliminary technical screening,
        not an economically optimized selection.
        """
    )


# ============================================================
# 6. WELL-SPECIFIC RECOMMENDATION PAGE
# ============================================================

elif page == "3. Well-Specific Recommendation":

    st.header("Well-Specific Artificial Lift Recommendation")

    if st.session_state["well_dataset"] is None:

        st.warning(
            "No dataset is loaded. Go to Data Upload & Instructions "
            "and upload your CSV first."
        )

        st.stop()

    df = st.session_state["well_dataset"].copy()

    required_columns = [
        "well_id",
        "field_id",
        "basin",
        "fluid_type",
        "completion_type",
        "initial_reservoir_pressure_psia",
        "reservoir_temperature_degF",
        "permeability_md",
        "porosity_pct",
        "net_pay_ft",
        "api_gravity",
        "bubble_point_pressure_psia",
        "oil_viscosity_cp",
        "avg_oil_rate_bopd",
        "avg_gas_rate_mcfd",
        "avg_water_rate_bwpd",
        "avg_gor_scf_bbl",
        "avg_water_cut_pct"
    ]

    missing_columns = [
        col for col in required_columns
        if col not in df.columns
    ]

    if missing_columns:

        st.error("The dataset is missing required columns:")

        for col in missing_columns:
            st.write(f"- `{col}`")

        st.stop()

    optional_columns = [
        "formation_name",
        "lateral_length_ft",
        "n_perforation_stages",
        "workover_count",
        "reservoir_drive_type",
        "aquifer_strength_index",
        "production_days"
    ]

    # Convert expected numerical columns safely.
    numeric_columns = [
        "initial_reservoir_pressure_psia",
        "reservoir_temperature_degF",
        "permeability_md",
        "porosity_pct",
        "net_pay_ft",
        "api_gravity",
        "bubble_point_pressure_psia",
        "oil_viscosity_cp",
        "avg_oil_rate_bopd",
        "avg_gas_rate_mcfd",
        "avg_water_rate_bwpd",
        "avg_gor_scf_bbl",
        "avg_water_cut_pct"
    ]

    for col in numeric_columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # Derived parameters.
    df["avg_liquid_rate_blpd"] = (
        df["avg_oil_rate_bopd"] +
        df["avg_water_rate_bwpd"]
    )

    df["pressure_to_bubble_point_ratio"] = (
        df["initial_reservoir_pressure_psia"] /
        df["bubble_point_pressure_psia"].replace(0, np.nan)
    )

    # --------------------------------------------------------
    # WELL FILTERS
    # --------------------------------------------------------

    st.sidebar.subheader("Select Well")

    basin_options = sorted(
        df["basin"].dropna().unique().tolist()
    )

    if not basin_options:
        st.error("No basin values are available.")
        st.stop()

    selected_basin = st.sidebar.selectbox(
        "Basin",
        basin_options
    )

    basin_df = df[df["basin"] == selected_basin]

    field_options = sorted(
        basin_df["field_id"].dropna().unique().tolist()
    )

    if not field_options:
        st.error("No fields are available for this basin.")
        st.stop()

    selected_field = st.sidebar.selectbox(
        "Field",
        field_options
    )

    field_df = basin_df[
        basin_df["field_id"] == selected_field
    ]

    well_options = sorted(
        field_df["well_id"].dropna().unique().tolist()
    )

    if not well_options:
        st.error("No wells are available for this field.")
        st.stop()

    selected_well = st.sidebar.selectbox(
        "Well",
        well_options
    )

    well = df[
        df["well_id"] == selected_well
    ].iloc[0]

    # --------------------------------------------------------
    # SAFE FORMATTING
    # --------------------------------------------------------

    def display_value(value, decimals=2, unit=""):

        if pd.isna(value):
            return "Unavailable"

        return f"{value:,.{decimals}f}{unit}"

    def get_value(column):

        if column not in well.index:
            return np.nan

        return well[column]

    # --------------------------------------------------------
    # WELL OVERVIEW
    # --------------------------------------------------------

    st.subheader("Selected Well")

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Well", str(well["well_id"]))
    c2.metric("Field", str(well["field_id"]))
    c3.metric("Basin", str(well["basin"]))

    if "formation_name" in df.columns:
        formation = well["formation_name"]
    else:
        formation = "Unavailable"

    c4.metric("Formation", str(formation))

    st.subheader("Well and Reservoir Properties")

    c1, c2, c3 = st.columns(3)

    with c1:
        st.write("**Fluid type:**", well["fluid_type"])
        st.write("**Completion:**", well["completion_type"])
        st.write(
            "**Lateral length:**",
            display_value(get_value("lateral_length_ft"), 1, " ft")
        )

    with c2:
        st.write(
            "**Reservoir pressure:**",
            display_value(get_value("initial_reservoir_pressure_psia"), 1, " psia")
        )
        st.write(
            "**Bubble-point pressure:**",
            display_value(get_value("bubble_point_pressure_psia"), 1, " psia")
        )
        st.write(
            "**Pressure / bubble-point ratio:**",
            display_value(get_value("pressure_to_bubble_point_ratio"), 3)
        )

    with c3:
        st.write(
            "**Reservoir temperature:**",
            display_value(get_value("reservoir_temperature_degF"), 1, " °F")
        )
        st.write(
            "**Oil viscosity:**",
            display_value(get_value("oil_viscosity_cp"), 2, " cP")
        )
        st.write(
            "**API gravity:**",
            display_value(get_value("api_gravity"), 1, "°")
        )

    # --------------------------------------------------------
    # PRODUCTION OVERVIEW
    # --------------------------------------------------------

    st.subheader("Production Information")

    p1, p2, p3, p4, p5 = st.columns(5)

    p1.metric(
        "Oil rate",
        display_value(get_value("avg_oil_rate_bopd"), 1, " BOPD")
    )

    p2.metric(
        "Water rate",
        display_value(get_value("avg_water_rate_bwpd"), 1, " BWPD")
    )

    p3.metric(
        "Liquid rate",
        display_value(get_value("avg_liquid_rate_blpd"), 1, " BLPD")
    )

    p4.metric(
        "GOR",
        display_value(get_value("avg_gor_scf_bbl"), 1, " scf/STB")
    )

    p5.metric(
        "Water cut",
        display_value(get_value("avg_water_cut_pct"), 1, "%")
    )

    # --------------------------------------------------------
    # USER INPUTS
    # --------------------------------------------------------

    st.subheader("Additional Engineering Inputs")

    st.write(
        "Enter these values if available. They are not present "
        "in the current dataset."
    )

    input1, input2, input3 = st.columns(3)

    with input1:

        depth_known = st.checkbox(
            "Well depth is available",
            value=False
        )

        if depth_known:
            well_depth = st.number_input(
                "Well depth (ft)",
                min_value=0.0,
                value=5000.0,
                step=100.0
            )
        else:
            well_depth = np.nan

        setting_known = st.checkbox(
            "Pump setting depth is available",
            value=False
        )

        if setting_known:
            pump_setting_depth = st.number_input(
                "Pump setting depth (ft)",
                min_value=0.0,
                value=4000.0,
                step=100.0
            )
        else:
            pump_setting_depth = np.nan

    with input2:

        gas_availability = st.selectbox(
            "Injection gas available?",
            ["Unknown", "Yes", "No"]
        )

        electrical_power = st.selectbox(
            "Electrical power available?",
            ["Unknown", "Yes", "No"]
        )

    with input3:

        sand_production = st.selectbox(
            "Significant sand production?",
            ["Unknown", "Yes", "No"]
        )

        surface_pressure_known = st.checkbox(
            "Surface pressure is available",
            value=False
        )

        if surface_pressure_known:
            surface_pressure = st.number_input(
                "Surface pressure (psi)",
                min_value=0.0,
                value=100.0,
                step=10.0
            )
        else:
            surface_pressure = np.nan

    # --------------------------------------------------------
    # SCREENING FUNCTIONS
    # --------------------------------------------------------

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

    def score_water_cut(water_cut):

        if pd.isna(water_cut):
            return None

        if water_cut < 50:
            return 4
        elif water_cut < 70:
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

    # --------------------------------------------------------
    # GET WELL PARAMETERS
    # --------------------------------------------------------

    liquid = get_value("avg_liquid_rate_blpd")
    viscosity = get_value("oil_viscosity_cp")
    gor = get_value("avg_gor_scf_bbl")
    api = get_value("api_gravity")
    pressure_ratio = get_value("pressure_to_bubble_point_ratio")
    water_cut = get_value("avg_water_cut_pct")
    temperature = get_value("reservoir_temperature_degF")

    # --------------------------------------------------------
    # METHOD FACTOR RATINGS
    # --------------------------------------------------------

    esp_components = {
        "Liquid rate": score_liquid_rate(liquid),
        "Viscosity": score_viscosity_for_esp(viscosity),
        "GOR": score_gor_for_esp(gor),
        "Water cut": score_water_cut(water_cut),
        "Pressure relative to bubble point": score_pressure_ratio(pressure_ratio),
        "Temperature": score_temperature(temperature)
    }

    gaslift_components = {
        "GOR": score_gor_for_gaslift(gor),
        "Liquid rate": score_liquid_rate(liquid),
        "Pressure relative to bubble point": score_pressure_ratio(pressure_ratio),
        "Viscosity": score_viscosity_for_esp(viscosity)
    }

    pcp_components = {
        "Viscosity": score_viscosity_for_pcp(viscosity),
        "Liquid rate": score_liquid_rate(liquid),
        "Water cut": score_water_cut(water_cut),
        "Temperature": score_temperature(temperature)
    }

    srp_components = {
        "Liquid rate": score_liquid_rate(liquid),
        "Viscosity": score_viscosity_for_esp(viscosity),
        "Water cut": score_water_cut(water_cut),
        "Temperature": score_temperature(temperature)
    }

    component_lookup = {
        "ESP": esp_components,
        "Gas Lift": gaslift_components,
        "PCP": pcp_components,
        "SRP": srp_components
    }

    # --------------------------------------------------------
    # CALCULATE SCORES
    # --------------------------------------------------------

    def calculate_score(components):

        available = [
            value for value in components.values()
            if value is not None
        ]

        if not available:
            return np.nan

        return float(np.mean(available))

    scores = {
        method: calculate_score(components)
        for method, components in component_lookup.items()
    }

    # --------------------------------------------------------
    # PRACTICAL FEASIBILITY FLAGS
    # --------------------------------------------------------

    feasibility = {
        "ESP": (
            electrical_power != "No"
        ),
        "Gas Lift": (
            gas_availability != "No"
        ),
        "PCP": (
            electrical_power != "No"
        ),
        "SRP": (
            electrical_power != "No"
        )
    }

    feasibility_notes = {
        "ESP": (
            "Electrical power is marked unavailable."
            if electrical_power == "No"
            else "Electrical power availability must be confirmed."
            if electrical_power == "Unknown"
            else "Electrical power is marked available."
        ),
        "Gas Lift": (
            "Injection gas is marked unavailable."
            if gas_availability == "No"
            else "Injection-gas supply and compression must be confirmed."
            if gas_availability == "Unknown"
            else "Injection gas is marked available."
        ),
        "PCP": (
            "Confirm a suitable prime-mover and power arrangement."
            if electrical_power == "No"
            else "Confirm the drive and power arrangement."
            if electrical_power == "Unknown"
            else "Power is marked available."
        ),
        "SRP": (
            "Confirm a suitable prime-mover and power arrangement."
            if electrical_power == "No"
            else "Confirm the drive and power arrangement."
            if electrical_power == "Unknown"
            else "Power is marked available."
        )
    }

    # --------------------------------------------------------
    # DATA COMPLETENESS
    # --------------------------------------------------------

    method_inputs = {
        "ESP": [
            liquid, viscosity, gor, water_cut,
            pressure_ratio, temperature
        ],
        "Gas Lift": [
            gor, liquid, pressure_ratio, viscosity,
            gas_availability if gas_availability != "Unknown" else None
        ],
        "PCP": [
            viscosity, liquid, water_cut, temperature,
            sand_production if sand_production != "Unknown" else None
        ],
        "SRP": [
            liquid, viscosity, water_cut, temperature,
            well_depth
        ]
    }

    completeness = {}

    for method, values in method_inputs.items():

        available = sum(
            value is not None and not pd.isna(value)
            for value in values
        )

        completeness[method] = (
            available / len(values) * 100
        )

    # --------------------------------------------------------
    # METHOD COMPARISON
    # --------------------------------------------------------

    st.divider()
    st.header("Artificial Lift Method Comparison")

    st.info(
        "The numerical score compares the factors included in the "
        "screening model. Practical constraints such as unavailable "
        "injection gas or electrical power are displayed separately."
    )

    comparison_rows = []

    for method, score in scores.items():

        comparison_rows.append({
            "Method": method,
            "Screening score (/5)": (
                round(score, 2) if pd.notna(score) else np.nan
            ),
            "Data coverage": f"{completeness[method]:.0f}%",
            "Current constraint status": (
                "Constraint reported"
                if not feasibility[method]
                else "No reported hard constraint"
            )
        })

    comparison_df = pd.DataFrame(comparison_rows)

    comparison_df = comparison_df.sort_values(
        "Screening score (/5)",
        ascending=False,
        na_position="last"
    )

    st.dataframe(
        comparison_df,
        use_container_width=True,
        hide_index=True
    )

    # --------------------------------------------------------
    # SELECT HIGHEST-SCORING FEASIBLE METHOD
    # --------------------------------------------------------

    feasible_scores = {
        method: score
        for method, score in scores.items()
        if pd.notna(score) and feasibility[method]
    }

    if feasible_scores:

        highest_score = max(feasible_scores.values())

        top_methods = [
            method
            for method, score in feasible_scores.items()
            if np.isclose(score, highest_score)
        ]

        if len(top_methods) == 1:

            selected_method = top_methods[0]

            st.success(
                f"Preliminary best available technical fit: "
                f"**{selected_method}** "
                f"(score: {highest_score:.2f}/5)"
            )

        else:

            selected_method = None

            st.warning(
                "The available factors produce a tie between: "
                + ", ".join(top_methods)
                + ". The dashboard cannot identify one clear winner."
            )

    else:

        selected_method = None

        st.warning(
            "No method can currently be identified as a feasible "
            "preliminary recommendation. Review the reported constraints."
        )

    # --------------------------------------------------------
    # PROPERTY-SPECIFIC EXPLANATIONS
    # --------------------------------------------------------

    def explain_factor(method, factor, rating):

        if rating is None or pd.isna(rating):
            return (
                f"**{factor}:** Data is unavailable, so this factor "
                f"cannot support or reduce the screening score."
            )

        if factor == "Liquid rate":

            if rating >= 4:
                return (
                    f"**Liquid rate ({display_value(liquid, 1, ' BLPD')}):** "
                    "The production requirement gives this method a "
                    "favourable rate-screening result. The actual pump "
                    "capacity and operating range must still be checked."
                )

            return (
                f"**Liquid rate ({display_value(liquid, 1, ' BLPD')}):** "
                "The rate does not provide a strong advantage in this "
                "screening model. Check the required production rate "
                "against the selected equipment's operating range."
            )

        if factor == "Viscosity":

            if method == "PCP":

                return (
                    f"**Oil viscosity ({display_value(viscosity, 2, ' cP')}):** "
                    "PCPs are positive-displacement pumps and are often "
                    "considered for viscous fluids. This viscosity therefore "
                    "supports PCP in the screening comparison."
                )

            if rating >= 4:

                return (
                    f"**Oil viscosity ({display_value(viscosity, 2, ' cP')}):** "
                    "The viscosity receives a favourable rating in this "
                    "method's screening function. Increasing viscosity can "
                    "increase hydraulic or mechanical losses, so the "
                    "equipment's viscosity correction must be checked."
                )

            return (
                f"**Oil viscosity ({display_value(viscosity, 2, ' cP')}):** "
                "Higher viscosity can increase flow resistance and reduce "
                "pump performance. This is a potential limitation for "
                "this method."
            )

        if factor == "GOR":

            if method == "Gas Lift":

                return (
                    f"**GOR ({display_value(gor, 1, ' scf/STB')}):** "
                    "The measured GOR provides information about the "
                    "produced gas relative to oil. It influences the "
                    "gas-related screening result, but it does not directly "
                    "measure free gas at the pump or determine the required "
                    "injection-gas rate."
                )

            return (
                f"**GOR ({display_value(gor, 1, ' scf/STB')}):** "
                "Higher produced GOR can indicate greater gas-handling "
                "requirements. Free gas entering a centrifugal pump can "
                "cause gas interference, so the actual free-gas fraction "
                "at pump intake must be determined."
            )

        if factor == "Water cut":

            return (
                f"**Water cut ({display_value(water_cut, 1, '%')}):** "
                "Water cut describes the proportion of produced liquid "
                "that is water. It helps characterize the fluid mixture "
                "and production duty, but it does not independently "
                "determine which lift method is best."
            )

        if factor == "Temperature":

            return (
                f"**Reservoir temperature "
                f"({display_value(temperature, 1, ' °F')}):** "
                "Temperature affects the operating limits of downhole "
                "equipment. For PCP, elastomer temperature compatibility "
                "is particularly important. The actual equipment rating "
                "must be checked."
            )

        if factor == "Pressure relative to bubble point":

            return (
                f"**Initial pressure / bubble-point pressure "
                f"({display_value(pressure_ratio, 3)}):** "
                "This ratio indicates the initial reservoir pressure "
                "relative to bubble-point pressure. It provides reservoir "
                "context but does not replace flowing bottomhole pressure "
                "or a free-gas calculation."
            )

        return (
            f"**{factor}:** This factor contributes a screening rating "
            "to the method comparison."
        )

    # --------------------------------------------------------
    # RECOMMENDATION EXPLANATION
    # --------------------------------------------------------

    st.divider()
    st.header("Why is this method recommended for this well?")

    if selected_method is not None:

        st.subheader(f"Recommended method: {selected_method}")

        st.write(
            f"The {selected_method} has the highest screening score "
            "among the methods that do not have a reported hard "
            "facility constraint."
        )

        st.markdown(
            f"**Why {selected_method} is suggested for "
            f"Well {selected_well}:**"
        )

        selected_components = component_lookup[selected_method]

        for factor, rating in selected_components.items():

            st.markdown(
                "- " + explain_factor(
                    selected_method,
                    factor,
                    rating
                )
            )

        st.subheader("Why did it rank above the other methods?")

        for other_method, other_score in scores.items():

            if other_method == selected_method:
                continue

            if pd.isna(other_score):
                st.write(
                    f"**{other_method}:** Insufficient available "
                    "factor data to calculate a screening score."
                )
                continue

            difference = highest_score - other_score

            if difference > 0.001:

                st.write(
                    f"**{other_method}:** Its screening score is "
                    f"{other_score:.2f}/5, compared with "
                    f"{highest_score:.2f}/5 for {selected_method}. "
                    "Review the factor breakdown below to see which "
                    "ratings produced this difference."
                )

            else:

                st.write(
                    f"**{other_method}:** It has a similar screening "
                    "score, so detailed well-specific design checks "
                    "will be important before choosing between them."
                )

    else:

        st.warning(
            "There is no single preliminary recommendation. "
            "Review the scores, missing inputs and practical constraints."
        )

    # --------------------------------------------------------
    # FACTOR BREAKDOWN FOR ALL METHODS
    # --------------------------------------------------------

    st.divider()
    st.subheader("Detailed factor breakdown")

    for method, components in component_lookup.items():

        with st.expander(
            f"{method} — "
            + (
                f"{scores[method]:.2f}/5"
                if pd.notna(scores[method])
                else "Score unavailable"
            ),
            expanded=(method == selected_method)
        ):

            for factor, rating in components.items():

                if rating is None:
                    rating_text = "Unavailable"
                else:
                    rating_text = f"{rating}/5"

                st.markdown(
                    f"**{factor}: {rating_text}**"
                )

                st.write(
                    explain_factor(method, factor, rating)
                )

            st.write(
                "**Practical constraint:** "
                + feasibility_notes[method]
            )

    # --------------------------------------------------------
    # INSTALLATION CHECKS - SEPARATE FROM SCORE CRITERIA
    # --------------------------------------------------------

    st.divider()
    st.header("Checks required before installing the selected method")

    st.write(
        "These are engineering design and feasibility checks. "
        "They are not all included in the numerical screening score."
    )

    if selected_method == "PCP":

        st.markdown(
            """
            **PCP installation checks**

            1. Confirm pump displacement and operating speed can deliver
               the required liquid rate.
            2. Check the required differential pressure and pump stages.
            3. Determine free-gas fraction at pump intake and evaluate
               gas-handling requirements.
            4. Confirm elastomer compatibility with temperature and
               produced-fluid chemistry.
            5. Evaluate sand concentration, particle size and abrasion risk.
            6. Check well depth, deviation, dogleg severity, rod loading
               and rod/tubing contact.
            7. Verify tubing, rod and surface-drive equipment limits.
            """
        )

    elif selected_method == "ESP":

        st.markdown(
            """
            **ESP installation checks**

            1. Match pump capacity to the required production rate.
            2. Determine flowing bottomhole pressure and pump intake pressure.
            3. Calculate free-gas fraction at pump intake.
            4. Check gas separator or gas-handler requirements.
            5. Check motor, cable, seal and temperature ratings.
            6. Confirm electrical supply and cable arrangement.
            7. Check casing clearance, setting depth and completion geometry.
            8. Evaluate solids and scaling risks.
            """
        )

    elif selected_method == "Gas Lift":

        st.markdown(
            """
            **Gas-lift installation checks**

            1. Confirm reliable injection-gas supply.
            2. Check compressor capacity and discharge pressure.
            3. Determine injection-gas requirement.
            4. Design valve type, spacing and injection depth.
            5. Check tubing and casing pressure limits.
            6. Perform gas-lift performance and nodal analysis.
            7. Confirm surface separation and gas-handling facilities.
            """
        )

    elif selected_method == "SRP":

        st.markdown(
            """
            **SRP installation checks**

            1. Confirm required pump displacement and pumping speed.
            2. Calculate rod loads and polished-rod loads.
            3. Check rod strength and fatigue limits.
            4. Evaluate deviation and dogleg severity.
            5. Check gas interference and pump fillage.
            6. Evaluate sand production and pump wear.
            7. Verify tubing, rod string and surface-unit compatibility.
            """
        )

    st.subheader("Additional information still needed")

    missing_inputs = []

    if pd.isna(well_depth):
        missing_inputs.append("Well depth")

    if pd.isna(pump_setting_depth):
        missing_inputs.append("Pump setting depth")

    if gas_availability == "Unknown":
        missing_inputs.append("Injection-gas availability")

    if electrical_power == "Unknown":
        missing_inputs.append("Electrical power availability")

    if sand_production == "Unknown":
        missing_inputs.append("Sand production")

    if pd.isna(gor):
        missing_inputs.append("Measured GOR")

    if pd.isna(viscosity):
        missing_inputs.append("Oil viscosity")

    if missing_inputs:

        st.warning(
            "The following information is still unavailable: "
            + ", ".join(missing_inputs)
        )

    else:

        st.success(
            "The additional screening inputs shown above have been provided. "
            "Detailed equipment and wellbore checks are still required."
        )

    st.caption(
        "Final selection requires detailed well data, PVT, flowing pressures, "
        "equipment performance curves, wellbore geometry and engineering design. "
        "This dashboard does not perform a final artificial-lift design."
    )

    # --------------------------------------------------------
    # DATA COMPLETENESS AND SOURCES
    # --------------------------------------------------------

    st.divider()
    st.header("Data Quality and Parameter Sources")

    quality_rows = []

    source_parameters = [
        ("Liquid rate", liquid, "Calculated from dataset oil and water rates"),
        ("Oil viscosity", viscosity, "Dataset"),
        ("GOR", gor, "Dataset"),
        ("Water cut", water_cut, "Dataset"),
        ("API gravity", api, "Dataset"),
        ("Reservoir temperature", temperature, "Dataset"),
        ("Pressure / bubble-point ratio", pressure_ratio, "Calculated from dataset"),
        ("Well depth", well_depth, "User entered" if pd.notna(well_depth) else "Unavailable"),
        ("Pump setting depth", pump_setting_depth, "User entered" if pd.notna(pump_setting_depth) else "Unavailable"),
        ("Gas availability", gas_availability, "User entered"),
        ("Electrical power", electrical_power, "User entered"),
        ("Sand production", sand_production, "User entered")
    ]

    for parameter, value, source in source_parameters:

        if value is None or pd.isna(value):
            shown_value = "Unavailable"
        else:
            shown_value = value

        quality_rows.append({
            "Parameter": parameter,
            "Value": shown_value,
            "Source": source
        })

    st.dataframe(
        pd.DataFrame(quality_rows),
        use_container_width=True,
        hide_index=True
    )

    st.subheader("Important limitations")

    st.warning(
        """
        This dashboard provides preliminary technical screening only.

        The numerical scores use simplified heuristic ratings. They have
        not been calibrated against equipment performance curves or
        validated field installations.

        The dashboard does not currently calculate:

        - Actual free-gas fraction at pump intake
        - Detailed PVT behaviour
        - Pump intake pressure
        - Detailed inflow and outflow performance
        - Rod loads or ESP motor loads
        - PCP elastomer compatibility
        - Gas-lift valve spacing or injection requirements
        - Detailed tubing/casing mechanical limits

        Economics are intentionally excluded.

        A final method selection requires detailed engineering design,
        operating-envelope checks and field validation.
        """
    )


# ============================================================
# END OF APPLICATION
# ============================================================

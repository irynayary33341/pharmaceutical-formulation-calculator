import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

from io import BytesIO
excel_buffer = BytesIO()
png_buffer = BytesIO()

from scipy.stats import pearsonr, spearmanr

st.title("Pharma R&D Toolkit")
mode_anal = st.radio(
    "Select section",['Formulation Calculations', 'Data Analysis'])
if mode_anal == 'Formulation Calculations':
    mode = st.radio("Select option",
    ["Liquid Dosage Forms", "Solid Dosage Forms", "Batch Size Calculator", "API & Filler Correction"])
    if mode == "Liquid Dosage Forms":
        ml_per_unit = st.number_input("Enter the fill volume per unit (ml):", min_value=0.1, value=1.0, step=0.01, key="ml_per_unit")
    
        number_of_units = st.number_input("Enter the number of units:", min_value= 1.0, value=100.0, step= 1.0, key="number_of_units")
    
        total_volume_weight = (ml_per_unit * number_of_units)
        st.write("Total solution volume:", total_volume_weight, "ml")

        total_ml_sol = st.number_input("Enter the API concentration (mg/mL):", min_value=0.1, value=0.5, step=0.1, key="total_weight_sol")

        weight_api_un = total_ml_sol * ml_per_unit
        st.write("Total API mass per unit (mg):", weight_api_un, "mg")
    
        batch_weight_API = (total_ml_sol * ml_per_unit * number_of_units)/1000
        st.write("Total API mass per batch:", batch_weight_API, "g")


    elif mode == "Solid Dosage Forms":
        total_weight = st.number_input("Enter the unit weight (mg):", min_value=1, value=500, step=1, key="total_weight")
        total_batch_kg = st.number_input("Enter the number of units:", min_value=1, value=1000, step=1, key="batch_size")
        batch_weight = (total_weight * total_batch_kg)/1000000
        st.write("Batch weight:", batch_weight, "kg")
    elif mode == "Batch Size Calculator":
        mode_calc = st.radio(
        "Calculation",
        ["mg", "% w/w", "mg/ml", "Binder Solution Preparation (% w/w)"])
        if mode_calc == "% w/w":
            total_weight = st.number_input("Enter the unit weight (mg):", min_value=1, value=100, step=1, key="total_weight_percent")
            total_batch_kg = st.number_input("Enter the desired batch weight (kg):", min_value=0.01, value=1.0, step=0.1, key="total_batch_kg")

            def update_formulation():
                changes = st.session_state["formulation_editor"]

                df = st.session_state["formulation"].copy()

                for row_index in sorted(changes["deleted_rows"], reverse=True):
                    df = df.drop(df.index[row_index])

                df = df.reset_index(drop=True)

                for row_index, values in changes["edited_rows"].items():
                    for column, value in values.items():
                        if column in ["Type", "%"] and row_index < len(df):
                            df.loc[row_index, column] = value

                for new_row in changes["added_rows"]:
                    df.loc[len(df)] = {
                        "Type": new_row.get("Type"),
                        "mg": None,
                        "%": new_row.get("%"),
                        "Batch weight": None}

                df["%"] = pd.to_numeric(df  ["%"], errors="coerce")
                df["Batch weight"] = (
                df["%"] * st.session_state["total_batch_kg"] / 100)
                df["mg"] = (df["%"] * st.session_state  ["total_weight_percent"]/100
                )
                st.session_state["formulation"] = df

            if "formulation" not in st.session_state:
                st.session_state["formulation"] = pd.DataFrame(
                    columns=["Type","mg","%","Batch weight"])
                
            edited_formulation = st.data_editor(st.session_state["formulation"],
                on_change=update_formulation,
                key="formulation_editor",
                num_rows="dynamic",
                disabled=["mg", "Batch weight"],
                column_config={ "mg": st.column_config.NumberColumn(
                "mg",
                min_value=0.0,
                step=0.01,
                format="%.2f"),
                "%": st.column_config.  NumberColumn(
                "%",
                min_value=0.0,
                max_value=100.0,
                step=0.01,
                format="%.2f"),
                "Batch weight": st.column_config.NumberColumn(
                "Batch weight",
                min_value=0.0000,
                step=0.0001,
                format="%.4f"),
                "Type": st.column_config.SelectboxColumn(
                "Type",
                options=["API", "Excipient"])})
    
            calc_percent = edited_formulation  ["%"].sum()
            if calc_percent == 0:
                st.info("Enter the formulation components.")
            elif abs(calc_percent - 100) > 0.01:
                st.error("incorect value")
            else:
                st.write("Total %:", calc_percent)
            edited_formulation["Batch weight"] = (edited_formulation["%"] * (total_batch_kg))/100


        elif mode_calc == "mg":
            total_weight = st.number_input("Enter the unit weight (mg):", min_value=1, value=100, step=1, key="total_weight_percent")
            total_batch_kg = st.number_input("Enter the desired batch weight (kg):", min_value=0.01, value=1.0, step=0.1, key="total_batch_kg")

            def update_formulation():
                changes = st.session_state["formulation_editor"]

                df = st.session_state["formulation"].copy()

                for row_index in sorted(changes["deleted_rows"], reverse=True):
                    df = df.drop(df.index[row_index])

                df = df.reset_index(drop=True)

                for row_index, values in changes["edited_rows"].items():
                    for column, value in values.items():
                        if column in ["Type", "mg"] and row_index < len(df):
                            df.loc[row_index, column] = value

                for new_row in changes["added_rows"]:
                    df.loc[len(df)] = {
                        "Type": new_row.get("Type"),
                        "%": None,
                        "mg": new_row.get("mg"),
                        "Batch weight": None}

                df["mg"] = pd.to_numeric(df ["mg"], errors="coerce")

                df["%"] = (
                    (df["mg"] * 100)/st.session_state["total_weight_percent"])
            
                df["Batch weight"] = (
                df["%"] * st.session_state["total_batch_kg"] / 100)
            
                st.session_state["formulation"] = df

            if "formulation" not in st.session_state:
                st.session_state["formulation"] = pd.DataFrame(
                columns=["Type","mg","%","Batch weight"])
            edited_formulation = st.data_editor(st.session_state["formulation"],
            on_change=update_formulation,
            key="formulation_editor",
            num_rows="dynamic",
            disabled=["%", "Batch weight"],
            column_config={ "mg": st.column_config.NumberColumn(
                "mg",
                min_value=0.0,
                step=0.01,
                format="%.2f"),
                "%": st.column_config.NumberColumn(
                "%",
                min_value=0.0,
                max_value=100.0,
                step=0.01,
                format="%.2f"),
                "Batch weight": st.column_config.NumberColumn(
                "Batch weight",
                min_value=0.0000,
                step=0.0001,
                format="%.4f"),
                "Type": st.column_config.SelectboxColumn(
                "Type",
                options=["API", "Excipient"])})
    
            calc_percent = edited_formulation["%"].sum()
            if calc_percent == 0:
                st.info("Enter the formulation components.")
            elif abs(calc_percent - 100) > 0.01:
                st.error("incorect value")
            else:
                st.write("Total %:", calc_percent)

            edited_formulation["Batch weight"] = (edited_formulation["%"] * (total_batch_kg))/100

            calc_mg = edited_formulation["mg"].sum()
            if calc_mg > total_weight:
                st.error("incorect value")
            else:
                st.write("Total mg:", calc_mg)
    
        elif mode_calc == "mg/ml":
            total_volume = st.number_input("Enter the unit volume (ml):", min_value= 0.1, value=1.0, step=0.1, key="total_volume")
            total_batch_l = st.number_input("Enter the desired batch volume (L):", min_value=0.01, value=1.0, step=0.1, key="total_batch_l")

            def update_formulation():
                changes = st.session_state["formulation_editor_ml"]

                df = st.session_state["formulation_ml"].copy()

                for row_index in sorted(changes["deleted_rows"], reverse=True):
                    df = df.drop(df.index[row_index])

                df = df.reset_index(drop=True)

                for row_index, values in changes["edited_rows"].items():
                    for column, value in values.items():
                        if column in ["Type", "mg/ml"] and row_index < len(df):
                            df.loc[row_index, column] = value

                for new_row in changes["added_rows"]:
                    df.loc[len(df)] = {
                        "Type": new_row.get("Type"),
                        "mg/unit": None,
                        "% w/v": None,
                        "mg/ml": new_row.get("mg"),
                        "Batch weight (g)": None}

                df["mg/ml"] = pd.to_numeric(df["mg/ml"], errors="coerce")

                df["mg/unit"] = (df["mg/ml"] * st.session_state["total_volume"])

                df["% w/v"] = (
                (df["mg/ml"] / 10)
            )
                df["Batch weight (g)"] = ( df["mg/ml"] * st.session_state["total_batch_l"])
                st.session_state["formulation_ml"] = df

            if "formulation_ml" not in st.session_state:
                st.session_state["formulation_ml"] = pd.DataFrame(
                columns=["Type","mg/unit", "mg/ml","% w/v","Batch weight (g)"])
            if "mg/unit" not in st.session_state["formulation_ml"].columns:
                st.session_state["formulation_ml"]["mg/unit"] = None

            edited_formulation = st.data_editor(st.session_state["formulation_ml"],
            on_change=update_formulation,
            key="formulation_editor_ml",
            num_rows="dynamic",
            disabled=["mg/unit", "% w/v", "Batch weight (g)"],
            column_config={ "mg/ml": st.    column_config.NumberColumn(
                "mg/ml",
                min_value=0.0,
                step=0.01,
                format="%.2f"
                ),
                "mg/unit": st.column_config.NumberColumn( "mg/unit",
                min_value=0.0,
                step=0.01,
                format="%.2f"),

                "% w/v": st.column_config.NumberColumn(
                "% w/v",
                min_value=0.0,
                max_value=100.0,
                step=0.01,
                format="%.2f"
                ),
                "Batch weight (g)": st.column_config.NumberColumn(
                "Batch weight (g)",
                min_value=0.0000,
                step=0.0001,
                format="%.4f"
                ),
                "Type": st.column_config.SelectboxColumn(
                "Type",
                options=["API", "Excipient"])
                }
            )
    
            calc_percent = edited_formulation["% w/v"].sum()
            if calc_percent == 0:
                st.info("Enter the formulation components.")

            edited_formulation["Batch weight (g)"] = (edited_formulation["mg/ml"] * (total_batch_l))

            edited_formulation["mg/unit"] = (edited_formulation["mg/ml"] * total_volume)

        if mode_calc in ["mg", "% w/w", "mg/ml"]:
            export_formulation = edited_formulation.copy()
        
            if mode_calc == "mg/ml":
                export_formulation = export_formulation.dropna( subset=["mg/ml"], how="all")
                valid_total = not export_formulation.empty
            else:
                export_formulation = export_formulation.dropna( subset=["mg", "%", "Batch weight"], how="all")
            
                valid_total = (
                not export_formulation.empty
                and abs(export_formulation["%"].sum() - 100) <= 0.01)
            
                cvs_data = export_formulation.to_csv(index=False)
        
                st.download_button( label="Download Formulation (CSV)", data=cvs_data, file_name="formulation.csv", mime="text/csv", disabled = not valid_total)
        
                with pd.ExcelWriter(excel_buffer, engine="openpyxl") as writer:
                    export_formulation.to_excel(writer, sheet_name="Formulation", index=False)
        
                st.download_button( label="Download Formulation (excel)",
                data=excel_buffer.getvalue(),
                file_name="formulation.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                disabled = not valid_total)


        if mode_calc == "Binder Solution Preparation (% w/w)":
            concentration = st.number_input("Enter the desired concantration (%) of solution:", min_value=0.001, max_value=100.000, value=None, key="concentration_input", disabled = st.session_state.get("solute_mass_input") is not None)
        
            mass_of_sol= st.number_input("Enter the desired solution mass (g):", min_value=1.0)
        
            solute_mass=st.number_input("Enter the substance mass (g):",min_value=0.01,  value=None, disabled=(concentration is not None), key="solute_mass_input")

            if solute_mass is None and concentration is not None:
                solute_mass= (concentration * mass_of_sol)/100
                st.write(f"Required amount of substance (g): {solute_mass:.3f}")
            elif concentration is None and solute_mass is not None:
                if solute_mass > mass_of_sol:
                    st.error("incorect value")
                else:
                    concentration = (solute_mass * 100)/mass_of_sol
                    st.write(f"Concentraion of solution (%): {concentration:.3f}")
        
            if solute_mass is not None and solute_mass < mass_of_sol:
                solvent_mass = mass_of_sol - solute_mass
                st.write(f"Required amount of solvent (g): {solvent_mass:.3f}")
    
        
    elif mode == "API & Filler Correction":
        total_API_kg = st.number_input("Enter the initial API weight (kg):", min_value=0.01, value=1.0, step=0.1, key="total_API_kg")
        assay = st.number_input( "Assay (%):", min_value=00.01,max_value=115.0, value=90.0)
        moisture = st.number_input(
            "Moisture (%):",
            min_value=0.0,
            max_value=99.99,
            value=1.5)
        assay_corrected = min(assay, 100)
        if assay > 100:
            st.warning("Assay exceeds 100%. The calculation uses 100%.")
        dry_basis = (total_API_kg * 100 * 100)/(assay_corrected * (100 - moisture))
        st.write(f"API mass adjusted to 100% dry basis (kg): {dry_basis:.4f}")
        filler_initial = st.number_input("Enter the initial filler weight (kg):", min_value=0.01, value=1.0, step=0.1, key="filler_initial")
        difference_API = dry_basis - total_API_kg
        filler_mass_adjustment = filler_initial - difference_API
        st.write(f"Adjusted Filler Mass (kg): {filler_mass_adjustment:.4f}")

if mode_anal == 'Data Analysis':
    mode_data = st.radio("Select option",
    ['Descriptive Statistics'])
    if mode_data == "Descriptive Statistics":
        st.info("CSV must contain two header rows")
        uploaded_file = st.file_uploader("Upload experimental data", type = ["csv"])

        analysis_mode = st.radio("Analysis mode", ["Single series", "Maltiple Series", "Relationship Analysis", "Correlation Matrix"])
        if uploaded_file is not None:
            df = pd.read_csv(uploaded_file, sep = ';',  decimal=",", header=[0, 1])
            st.dataframe(df)

            if analysis_mode == "Single series":
                numeric_columns = df.select_dtypes(include="number").columns

                selected_colomn = st.selectbox("Select parameter for analysis", numeric_columns)

                value = df[selected_colomn].to_numpy()
                is_nan = np.isnan(value)  
                valid_val = np.isfinite(value)
                clean_values = value[valid_val]
                total_count = np.size(value)
                valid_count = np.count_nonzero(valid_val)
                invalid_count = total_count - valid_count
                st.write(f"Total count of number: {total_count}")
                st.write(f"Count of invalid number: {invalid_count}")
                if invalid_count > 0:
                    st.warning(f"{invalid_count} observation contains a missing or non-finite value and was excluded from the descriptive calculations.")

                if valid_count == 0:
                    st.error("Statistical calculations are not performed")
                elif valid_count == 1:
                    st.warning("At least two value are required for a sample SD.")
                elif valid_count >= 2:
                    mean_value = np.mean(clean_values)
                    st.write(f"Arithmetic mean value: {mean_value:.3f}")

                    sd_val = np.std(clean_values, ddof=1)
                    st.write(f"Standard Deviation (SD): {sd_val:.3f}")

                    if mean_value != 0:
                        rsd_val = (sd_val / mean_value) * 100
                        st.write(f"RSD: {rsd_val:.2f}%")
                    else:
                        st.warning("RSD cannot be calculated when Mean = 0.")

                    median = np.median(clean_values)
                    min_val = np.min(clean_values)
                    max_val = np.max(clean_values)

                    st.write(f"Median : {median:.2f}")
                    st.write(f"Minimum Value (Min) : {min_val:.2f}")
                    st.write(f"Maximum Value (Max) : {max_val:.2f}")


                    percentile_val = np.percentile(clean_values, [10, 25, 50, 75, 90])
                    percentile_labels = [
                        "P10",
                        "P25 (Q1)",
                        "P50 (Median)",
                        "P75 (Q3)",
                        "P90"
                        ]
                    for label, result in zip(percentile_labels, percentile_val):
                        st.write(f"{label}: {result:.2f}")

                    iqr_val = percentile_val[3] - percentile_val[1]
                    st.write(f"Interquartile Range (IQR): {iqr_val:.2f}")
                    chart_type = st.selectbox("Select chart type", ["Histogram", "Boxplot", "Line plot", "Scatter plot", "Violin Plot"])
                    def create_chart(data, chart_type, axis_label):
                        st.write("Number of measurements:", len(data), "Selected chart:", chart_type )
    
                        if chart_type == "Histogram":
                            fig, ax = plt.subplots()
        
                            ax.hist(data, bins=5, edgecolor="black")
                            mean_value = np.mean(data)
                            median = np.median(data)
                            ax.set_xlabel(axis_label)
                            ax.set_ylabel("Frequency")
                            ax.set_title("Distribution of Experimental Results")

                            ax.axvline(x = mean_value, label = f"Mean: {mean_value:.2f}" , color = "red")
                            ax.axvline(x = median, linestyle = "--", label = f"Median: {median:.2f}", color = "green")
        
                            ax.legend()

                            st.pyplot(fig)

                        elif chart_type == "Boxplot":
                            fig, ax = plt.subplots()
                            ax.boxplot(data)
                            ax.set_title("Distribution of Experimental Results")
                            ax.set_ylabel(axis_label)

                            ax.set_xticks([])

                            show_points = st.checkbox("Show individual data points")

                            if show_points: 
                                apply_jitter = st.checkbox("Apply jitter")
                                x_positions = np.ones(len(data))
                                if apply_jitter:
                                    rng = np.random.default_rng(42)
                                    jitter = rng.uniform(-0.1, 0.1,len(data))
                                    x_positions = x_positions + jitter
                                ax.scatter(x_positions, data)    

                            st.pyplot(fig)

                        elif chart_type == "Line plot":
                            fig, ax = plt.subplots()
                            apply_grid = st.checkbox("Apply grid")
                            if apply_grid:
                                ax.grid(True,  alpha=0.3)
                            st.write("Grid enabled:", apply_grid)

                            x = np.arange(1, len(data) + 1)
                            ax.plot(x, data)
                            
                            ax.set_xlabel("Measurement number")
                            ax.set_ylabel(axis_label)
                            ax.set_title("Experimental Results by Measurement")
                            ax.scatter(x, data)
                            ax.set_xticks(x)

                            st.pyplot(fig)

                        elif chart_type == "Scatter plot":
                            fig, ax = plt.subplots()
                            apply_grid = st.checkbox("Apply grid")
                            if apply_grid:
                                ax.grid(True,  alpha=0.3)
                            st.write("Grid enabled:", apply_grid)

                            x = np.arange(1, len(data) + 1)
                            ax.scatter(x, data)
                            ax.set_xlabel("Measurement number")
                            ax.set_ylabel(axis_label)
                            ax.set_title("Experimental Results by Measurement")
                            ax.set_xticks(x)
                            st.pyplot(fig)

                        elif chart_type == "Violin Plot":
                            fig, ax = plt.subplots()
                            if len(data) < 2 or len(np.unique(data)) < 2:
                                st.warning("Violin Plot requires at least two distinct values.")
                            else:
                                ax.violinplot(data, showmedians=True)
                                ax.set_xticks([])
                                ax.set_ylabel(axis_label)
                                ax.set_title("Distribution of Experimental Results")
                                st.pyplot(fig)

                        png_buffer = BytesIO()
                        fig.savefig(png_buffer, format="png", dpi=300, bbox_inches="tight")
                        png_buffer.seek(0)

                        st.download_button( label="Download Chart (PNG(300 DPI))", data=png_buffer,file_name=f"{axis_label}_{chart_type.replace(' ', '_')}.png",mime="image/png")

                    create_chart(clean_values, chart_type, selected_colomn)


            if analysis_mode == "Maltiple Series":
                parameter = st.selectbox( "Select parameter",
                df.columns.get_level_values(1).unique())

                series_df = df.xs(parameter, axis=1, level=1)

                selected_series = []

                for series_name in series_df.columns:
                    if st.checkbox(series_name, value=True):
                        selected_series.append(series_name)

                if selected_series:
                    series_df = series_df[selected_series]
                else:
                    st.warning("Select at least one series for analysis.")
                    st.stop()

                valid_mask = np.isfinite(series_df)
                clean_df = series_df.where(valid_mask)
                total_count = len(series_df)
                valid_count = clean_df.count()
                invalid_count = total_count - valid_count

                mean_value = clean_df.mean()
                sd_value = clean_df.std()
                rsd_value = (sd_value /mean_value.abs().where(mean_value != 0)) * 100
                median = clean_df.median()
                min_value = clean_df.min()
                max_value = clean_df.max()
                percentile_val = clean_df.quantile([0.10, 0.25, 0.50, 0.75, 0.90])
                iqr_val = percentile_val.loc[0.75] - percentile_val.loc[0.25]

                statistics_df = pd.DataFrame({
                    "Valid observations": valid_count,
                    "Invalid observations": invalid_count,
                    "Mean": mean_value,
                    "Standard Deviation": sd_value,
                    "RSD (%)": rsd_value,
                    "Median": median,
                    "Minimum value": min_value,
                    "Maximum value": max_value,
                    "P10": percentile_val.loc[0.10],
                    "P25": percentile_val.loc[0.25],
                    "P50": percentile_val.loc[0.50],
                    "P75": percentile_val.loc[0.75],
                    "P90": percentile_val.loc[0.90],
                    "IQR": iqr_val
                    })

                statistics_df = statistics_df.T
                st.dataframe(statistics_df)

                excel_buffer = BytesIO()

                with pd.ExcelWriter(excel_buffer, engine = "openpyxl") as writer:
                    statistics_df.to_excel(writer, sheet_name= "Statistical Results", index=True)

                excel_buffer.seek(0)

                st.download_button(label = "Download Statistics (Excel)", data = excel_buffer, file_name = "Statistical_Results.xlsx", mime = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

                chart_type = st.selectbox("Select chart type", ["Boxplot", "Line plot","Violin Plot", "Mean ± SD (Error Bar Plot)"])

                def create_multiple_chart(data, chart_type, parameter):
                    series_values = [ data[col].dropna().to_numpy()for col in data.columns]

                    if chart_type == "Boxplot":
                        fig, ax = plt.subplots()
                        ax.boxplot(series_values)

                        ax.set_xticks(np.arange(1, len(series_values) + 1))

                        ax.set_xticklabels(data.columns)
                        ax.set_ylabel(parameter)

                        show_points = st.checkbox("Show individual data points")

                        if show_points:
                            apply_jitter = st.checkbox("Apply jitter")
                            rng = np.random.default_rng(42)
                            
                            for position, values in enumerate(series_values, start=1):
                                x_positions = np.full(len(values), position)

                                if apply_jitter:
                                    jitter = rng.uniform(-0.1, 0.1, len(values))
                                    
                                    x_positions = x_positions + jitter
                                    
                                ax.scatter(x_positions, values)   
                        st.pyplot(fig)

                    elif chart_type == "Line plot":
                        fig, ax = plt.subplots()
                        apply_grid = st.checkbox("Apply grid")
                        if apply_grid:
                            ax.grid(True,  alpha=0.3)
                        st.write("Grid enabled:", apply_grid)


                        for series_name in series_df.columns:
                            ax.plot(np.arange(1, len(data) + 1),data[series_name], label=series_name )
                            ax.legend()
                            ax.set_xticks(np.arange(1, len(data) + 1))

                        st.pyplot(fig)
                        
                    elif chart_type == "Violin Plot":
                        fig, ax = plt.subplots()
                        ax.violinplot(series_values, showmedians=True)

                        for values in series_values:
                            if len(values) < 2 or len(np.unique(values)) < 2:
                                st.warning("Violin Plot requires at least two distinct values.")
                        ax.set_xticks(np.arange(1, len(series_values) + 1))
                        ax.set_xticklabels(data.columns)
                        ax.set_ylabel(parameter)

                        st.pyplot(fig)

                    elif chart_type == "Mean ± SD (Error Bar Plot)":
                        fig, ax = plt.subplots()

                        ax.errorbar(np.arange(1, len(series_values) + 1), mean_value, sd_value, fmt="o", capsize=5)

                        ax.set_xticks(np.arange(1, len(series_values) + 1))
                        ax.set_xticklabels(data.columns)
                        
                        show_points = st.checkbox("Show individual data points")

                        if show_points:
                            apply_jitter = st.checkbox("Apply jitter")
                            rng = np.random.default_rng(42)
                            
                            for position, values in enumerate(series_values, start=1):
                                x_positions = np.full(len(values), position)

                                if apply_jitter:
                                    jitter = rng.uniform(-0.1, 0.1, len(values))
                                    
                                    x_positions = x_positions + jitter
                                    
                                ax.scatter(x_positions, values) 



                        st.pyplot(fig)
               
                    png_buffer = BytesIO()
                    fig.savefig(png_buffer, format="png", dpi=300, bbox_inches="tight")
                    png_buffer.seek(0)
                    
                    st.download_button( label="Download Chart (PNG (300 DPI))", data=png_buffer,file_name=f"{parameter}_{chart_type.replace(' ', '_')}.png", mime="image/png")

            
                create_multiple_chart(clean_df, chart_type, parameter)

            elif analysis_mode == "Relationship Analysis":
                numeric_columns = df.select_dtypes(include="number").columns

                selected_colomn_x = st.selectbox("Select X-axis parameter", numeric_columns)

                selected_colomn_y = st.selectbox("Select Y-axis parameter", numeric_columns)

                clean_df = df.dropna(subset=[selected_colomn_x, selected_colomn_y ])

                valid_mask = np.isfinite(clean_df[[selected_colomn_x, selected_colomn_y]]).all(axis=1)

                clean_values = clean_df[valid_mask]

                if selected_colomn_x == selected_colomn_y:
                    st.warning("Please select two different parameters.")
                elif clean_values.empty:
                    st.warning("No valid data available for analysis.")
                else:
                    relationship_analysis_mode = st.radio("Select analysis method", ["Scatter Plot", "Line Plot"])

                    fig, ax = plt.subplots()

                    y = clean_values[selected_colomn_y]

                    x = clean_values[selected_colomn_x]

                    if len(x) < 2 or x.nunique() < 2 or y.nunique() < 2:
                        st.warning("Insufficient variability for correlation analysis.")

                    else:
                        pearson_result = pearsonr(x, y)
                        pearson_p = pearson_result.pvalue

                        spearman_result = spearmanr(x ,y)

                        spearman_p = spearman_result.pvalue

                        pearson_r = pearson_result.statistic

                        pearson_p = pearson_result.pvalue

                        spearman_r = spearman_result.statistic
                        spearman_p = spearman_result.pvalue

                        n_observations = len(clean_values)

                        st.write("Number of paired observations:", n_observations)

                        col1, col2 = st.columns(2)
                        with col1:
                            st.metric(label="Pearson correlation (r)", value=f"{pearson_r:.3f}")
                            st.metric(label="p-value", value=f"{pearson_p:.2e}")


                        with col2:
                            st.metric(label="Spearman correlation (ρ)", value=f"{spearman_r:.3f}")
                            st.metric(label="p-value", value=f"{spearman_p:.2e}")

                        with st.expander("How to interpret correlation results?"):
                            st.markdown("""
                            **Pearson correlation (r):** Measures the strength and direction of a linear relationship.

                            **Spearman correlation (ρ):** Measures the strength and direction of a monotonic relationship.

                            **p-value:** Indicates statistical significance
                            under the null hypothesis of no correlation.

                            **N:** Number of paired observations.""")

                        def create_correlation_scale(pearson_r, spearman_r):
                            fig, ax = plt.subplots(figsize=(10, 2.5))

                            ax.set_xlim(-1.1, 1.1)
                            ax.set_ylim(-1, 1)

                            ax.axvspan(-1.1, -0.7, color="lightcoral", alpha=0.3)
                            ax.axvspan(-0.7, -0.3,color = "peachpuff", alpha=0.3)
                            ax.axvspan(-0.3, 0.3, color = "lightyellow", alpha=0.3)
                            ax.axvspan(0.3, 0.7, color = "lightgreen", alpha=0.3)
                            ax.axvspan(0.7, 1.1, color="lightblue", alpha=0.3)

                            ax.hlines(y=0, xmin=-1, xmax=1)

                            ax.axvline(0, linestyle="--")

                            ax.scatter(pearson_r, 0.3, s=120, label=f"Pearson r = {pearson_r:.3f}")
                            ax.scatter(spearman_r, -0.3, s=120, label=f"Spearman ρ = {spearman_r:.3f}")

                            ax.text(-0.85, 0.7, "Strong\nnegative", ha="center", fontsize=8)
                            ax.text(-0.5, 0.7, "Moderate\nnegative", ha="center", fontsize=8)
                            ax.text(0, 0.7, "Weak / near zero", ha="center", fontsize=8)
                            ax.text(0.5, 0.7, "Moderate\npositive", ha="center", fontsize=8)
                            ax.text(0.85, 0.7, "Strong\npositive", ha="center", fontsize=8)

                            ax.set_xticks([-1, -0.5, 0, 0.5, 1])
                            ax.set_yticks([])

                            ax.spines["left"].set_visible(False)
                            ax.spines["right"].set_visible(False)
                            ax.spines["top"].set_visible(False)
                            ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.15), ncol=2)
                            ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.15), ncol=2)

                            return fig


                        fig_scale = create_correlation_scale(pearson_r, spearman_r)
                        st.pyplot(fig_scale)  


                    if relationship_analysis_mode == "Scatter Plot":
                        ax.scatter(x, y)

                        ax.set_xticks(x)
                        
                    elif relationship_analysis_mode == "Line Plot":

                        sorted_df = clean_values.sort_values(by= selected_colomn_x)

                        x_sorted = sorted_df[selected_colomn_x]

                        y_sorted = sorted_df[selected_colomn_y]

                        ax.plot(x_sorted, y_sorted, marker="o")

                        ax.set_xticks(x_sorted)

                    
                    ax.set_xlabel(f"{selected_colomn_x}")

                    ax.set_ylabel(f"{selected_colomn_y}")

                    apply_grid = st.checkbox("Apply grid")

                    if apply_grid:
                        ax.grid(True,  alpha=0.3)

                    st.pyplot(fig)

            if analysis_mode == "Correlation Matrix":
                select_param = df.select_dtypes(include="number")
                selected_params = st.multiselect( "Select parameters for correlation", options=select_param.columns)
                if len(selected_params) < 2:
                    st.warning("Select at least two parameters")
                else:
                    correlation_data = df[selected_params]
                    data_after_cor = correlation_data.corr(method="pearson")
                    st.dataframe(data_after_cor)
                    fig, ax = plt.subplots(figsize=(8, 6))
                    
                    sns.heatmap( data_after_cor, annot=True, fmt=".3f", cmap="coolwarm",vmin=-1, vmax=1, center=0, ax=ax)
                    ax.set_xlabel("")
                    ax.set_ylabel("")
                    labels = data_after_cor.columns.get_level_values(1)
                    ax.set_xticklabels(labels, rotation=45, ha="right")
                    ax.set_yticklabels(labels, rotation=0)

                    st.pyplot(fig)
                    











                    


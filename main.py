import streamlit as st
import pandas as pd

from io import BytesIO
excel_buffer = BytesIO()


st.title("Formulation Calculator")
mode = st.radio(
    "Calculation mode",
    ["Liquid Dosage Forms", "Solid Dosage Forms", "Batch Size Calculator", "API & Filler Correction"]
)
if mode == "Liquid Dosage Forms":
    ml_per_unit = st.number_input("Enter the fill volume per unit (ml):", min_value=0.1, value=1.0, step=0.01, key="ml_per_unit")
    number_of_units = st.number_input("Enter the number of units:", min_value= 1.0, value=100.0, step= 1.0, key="number_of_units")
    total_volume_weight = (ml_per_unit * number_of_units)/1000
    st.write("Total solution volume:", total_volume_weight, "L")

    total_ml_sol = st.number_input("Enter the API concentration (mg/mL):", min_value=0.1, value=0.5, step=0.1, key="total_weight_sol")
    batch_weight_API = (total_ml_sol * ml_per_unit * number_of_units)/1000
    st.write("Total API mass per unit:", batch_weight_API, "g")


elif mode == "Solid Dosage Forms":
    total_weight = st.number_input("Enter the unit weight (mg):", min_value=1, value=500, step=1, key="total_weight")
    total_batch_kg = st.number_input("Enter the number of units:", min_value=1, value=1000, step=1, key="batch_size")
    batch_weight = (total_weight * total_batch_kg)/1000000
    st.write("Batch weight:", batch_weight, "kg")
elif mode == "Batch Size Calculator":
    mode_calc = st.radio(
    "Calculation",
    ["mg", "% w/w", "mg/ml"])
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
                    "Batch weight": None
                }

            df["%"] = pd.to_numeric(df["%"], errors="coerce")
            df["Batch weight"] = (
            df["%"] * st.session_state["total_batch_kg"] / 100
            )
            df["mg"] = (
                df["%"] * st.session_state["total_weight_percent"]/100
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
                format="%.2f"
            ),
            "%": st.column_config.NumberColumn(
                "%",
                min_value=0.0,
                max_value=100.0,
                step=0.01,
                format="%.2f"
            ),
            "Batch weight": st.column_config.NumberColumn(
                "Batch weight",
                min_value=0.0000,
                step=0.0001,
                format="%.4f"
            ),
            "Type": st.column_config.SelectboxColumn(
                "Type",
                options=["API", "Excipient"])
            }
        )
    
        calc_percent = edited_formulation["%"].sum()
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
                    "Batch weight": None
                }

            df["mg"] = pd.to_numeric(df["mg"], errors="coerce")

            df["%"] = (
                (df["mg"] * 100)/st.session_state["total_weight_percent"]
            )
            df["Batch weight"] = (
            df["%"] * st.session_state["total_batch_kg"] / 100
            )
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
                format="%.2f"
            ),
            "%": st.column_config.NumberColumn(
                "%",
                min_value=0.0,
                max_value=100.0,
                step=0.01,
                format="%.2f"
            ),
            "Batch weight": st.column_config.NumberColumn(
                "Batch weight",
                min_value=0.0000,
                step=0.0001,
                format="%.4f"
            ),
            "Type": st.column_config.SelectboxColumn(
                "Type",
                options=["API", "Excipient"])
            }
        )
    
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
                    "Batch weight (g)": None
                }

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
        column_config={ "mg/ml": st.column_config.NumberColumn(
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

    export_formulation = edited_formulation.copy()
    if mode_calc == "mg/ml":
        export_formulation = export_formulation.dropna(
        subset=["mg/ml"],
        how="all")
        valid_total = not export_formulation.empty
    else:
        export_formulation = export_formulation.dropna( subset=["mg", "%", "Batch weight"], how="all")
        valid_total = (
            not export_formulation.empty
            and abs(export_formulation["%"].sum() - 100) <= 0.01)
    
    cvs_data = export_formulation.to_csv(index=False)

    st.download_button(
    label="Download Formulation (CSV)",
    data=cvs_data,
    file_name="formulation.csv",
    mime="text/csv",
    disabled = not valid_total
)
    with pd.ExcelWriter(excel_buffer, engine="openpyxl") as writer:
        export_formulation.to_excel(writer, sheet_name="Formulation", index=False)

    st.download_button(
        label="Download Formulation (excel)",
        data=excel_buffer.getvalue(),
        file_name="formulation.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        disabled = not valid_total)

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


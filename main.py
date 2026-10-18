import streamlit as st
import pandas as pd
st.title("Formulation Calculator")
mode = st.radio(
    "Calculation mode",
    ["Manual", "Automatic"]
)
if mode == "Manual":
    total_weight = st.number_input("Enter the unit weight (mg):", min_value=1, value=500, step=1, key="total_weight")
    total_batch_kg = st.number_input("Enter the number of units:", min_value=1, value=1000, step=1, key="batch_size")
    batch_weight = (total_weight * total_batch_kg)/1000000
    st.write("Batch weight:", batch_weight, "kg")
else:
    mode_calc = st.radio(
    "Calculation",
    ["mg", "%"])
    if mode_calc == "%":
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
        if calc_percent > 100.00:
             st.error("incorect value")
        else:
            st.write("Total %:", calc_percent)
        edited_formulation["Batch weight"] = (edited_formulation["%"] * (total_batch_kg))/100


    else:
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
        if calc_percent > 100.00:
             st.error("incorect value")
        else:
            st.write("Total %:", calc_percent)
        edited_formulation["Batch weight"] = (edited_formulation["%"] * (total_batch_kg))/100

        calc_mg = edited_formulation["mg"].sum()
        if calc_mg > total_weight:
             st.error("incorect value")
        else:
            st.write("Total mg:", calc_mg)

       


import streamlit as st
import pandas as pd
import random

# -----------------------------
# App Title & Instructions
# -----------------------------
st.title("🎯 Student Performance Segmentation & Mixed-Ability Grouping Tool")

st.markdown("""
📌 **Instructions for Uploading File**
1. Prepare an Excel/CSV file with the following columns:  
   - **ID** (e.g., `L24-8928`)  
   - **Name** (Student name)  
   - **Score** (Numerical marks)  
2. Upload the file using the uploader below.  
3. The tool will:  
   - Categorize students into performance bands.  
   - Form **balanced mixed-ability groups** automatically.  
""")

# -----------------------------
# File Upload
# -----------------------------
uploaded_file = st.file_uploader("📂 Upload Excel/CSV file", type=["xlsx", "csv"])

if uploaded_file is not None:
    # Read file
    if uploaded_file.name.endswith(".xlsx"):
        df = pd.read_excel(uploaded_file)
    else:
        df = pd.read_csv(uploaded_file)

    # Validate file
    expected_cols = ["ID", "Name", "Score"]
    if not all(col in df.columns for col in expected_cols):
        st.error(f"❌ The file must contain columns: {expected_cols}")
    else:
        # -----------------------------
        # Categorization
        # -----------------------------
        def categorize(score):
            if score < 40:
                return "Minimal"
            elif score < 60:
                return "Needs Improvement"
            elif score < 70:
                return "Satisfactory"
            elif score < 85:
                return "Good"
            else:
                return "Excellent"

        df["Category"] = df["Score"].apply(categorize)

        # Assign color for categories
        color_map = {
            "Minimal": "red",
            "Needs Improvement": "orange",
            "Satisfactory": "yellow",
            "Good": "blue",
            "Excellent": "green"
        }
        df["Color"] = df["Category"].map(color_map)

        # -----------------------------
        # Show Segmentation Table
        # -----------------------------
        st.subheader("📊 Student Performance Segmentation")

        def highlight_row(row):
            return [f"background-color: {row['Color']}; text-align: center;"] * len(row)

        styled_df = (
            df.style.apply(highlight_row, axis=1)
            .set_properties(**{"text-align": "center"})
            .set_table_styles([
                {"selector": "th", "props": [("font-weight", "bold"), ("color", "black"), ("text-align", "center")]}
            ])
        )
        st.dataframe(styled_df, use_container_width=True)

        # -----------------------------
        # Mixed-Ability Grouping
        # -----------------------------
        st.subheader("👥 Mixed-Ability Groups")

        # Separate students by category
        grouped = {cat: df[df["Category"] == cat].copy() for cat in df["Category"].unique()}

        # Decide number of groups = max category size
        num_groups = max(len(v) for v in grouped.values())

        groups = [[] for _ in range(num_groups)]

        # Distribute students category-wise into groups
        for cat, students in grouped.items():
            students_list = students.to_dict("records")
            random.shuffle(students_list)
            for i, student in enumerate(students_list):
                groups[i % num_groups].append(student)

        # Convert groups to DataFrame
        groups_data = []
        for i, group in enumerate(groups, 1):
            for student in group:
                groups_data.append({
                    "Group": f"Group {i}",
                    "ID": student["ID"],
                    "Name": student["Name"],
                    "Score": student["Score"],
                    "Category": student["Category"],
                    "Color": student["Color"]
                })

        groups_df = pd.DataFrame(groups_data)

        def highlight_group_row(row):
            return [f"background-color: {row['Color']}; text-align: center;"] * len(row)

        styled_groups_df = (
            groups_df.drop(columns=["Color"])  # no color column here
            .style.apply(highlight_group_row, axis=1)
            .set_properties(**{"text-align": "center"})
            .set_table_styles([
                {"selector": "th", "props": [("font-weight", "bold"), ("color", "black"), ("text-align", "center")]}
            ])
        )

        st.dataframe(styled_groups_df, use_container_width=True)

else:
    st.info("ℹ️ Please upload a file to begin.")

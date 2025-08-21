import streamlit as st
import pandas as pd

st.title("Student Assessment & Mixed Ability Grouping Tool")

# ---- Instructions ----
st.info(
    """
    📌 **Instructions for Uploading File**  
    - Upload an **Excel (.xlsx)** file only.  
    - The file must contain the following columns (in order):  
      1. **ID** → Student ID (e.g., L24-8928)  
      2. **Name** → Student’s Full Name  
      3. **Score** → Marks between **0 and 100**  
    - Example row: `L24-8928 | Ali Khan | 72`  
    """
)

# ---- File Upload ----
uploaded_file = st.file_uploader("Upload Excel file with Student Data", type=["xlsx"])

if uploaded_file:
    # Read Excel file
    df = pd.read_excel(uploaded_file)

    # Ensure correct columns exist
    expected_cols = ["ID", "Name", "Score"]
    if not all(col in df.columns for col in expected_cols):
        st.error(f"Excel must have columns: {expected_cols}")
    else:
        # ---- Step 1: Validate Scores ----
        df = df[(df["Score"] >= 0) & (df["Score"] <= 100)]

        # ---- Step 2: Assign Segments & Colors ----
        def get_segment(score):
            if score <= 20:
                return "Minimal", "Red"
            elif score <= 40:
                return "Needs Improvement", "Orange"
            elif score <= 60:
                return "Developing", "Yellow"
            elif score <= 80:
                return "Proficient", "Blue"
            else:
                return "Exemplary", "Green"

        df[["Segment", "Color"]] = df["Score"].apply(lambda x: pd.Series(get_segment(x)))

        # ---- Table 1: Segmentation with Darker Colors ----
        def highlight_row(row):
            color_map = {
                "Red": "background-color: #ff4d4d; color: black; text-align: center;",
                "Orange": "background-color: #ffa64d; color: black; text-align: center;",
                "Yellow": "background-color: #ffff66; color: black; text-align: center;",
                "Blue": "background-color: #4da6ff; color: black; text-align: center;",
                "Green": "background-color: #70db70; color: black; text-align: center;",
            }
            return [color_map.get(row["Color"], "text-align: center;")] * len(row)

        styled_df = (
            df.style
            .apply(highlight_row, axis=1)
            .set_properties(**{"text-align": "center"})
            .set_table_styles([
                {"selector": "th", "props": [("font-weight", "bold"), ("color", "black"), ("text-align", "center")]}
            ])
        )

        st.subheader("📊 Student Segmentation by Score")
        st.dataframe(styled_df, use_container_width=True)

        # ---- Step 3: Create Mixed Ability Groups ----
        groups = []
        grouped = {color: df[df["Color"] == color].values.tolist() for color in df["Color"].unique()}

        group_num = 1
        while any(grouped.values()):
            group = []
            for color in ["Red", "Orange", "Yellow", "Blue", "Green"]:
                if grouped.get(color) and len(grouped[color]) > 0:
                    group.append(grouped[color].pop(0))
            if group:
                for student in group:
                    groups.append([f"Group {group_num}"] + student)
                group_num += 1

        groups_df = pd.DataFrame(groups, columns=["Group", "ID", "Name", "Score", "Segment", "Color"])

        # ---- Table 2: Groups with Full Row Colors (better look) ----
        def highlight_group_row(row):
            color_map = {
                "Red": "background-color: #ff9999; color: black; text-align: center;",
                "Orange": "background-color: #ffcc99; color: black; text-align: center;",
                "Yellow": "background-color: #ffffb3; color: black; text-align: center;",
                "Blue": "background-color: #99ccff; color: black; text-align: center;",
                "Green": "background-color: #b3ffb3; color: black; text-align: center;",
            }
            return [color_map.get(row["Color"], "text-align: center;")] * len(row)

        styled_groups_df = (
            groups_df.drop(columns=["Color"])  # don't show color name
            .style
            .apply(highlight_group_row, axis=1)
            .set_properties(**{"text-align": "center"})
            .set_table_styles([
                {"selector": "th", "props": [("font-weight", "bold"), ("color", "black"), ("text-align", "center")]}
            ])
        )

        st.subheader("👥 Mixed Ability Groups")
        st.dataframe(styled_groups_df, use_container_width=True)

        # ---- Download Option ----
        output_excel = "student_groups.xlsx"
        groups_df.to_excel(output_excel, index=False)

        with open(output_excel, "rb") as f:
            st.download_button("📥 Download Groups Excel", f, file_name="student_groups.xlsx")

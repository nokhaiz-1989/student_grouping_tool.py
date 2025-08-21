import streamlit as st
import pandas as pd
import random

# App title
st.title("🎯 Student Grouping Tool")

# Instructions
st.markdown("""
**Instructions:**  
1. Upload an Excel file containing student records.  
2. The file should have the following columns:  
   - **ID** (e.g., L24-8928)  
   - **Name** (student name)  
   - **Score** (numeric score)  
3. The system will group students into mixed-ability groups and show results in two tables.  
""")

# File upload
uploaded_file = st.file_uploader("📂 Upload your Excel file", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)

    # Define colors (dark shades for first table, lighter for groups)
    colors = ["red", "blue", "green", "yellow", "orange"]
    color_map = {
        "red": "background-color: #ff4d4d; text-align: center;",
        "blue": "background-color: #4da6ff; text-align: center;",
        "green": "background-color: #5cd65c; text-align: center;",
        "yellow": "background-color: #ffff66; text-align: center;",
        "orange": "background-color: #ffb84d; text-align: center;",
    }

    # Assign colors and groups
    df["Color"] = [random.choice(colors) for _ in range(len(df))]
    num_groups = len(df) // 5 + 1
    df["Group"] = ["Group " + str(i+1) for i in range(len(df))]

    # Table 1: Students with Colors
    def highlight_color_row(row):
        return [color_map.get(row["Color"], "text-align: center;")] * len(row)

    styled_df = df.style.apply(highlight_color_row, axis=1)\
                        .set_properties(**{"text-align": "center"})\
                        .set_table_styles([{"selector": "th", "props": [("font-weight", "bold")]}])

    st.subheader("📋 Student List with Assigned Colors")
    st.dataframe(styled_df, use_container_width=True)

    # Table 2: Groups (without color column, but rows are colored)
    groups_df = df[["Group", df.columns[0], "Name", "Score"]]  # keep Group, ID, Name, Score

    def highlight_group_row(row):
        return [color_map.get(df.loc[row.name, "Color"], "text-align: center;")] * len(row)

    styled_groups_df = groups_df.style.apply(highlight_group_row, axis=1)\
                                      .set_properties(**{"text-align": "center"})\
                                      .set_table_styles([{"selector": "th", "props": [("font-weight", "bold")]}])

    st.subheader("👥 Mixed-Ability Groups")
    st.dataframe(styled_groups_df, use_container_width=True)

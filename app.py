import streamlit as st
import pandas as pd
import random

# Title
st.title("📊 Student Grouping Tool")
st.write("""
Upload an Excel file with three columns:
1. **ID** (e.g., L24-8928)  
2. **Name** (Student name)  
3. **Score** (0–100)  

The tool will:
- Classify students into categories (Minimal, Needs Improvement, Developing, Proficient, Exemplary).  
- Color-code results.  
- Form mixed-ability groups with one student from each category.  
""")

# File upload
uploaded_file = st.file_uploader("📂 Upload your Excel file", type=["xlsx"])

# Category assignment function
def assign_category(score):
    if score <= 20:
        return "Minimal", "red"
    elif score <= 40:
        return "Needs Improvement", "orange"
    elif score <= 60:
        return "Developing", "yellow"
    elif score <= 80:
        return "Proficient", "blue"
    else:
        return "Exemplary", "green"

# Styling function for DataFrame
def highlight_rows(row):
    return [f"background-color: {row['Color']}; text-align: center;"] * len(row)

if uploaded_file:
    # Read file
    df = pd.read_excel(uploaded_file)

    # Ensure proper columns
    df.columns = ["ID", "Name", "Score"]

    # Assign categories & colors
    df[["Category", "Color"]] = df["Score"].apply(lambda x: pd.Series(assign_category(x)))

    # ===== First Table: Classification =====
    st.subheader("📌 Classification by Score")
    styled_df = df.style.apply(highlight_rows, axis=1)\
                        .set_properties(**{"text-align": "center"})\
                        .set_table_styles([{"selector": "th", "props": [("font-weight", "bold"), ("text-align", "center")]}])
    st.dataframe(styled_df, use_container_width=True)

    # ===== Second Table: Mixed Ability Groups =====
    st.subheader("👥 Mixed Ability Groups")

    # Shuffle within categories
    categories = df["Category"].unique()
    grouped_students = {cat: df[df["Category"] == cat].sample(frac=1).reset_index(drop=True) for cat in categories}

    # Minimum group count possible
    min_count = min(len(studs) for studs in grouped_students.values())
    groups = []

    for i in range(min_count):
        group = []
        for cat, studs in grouped_students.items():
            group.append(studs.iloc[i])
        groups.append(pd.DataFrame(group))

    groups_df = pd.concat(groups, keys=[f"Group {i+1}" for i in range(len(groups))]).reset_index(level=1, drop=True)
    groups_df = groups_df.reset_index().rename(columns={"index": "Group"})

    # Keep group colors for highlighting
    styled_groups_df = groups_df.style.apply(lambda row: [f"background-color: {row['Color']}; text-align: center;"] * len(row), axis=1)\
                                      .set_properties(**{"text-align": "center"})\
                                      .set_table_styles([{"selector": "th", "props": [("font-weight", "bold"), ("text-align", "center")]}])

    st.dataframe(styled_groups_df, use_container_width=True)

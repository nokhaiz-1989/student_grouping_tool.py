import streamlit as st
import pandas as pd
import random

st.set_page_config(page_title="Student Grouping Tool", layout="wide")

st.title("🎓 Student Grouping Tool")
st.write("""
Upload an Excel file with the following format:

- **First column:** Student ID (e.g., L24-8928)  
- **Second column:** Student Name  
- **Third column:** Score (numeric)  

The app will:  
1. Segment students into categories (Excellent, Good, Needs Improvement, Minimal).  
2. Form **mixed-ability groups** (each group will try to have one student from each category).  
3. Display results in styled tables.  
""")

# File uploader
uploaded_file = st.file_uploader("📂 Upload Excel File", type=["xlsx"])

if uploaded_file:
    # Read the file
    df = pd.read_excel(uploaded_file)

    # Ensure columns are correct
    df.columns = ["Student ID", "Name", "Score"]

    # Define categories and their colors
    categories = {
        "Excellent": "green",
        "Good": "blue",
        "Needs Improvement": "orange",
        "Minimal": "red"
    }

    def assign_category(score):
        if score >= 85:
            return "Excellent"
        elif score >= 70:
            return "Good"
        elif score >= 50:
            return "Needs Improvement"
        else:
            return "Minimal"

    # Assign categories
    df["Category"] = df["Score"].apply(assign_category)

    # --- Table 1: Segmentation ---
    st.subheader("📊 Student Segmentation")

    def highlight_row(row):
        color = categories[row["Category"]]
        return [f"background-color: {color}; text-align: center;"] * len(row)

    styled_df = (
        df.style
        .apply(highlight_row, axis=1)
        .set_properties(**{"text-align": "center"})
        .set_table_styles([
            {"selector": "th", "props": [("font-weight", "bold"),
                                         ("color", "black"),
                                         ("text-align", "center")]}
        ])
    )
    st.dataframe(styled_df, use_container_width=True)

    # --- Table 2: Mixed-Ability Groups ---
    st.subheader("👥 Mixed-Ability Groups")

    # Separate by category
    cat_dfs = {cat: df[df["Category"] == cat].copy() for cat in categories.keys()}
    max_len = max(len(c) for c in cat_dfs.values())

    # Shuffle each category
    for cat in cat_dfs:
        cat_dfs[cat] = cat_dfs[cat].sample(frac=1).reset_index(drop=True)

    groups = []
    for i in range(max_len):
        group = {"Group": f"Group {i+1}"}
        for cat, cat_df in cat_dfs.items():
            if i < len(cat_df):
                student = cat_df.iloc[i]
                group[cat] = f"{student['Student ID']} - {student['Name']}"
        groups.append(group)

    groups_df = pd.DataFrame(groups)

    # Styling for groups table
    def highlight_group_row(row):
        styles = []
        for col in row.index:
            if col in categories:
                styles.append(f"background-color: {categories[col]}; text-align: center;")
            else:
                styles.append("text-align: center;")
        return styles

    styled_groups_df = (
        groups_df.style
        .apply(highlight_group_row, axis=1)
        .set_properties(**{"text-align": "center"})
        .set_table_styles([
            {"selector": "th", "props": [("font-weight", "bold"),
                                         ("color", "black"),
                                         ("text-align", "center")]}
        ])
    )
    st.dataframe(styled_groups_df, use_container_width=True)

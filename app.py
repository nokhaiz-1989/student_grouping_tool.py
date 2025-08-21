import streamlit as st
import pandas as pd
import random

# Function to categorize students
def categorize(score):
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

# Streamlit UI
st.title("🎓 Student Grouping Tool")
st.write("Upload an Excel file with columns: **Student ID | Name | Score**. "
         "The system will categorize students and create groups of 5 students each.")

# File uploader
uploaded_file = st.file_uploader("Upload Excel file", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)

    # Categorize students
    df[["Category", "Color"]] = df["Score"].apply(lambda x: pd.Series(categorize(x)))

    # Show categorized students table
    st.subheader("📊 Categorized Students")
    st.dataframe(df.style.set_properties(**{
        "text-align": "center"
    }).set_table_styles([{
        "selector": "th",
        "props": [("font-weight", "bold"), ("text-align", "center")]
    }]).apply(lambda x: [f"background-color: {c}" for c in df["Color"]], axis=0))

    # Create groups of 5 students ensuring mix
    st.subheader("👥 Mixed-Ability Groups (5 Students Each)")

    categories = df["Category"].unique()
    grouped_students = {cat: df[df["Category"] == cat].to_dict("records") for cat in categories}

    groups = []
    group_number = 1
    while any(grouped_students.values()):
        group = []
        for cat in categories:
            if grouped_students[cat]:
                group.append(grouped_students[cat].pop(0))
            if len(group) == 5:
                break
        if group:
            groups.append((f"Group {group_number}", group))
            group_number += 1

    # Display groups
    for group_name, members in groups:
        st.markdown(f"### {group_name}")
        group_df = pd.DataFrame(members)[["Student ID", "Name", "Score", "Category"]]
        st.dataframe(group_df.style.set_properties(**{
            "text-align": "center"
        }).set_table_styles([{
            "selector": "th",
            "props": [("font-weight", "bold"), ("text-align", "center")]
        }]).apply(lambda x: [f"background-color: {c}" for c in group_df["Category"].map({
            "Minimal": "red",
            "Needs Improvement": "orange",
            "Developing": "yellow",
            "Proficient": "blue",
            "Exemplary": "green"
        })], axis=0))
        st.markdown("---")

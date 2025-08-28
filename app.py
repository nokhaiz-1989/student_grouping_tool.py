import streamlit as st
import pandas as pd
import random

st.set_page_config(page_title="Student Grouping Tool", layout="wide")

# -------------------------------
# Instructions for the interface
# -------------------------------
st.title("🎓 Student Grouping Tool")
st.markdown("""
Welcome to the **Student Grouping Tool**!  
Please follow the steps below to get started:

1. 📂 **Upload an Excel file** containing student details with the following columns:
   - `Student ID`
   - `Name`
   - `Score` (0–100)

2. 📝 The system will automatically categorize students into:
   - 🔴 Minimal  
   - 🟠 Needs Improvement  
   - 🟡 Developing  
   - 🔵 Proficient  
   - 🟢 Exemplary  

3. 👥 The tool will form **mixed-ability groups** of **5 students each**, ensuring fair distribution.
""")

# -------------------------------
# File upload
# -------------------------------
uploaded_file = st.file_uploader("📥 Upload your Excel file", type=["xlsx"])

# Category & color assignment
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

if uploaded_file:
    df = pd.read_excel(uploaded_file)

    # Categorize students
    df[["Category", "Color"]] = df["Score"].apply(lambda s: pd.Series(categorize(s)))

    st.subheader("📊 Uploaded Student Data with Categories")
    styled_df = df.style.apply(lambda _: [f"background-color: {c}; text-align:center;" for c in df["Color"]], axis=0)
    st.dataframe(styled_df, use_container_width=True)

    # -------------------------------
    # Create Mixed Ability Groups (Balanced of 5 Students, 1 from each Category if possible)
    # -------------------------------
    st.subheader("👥 Mixed Ability Groups")

    group_size = 5  # since 5 categories
    groups = []

    # Split by category
    categories = df["Category"].unique()
    category_groups = {
        cat: df[df["Category"] == cat].sort_values(by="Score", ascending=False).to_dict("records")
        for cat in categories
    }

    # Find max groups possible
    max_groups = max(len(students) for students in category_groups.values())

    # Build groups round-robin: try to take one student from each category
    for i in range(max_groups):
        group_members = []
        for cat in categories:
            if i < len(category_groups[cat]):
                group_members.append(category_groups[cat][i])  # already dict now
        # If group not complete, fill with closest-score students from remaining pool
        if len(group_members) < group_size:
            used_ids = [m["Student ID"] for m in group_members]
            remaining = df[~df["Student ID"].isin(used_ids)].sort_values(by="Score", ascending=False)
            if not remaining.empty:
                needed = group_size - len(group_members)
                extra = remaining.iloc[:needed].to_dict("records")
                group_members.extend(extra)
        groups.append((f"Group {len(groups)+1}", pd.DataFrame(group_members)))

    # Display groups
    color_map = {
        "Minimal": "red",
        "Needs Improvement": "orange",
        "Developing": "yellow",
        "Proficient": "blue",
        "Exemplary": "green"
    }

    for group_name, group_df in groups:
        st.markdown(f"### {group_name}")

        expected_cols = ["Student ID", "Name", "Score", "Category"]
        available_cols = [col for col in expected_cols if col in group_df.columns]
        group_df = group_df[available_cols]

        if "Category" in group_df.columns:
            styled_group = group_df.style.apply(
                lambda x: [
                    f"background-color: {color_map.get(v, 'white')}; text-align:center;"
                    if x.name == "Category" else "" for v in x
                ],
                axis=0
            )
        else:
            styled_group = group_df.style

        st.dataframe(styled_group, use_container_width=True)
        st.markdown("---")  # adds gap between groups

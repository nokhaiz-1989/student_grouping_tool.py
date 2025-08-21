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
    # Create Mixed Ability Groups (Balanced)
    # -------------------------------
    st.subheader("👥 Mixed Ability Groups")

    groups = []
    group_size = 5

    # Split by category
    categories = df["Category"].unique()
    category_groups = {cat: df[df["Category"] == cat].to_dict("records") for cat in categories}

    # Shuffle within each category
    for cat in category_groups:
        random.shuffle(category_groups[cat])

    # Find max groups possible
    max_groups = max(len(students) for students in category_groups.values())

    # Build groups round-robin from each category
    for i in range(max_groups):
        group_members = []
        for cat in categories:
            if i < len(category_groups[cat]):
                group_members.append(category_groups[cat][i])
        groups.append((f"Group {len(groups)+1}", pd.DataFrame(group_members)))

    # Display groups separately with spacing
    color_map = {

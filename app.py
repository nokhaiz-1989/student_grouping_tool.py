import streamlit as st
import pandas as pd
import random

st.title("🎓 Student Grouping Tool")
st.write("Upload a CSV/Excel file with **Name** and **Score** columns to generate categorized students and mixed-ability groups.")

# -------------------------
# Upload File
# -------------------------
uploaded_file = st.file_uploader("📂 Upload your student file (CSV or Excel)", type=["csv", "xlsx"])

# -------------------------
# Category Function
# -------------------------
def categorize_student(score):
    if score <= 20:
        return "Minimal", "#FF4C4C"       # Dark Red
    elif score <= 40:
        return "Needs Improvement", "#FF8000"  # Orange
    elif score <= 60:
        return "Developing", "#FFD700"    # Golden Yellow
    elif score <= 80:
        return "Proficient", "#1E90FF"    # Dodger Blue
    else:
        return "Exemplary", "#228B22"     # Forest Green

# -------------------------
# If File Uploaded
# -------------------------
if uploaded_file:
    # Load file
    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)

    # Ensure columns exist
    if "Name" not in df.columns or "Score" not in df.columns:
        st.error("❌ File must contain 'Name' and 'Score' columns.")
    else:
        # Categorize
        df["Category"], df["Color"] = zip(*df["Score"].apply(categorize_student))

        # -------------------------
        # First Table: All Students
        # -------------------------
        st.subheader("📊 Student Categories")

        def highlight_category(row):
            return [f"background-color: {row['Color']}; text-align: center; font-weight: bold;"] * len(row)

        styled_df = (
            df.style
            .apply(highlight_category, axis=1)
            .hide_columns(["Color"])
            .set_properties(**{"text-align": "center"})
            .set_table_styles([{
                'selector': 'th',
                'props': [('font-weight', 'bold'), ('text-align', 'center')]
            }])
        )

        st.dataframe(styled_df, use_container_width=True)

        # -------------------------
        # Mixed Ability Groups
        # -------------------------
        st.subheader("👥 Mixed-Ability Groups")

        # Shuffle within categories
        grouped = {cat: df[df["Category"] == cat].sample(frac=1, random_state=42) for cat in df["Category"].unique()}

        # Find max group size
        max_size = max(len(students) for students in grouped.values())

        # Create groups by round-robin
        groups = []
        for i in range(max_size):
            group = []
            for cat, students in grouped.items():
                if i < len(students):
                    group.append(students.iloc[i])
            if group:
                groups.append(pd.DataFrame(group))

        # Display each group separately
        for idx, group_df in enumerate(groups, start=1):
            st.markdown(f"### Group {idx}")

            def highlight_row(row):
                return [f"background-color: {row['Color']}; text-align: center; font-weight: bold;"] * len(row)

            styled_group = (
                group_df.style
                .apply(highlight_row, axis=1)
                .hide_columns(["Color", "Score"])  # only Name + Category
                .set_properties(**{"text-align": "center"})
                .set_table_styles([{
                    'selector': 'th',
                    'props': [('font-weight', 'bold'), ('text-align', 'center')]
                }])
            )

            st.dataframe(styled_group, use_container_width=True)
            st.markdown("---")  # separator

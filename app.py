import streamlit as st
import pandas as pd

st.set_page_config(page_title="Student Grouping Tool", layout="wide")

st.title("🎓 Student Grouping and Performance Tool")
st.write("""
📌 **Instructions**  
1. Upload an Excel file with columns: **ID, Name, Score**.  
   Example ID format: `L24-8928`  
2. The app will categorize students into performance levels.  
3. Groups will be formed with at least one student from each level.  
""")

# --- File Upload ---
uploaded_file = st.file_uploader("📂 Upload your Excel file", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)

    # --- Ensure correct columns ---
    expected_columns = ["ID", "Name", "Score"]
    if not all(col in df.columns for col in expected_columns):
        st.error(f"Your file must contain the columns: {expected_columns}")
    else:
        # --- Categorize performance ---
        def categorize(score):
            if score < 20:
                return "Minimal", "red"
            elif score <= 40:
                return "Needs Improvement", "orange"
            elif score <= 60:
                return "Developing", "yellow"
            elif score <= 80:
                return "Proficient", "blue"
            else:
                return "Exemplary", "green"

        df[["Category", "ColorName"]] = df["Score"].apply(lambda x: pd.Series(categorize(x)))

        # Softer pastel background colors
        category_colors = {
            "red": "#f8d7da",
            "orange": "#ffe5b4",
            "yellow": "#fff9c4",
            "blue": "#d6eaff",
            "green": "#d4edda"
        }

        # --- Styling function for first table ---
        def highlight_category(row):
            return [f"background-color: {category_colors[row['ColorName']]}; text-align: center;"] * len(row)

        styled_df = df.style.apply(highlight_category, axis=1).set_table_styles(
            [{'selector': 'th', 'props': [('font-weight', 'bold'), ('text-align', 'center')]}]
        )

        st.subheader("📊 Student Performance by Category")
        st.dataframe(styled_df, use_container_width=True)

        # --- Mixed Ability Group Formation ---
        groups = []
        categories = df["Category"].unique()
        category_students = {cat: df[df["Category"] == cat].sample(frac=1).to_dict("records") for cat in categories}

        # Form groups with at least one from each category
        while any(category_students.values()):
            group = []
            for cat in categories:
                if category_students[cat]:
                    group.append(category_students[cat].pop())
            if group:
                groups.append(group)

        # Convert groups into DataFrame
        group_rows = []
        for i, group in enumerate(groups, start=1):
            for student in group:
                group_rows.append({
                    "Group": f"Group {i}",
                    "ID": student["ID"],
                    "Name": student["Name"],
                    "Score": student["Score"],
                    "Category": student["Category"],
                    "ColorName": student["ColorName"],
                    "Color": category_colors[student["ColorName"]]
                })

        groups_df = pd.DataFrame(group_rows)

        # --- Styling for grouped table ---
        def highlight_group_row(row):
            return [f"background-color: {row['Color']}; text-align: center;"] * len(row)

        styled_groups_df = groups_df.drop(columns=["Color"]).style.apply(highlight_group_row, axis=1).set_table_styles(
            [{'selector': 'th', 'props': [('font-weight', 'bold'), ('text-align', 'center')]}]
        )

        st.subheader("👥 Mixed Ability Groups")
        st.dataframe(styled_groups_df, use_container_width=True)

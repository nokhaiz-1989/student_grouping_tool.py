import streamlit as st
import pandas as pd
import re

st.set_page_config(page_title="Writing Skills Assessment", layout="wide")

st.title("📊 Writing Skills Assessment Tool")

# --- STEP 1: Upload Excel ---
uploaded_file = st.file_uploader("Upload Excel file with Student IDs, Names and Scores", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)

    # Expected columns: ID, Name, Score
    expected_cols = ["ID", "Name", "Score"]
    if not all(col in df.columns for col in expected_cols):
        st.error(f"❌ Excel must contain columns: {expected_cols}")
    else:
        # Validate IDs: allow L24-#### format
        id_pattern = r"^L\d{2}-\d{4}$"
        if not all(df['ID'].astype(str).apply(lambda x: bool(re.match(id_pattern, x)))):
            st.error("❌ IDs must follow the format Lxx-xxxx (e.g., L24-8928)")
        elif not all((df['Score'] >= 0) & (df['Score'] <= 100)):
            st.error("❌ Scores must be between 0 and 100")
        else:
            # --- STEP 2: Segmentation by Color ---
            def segment(score):
                if score <= 20:
                    return "Minimal", "#ff9999"   # light red
                elif score <= 40:
                    return "Needs Improvement", "#ffcc99"   # light orange
                elif score <= 60:
                    return "Developing", "#ffff99"   # light yellow
                elif score <= 80:
                    return "Proficient", "#99ccff"   # light blue
                else:
                    return "Exemplary", "#99ff99"   # light green

            df["Segment"], df["Color"] = zip(*df["Score"].apply(segment))

            st.subheader("🎨 Student Segmentation")

            # Apply row-wise color formatting
            def highlight_row(row):
                return [f'background-color: {row["Color"]}'] * len(row)

            styled_df = df.style.apply(highlight_row, axis=1)
            st.dataframe(styled_df, use_container_width=True)

            # --- STEP 3: Mixed Ability Groups ---
            st.subheader("👥 Mixed Ability Groups")

            # Separate students by segment
            segment_groups = {
                "Minimal": df[df["Segment"] == "Minimal"][["ID", "Name"]].values.tolist(),
                "Needs Improvement": df[df["Segment"] == "Needs Improvement"][["ID", "Name"]].values.tolist(),
                "Developing": df[df["Segment"] == "Developing"][["ID", "Name"]].values.tolist(),
                "Proficient": df[df["Segment"] == "Proficient"][["ID", "Name"]].values.tolist(),
                "Exemplary": df[df["Segment"] == "Exemplary"][["ID", "Name"]].values.tolist()
            }

            groups = []
            # Make 20 groups
            for i in range(20):
                group = []
                for seg in ["Minimal", "Needs Improvement", "Developing", "Proficient", "Exemplary"]:
                    if segment_groups[seg]:
                        student = segment_groups[seg].pop(0)
                        group.append(f"{student[0]} ({student[1]})")
                groups.append(group)

            # Add group numbers
            groups_df = pd.DataFrame(
                groups,
                columns=["Red (Minimal)", "Orange (Needs Improvement)", 
                         "Yellow (Developing)", "Blue (Proficient)", 
                         "Green (Exemplary)"]
            )
            groups_df.index = [f"Group {i+1}" for i in range(len(groups_df))]

            st.dataframe(groups_df, use_container_width=True)

            # Download option
            csv = groups_df.to_csv(index=True).encode("utf-8")
            st.download_button("⬇️ Download Groups CSV", csv, "mixed_ability_groups.csv", "text/csv")

else:
    st.info("👆 Please upload an Excel file with columns: `ID` (e.g., L24-8928), `Name`, and `Score` (0–100).")

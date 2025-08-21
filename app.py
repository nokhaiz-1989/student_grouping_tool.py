import streamlit as st
import pandas as pd

# --- STEP 1: Upload Excel ---
st.title("Writing Skills Assessment Tool")

uploaded_file = st.file_uploader("Upload Excel file with Student IDs and Scores", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)

    # Validate IDs and Scores
    if not all(df['ID'].str.startswith("STD-")):
        st.error("Student IDs must be in the format STD-001 to STD-100")
    elif not all((df['Score'] >= 0) & (df['Score'] <= 100)):
        st.error("Scores must be between 0 and 100")
    else:
        # --- STEP 2: Segmentation by Color ---
        def segment(score):
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

        df["Segment"], df["Color"] = zip(*df["Score"].apply(segment))

        st.subheader("Student Segmentation")
        st.dataframe(df.style.apply(lambda x: [f"background-color: {c}" for c in df["Color"]], axis=1))

        # --- STEP 3: Mixed Ability Groups ---
        st.subheader("Mixed Ability Groups")

        groups = []
        segment_groups = {seg: df[df["Segment"] == seg]["ID"].tolist() for seg in df["Segment"].unique()}

        # Make 20 groups
        for i in range(20):
            group = []
            for seg in ["Minimal", "Needs Improvement", "Developing", "Proficient", "Exemplary"]:
                if segment_groups[seg]:
                    group.append(segment_groups[seg].pop(0))
            groups.append(group)

        groups_df = pd.DataFrame(groups, columns=["Red", "Orange", "Yellow", "Blue", "Green"])
        st.write(groups_df)

        # Download option
        csv = groups_df.to_csv(index=False).encode("utf-8")
        st.download_button("Download Groups CSV", csv, "mixed_ability_groups.csv", "text/csv")

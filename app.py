import streamlit as st
import pandas as pd
from collections import deque

st.set_page_config(page_title="Student Grouping Tool", layout="wide")

st.title("🎓 Student Grouping and Performance Tool")

st.info(
    """
    📌 **Upload Instructions**
    - File type: **Excel (.xlsx)**
    - Required columns (exact names): **ID**, **Name**, **Score**
    - Example row: `L24-8928 | Ali Khan | 72`
    - Scores must be between **0 and 100**.
    """
)

# -------------------------
# Helpers
# -------------------------
def segment_and_color(score: float):
    """Return (SegmentName, ColorName) per your exact rules."""
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

# Medium-dark, clear tones (good visibility without being neon)
COLOR_HEX = {
    "red":    "#EF5350",
    "orange": "#FB8C00",
    "yellow": "#FBC02D",
    "blue":   "#42A5F5",
    "green":  "#66BB6A",
}

SEGMENT_ORDER = ["Minimal", "Needs Improvement", "Developing", "Proficient", "Exemplary"]

def style_entire_row_using_series(display_df: pd.DataFrame, color_series: pd.Series):
    """
    Style a DataFrame (with Color column already dropped) by fetching each row's color
    from a parallel Series indexed the same as display_df.
    """
    def _apply(row):
        col = color_series.loc[row.name]
        return [f"background-color: {col}; text-align: center;"] * len(row)

    return (
        display_df.style
        .apply(_apply, axis=1)
        .set_properties(**{"text-align": "center"})
        .set_table_styles([
            {"selector": "th",
             "props": [("font-weight", "bold"), ("color", "black"), ("text-align", "center")]}
        ])
    )

# -------------------------
# Upload
# -------------------------
uploaded = st.file_uploader("📂 Upload Excel (.xlsx) with ID, Name, Score", type=["xlsx"])

if not uploaded:
    st.stop()

# Read file
df = pd.read_excel(uploaded)

# Validate columns
expected_cols = ["ID", "Name", "Score"]
if not all(c in df.columns for c in expected_cols):
    st.error(f"❌ Your file must contain columns: {expected_cols}")
    st.stop()

# Validate score bounds
df = df.copy()
df = df[(pd.to_numeric(df["Score"], errors="coerce") >= 0) & (pd.to_numeric(df["Score"], errors="coerce") <= 100)]
df["Score"] = pd.to_numeric(df["Score"], errors="coerce").fillna(0)

# Segment + color names + hex for styling
df[["Segment", "ColorName"]] = df["Score"].apply(lambda x: pd.Series(segment_and_color(x)))
df["ColorHex"] = df["ColorName"].map(COLOR_HEX)

# -------------------------
# Table 1: All students (no group numbers)
# -------------------------
st.subheader("📊 Student Segmentation (All Students)")

# show color names here; shade rows using ColorHex
display_1 = df[["ID", "Name", "Score", "Segment", "ColorName"]].copy()
styled_1 = style_entire_row_using_series(display_1, df["ColorHex"])
st.dataframe(styled_1, use_container_width=True)

# -------------------------
# Build Mixed-Ability Groups
# -------------------------
st.subheader("👥 Mixed-Ability Groups (separate tables)")

# Create queues per segment in the required order
queues = {seg: deque(df[df["Segment"] == seg].index.tolist()) for seg in SEGMENT_ORDER}

groups = []  # list of lists of row indices
# First pass: form "perfect" groups with one from each segment
while all(len(queues[seg]) > 0 for seg in SEGMENT_ORDER):
    group_indices = []
    for seg in SEGMENT_ORDER:
        group_indices.append(queues[seg].popleft())
    groups.append(group_indices)

# Collect leftovers (any remaining students in any segment)
leftovers = []
for seg in SEGMENT_ORDER:
    leftovers.extend(list(queues[seg]))

# Distribute leftovers round-robin across existing groups; if no groups yet, start new groups
if groups:
    gi = 0
    for idx in leftovers:
        groups[gi % len(groups)].append(idx)
        gi += 1
else:
    # No perfect groups possible; create groups directly from leftovers in blocks of up to 5
    block = []
    for idx in leftovers:
        block.append(idx)
        if len(block) == 5:
            groups.append(block)
            block = []
    if block:
        groups.append(block)

# -------------------------
# Show each group as a separate table, with a gap
# -------------------------
if not groups:
    st.warning("No groups could be formed from the uploaded data.")
else:
    for gnum, gindices in enumerate(groups, start=1):
        st.markdown(f"### Group {gnum}")

        gdf = df.loc[gindices, ["ID", "Name", "Score", "Segment", "ColorHex"]].copy()

        # We don't want to *display* color names in groups; only background color.
        display_g = gdf[["ID", "Name", "Score", "Segment"]].copy()
        colors_g = gdf["ColorHex"]

        styled_g = style_entire_row_using_series(display_g, colors_g)
        st.dataframe(styled_g, use_container_width=True)
        st.markdown("---")

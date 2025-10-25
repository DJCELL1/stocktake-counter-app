import streamlit as st
import pandas as pd
import io
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

st.set_page_config(page_title="Stocktake Counter", layout="wide")

st.title("📦 Stocktake Counter with Areas")

# --- Step 1: Upload file ---
uploaded_file = st.file_uploader("Upload your product file (CSV or Excel)", type=["csv", "xlsx"])

if uploaded_file:
    # Load file
    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)

    # Normalize column names
    df.columns = [c.strip().capitalize() for c in df.columns]

    # Check for required columns
    required_cols = {"Area", "Description", "Qty"}
    if not required_cols.issubset(df.columns):
        st.error("Your file must have columns named 'Area', 'Description', and 'Qty'.")
        st.stop()

    # --- Step 2: Select Area ---
    areas = df["Area"].dropna().unique()
    selected_area = st.selectbox("Select Area to Count", areas)

    # Filter by selected area
    df_area = df[df["Area"] == selected_area].reset_index(drop=True)

    # Initialize session state for area
    area_key = f"counts_{selected_area}"
    index_key = f"index_{selected_area}"

    if area_key not in st.session_state:
        st.session_state[area_key] = [0 if pd.isna(q) else int(q) for q in df_area["Qty"]]
        st.session_state[index_key] = 0
        st.session_state[f"finished_{selected_area}"] = False

    i = st.session_state[index_key]
    counts = st.session_state[area_key]

    st.subheader(f"Area: {selected_area} | Product {i+1} of {len(df_area)}")
    st.write(f"**Description:** {df_area.iloc[i]['Description']}")
    st.markdown(f"### Current Count: {counts[i]}")

    # --- Keypad ---
    keypad = [
        ["1", "2", "3"],
        ["4", "5", "6"],
        ["7", "8", "9"],
        ["0", "Clear", "Enter"]
    ]

    def handle_input(value):
        if value == "Clear":
            counts[i] = 0
        elif value == "Enter":
            if st.session_state[index_key] < len(df_area) - 1:
                st.session_state[index_key] += 1
            else:
                st.session_state[f"finished_{selected_area}"] = True
        else:
            current = str(counts[i])
            if current == "0":
                current = ""
            counts[i] = int(current + value)
        st.rerun()

    for row in keypad:
        cols = st.columns(3)
        for j, label in enumerate(row):
            if cols[j].button(label, use_container_width=True):
                handle_input(label)

    # --- Navigation buttons ---
    nav_cols = st.columns(2)
    if nav_cols[0].button("⬅ Previous", use_container_width=True):
        if st.session_state[index_key] > 0:
            st.session_state[index_key] -= 1
            st.rerun()
    if nav_cols[1].button("➡ Next", use_container_width=True):
        if st.session_state[index_key] < len(df_area) - 1:
            st.session_state[index_key] += 1
            st.rerun()

    # --- Area completion ---
    if st.session_state.get(f"finished_{selected_area}", False):
        df_area["Qty"] = counts
        st.success(f"✅ Finished counting area: {selected_area}")

        # Update main dataframe
        for idx, row in df_area.iterrows():
            df.loc[(df["Area"] == selected_area) & (df["Description"] == row["Description"]), "Qty"] = row["Qty"]

        # Summary for area
        total_items = len(df_area)
        total_counted = sum(df_area["Qty"])
        zero_items = len(df_area[df_area["Qty"] == 0])

        st.markdown(f"### Summary for {selected_area}")
        st.write(f"- Total items: **{total_items}**")
        st.write(f"- Total counted: **{total_counted}**")
        st.write(f"- Items with zero count: **{zero_items}**")

    # --- Restart or Switch area ---
    st.markdown("---")
    col1, col2 = st.columns(2)
    if col1.button("🔄 Restart This Area"):
        st.session_state[area_key] = [0] * len(df_area)
        st.session_state[index_key] = 0
        st.session_state[f"finished_{selected_area}"] = False
        st.rerun()
    if col2.button("🏁 Switch Area"):
        st.session_state[index_key] = 0
        st.rerun()

    # --- Global summary ---
    st.markdown("## 📦 All Areas Summary")

    # Combine all areas
    full_df = df.copy()
    for area in df["Area"].unique():
        key = f"counts_{area}"
        if key in st.session_state:
            area_counts = st.session_state[key]
            full_df.loc[full_df["Area"] == area, "Qty"] = area_counts

    summary = (
        full_df.groupby("Area", as_index=False)
        .agg(Total_Items=("Description", "count"), Total_Qty=("Qty", "sum"))
    )
    st.dataframe(summary, use_container_width=True)

    # --- Download & Email buttons ---
    colA, colB = st.columns(2)

    # 📥 Download All
    buffer_all = io.StringIO()
    full_df.to_csv(buffer_all, index=False)
    buffer_all.seek(0)
    colA.download_button(
        "📥 Download All Results (CSV)",
        data=buffer_all.getvalue(),
        file_name="stocktake_results_all_areas.csv",
        mime="text/csv",
        use_container_width=True
    )

    # 📧 Send All via Email
    if colB.button("📧 Send All Results via Email", use_container_width=True):
        sender_email = "stocktake.bot@gmail.com"
        receiver_email = "lopatifam@hotmail.com"
        subject = "Full Stocktake Results"
        body = "Attached are the complete stocktake results for all areas."

        msg = MIMEMultipart()
        msg["From"] = sender_email
        msg["To"] = receiver_email
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))

        part = MIMEBase("application", "octet-stream")
        part.set_payload(buffer_all.getvalue().encode("utf-8"))
        encoders.encode_base64(part)
        part.add_header("Content-Disposition", "attachment; filename=stocktake_results_all_areas.csv")
        msg.attach(part)

        try:
            with smtplib.SMTP("smtp.gmail.com", 587) as server:
                server.starttls()
                # Replace with a valid Gmail app password if you want to actually send mail
                server.login(sender_email, "your-app-password")
                server.send_message(msg)
            st.success(f"📧 Email sent to {receiver_email}")
        except Exception as e:
            st.warning(f"Email not sent (likely missing credentials): {e}")



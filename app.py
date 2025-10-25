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
    # Read the file
    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)

    # Normalize headers
    df.columns = [c.strip().capitalize() for c in df.columns]

    # Check required columns
    required_cols = {"Area", "Description", "Qty"}
    if not required_cols.issubset(df.columns):
        st.error("Your file must have columns named 'Area', 'Description', and 'Qty'.")
        st.stop()

    # --- Step 2: Select area to work on ---
    areas = df["Area"].dropna().unique()
    selected_area = st.selectbox("Select Area to Count", areas)

    # Filter by selected area
    df_area = df[df["Area"] == selected_area].reset_index(drop=True)

    # Initialize session state for this area
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

    # --- Finish for this area ---
    if st.session_state.get(f"finished_{selected_area}", False):
        df_area["Qty"] = counts
        st.success(f"✅ Finished counting area: {selected_area}")

        # Update main dataframe
        for idx, row in df_area.iterrows():
            df.loc[(df["Area"] == selected_area) & (df["Description"] == row["Description"]), "Qty"] = row["Qty"]

        # Summary
        total_items = len(df_area)
        total_counted = sum(df_area["Qty"])
        zero_items = len(df_area[df_area["Qty"] == 0])

        st.markdown(f"### Summary for {selected_area}")
        st.write(f"- Total items: **{total_items}**")
        st.write(f"- Total counted: **{total_counted}**")
        st.write(f"- Items with zero count: **{zero_items}**")

        # Convert to CSV
        buffer = io.StringIO()
        df.to_csv(buffer, index=False)
        buffer.seek(0)

        st.download_button(
            "📥 Download Updated File",
            data=buffer.getvalue(),
            file_name=f"stocktake_results_{selected_area}.csv",
            mime="text/csv"
        )

        # --- Email results ---
        sender_email = "stocktake.bot@gmail.com"  # dummy sender
        receiver_email = "lopatifam@hotmail.com"
        subject = f"Stocktake Results - {selected_area}"
        body = f"Attached are your stocktake results for area: {selected_area}."

        msg = MIMEMultipart()
        msg["From"] = sender_email
        msg["To"] = receiver_email
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))

        part = MIMEBase("application", "octet-stream")
        part.set_payload(buffer.getvalue().encode("utf-8"))
        encoders.encode_base64(part)
        part.add_header("Content-Disposition", f"attachment; filename=stocktake_results_{selected_area}.csv")
        msg.attach(part)

        try:
            with smtplib.SMTP("smtp.gmail.com", 587) as server:
                server.starttls()
                # Replace with valid app password if using a real Gmail sender
                server.login(sender_email, "your-app-password")
                server.send_message(msg)
            st.success(f"📧 Email sent to {receiver_email}")
        except Exception as e:
            st.warning(f"Email not sent (likely missing credentials): {e}")

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


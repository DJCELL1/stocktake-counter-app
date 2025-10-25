import streamlit as st
import pandas as pd
import io
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime

st.set_page_config(page_title="Stocktake Counter", layout="wide")

st.title("📦 Stocktake Counter – Built-In List")

# --- Hardcoded stock list ---
data = [
    # Upstairs Wardrobe
    ("Upstairs Wardrobe", "Ready salted chips", ""),
    ("Upstairs Wardrobe", "Chicken chips", ""),
    ("Upstairs Wardrobe", "Seaweed", ""),
    ("Upstairs Wardrobe", "Muesli bars", ""),
    ("Upstairs Wardrobe", "Nutella/Hazelnut spread", ""),
    ("Upstairs Wardrobe", "Nut bars", ""),
    ("Upstairs Wardrobe", "UHT milk", ""),
    ("Upstairs Wardrobe", "Vitafresh", ""),

    # Selws lunches
    ("Selws lunches", "Sweet chilli tuna", ""),
    ("Selws lunches", "Microwave rice 2 pack/", ""),
    ("Selws lunches", "Dads steam vegetables bag of 9x", ""),
    ("Selws lunches", "Dads Noodle box", ""),
    ("Selws lunches", "Cheese n crackers", ""),
    ("Selws lunches", "Yogurt 12 pack", ""),
    ("Selws lunches", "Multi chips", ""),
    ("Selws lunches", "Nut bars", ""),
    ("Selws lunches", "Kewpie mayo", ""),
    ("Selws lunches", "Siracha mayonnaise", ""),

    # Blackbox
    ("Blackbox", "bodywash", ""),
    ("Blackbox", "Shampoo", ""),
    ("Blackbox", "Conditioner", ""),
    ("Blackbox", "Shavers", ""),
    ("Blackbox", "Floss", ""),
    ("Blackbox", "Toothpaste", ""),
    ("Blackbox", "Men’s roll on", ""),
    ("Blackbox", "Women’s roll on", ""),
    ("Blackbox", "Men’s deodorant spray", ""),
    ("Blackbox", "Women’s spray deodorant", ""),
    ("Blackbox", "Toothbrushes packs/", ""),
    ("Blackbox", "Hairfood", ""),
    ("Blackbox", "Toilet cleaner", ""),
    ("Blackbox", "Air freshener/Toilet spray", ""),
    ("Blackbox", "Disinfectant for bathroom", ""),
    ("Blackbox", "Regular pads", ""),
    ("Blackbox", "Goodnights", ""),

    # Downstairs Freezer
    ("Downstairs Freezer", "Frozen vegetables", ""),
    ("Downstairs Freezer", "Mixed vegetables 1kg", ""),
    ("Downstairs Freezer", "Dads steam vegetables", ""),
    ("Downstairs Freezer", "Country soft", ""),
    ("Downstairs Freezer", "Cheese slices", ""),
    ("Downstairs Freezer", "Pies pack of 4/", ""),
    ("Downstairs Freezer", "White bread", ""),
    ("Downstairs Freezer", "Brown bread", ""),
    ("Downstairs Freezer", "Any meat left", ""),

    # Pantry
    ("Pantry", "Tomato sauce", ""),
    ("Pantry", "Mayonnaise", ""),
    ("Pantry", "Mustard", ""),
    ("Pantry", "ABC sauce", ""),
    ("Pantry", "Dark Soy sauce", ""),
    ("Pantry", "Oyster sauce", ""),
    ("Pantry", "Worcestershire sauce", ""),
    ("Pantry", "Full Tray eggs", ""),
    ("Pantry", "Migoreng noodles 1 box", ""),
    ("Pantry", "Bag of Apples", ""),
    ("Pantry", "Canned Tuna", ""),
    ("Pantry", "Cooking oil", ""),
    ("Pantry", "Oxo Beef", ""),
    ("Pantry", "Oxo Chicken", ""),
    ("Pantry", "Curry", ""),
    ("Pantry", "Herbs (if needed)", ""),
    ("Pantry", "Cornflour", ""),
    ("Pantry", "Standard flour", ""),
    ("Pantry", "Rice", ""),
    ("Pantry", "Potatoes", ""),
    ("Pantry", "Others sauces needed", ""),
    ("Pantry", "Other seasonings needed", ""),
    ("Pantry", "Other pasta needed", ""),

    # Fridge
    ("Fridge", "Bag of Onions", ""),
    ("Fridge", "Luncheon", ""),
    ("Fridge", "Salad", ""),
    ("Fridge", "Block of cheese", ""),
    ("Fridge", "Full pack of Cheese slices", ""),

    # Bottom drawer
    ("Bottom drawer", "Big rubbish bags", ""),
    ("Bottom drawer", "Wheelie bin liners (lines the bin)", ""),
    ("Bottom drawer", "Small rubbish bags(for recycling)", ""),
    ("Bottom drawer", "Glad wrap", ""),
    ("Bottom drawer", "Foil", ""),
    ("Bottom drawer", "Baking paper", ""),
    ("Bottom drawer", "Large sealable bags", ""),

    # Under sink
    ("Under sink", "Roll of Cleaning cloths", ""),
    ("Under sink", "Dishwasher detergent", ""),
    ("Under sink", "Dishwasher tablets", ""),
    ("Under sink", "Scouring pads", ""),
    ("Under sink", "Metallic sponges", ""),
    ("Under sink", "Dish brush", ""),
    ("Under sink", "Cream cleanser (Cheap jiff/ajax)", ""),
    ("Under sink", "Multi spray", ""),
    ("Under sink", "Cleanery - (sachet to refill multispray bottles)", ""),
    ("Under sink", "Laundry powder", ""),
    ("Under sink", "Flyspray", ""),
    ("Under sink", "Disinfectant", ""),
    ("Under sink", "White vinegar", ""),
    ("Under sink", "Baking soda", ""),
    ("Under sink", "Big waters", "")
]

df = pd.DataFrame(data, columns=["Area", "Description", "Qty"])

# --- Streamlit interaction ---
areas = df["Area"].unique()
selected_area = st.selectbox("Select Area to Count", areas)

df_area = df[df["Area"] == selected_area].reset_index(drop=True)

# Session state setup
area_key = f"counts_{selected_area}"
index_key = f"index_{selected_area}"
finished_key = f"finished_{selected_area



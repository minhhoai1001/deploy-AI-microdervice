import streamlit as st

from database_orm import *
import datetime
import os
from PIL import Image
import pandas as pd
import api

st.set_page_config(layout="wide")


st.markdown("<h1 style='text-align: center; color: grey;'>Fish Farm Management</h1>", unsafe_allow_html=True)

farm_id = 1

infor1, infor2, infor3, infor4, infor5 = st.columns(5)
char1, table2 = st.columns(2)
# Select Cage location from Farm name
df_cage = api.get_cage_by_farm(farm_id=farm_id)
cage_location_sb = infor1.selectbox(
    'Farm Location',
    df_cage['cage_location'])

# Select Cage name from Cage location
df_cage = api.get_cage_by_cage_location(cage_location_sb)
cage_name_sb = infor2.selectbox(
    'Cage Name',
    df_cage['cage_name']
)

# Select week
week_list = [i for i in range(int(datetime.date.today().isocalendar()[1]), 0, -1)]
week_sb = infor3.selectbox(
    'Week',
    week_list
)

# Select date
days = api.get_days_in_week(2023, int(week_sb))
date_sb = infor4.selectbox(
    'Date',
    days
)

weather = infor5.selectbox(
    'Weather',
    ['Sunny']
)


cage_id = api.get_cageid_by_name(cage_name_sb)
df_fish = api.get_fish_by_week_and_cage(week_sb, cage_id)

chart_data = df_fish[['CaptureDate']]
chart_data['LiceAdultFemaleRate'] = df_fish['LiceAdultFemaleSum']/df_fish['FishCount']
chart_data['LiceMobilityRate'] = df_fish['LiceMobilitySum']/df_fish['FishCount']
chart_data['LiceAttachedRate'] = df_fish['LiceAttachedSum']/df_fish['FishCount']

char1.line_chart(chart_data, x='CaptureDate')


df_fish_table = df_fish[['CaptureDate', 'FishCount', 'LiceAdultFemaleSum','LiceMobilitySum', 'LiceAttachedSum']]
df_fish_table['LicePerFish'] = df_fish['LiceTotal']/df_fish['FishCount']

table2.write(df_fish_table)

fish_img = st.radio(
    "Choice fish to show",
    ["No Lice", "Lice"]
    )

img, text = st.columns([2, 1])
img.empty()
text.empty()
path = "/home/hoaitran/dev/AI-microservice/imgs/lice_detect"

if fish_img == "No Lice":
    df_fish_nolice = api.get_fish_nolice_by_date(farm_id, cage_id, date_sb)
    imgs = df_fish_nolice['ImagePath']
    img_path = os.path.join(path, imgs[0])
    image = Image.open(img_path)
    img.image(image)
else:
    df_fish_lice = api.get_fish_lice_by_date(farm_id, cage_id, date_sb)
    st.write(df_fish_lice)
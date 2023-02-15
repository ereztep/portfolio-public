import streamlit as st
import os
from PIL import Image
from utils.general_utils import present_photos

st.set_page_config(
    page_title='University, Courses, Achievements',
    layout="wide",
    initial_sidebar_state="auto",
    menu_items=None)

st.header('My Certifications')

#The idea with this structure was to make it more maintainable in case
# I would want to add pictures to certain
#Categories, or add categories, etc.


categories = ['Academic', 'Data', 'Web', 'Social Entrepreneurship', 'Other']

tabs = st.tabs(categories)

for i, category in enumerate(categories):

    base_path = f'bucket/Certifications/{categories[i]}'

    if i == categories.index('Data'):
        with tabs[i]:

            wagon_path = base_path + '/Le Wagon'
            present_photos(wagon_path)

            camp_path = base_path + '/Data Camp'
            present_photos(camp_path)

    elif i == categories.index('Academic'):
        with tabs[i]:

            uni_directory_path = base_path+ '/The Open University'
            present_photos(uni_directory_path)

            other_directory_path = base_path + '/Other'
            present_photos(other_directory_path)

    else:
        if category != 'Other':
            with tabs[i]:
                present_photos(base_path)

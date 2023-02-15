import streamlit as st
import os

st.set_page_config(
    page_title='Social Entrepreneurship',
    layout="wide",
    initial_sidebar_state="auto",
    menu_items=None)

st.header('Social Entrepreneurship')

ted = 'https://www.youtube.com/watch?v=ILG9f8cz4AA'
wow = 'https://www.youtube.com/watch?v=mRtk5CvWmAs'



cols = st.columns(2)

with cols[0]:
    with st.expander('TEDx Talk'):
        st.video(ted)

with cols[1]:
    with st.expander('Second WOW Talk'):
        st.video(wow)


photo_directory_path = 'bucket/Social'
images = [img for img in os.listdir(photo_directory_path)]



st.markdown('''
            When I was 16, I founded and managed a nationwide education NGO- "Project121", that included, at its peak, 400 volunteers, and several thousand students in dozens of schools across the country at the age of 16.
            The project was focused on:
            * Changing the education paradigma to skill-based one.
            * Integrating students at decision making processes, from school level to ministry.
            * Using various learning styles

            During my time as founder and manager of this project, I lectured in various places including a TEDx and WOW talks, presented above, and Advised in committees of the ministry of education, and formed a group of education project leaders to better cooperate and to learn from each other's insights.

            I believe this experience shows my ability to work independently, innovate, collaborate, and lead- when needed.
            ''')

with st.expander('Images'):
    cols = st.columns(2)

    for i, image in enumerate(images):
        image_path = f'{photo_directory_path}/{image}'
        with cols[i%2]:
            st.image(image_path, image.split('.')[0], 300, 150)
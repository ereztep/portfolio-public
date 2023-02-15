import openai
import PyPDF2
import extcolors as ec
from PIL import Image
import streamlit as st
import numpy as np
import time
from utils.job_application_utils import *

st.set_page_config(
    page_title='NLP Job Applications Tool',
    layout="wide",
    initial_sidebar_state="auto",
    menu_items=None)

gpt = openai.Completion()
model = 'text-davinci-003'


resume_text = ''
cover_text = ''

st.header('My NLP Job Hunt Tool')

intro_tab, pdf_tab, logo_tab, future_tab = st.tabs(['Introduction', 'Resume, Cover Letter and Job Listing analysis', 'Color Palette Extraction', 'Future'])

with intro_tab:
    st.markdown('''
                #### This section is my inner tool for optimizing job applications.
                * Upload your resume, and/or cover letter, and job description, and get back:
                    * Gaps between requirements and candidate experience
                    * Soft skills, hard skills and tools that were not mentioned in the documents
                    * Ideas how to improve the douments to better apply for the job
                    * General conclusion
                * Upload the logo of the company, and extract main color palette from it to improve design.
                * Use your openAI token or the password provided by me.
                ''')

with pdf_tab:

    token = st.text_input('What is your openai api token or given password?')

    if token is not None:

        if (len(token) > 15) & (token[:2] == 'sk'):
            openai.api_key = token

        elif token == st.secrets.password:
            openai.api_key = st.secrets.my_key

        elif len(token) != 0:
            st.warning('Invalid token format! (sk-...aaa1)')

    col1, col2 = st.columns(2)

    with col1:
        uploaded_resume = st.file_uploader('Upload your resume')
        if uploaded_resume != None:
            resume_text = extract_content(uploaded_resume)

    with col2:
        uploaded_cover = st.file_uploader('Upload your cover letter')
        if uploaded_cover != None:
            cover_text = extract_content(uploaded_cover)

    text = resume_text + cover_text



    job_description = st.text_area('Enter job description')

    if (job_description != '') & ((resume_text != '') | (cover_text != '')) & (token is not None):


        if st.button('What am I missing?'):
            with st.spinner('Summarizing job...'):
                summary = gpt_job(job_description)['choices'][0]['text']

                with st.expander('Job Summary:'):
                    st.write(f"Summary: {summary}")

            with st.spinner('Comparing and getting gaps...'):

                time.sleep(5)
                missing = super_gpt(summary = summary, resume = resume_text, cover = cover_text)

                with st.expander('Gaps and Conclusion'):
                    st.write(missing['choices'][0]['text'])

with logo_tab:

    col1, col2 = st.columns(2)

    with col1:
        tolerance = st.number_input('Tolerance: ', 5, 30, 12, 1)

    with col2:
        limit = st.number_input('Limit: ', 3, 15, 9, 1)

    uploaded_logo = st.file_uploader("Upload logo or homepage screenshot")

    if uploaded_logo is not None:

        logo = Image.open(uploaded_logo)
        main_colors = extract_colors(logo, tolerance = tolerance, limit = limit)
        st.write('Logo color palette:')

        columns = st.columns(4)

        for i, color in enumerate(main_colors):
            with columns[i%4]:
                st.color_picker(label =color[0], value = color[0])

with future_tab:
    st.header('These are my future plans:')
    st.markdown('''
                * Web scraping feature for job description extraction with a link
                * Company homepage design for a color palette feature with a link
                * Fonts extraction feature
                * Documents modifier feature
                '''
                )

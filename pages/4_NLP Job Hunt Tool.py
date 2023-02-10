import openai
import PyPDF2
import extcolors as ec
from PIL import Image
import streamlit as st
import numpy as np
import time

st.set_page_config(
    page_title='NLP Job Applications Tool',
    layout="wide",
    initial_sidebar_state="auto",
    menu_items=None)

gpt = openai.Completion()
model = 'text-davinci-003'

def extract_content(pdf):

    doc = PyPDF2.PdfReader(pdf)
    text = ''

    for page in doc.pages:
        text = text + page.extract_text()

    return text

def rgb_to_hex(r, g, b):
    return '#{:02X}{:02X}{:02X}'.format(r, g, b)

def extract_colors(image, tolerance = 25, limit = 8):
    colors = ec.extract_from_image(image, tolerance= tolerance, limit = limit)
    colors_pre_list = str(colors).replace('([(','').split(', (')[0:-1]
    rgb = [i.split('), ')[0] + ')' for i in colors_pre_list]
    percent = [i.split('), ')[1].replace(')','') for i in colors_pre_list]

    #convert RGB to HEX code
    to_hex = [rgb_to_hex(int(i.split(", ")[0].replace("(","")),int(i.split(", ")[1]),int(i.split(", ")[2].replace(")",""))) for i in rgb]

    zipped = list(zip(to_hex, percent))
    return zipped

def gpt_job(job):

    prompt = f"This is a job listing: {job}. Give me a list of soft skills, personal qualities, hard skills, tools, recurring words about the candidate, required experiences, described directly in the job listing."
    lists = prompt
    st.write('Extracting summary...')
    lists = gpt.create(model = model, prompt = prompt, max_tokens = 500)
    st.write(f"Summary: {lists['choices'][0]['text']}")

    return lists

def super_gpt(summary, resume = None, cover = None):

    st.spinner('Working on your request...')
    na = 0
    prompt =  f'These are lists of requirements for a in a job: "{summary}". Write a detailed list of the gaps I have for the job in terms of soft skills, experience and tools, give me a conclusion about my chances of getting that job, and improve my cover letter by demonstrating missing key words and soft skills based on my experience:'

    if cover is not None:
        prompt =  f'This is my cover letter: "{cover}".' + prompt
        na +=1

    if resume is not None:
        prompt = f'This is my resume: "{resume}".' + prompt
        na += 1

    if na == 0:
        st.warning('Upload at least one document')
        return None

    missing = prompt
    st.write('comparing...')
    missing = gpt.create(model = model, prompt = prompt, max_tokens = 1000)
    st.write(missing['choices'][0]['text'])

    return missing, summary



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
        else:
            st.warning('Wrong key!')

        ##In the private repository holding the website the part with the passwords is here


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

        openai.api_key = token

        if st.button('What am I missing?'):

            summary = gpt_job(job_description)['choices'][0]['text']
            time.sleep(30)
            missing, summary = super_gpt(summary = summary, resume = resume_text, cover = cover_text)

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

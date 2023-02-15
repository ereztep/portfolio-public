import PyPDF2
import openai
import streamlit as st
import extcolors as ec


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

def gpt_job(job, model = 'davinchi-text-003'):

    prompt = f"This is a job listing: {job}. Give me a list of soft skills, personal qualities, hard skills, tools, recurring words about the candidate, required experiences, described directly in the job listing."
    lists = prompt
    lists = openai.Completion().create(model = model, prompt = prompt, max_tokens = 500)

    return lists

def super_gpt(summary, resume = None, cover = None, model = 'davinchi-text-003'):

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
    missing = openai.Completion().create(model = model, prompt = prompt, max_tokens = 1000)

    return missing

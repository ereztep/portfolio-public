import streamlit as st
import os
from utils.general_utils import present_photos

st.set_page_config(
    page_title='Erez Tepper Portfolio Site',
    layout="wide",
    initial_sidebar_state="auto",
    menu_items=None)

width = 120
col_num = 3



st.markdown('''
# This website will show you the value and spirit I try to bring to a team (maybe yours!), and demonstrate my path.

**Thanks for droping by- and don't judge a book by its cover. After all, I don't claim to be a FE developer :)**
''')

tab_names = ['Why I Might Be Right For You?', 'Why Data Science?', 'You Will Find Here']

tabs = st.tabs(tab_names)

with tabs[0]:
    st.markdown('''
                **I believe I can be the person you're looking for.**

                I understand that a new recruit shouldn't be a liability and a burdon for you, and should give value for the company even in the adjustment period.

                Here's what you will get from me, beside the tech stack, based on my experience and demonstrated qualities:
        ''')

    with st.expander('Proactivity from day one'):

        st.markdown('''

        Naturally, I will be a proactive employee and will constantly come with ideas and suggestions. If my future employer would want, I will know how to take those ideas and suggestions and make them come to life, for the benefits of the organization and/or the society. My work is highly energetic and can be independent, if needed. Here are just few examples:
        - During high-school, I researched, founded and managed an NGO in the education system field.

        - During my army service, I maintained an active scheduale, including reforms in the structure of the unit, building an entirely new training methods, championing the experiemnt of building an autonomous training system, reorganizing our mid-range planning, and more, while preforming well on the core missions.

        - Right "Le Wagon", an intensive machine learning program, I formed a group that is building a system to detect illegal activity in the peruvian rainforest, provided for a local NGO. The work to be done has 4 parts- machine learning, web development, satellite imagey logic and stakeholders communication.
        ''')

    with st.expander('Diving into the domain and holistic learning'):
        st.markdown('''
        I understand the importancy of understanding the domain that data comes from, and I would like to show you that I will be able to keep up thanks to my fast, versitile and holistic learning abilities.

        - Since a very young age I have shown my ability for versitile, fast learning, when I started a double bachlor in chemistry and physics in the ninth grade (with honors).

        - Later on, without interupting to my day-to-day duties. I have taken courses in economy, neurology, web development, and data analysis.

        - In my work assisting a COO of a startup company, I had the opportunity to assist in UI/UX QA, stakeholder communications and product specifications.

        - All you see in this website and the prjects was learned in five months (Including all tech stack and programming).

        If relevant, I would like to take, in my free time, university courses in the domain of your company, to better understand the data and the business.

        I will continue to learn always anyway, better to make it for a good cause!
    ''')
    with st.expander('Vaccum filler'):
        st.markdown('''
                    My natural position in a versitile/cross-functionality team is to detect and fill vaccum that is being created, always, by the nature of cross-functionality teams, or inter-disciplinary projects.

                    You could expect me to go the extra mile for my team, look to the sides and into the future, trying to see what can go wrong and what are the points that were left in the corner unintentionally.
                    ''')

    with st.expander('Cummunication and collaboration'):
        st.markdown("Easier said then done, I know. Let me show you :) ")

with tabs[1]:
    st.markdown('''
            **I am excited to start my data science path.**

            - I chose to be in data science because it is a tech profession with a never-ending inter-disciplinary learning opportunities.

            - It has a flexible, cross-industries possibilities.

            - It has the ability to make a real impact.

            - It is interesting, and the perfect mix between everything I love doing.

            Data analyst positions in a data-science center company are also relevant for me.
        ''')

with tabs[2]:
    st.markdown('''
    **In order to show you some of what I can bring to the table, you would find here:**

    1. My current project- Amazon rainforest illegal activity monitor,
    that will actually be deployed in cooparation with NGOs from Peru, in order to assist them.

    2. The final project in a machine learning program-
    A UI that allows you to sketch, and transform your sketch into an image,
    build with my amazing team at "Le Wagon".

    3. A tool that I built for my self, based on GPT3, for optimizing job applications.

    4. Just a short description of my current contract in NLP, because it is protected with an NDA.

    5. Summary of my social enterprenaurship national projects.

    6. Certifications, courses and University honors.

    7. References.
    ''')


with open("other/resume.pdf", "rb") as pdf_file:
    resume = pdf_file.read()

with open("other/cover_letter.pdf", "rb") as pdf_file:
    cover = pdf_file.read()


cols = st.columns(2)
with cols[0]:
    st.download_button('Download my resume', resume, 'Erez-Tepper-Data-Scientist-Resume.pdf')

with cols[1]:
    st.download_button('Download my cover letter', cover, 'Erez-Tepper-Data-Scientist-Cover-Letter.pdf')

categories = ['Languages', 'Collection, Analysis, Visualization', 'Machine Learning', 'Deployment', 'On My Watchlist']
tabs = st.tabs(categories)
for i, category in enumerate(categories):

    base_path = f'bucket/Tech Stack/{categories[i]}'

    with tabs[i]:
        present_photos(base_path, width = width, col_num = col_num)

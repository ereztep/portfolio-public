import streamlit as st
from PIL import Image

st.set_page_config(
    page_title='Amazon Rainforest Satellite Monitor',
    layout="wide",
    initial_sidebar_state="auto",
    menu_items=None)

web_figma = 'https://www.figma.com/proto/iYcia4Uf6Kd7mzC9yssKKd/deforestationWeb?node-id=1%3A3&starting-point-node-id=1%3A3&scaling=scale-down'
project_notebook = 'https://github.com/ereztep/deforestation/blob/baseline/Final.ipynb'
kaggle_competition = 'https://www.kaggle.com/c/planet-understanding-the-amazon-from-space/data'


import streamlit as st
import pandas as pd
import numpy as np
from datetime import date
from pystac_client import Client
from shapely import geometry
import rioxarray
from utils.amazon_utils import *



st.header('Amazon Rainforest Deforestation Satellite Monitor')

st.markdown(f'''Me and my team still working on this project, so this page is under construction.
                You may see the project notebook [here]({project_notebook}).
                This is a description of what we are doing, and the challenges we face:
                ''')



tabs = ['Introduction', 'Data', 'Model', 'Satellite', 'User Interface'] #Add the team tab

intro_tab, data_tab, model_tab, sat_tab, user_int_tab = st.tabs(tabs)

with intro_tab:

    st.markdown(f'''

    I formed this team after an intensive machine learning program, from the understanding of the structure of forest preservation in the area.
    We wanted to make a holistic project, from idea to production, on a real-world problem.
    We contacted NGOs from the peruvian amazon and added a web development program alumni in order to deploy it in a comfortable way for them.
''')

with data_tab:
    with st.expander('Dataset'):
        st.markdown(f'''
    - [Dataset]({kaggle_competition}): Produced by "Planet" satellites, with 3m per pixel resolution.

    - Satellite for production: "Sentinel-2", with 10m per pixel resolution.
''')
    with st.expander('Challenges'):
        st.markdown('''
        Challenges:

        * Different satellites for training and production
        * Data is tagged in a continueos string, when some labels are relevant, some not, and include priority hierarchy, and under repersentations.
        * In reality, relatively small class 1 samples vs. a large number of samples in general, resulting a potential large false positive number.
        * NGO needs that we discussed (highest priority for detection, but also a need for deforestation drive, and more).
        * High cloud coverage in reality in comparasion to the training dataset, and a large number of under represented sub-classes.
        * Handling the satellite information recieved by the sentinel API.
        ''')

    with st.expander('Preparation'):
        st.markdown('''
        4. Data Preparation:
            * Creating a cloud and haze layer and augment 30% of all data, and a bit of contrast (to assimulate vegetetion change, according to a research).
            * Augment the under represented labels, or labels that we care about specifically, up to about 50% with haze, clouds, rotations, flipping, contrast, etc.

 ''')

with model_tab:
    with st.expander('Model graph'):
        st.image('bucket/Amazon/model_graph.png', width = 500)

    with st.expander('Input and Transfer Learning'):
        st.markdown(f'''
            - The input is our Planet dataset.
            The output is binary damage detection and damage driver detection, divided into 2 categories that were decided with the NGO, according to their needs.

            - First layer of the model is a pre trained ResNet50.

                * That layer was trained on the Euro-Sat landscape dataset (taken by "Sentinel-2" satellite), wrapped in tensorflow hub keras layer.
                * This format is not trainable, and in the future we will reconstract it and load the weights with keras functional API for fine tuning.
                * This model last layer is a 2048 feature space for 10 landscape image classification of "Sentinel-2". Each picture is homogenous and not hetrogenous like in our case.
                * This layer is connected directly to both of the prediction layers.
                * Using this as base will allow us to build in the UI functionality to collect updated labels from "Sentinel-2" images and re-train the top layers, to fix the variance caused by using "Planet" (for now).
                ''')
    with st.expander('Additional Layers and Outputs'):
        st.markdown('''
            - The ResNet is connected to a 512 and 256 units dense layers that are connected to both of the predictive layers, to allow the model to learn satellite images that contain multiple landscapes in one image, and classify them according to our labeling priorities.

            - The categorical classification is also connected to the binary classification, in order to allow it to tune itself better with the results')

        ''')

with sat_tab:

    with st.expander('Sentinel2 Image Retreivel Demo'):

        col3, col4 = st.columns(2)

        with col3:
            start_date = st.slider("When do you start?",
                                value=date(2022, 1, 1),
                                format="DD/MM/YY")

        with col4:
            end_date = st.slider("When do you stop?",
                                value=date(2023, 2, 10),
                                format="DD/MM/YY")


        col5, col6 = st.columns(2)
        with col5:
            lat = st.slider('Latitude - Y',  -9.0, -7.0, -8.0)

        with col6:
            lon = st.slider('Longitude - X', -74.0, -72.0, -73.0)


        html_str = f"""
        <p class="a">You picked a point at Latitude {lat} and Longitude {lon}. <br />
        Images collected between {start_date} and {end_date}.</p>
        """

        st.markdown(html_str, unsafe_allow_html=True)

        lat_long_df = pd.DataFrame(data={'lat' : [lat], 'lon': [lon]})

        col7, col8, col9 = st.columns(3)

        show_mosaic = 100

        with col8:
            st.map(lat_long_df)
            if st.button('Get chip'):
                items =  aws_sentinel_retrieve_item(15, 70,start_date,end_date,[lon,lat])

                if items == 'failed':
                    show_mosaic = 0

                else:
                    print(items)
                    mosaic_rgb  = aws_sentinel_chip(items,[lon,lat])
                    show_mosaic = 1

            if show_mosaic == 1:
                # st.write(mosaic_rgb)
                st.image(mosaic_rgb, clamp=True, channels='RGB')
            elif show_mosaic == 0:
                st.write('No image returned. Please increase the considered period (start and end dates) or allow for more clouds (Maximum cloud cover).')

    st.markdown('''
    * This part is a POC of image retreivel and chipping.
    * In the trade-off between speed and other qualities, we gave up some of the speed. In a weekly report, when the user gets it automatically when its ready, few minitues more will not make the difference.
    * On the deployed version it will be faster, but still- not meant for an instant use, due to the size of the area scanned and classified, and the nature of user use.
    * Those images will be sent to a docker container holding our model via an API, and the client will get back a visualization of the damaged areas and their coordinates.
    * They will also mark for the model where the deforestation was actually true, allowing us to retrain it and improve it constantly.
    * Unfortunatly, streamlit server has restricted limitations so in order to try it here you would have to be patient.
    ''')


with user_int_tab:
    st.markdown(f'''
                * This part is still under construction by our web development team member.
                * An initial sketch may be found [here](https://www.figma.com/proto/iYcia4Uf6Kd7mzC9yssKKd/deforestationWeb?node-id=23%3A1388&scaling=scale-down&page-id=0%3A1&starting-point-node-id=23%3A1388&show-proto-sidebar=1).
                * This sketch was changed in the recent version to allow easier real images tagging and deforestated area management in the user interface.
                * The users are reporting to the back-end the true labels after examination anyway (for management), and we use it to re-train the model, to fine tune it speceifically to our areas.
                ''')

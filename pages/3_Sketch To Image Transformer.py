import streamlit as st
from streamlit_drawable_canvas import st_canvas
import requests
import numpy as np
import time
import pandas as pd
import os
import requests
from google.cloud import storage
from gcs_helper import gcs_list_folders
from gcs_helper import gcs_list_files
from gcs_helper import gcs_download_image_bytes
from cv2 import resize
from PIL import Image

st.set_page_config(
    page_title='Sketchy',
    page_icon=':frame_with_picture:',
    layout="wide",
    initial_sidebar_state="auto",
    menu_items=None)


multi_width = 224
single_width = 336
width  = 120
base_sketch_single = np.full((single_width, single_width, 3), 255)
base_sketch_multi = np.full((multi_width, multi_width, 3), 255)
base_sketch = np.full((224, 224, 3), 255)


int_str = ['0', '1','2','3','4','5','6','7']


storage_client = storage.Client()
bucket = storage_client.bucket('portfolio-site-376821')

selectbox_dont_know_copy = "I don't know yet"


labels = ['airplane', 'alarm_clock', 'ant', 'ape', 'apple', 'armor', 'axe',
        'banana', 'bat', 'bear', 'bee', 'beetle', 'bell', 'bench', 'bicycle',
        'blimp', 'bread', 'butterfly', 'cabin', 'camel', 'candle', 'cannon',
        'car_(sedan)', 'castle', 'cat', 'chair', 'chicken', 'church', 'couch',
        'cow', 'crab', 'crocodilian', 'cup', 'deer', 'dog', 'dolphin', 'door',
        'duck', 'elephant', 'eyeglasses', 'fan', 'fish', 'flower', 'frog',
        'geyser', 'giraffe', 'guitar', 'hamburger', 'hammer', 'harp', 'hat',
        'hedgehog', 'helicopter', 'hermit_crab', 'horse', 'hot-air_balloon',
        'hotdog', 'hourglass', 'jack-o-lantern', 'jellyfish', 'kangaroo',
        'knife', 'lion', 'lizard', 'lobster', 'motorcycle', 'mouse', 'mushroom',
        'owl', 'parrot', 'pear', 'penguin', 'piano', 'pickup_truck', 'pig',
        'pineapple', 'pistol', 'pizza', 'pretzel', 'rabbit', 'raccoon',
        'racket', 'ray', 'rhinoceros', 'rifle', 'rocket', 'sailboat', 'saw',
        'saxophone', 'scissors', 'scorpion', 'sea_turtle', 'seagull', 'seal',
        'shark', 'sheep', 'shoe', 'skyscraper', 'snail', 'snake', 'songbird',
        'spider', 'spoon', 'squirrel', 'starfish', 'strawberry', 'swan',
        'sword', 'table', 'tank', 'teapot', 'teddy_bear', 'tiger', 'tree',
        'trumpet', 'turtle', 'umbrella', 'violin', 'volcano', 'wading_bird',
        'wheelchair', 'windmill', 'window', 'wine_bottle', 'zebra']

labels2 = [selectbox_dont_know_copy] + labels

api_url = 'https://sketchy2-qrozxtxbpa-zf.a.run.app'
prediction_url = api_url + '/classify'
requests.get(api_url) #to activate container
demo_video_url = 'https://youtu.be/bJIvyjlmfcU'
sketchy_url = 'https://github.com/ereztep/portfolio-site/blob/main/pages/3_Sketch%20To%20Image%20Transformer.py'

def normalize_labels(label):
    return label.capitalize().replace("_", " ")

df = None

st.markdown("""## Let's transform your sketches with our AI! :cat:""")
st.write('description bellow- streamlit canvas is not supported inside tabs')


#image_choice = st.radio('I want to see similar:', ('photo', 'sketch'), horizontal = True)
image_choice = 'photo'


col1, col2, col3=st.columns(3)

with col2:
    target = st.selectbox('What do you want to sketch?', labels2, format_func= normalize_labels)

    canvas_result_single = st_canvas(
        fill_color="rgba(255, 165, 0, 0.3)",  # Fixed fill color with some opacity
        stroke_width=3,
        stroke_color="#000000",
        background_color="#FFFFFF",
        background_image=None,
        update_streamlit=True,
        height=single_width,
        width=single_width,
        drawing_mode='freedraw',
        key = 'single'
        )

    if st.button('My sketch looks like...'):

        sketch = canvas_result_single.image_data[:, :, :3]
        sketch_resized = resize(sketch,  dsize=(224, 224))

        if np.all(sketch_resized == base_sketch):
            st.warning('Please sketch something')
            st.stop()
        st.success('Work in progress...')
        sketch_byte = sketch_resized.tobytes()
        response_classes = requests.post(prediction_url, files={'sketch': sketch_byte}).json()

        prediction = np.array(response_classes['prediction'])
        df = pd.DataFrame({'label': labels,
        'proba': prediction[0]}).sort_values(
            'proba',
            ascending = False,
            ignore_index = True
            )


        tmp = {'label': selectbox_dont_know_copy, 'proba': 0.0}
        df = df.append(tmp, ignore_index = True)

if df is not None:

    index_target = df.index[df['label'] == target].tolist()[0]
    proba_target = df.proba[index_target]*100
    prediction = df.label[0]
    proba_prediction = df.proba[0]*100
    second_proba = df.proba[1]*100
    second_label = df.label[1]
    third_label = df.label[2]
    third_proba = df.proba[2]*100

    if prediction == target or target == selectbox_dont_know_copy:

        if response_classes[prediction][0]:

            st.balloons()
            st.markdown(f'''
            # Our AI recognized a {prediction} ({round(proba_prediction, 2)}%)!
            ''')
            with st.spinner(f'Loading {image_choice}'):
                for num in int_str[:4]:
                    with col1:
                        st.image(bucket.blob(f'Sketchy/{prediction}/{response_classes[prediction][0][num]}.jpg').download_as_bytes(), width = witdh)

                for num in int_str[4:]:
                    with col3:
                        st.image(bucket.blob(f'Sketchy/{prediction}/{response_classes[prediction][0][num]}.jpg').download_as_bytes(), width = witdh)



        else:
            st.markdown(f'''
            # Our AI recognized a {prediction} ({round(proba_prediction, 2)}%)!
            ''')
            with st.spinner(f'Loading {image_choice}'):
                first_pred = gcs_list_files(bucket, f'Sketchy/{df.iloc[0, :].label}')
                with col1:
                    st.image(first_pred[np.random.randint(0, len(first_pred))].download_as_bytes(), width = witdh)
                    st.image(first_pred[np.random.randint(0, len(first_pred))].download_as_bytes(), width = witdh)
                    st.image(first_pred[np.random.randint(0, len(first_pred))].download_as_bytes(), width = witdh)
                    st.image(first_pred[np.random.randint(0, len(first_pred))].download_as_bytes(), width = witdh)


                with col3:
                    st.image(first_pred[np.random.randint(0, len(first_pred))].download_as_bytes(), width = witdh)
                    st.image(first_pred[np.random.randint(0, len(first_pred))].download_as_bytes(), width = witdh)
                    st.image(first_pred[np.random.randint(0, len(first_pred))].download_as_bytes(), width = witdh)
                    st.image(first_pred[np.random.randint(0, len(first_pred))].download_as_bytes(), width = witdh)


    else:

        with st.spinner(f'Loading {image_choice}'):
            first_pred = gcs_list_files(bucket, f'Sketchy/{df.iloc[0, :].label}')
            second_pred = gcs_list_files(bucket, f'Sketchy/{df.iloc[1, :].label}')
            third_pred = gcs_list_files(bucket, f'Sketchy/{df.iloc[2, :].label}')

            if proba_prediction >= 96:
                    if target == selectbox_dont_know_copy:
                        st.markdown(f"## Our AI thinks that your sketch looks like {prediction} ({round(proba_prediction, 2)}%).")
                        st.balloons()

                    else:
                        st.markdown(f"## Our AI thought that it's a {prediction} ({round(proba_prediction, 2)}%).")
                        st.markdown(f"{target.capitalize()} is in the {index_target + 1} place with ({round(proba_target,2)}%).")
                        st.markdown("Try again!")

                        st.snow()

                    if response_classes[prediction][0]:
                        for num in int_str[:4]:
                            with col1:
                                st.image(bucket.blob(f'Sketchy/{prediction}/{response_classes[prediction][0][num]}.jpg').download_as_bytes(), width = witdh)

                        for num in int_str[4:]:
                            with col3:
                                st.image(bucket.blob(f'Sketchy/{prediction}/{response_classes[prediction][0][num]}.jpg').download_as_bytes(), width = witdh)

                    else:
                        with col1:
                            st.image(first_pred[np.random.randint(0, len(first_pred))].download_as_bytes(), width = witdh)
                            st.image(first_pred[np.random.randint(0, len(first_pred))].download_as_bytes(), width = witdh)
                            st.image(first_pred[np.random.randint(0, len(first_pred))].download_as_bytes(), width = witdh)
                            st.image(first_pred[np.random.randint(0, len(first_pred))].download_as_bytes(), width = witdh)


                        with col3:
                            st.image(first_pred[np.random.randint(0, len(first_pred))].download_as_bytes(), width = witdh)
                            st.image(first_pred[np.random.randint(0, len(first_pred))].download_as_bytes(), width = witdh)
                            st.image(first_pred[np.random.randint(0, len(first_pred))].download_as_bytes(), width = witdh)
                            st.image(first_pred[np.random.randint(0, len(first_pred))].download_as_bytes(), width = witdh)


            elif 75 < proba_prediction < 96:

                if target == "I want the image search engine":
                    st.markdown(f"## Our AI thinks that your sketch looks like {prediction} ({round(proba_prediction, 2)}%) or a {second_label}.")
                    st.balloons()
                else:
                    st.markdown(f"# It's a {prediction} ({round(proba_prediction, 2)}%) or {second_label} ({round(second_proba, 2)}%)")
                    st.markdown(f"{target.capitalize()} is in the {index_target + 1} place.")
                    st.markdown('Try again!')

                    st.snow()
                if response_classes[prediction][0]:
                    if response_classes[second_pred][0]:

                        for num in int_str[:3]:
                            with col1:
                                st.image(bucket.blob(f'Sketchy/{prediction}/{response_classes[prediction][0][num]}.jpg').download_as_bytes(), width = witdh)

                        for num in int_str[3:6]:
                            with col3:
                                st.image(bucket.blob(f'Sketchy/{prediction}/{response_classes[prediction][0][num]}.jpg').download_as_bytes(), width = witdh)

                        with col1:
                            st.image(bucket.blob(f'Sketchy/{second_pred}/{response_classes[second_pred][0][num]}.jpg').download_as_bytes(), width = witdh)

                        with col3:
                            st.image(bucket.blob(f'Sketchy/{second_pred}/{response_classes[second_pred][0][num]}.jpg').download_as_bytes(), width = witdh)

                else:
                    with col1:
                        st.image(first_pred[np.random.randint(0, len(first_pred))].download_as_bytes(), width = witdh)
                        st.image(first_pred[np.random.randint(0, len(first_pred))].download_as_bytes(), width = witdh)
                        st.image(first_pred[np.random.randint(0, len(first_pred))].download_as_bytes(), width = witdh)
                        st.image(second_pred[np.random.randint(0, len(second_pred))].download_as_bytes(), width = witdh)


                    with col3:
                        st.image(first_pred[np.random.randint(0, len(first_pred))].download_as_bytes(), width = witdh)
                        st.image(first_pred[np.random.randint(0, len(first_pred))].download_as_bytes(), width = witdh)
                        st.image(first_pred[np.random.randint(0, len(first_pred))].download_as_bytes(), width = witdh)
                        st.image(second_pred[np.random.randint(0, len(second_pred))].download_as_bytes(), width = witdh)

            if proba_prediction <= 75:
                if target == "I want the image search engine":
                    st.markdown(f"## Our AI thinks that your sketch looks like {prediction} ({round(proba_prediction, 2)}%), a {second_label} or a {third_label}.")
                    st.balloons()
                else:
                    st.markdown(f"## Work on your sketch skills!")
                    st.markdown(f"### Looks like a {prediction}, a {second_label}, or a {third_label}")
                    st.markdown(f"### {target.capitalize()} only in the {index_target + 1} location.")
                    st.markdown(f"### Try again!")

                    st.snow()
                if response_classes[prediction][0]:
                    if response_classes[second_label][0]:
                        if response_classes[third_label][0]:
                            for num in int_str[0:2]:
                                with col1:
                                    st.image(bucket.blob(f'Sketchy/{prediction}/{response_classes[prediction][0][num]}.jpg').download_as_bytes(), width = witdh)
                                    st.image(bucket.blob(f'Sketchy/{third_label}/{response_classes[third_label][0][num]}.jpg').download_as_bytes(), width = witdh)


                            for num in int_str[2:4]:
                                with col3:
                                    st.image(bucket.blob(f'Sketchy/{prediction}/{response_classes[prediction][0][num]}.jpg').download_as_bytes(), width = witdh)
                                    st.image(bucket.blob(f'Sketchy/{second_label}/{response_classes[second_label][0][num]}.jpg').download_as_bytes(), width = witdh)


                with col1:
                    st.image(first_pred[np.random.randint(0, len(first_pred))].download_as_bytes(), width = witdh)
                    st.image(first_pred[np.random.randint(0, len(first_pred))].download_as_bytes(), width = witdh)
                    st.image(second_pred[np.random.randint(0, len(second_pred))].download_as_bytes(), width = witdh)
                    st.image(second_pred[np.random.randint(0, len(second_pred))].download_as_bytes(), width = witdh)


                with col3:
                    st.image(first_pred[np.random.randint(0, len(first_pred))].download_as_bytes(), width = witdh)
                    st.image(first_pred[np.random.randint(0, len(first_pred))].download_as_bytes(), width = witdh)
                    st.image(third_pred[np.random.randint(0, len(third_pred))].download_as_bytes(), width = witdh)
                    st.image(third_pred[np.random.randint(0, len(third_pred))].download_as_bytes(), width = witdh)

intro_tab, multi_tab, future_tab = st.tabs(['Introduction', 'Sketch Duals', 'Future'])

with intro_tab:
    st.markdown(f'''
                The model was trained on TAU dataset, which contain 125 categories, with photos and sketches for each.
                This is how it works:
                1. You sketch is being sent to a docker image in google containery service.
                2. It is being processed, and sent into 2 models:
                    * Categorical classification model to one of the 125 categories in the data set.
                    * Model that casts it into a common photos-sketches feature space, produced by a triplet model.
                3.The api sends back the classification results and the names of the closest images (If existing)
                4. We take the images from a bucket that is contained on google cloud and present it to you.
                [code is available here]({sketchy_url}).
                ''')
    cols = st.columns(2)
    with cols[0]:
        st.write('Presentation video from "Le Wagon" demo day:')
        st.video(demo_video_url)




# with single_tab:
    # st.markdown("""## Let's transform your sketches with our AI! :cat:""")


    # #image_choice = st.radio('I want to see similar:', ('photo', 'sketch'), horizontal = True)
    # image_choice = 'photo'

    # target = st.selectbox('If you want to practice your sketch skills and see your rating, choose what to sketch:', labels2, format_func= normalize_labels)

    # col1, col2, col3=st.columns(3)

    # with col2:
    #     canvas_result_single = st_canvas(
    #         fill_color="rgba(255, 165, 0, 0.3)",  # Fixed fill color with some opacity
    #         stroke_width=3,
    #         stroke_color="#000000",
    #         background_color="#FFFFFF",
    #         background_image=None,
    #         update_streamlit=True,
    #         height=single_width,
    #         width=single_width,
    #         drawing_mode='freedraw',
    #         key = 'single'
    #         )

    #     if st.button('My sketch looks like...'):

    #         sketch = canvas_result_single.image_data[:, :, :3]
    #         sketch_resized = resize(sketch,  dsize=(224, 224))

    #         if np.all(sketch_resized == base_sketch):
    #             st.warning('Please sketch something')
    #             st.stop()
    #         st.success('Work in progress...')
    #         sketch_byte = sketch_resized.tobytes()
    #         response_classes = requests.post(prediction_url, files={'sketch': sketch_byte}).json()

    #         prediction = np.array(response_classes['prediction'])
    #         df = pd.DataFrame({'label': labels,
    #         'proba': prediction[0]}).sort_values(
    #             'proba',
    #             ascending = False,
    #             ignore_index = True
    #             )


    #         tmp = {'label': selectbox_dont_know_copy, 'proba': 0.0}
    #         df = df.append(tmp, ignore_index = True)

    # if df is not None:

    #     index_target = df.index[df['label'] == target].tolist()[0]
    #     proba_target = df.proba[index_target]*100
    #     prediction = df.label[0]
    #     proba_prediction = df.proba[0]*100
    #     second_proba = df.proba[1]*100
    #     second_label = df.label[1]
    #     third_label = df.label[2]
    #     third_proba = df.proba[2]*100

    #     if prediction == target or target == selectbox_dont_know_copy:

    #         if response_classes[prediction][0]:

    #             st.balloons()
    #             st.markdown(f'''
    #             # Our AI recognized a {prediction} ({round(proba_prediction, 2)}%)!
    #             ''')
    #             with st.spinner(f'Loading {image_choice}'):
    #                 for num in int_str[:4]:
    #                     with col1:
    #                         st.image(bucket.blob(f'Sketchy/{prediction}/{response_classes[prediction][0][num]}.jpg').download_as_bytes(), width = witdh)

    #                 for num in int_str[4:]:
    #                     with col3:
    #                         st.image(bucket.blob(f'Sketchy/{prediction}/{response_classes[prediction][0][num]}.jpg').download_as_bytes(), width = witdh)



    #         else:
    #             st.markdown(f'''
    #             # Our AI recognized a {prediction} ({round(proba_prediction, 2)}%)!
    #             ''')
    #             with st.spinner(f'Loading {image_choice}'):
    #                 first_pred = gcs_list_files(bucket, f'Sketchy/{df.iloc[0, :].label}')
    #                 with col1:
    #                     st.image(first_pred[np.random.randint(0, len(first_pred))].download_as_bytes(), width = witdh)
    #                     st.image(first_pred[np.random.randint(0, len(first_pred))].download_as_bytes(), width = witdh)
    #                     st.image(first_pred[np.random.randint(0, len(first_pred))].download_as_bytes(), width = witdh)
    #                     st.image(first_pred[np.random.randint(0, len(first_pred))].download_as_bytes(), width = witdh)


    #                 with col3:
    #                     st.image(first_pred[np.random.randint(0, len(first_pred))].download_as_bytes(), width = witdh)
    #                     st.image(first_pred[np.random.randint(0, len(first_pred))].download_as_bytes(), width = witdh)
    #                     st.image(first_pred[np.random.randint(0, len(first_pred))].download_as_bytes(), width = witdh)
    #                     st.image(first_pred[np.random.randint(0, len(first_pred))].download_as_bytes(), width = witdh)


    #     else:

    #         with st.spinner(f'Loading {image_choice}'):
    #             first_pred = gcs_list_files(bucket, f'Sketchy/{df.iloc[0, :].label}')
    #             second_pred = gcs_list_files(bucket, f'Sketchy/{df.iloc[1, :].label}')
    #             third_pred = gcs_list_files(bucket, f'Sketchy/{df.iloc[2, :].label}')

    #             if proba_prediction >= 96:
    #                     if target == selectbox_dont_know_copy:
    #                         st.markdown(f"## Our AI thinks that your sketch looks like {prediction} ({round(proba_prediction, 2)}%).")
    #                         st.balloons()

    #                     else:
    #                         st.markdown(f"## Our AI thought that it's a {prediction} ({round(proba_prediction, 2)}%).")
    #                         st.markdown(f"{target.capitalize()} is in the {index_target + 1} place with ({round(proba_target,2)}%).")
    #                         st.markdown("Try again!")

    #                         st.snow()

    #                     if response_classes[prediction][0]:
    #                         for num in int_str[:4]:
    #                             with col1:
    #                                 st.image(bucket.blob(f'Sketchy/{prediction}/{response_classes[prediction][0][num]}.jpg').download_as_bytes(), width = witdh)

    #                         for num in int_str[4:]:
    #                             with col3:
    #                                 st.image(bucket.blob(f'Sketchy/{prediction}/{response_classes[prediction][0][num]}.jpg').download_as_bytes(), width = witdh)

    #                     else:
    #                         with col1:
    #                             st.image(first_pred[np.random.randint(0, len(first_pred))].download_as_bytes(), width = witdh)
    #                             st.image(first_pred[np.random.randint(0, len(first_pred))].download_as_bytes(), width = witdh)
    #                             st.image(first_pred[np.random.randint(0, len(first_pred))].download_as_bytes(), width = witdh)
    #                             st.image(first_pred[np.random.randint(0, len(first_pred))].download_as_bytes(), width = witdh)


    #                         with col3:
    #                             st.image(first_pred[np.random.randint(0, len(first_pred))].download_as_bytes(), width = witdh)
    #                             st.image(first_pred[np.random.randint(0, len(first_pred))].download_as_bytes(), width = witdh)
    #                             st.image(first_pred[np.random.randint(0, len(first_pred))].download_as_bytes(), width = witdh)
    #                             st.image(first_pred[np.random.randint(0, len(first_pred))].download_as_bytes(), width = witdh)


    #             elif 75 < proba_prediction < 96:

    #                 if target == "I want the image search engine":
    #                     st.markdown(f"## Our AI thinks that your sketch looks like {prediction} ({round(proba_prediction, 2)}%) or a {second_label}.")
    #                     st.balloons()
    #                 else:
    #                     st.markdown(f"# It's a {prediction} ({round(proba_prediction, 2)}%) or {second_label} ({round(second_proba, 2)}%)")
    #                     st.markdown(f"{target.capitalize()} is in the {index_target + 1} place.")
    #                     st.markdown('Try again!')

    #                     st.snow()
    #                 if response_classes[prediction][0]:
    #                     if response_classes[second_pred][0]:

    #                         for num in int_str[:3]:
    #                             with col1:
    #                                 st.image(bucket.blob(f'Sketchy/{prediction}/{response_classes[prediction][0][num]}.jpg').download_as_bytes(), width = witdh)

    #                         for num in int_str[3:6]:
    #                             with col3:
    #                                 st.image(bucket.blob(f'Sketchy/{prediction}/{response_classes[prediction][0][num]}.jpg').download_as_bytes(), width = witdh)

    #                         with col1:
    #                             st.image(bucket.blob(f'Sketchy/{second_pred}/{response_classes[second_pred][0][num]}.jpg').download_as_bytes(), width = witdh)

    #                         with col3:
    #                             st.image(bucket.blob(f'Sketchy/{second_pred}/{response_classes[second_pred][0][num]}.jpg').download_as_bytes(), width = witdh)

    #                 else:
    #                     with col1:
    #                         st.image(first_pred[np.random.randint(0, len(first_pred))].download_as_bytes(), width = witdh)
    #                         st.image(first_pred[np.random.randint(0, len(first_pred))].download_as_bytes(), width = witdh)
    #                         st.image(first_pred[np.random.randint(0, len(first_pred))].download_as_bytes(), width = witdh)
    #                         st.image(second_pred[np.random.randint(0, len(second_pred))].download_as_bytes(), width = witdh)


    #                     with col3:
    #                         st.image(first_pred[np.random.randint(0, len(first_pred))].download_as_bytes(), width = witdh)
    #                         st.image(first_pred[np.random.randint(0, len(first_pred))].download_as_bytes(), width = witdh)
    #                         st.image(first_pred[np.random.randint(0, len(first_pred))].download_as_bytes(), width = witdh)
    #                         st.image(second_pred[np.random.randint(0, len(second_pred))].download_as_bytes(), width = witdh)

    #             if proba_prediction <= 75:
    #                 if target == "I want the image search engine":
    #                     st.markdown(f"## Our AI thinks that your sketch looks like {prediction} ({round(proba_prediction, 2)}%), a {second_label} or a {third_label}.")
    #                     st.balloons()
    #                 else:
    #                     st.markdown(f"## Work on your sketch skills!")
    #                     st.markdown(f"### Looks like a {prediction}, a {second_label}, or a {third_label}")
    #                     st.markdown(f"### {target.capitalize()} only in the {index_target + 1} location.")
    #                     st.markdown(f"### Try again!")

    #                     st.snow()
    #                 if response_classes[prediction][0]:
    #                     if response_classes[second_label][0]:
    #                         if response_classes[third_label][0]:
    #                             for num in int_str[0:2]:
    #                                 with col1:
    #                                     st.image(bucket.blob(f'Sketchy/{prediction}/{response_classes[prediction][0][num]}.jpg').download_as_bytes(), width = witdh)
    #                                     st.image(bucket.blob(f'Sketchy/{third_label}/{response_classes[third_label][0][num]}.jpg').download_as_bytes(), width = witdh)


    #                             for num in int_str[2:4]:
    #                                 with col3:
    #                                     st.image(bucket.blob(f'Sketchy/{prediction}/{response_classes[prediction][0][num]}.jpg').download_as_bytes(), width = witdh)
    #                                     st.image(bucket.blob(f'Sketchy/{second_label}/{response_classes[second_label][0][num]}.jpg').download_as_bytes(), width = witdh)


    #                 with col1:
    #                     st.image(first_pred[np.random.randint(0, len(first_pred))].download_as_bytes(), width = witdh)
    #                     st.image(first_pred[np.random.randint(0, len(first_pred))].download_as_bytes(), width = witdh)
    #                     st.image(second_pred[np.random.randint(0, len(second_pred))].download_as_bytes(), width = witdh)
    #                     st.image(second_pred[np.random.randint(0, len(second_pred))].download_as_bytes(), width = witdh)


    #                 with col3:
    #                     st.image(first_pred[np.random.randint(0, len(first_pred))].download_as_bytes(), width = witdh)
    #                     st.image(first_pred[np.random.randint(0, len(first_pred))].download_as_bytes(), width = witdh)
    #                     st.image(third_pred[np.random.randint(0, len(third_pred))].download_as_bytes(), width = witdh)
    #                     st.image(third_pred[np.random.randint(0, len(third_pred))].download_as_bytes(), width = witdh)

with multi_tab:
    st.markdown("""## Sketch Duall! :crossed_swords:""")
    st.write('Streamlit canvas currently is not supported inside the tabs, I decided to put it here as concept demonstration')


    selected_category = st.selectbox('Choose category...', labels, format_func = normalize_labels)
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""## Draw Player 1! :cat:""")

        canvas_result_1 = st_canvas(
            fill_color="rgba(255, 165, 0, 0.3)",  # Fixed fill color with some opacity
            stroke_width=3,
            stroke_color="#000000",
            background_color="#FFFFFF",
            update_streamlit=True,
            height= multi_width,
            width= multi_width,
            drawing_mode="freedraw",
            point_display_radius= 0,
            key = 'multiple1'
            )

    with col2:
        st.markdown("""## Draw Player 2! :dog:""")

        canvas_result_2 = st_canvas(
            fill_color="rgba(255, 165, 0, 0.3)",  # Fixed fill color with some opacity
            stroke_width=3,
            stroke_color="#000000",
            background_color="#FFFFFF",
            update_streamlit=True,
            height= multi_width,
            width= multi_width,
            drawing_mode="freedraw",
            point_display_radius= 0,
            key = 'multiple2'
            )

    with st.container():
        btm1, btm2, btm3 = st.columns(3)
        with btm2:
            if st.button('who will pay for the drinks?!'):
                sketch1 = canvas_result_1.image_data[:, :, :3]
                sketch2 = canvas_result_2.image_data[:, :, :3]
                if np.all(sketch1 == base_sketch_multi) or np.all(sketch2 == base_sketch_multi) :
                    st.warning('Please sketch something')
                    st.stop()

                im1 = Image.fromarray(sketch1)
                im1.thumbnail((224,224), Image.ANTIALIAS)
                np_im1 = np.array(im1)
                sketch_byte1 = np_im1[:,:,:3].tobytes()
                response1 = requests.post(prediction_url, files={'sketch': sketch_byte1}).json()
                prediction1 = np.array(response1['prediction'])

                im2 = Image.fromarray(sketch2)
                im2.thumbnail((224,224), Image.ANTIALIAS)
                np_im2 = np.array(im2)
                sketch_byte2 = np_im2[:,:,:3].tobytes()
                response2 = requests.post(prediction_url, files={'sketch': sketch_byte2}).json()
                prediction2 = np.array(response2['prediction'])

                df = pd.DataFrame({'label': labels,
                'proba1': prediction1[0],
                'proba2': prediction2[0]}).sort_values(
                        'proba1',
                        ascending = False,
                        ignore_index = True
                        )

                row = df.loc[df['label'] == selected_category]
                with col1:
                    st.markdown(f'### Score: {round(row.proba1.iloc[0]*100, 2)}%')
                with col2:
                    st.markdown(f'### Score: {round(row.proba2.iloc[0]*100, 2)}%')

                if row.proba1.iloc[0] < row.proba2.iloc[0]:
                    st.markdown('## Player 1 pays for the drinks! :tada:')
                else:
                    st.markdown('## Player 2 pays for the drinks! :tada:')
                st.balloons()
        audio_file = open('other/dramatic.mp3', 'rb')
        audio_bytes = audio_file.read()

        st.audio(audio_bytes, format='audio/ogg', start_time = 2)

with future_tab:
    st.markdown('''
                ### Possible improvements to this page will be:
                * Finish the training of the model and complete the feature space for every category
                * Make the code more robust and maintainable, by:
                   * Holding the copy writing in variables and change it only once
                   * Defining the control flow better
                   * Building a professional UI
                * Possible use cases:
                   * Integrate commercials and deploy it as a game
                   * After full training, transforming it to a full interface of sketch-to-image
                   * Draw training
                ''')

import streamlit as st

st.set_page_config(
    page_title='References',
    layout="wide",
    initial_sidebar_state="auto",
    menu_items=None)

st.header('References and Reccomendation Letters')
st.write('I am sorry, I am collecting approvals to present the reccomendations here with links to the reccomender.')
st.write('I must be very excited to apply if I have sent it to you before! ')

# references = {'Tech': ['William', 'Yehonadav Yekoutiel (I need)', 'Joao Semao', 'Carsten (asked, I need)'], 'Lead and Social Enterprises': ['Eliav Zacay', 'Karin Malka', 'Yarden Lam', 'Someone from 121'],'University': ['Shoshi Marinov (asked, I need)'], 'Army': ['Noa Berkovitz (they are)', 'Ofer Simha (they are)', 'Alon Nissani (asked)']}
# references_tabs = ['Introduction'] + list(references.keys())
# tabs = st.tabs(references_tabs)

# for i, tab in enumerate(tabs):
#     with tab:
#         if i == 0:
#             st.markdown("In this page you can find letters of reccomendation divided by field, from my employers, superiors, and partners")

#         else:
#             tab_name = references_tabs[i]
#             references_of_tab = references[tab_name]
#             st.write(references_of_tab)

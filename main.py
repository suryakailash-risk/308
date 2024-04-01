import streamlit as st
from pymongo import MongoClient
import datetime
from bson.objectid import ObjectId
import pandas as pd
import certifi
ca = certifi.where()
DB_USERNAME=st.secrets.db_credentials['username']
KEY=st.secrets.db_credentials['password']
client = MongoClient(f'mongodb+srv://{DB_USERNAME}:{KEY}@cluster0.jyel19j.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0', tlsCAFile=ca)
try: 
    db = client.Login
    db.create_collection('Users') 
except Exception as e:
    print(f"An error occurred: {e}")

try: 
    db = client.Login
    db.create_collection('Split') 
except Exception as e:
    print(f"An error occurred: {e}")
# streamlit_app.py

import hmac
import streamlit as st

tempusername=""
def check_password():
    """Returns `True` if the user had a correct password."""

    def login_form():
        """Form with widgets to collect user information"""
        with st.form("Credentials"):
            tempusername=st.text_input("Username", key="username")
            st.text_input("Password", type="password", key="password")
            st.form_submit_button("Log in", on_click=password_entered)
            collection_user = db.Split
            users_details = collection_user.find({"payto":tempusername,"paid":False})
            users_details = pd.DataFrame(list(users_details))
            # tempusername=users_details['name']
            print(users_details)

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if st.session_state["username"] in st.secrets[
            "passwords"
        ] and hmac.compare_digest(
            st.session_state["password"],
            st.secrets.passwords[st.session_state["username"]],
        ):
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # Don't store the username or password.
        else:
            st.session_state["password_correct"] = False

    # Return True if the username + password is validated.
    if st.session_state.get("password_correct", False):
        return True

    # Show inputs for username + password.
    login_form()
    if "password_correct" in st.session_state:
        st.error("😕 User not known or password incorrect")
    return False


if not check_password():
    st.stop()

# Main Streamlit app starts here
hide_streamlit_style = """
                <style>
                #MainMenu {visibility: hidden;}
                footer {visibility: hidden;}
                </style>
                """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)
st.title('Budget Application')
st.sidebar.title('Menu')
menu = st.sidebar.radio('Select an option', ['You Owe Me', 'Add Split','Person','I Owe You','My Budget'])
if menu == 'You Owe Me':
    option = st.selectbox("Select", ("Yet to get Payment", "Have already paid"), placeholder="Select contact method...",)
    if option == "Yet to get Payment":
        collection = db.Split
        users = collection.find({"payto":tempusername,"paid":False})
        temp=0
        for item in users:
            col1, col2,col3 = st.columns(3)
            with col1:
                    item['shop']
            with col2:
                    item['name']
            with col3:
                    item['cost']  
                    agree = st.checkbox(f"{item['shop']} - {item['cost']} ",value=item['paid']) 
            if st.button(f"Submit Update Item {temp}"):
                myquery = {"_id": ObjectId(item['_id'])}
                newvalues = {"$set": {"paid": agree,"updated":datetime.datetime.now()}}
                collection = db.Split
                collection.update_one(myquery, newvalues)
            temp=temp+1
    if option == "Have already paid":
        collection = db.Split
        users = collection.find({"payto":tempusername,"paid":True})
        temp=0
        for item in users:
            col1, col2,col3 = st.columns(3)
            with col1:
                    item['shop']
            with col2:
                    item['name']
            with col3:
                    item['cost']  
                    agree = st.checkbox(f"{item['shop']} - {item['cost']} ",value=item['paid']) 
            if st.button(f"Submit Update Item {temp}"):
                myquery = {"_id": ObjectId(item['_id'])}
                newvalues = {"$set": {"paid": agree,"updated":datetime.datetime.now()}}
                collection = db.Split
                collection.update_one(myquery, newvalues)
            temp=temp+1  
elif menu == 'Add Split':
    collection = db.Users
    users = collection.find()
    res=[]
    for user in users:
        res.append(user['name'])
    collection = db.Split
    if 'num_field_pairs' not in st.session_state:
        st.session_state.num_field_pairs = 1
    def add_field_pair():
        st.session_state.num_field_pairs += 1
    def remove_field_pair():
        st.session_state.num_field_pairs = max(1, st.session_state.num_field_pairs - 1)

    st.subheader('Add a new item')
    item_name = st.text_input('Shop')
    item_cost = st.number_input('Item Cost', min_value=0)
    date_shopping = st.date_input("Date of shopping")

    datetime_obj = datetime.datetime.combine(date_shopping, datetime.time.min)

    col1, col2 = st.columns(2)
    with col1:
        st.button("Add Field", on_click=add_field_pair)
    with col2:
        st.button("Remove Field", on_click=remove_field_pair)

    for i in range(1, st.session_state.num_field_pairs + 1):
        with st.container():
            col1, col2 = st.columns(2)
            with col1:
                st.selectbox('Who has to pay',res,key=f"text_field_{i}")
            with col2:
                st.number_input(f"Number Field {i}", key=f"number_field_{i}")
    text_inputs = [st.session_state[f"text_field_{i}"] for i in range(1, st.session_state.num_field_pairs + 1)]
    number_inputs = [st.session_state[f"number_field_{i}"] for i in range(1, st.session_state.num_field_pairs + 1)]
    # st.write("Current Text Inputs:", text_inputs)
    # st.write("Current Number Inputs:", number_inputs)
    paid_by= st.selectbox(
    'Who paid',res)
    if st.button('Add Item'):
        for i in range(len(text_inputs)):
            collection.insert_one({'shop':item_name,'totalcost':item_cost,'date':datetime_obj,'name': text_inputs[i], 'cost': number_inputs[i], 'payto':paid_by,'paid':False})
        st.success('Item added successfully!')


elif menu == 'Person':
    if tempusername=="Surya":
        person_id = st.text_input('Enter Person Name')
        person_username = st.text_input('Enter Person Username')
        person_phone = st.text_input('Enter Person Phone')
        person_email = st.text_input('Enter Person Email')
        person_roomid = st.text_input('Enter Person RoomID')
        person_password = st.text_input('Enter Person Password')
        if  st.button('Save Details'):
            collection = db.Users
            new_user = {
            "name":person_id,
            "username": person_username,
            "phone_number": person_phone,
            "emailid": person_email,
            "roomid":person_roomid,
            "password":person_password
            }
            result = collection.insert_one(new_user)

elif menu == 'I Owe You':
    collection = db.Split
    users = collection.find({"name":tempusername,"paid":False})
    temp=0
    for item in users:
        col1, col2,col3 = st.columns(3)
        with col1:
                item['shop']
        with col2:
                item['name']
        with col3:
                item['cost']  

elif menu == 'My Budget':
    start_date = st.date_input('Start date',value=datetime.date.today())
    start_date = datetime.datetime.combine(start_date, datetime.time.min)
    end_date = st.date_input('End date')
    end_date = datetime.datetime.combine(end_date, datetime.time.min)
    myquery = {}
    if  st.button("Search"):
        collection = db.Split
        users = collection.find({"name":tempusername,"date": {"$gte": start_date, "$lte": end_date}})
        temp=0
        df = pd.DataFrame(list(users))
        del df["_id"]
        del df["name"]
        del df["totalcost"]
        edited_df = st.data_editor(df)
        import matplotlib.pyplot as plt

        # Your data
        sizes = list(df['cost'])
        labels = list(df['shop'])

        # Create a pie chart
        fig, ax = plt.subplots()
        ax.pie(sizes, labels=labels, autopct='%1.1f%%')

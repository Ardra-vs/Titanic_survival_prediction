import streamlit as st
import pickle
import pymysql
import base64

# PAGE CONFIGURATION
st.set_page_config(
    page_title="Titanic Survival Prediction",)

# LOAD BACKGROUND IMAGE
with open("titanic.jpg", "rb") as f:
    image_base64 = base64.b64encode(f.read()).decode()

#CUSTOM CSS
st.markdown(f"""
<style>
.stApp {{
    background-color: #f0f5f9;
}}

.block-container {{
    padding-top: 1.5rem;
    max-width: 1200px;
}}

/* Heading */
.header {{
    background: linear-gradient(90deg, #102a43, #176b87);
    padding: 25px;
    border-radius: 15px;
    text-align: center;
    margin-bottom: 25px;
}}

.header h1 {{
    color: white;
    font-size: 36px;
    margin-bottom: 5px;
}}

.header p {{
    color: #d9edf7;
    font-size: 16px;
}}

/* Titanic image behind passenger input area */
.st-key-passenger_form {{
    background-image:
        linear-gradient(
            rgba(10, 30, 50, 0.48),
            rgba(10, 30, 50, 0.48)
        ),
        url("data:image/jpeg;base64,{image_base64}");
    background-size: cover;
    background-position: center;
    background-repeat: no-repeat;
    padding: 28px;
    border-radius: 18px;
    border: 1px solid #dce6ed;
}}

/* Passenger section heading */
.passenger-title {{
    color: white;
    font-size: 27px;
    font-weight: bold;
}}

.passenger-description {{
    color: white;
    font-size: 16px;
    margin-bottom: 18px;
}}

/* Input labels */
.st-key-passenger_form label {{
    color: white !important;
    font-weight: 600 !important;
}}

/* Input fields */
.st-key-passenger_form div[data-baseweb="select"] > div,
.st-key-passenger_form div[data-baseweb="input"] > div {{
    background-color: white;
    border-radius: 8px;
}}

/* Predict button */
div.stButton > button {{
    background-color: #176b87;
    color: white;
    border-radius: 10px;
    border: none;
    height: 48px;
    font-size: 17px;
    font-weight: bold;
    width: 100%;
}}

div.stButton > button:hover {{
    background-color: #102a43;
    color: white;
}}

/* Prediction results */
.result-success {{
    background-color: #d9f5e5;
    color: #176b3a;
    padding: 22px;
    border-radius: 12px;
    text-align: center;
    font-size: 25px;
    font-weight: bold;
}}

.result-failure {{
    background-color: #fde8e7;
    color: #a93226;
    padding: 22px;
    border-radius: 12px;
    text-align: center;
    font-size: 25px;
    font-weight: bold;
}}

/* Footer */
.footer {{
    text-align: center;
    color: #64748b;
    padding: 20px;
    font-size: 14px;
}}
</style>
""", unsafe_allow_html=True)


#DATABASE FUNCTION
def save_data(values):
    conn = pymysql.connect(
        host="localhost",
        user="root",
        password="your_password",
        db="titanic_db"
    )

    try:
        with conn.cursor() as cursor:
            q1 = """insert into titanic_his(Pclass, Sex, Age, SibSp, Parch, Fare, Embarked, result) values(%s, %s, %s, %s, %s, %s, %s, %s)"""
            cursor.execute(q1, values)
        conn.commit()
    finally:
        conn.close()

# MAIN FUNCTION
def main():
# Heading
    st.markdown("""
    <div class="header">
        <h1>TITANIC SURVIVAL PREDICTION</h1>
        <p>Machine Learning Based Passenger Survival Analysis</p>
    </div>
    """, unsafe_allow_html=True)
# Passenger form with Titanic background
    with st.container(key="passenger_form"):
        st.markdown(
            '<div class="passenger-title">👤 Passenger Details</div>',
            unsafe_allow_html=True
        )
        st.markdown(
            '<div class="passenger-description">'
            'Enter passenger information to predict the survival result.'
            '</div>',
            unsafe_allow_html=True
        )

        col1= st.columns(1)[0]
        with col1:
            Pclass = st.selectbox("Passenger Class",[1, 2, 3],
                                  format_func=lambda x: {1: "1 - First Class",2: "2 - Second Class",3: "3 - Third Class"}[x])

            Sex = st.selectbox("Gender",["male", "female"])

            Age = st.number_input("Age",min_value=0.0,max_value=100.0,step=1.0)

            SibSp = st.number_input("Siblings / Spouses",min_value=0,max_value=20,value=0)

            Parch = st.number_input("Parents / Children",min_value=0,max_value=20,value=0)

            Fare = st.number_input("Ticket Fare",min_value=0.0,step=1.0)

            Embarked = st.selectbox("Port of Embarkation",["C", "Q", "S"],
                                    format_func=lambda x: {"C": "C - Cherbourg","Q": "Q - Queenstown","S": "S - Southampton"}[x])

        st.markdown("---")
        pred = st.button("Predict")

# PREDICTION
    if pred:
        try:
            Sex_male = 1 if Sex == "male" else 0
            Embarked_Q = 1 if Embarked == "Q" else 0
            Embarked_S = 1 if Embarked == "S" else 0

            # Keep feature order identical to model training
            feature = [
                Pclass, Age, SibSp, Parch, Fare,
                Sex_male, Embarked_Q, Embarked_S
            ]

            with open("Titanic_model.sav", "rb") as f:
                model = pickle.load(f)

            with open("Titanic_scaler.sav", "rb") as f:
                scaler = pickle.load(f)

            scaled_feature = scaler.transform([feature])
            result = int(model.predict(scaled_feature)[0])

            st.markdown("---")
            st.write("Prediction Result")

            if result == 0:
                st.markdown("""
                <div class="result-failure">
                    Passenger Not Survived
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div class="result-success">
                    Passenger Survived
                </div>
                """, unsafe_allow_html=True)

            st.caption(
                "This is a model prediction, not a guarantee of the actual outcome."
            )

            # Save prediction to MySQL
            values = [Pclass, Sex, Age, SibSp,Parch, Fare, Embarked, result]
            try:
                save_data(values)
                st.success("Prediction details saved successfully ")
            except Exception as e:
                st.error(f"Database error: {e}")

        except Exception as e:
            st.error(f"Prediction error: {e}")


main()

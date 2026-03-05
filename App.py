from supabase import create_client
import streamlit as st
import os, nltk
import pandas as pd  # already imported, just in case

# Connect to Supabase using secrets.toml
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
# Ensure nltk data is saved locally in project folder
nltk_data_dir = os.path.join(os.getcwd(), "nltk_data")
os.makedirs(nltk_data_dir, exist_ok=True)
nltk.data.path.append(nltk_data_dir)

# Download required NLTK datasets
nltk.download('stopwords', download_dir=nltk_data_dir)

# After this, import modules that depend on stopwords


# Safe patch: make PyResparser use the correct SpaCy model
import pandas as pd
import base64, random
import time, datetime
from pdfminer.high_level import extract_text
import io, random
from streamlit_tags import st_tags
from PIL import Image
from Courses import ds_course, web_course, android_course, ios_course, uiux_course, resume_videos, interview_videos
import plotly.express as px
import re

def simple_parse(text):
    data = {}

    # emails
    emails = re.findall(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", text)
    data["email"] = emails[0] if emails else ""

    # phone numbers
    phones = re.findall(r"\+?\d[\d\-\s]{8,}\d", text)
    data["phone"] = phones[0] if phones else ""

    # name guess — take the first non‑empty line
    lines = [l.strip() for l in text.split("\n") if l.strip()]
    data["name"] = lines[0] if lines else ""

    # skill matching (basic list)
    key_skills = ["python","javascript","java","sql","html","css",
                  "machine learning","deep learning","react",
                  "django","node","flask"]
    found_skills = []
    lowered = text.lower()
    for skill in key_skills:
        if skill.lower() in lowered:
            found_skills.append(skill)
    data["skills"] = list(set(found_skills))

    return data


def get_table_download_link(df, filename, text):
    """Generates a link allowing the data in a given panda dataframe to be downloaded
    in:  dataframe
    out: href string
    """
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()  # some strings <-> bytes conversions necessary here
    # href = f'<a href="data:file/csv;base64,{b64}">Download Report</a>'
    href = f'<a href="data:file/csv;base64,{b64}" download="{filename}">{text}</a>'
    return href


def pdf_reader(file):
    resource_manager = PDFResourceManager()
    fake_file_handle = io.StringIO()
    converter = TextConverter(resource_manager, fake_file_handle, laparams=LAParams())
    page_interpreter = PDFPageInterpreter(resource_manager, converter)
    with open(file, 'rb') as fh:
        for page in PDFPage.get_pages(fh,
                                      caching=True,
                                      check_extractable=True):
            page_interpreter.process_page(page)
            print(page)
        text = fake_file_handle.getvalue()

    # close open handles
    converter.close()
    fake_file_handle.close()
    return text


def show_pdf(file_path):
    with open(file_path, "rb") as f:
        base64_pdf = base64.b64encode(f.read()).decode('utf-8')
    # pdf_display = f'<embed src="data:application/pdf;base64,{base64_pdf}" width="700" height="1000" type="application/pdf">'
    pdf_display = F'<iframe src="data:application/pdf;base64,{base64_pdf}" width="700" height="1000" type="application/pdf"></iframe>'
    st.markdown(pdf_display, unsafe_allow_html=True)


def course_recommender(course_list):
    st.subheader("**Courses & Certificates🎓 Recommendations**")
    c = 0
    rec_course = []
    no_of_reco = st.slider('Choose Number of Course Recommendations:', 1, 10, 4)
    random.shuffle(course_list)
    for c_name, c_link in course_list:
        c += 1
        st.markdown(f"({c}) [{c_name}]({c_link})")
        rec_course.append(c_name)
        if c == no_of_reco:
            break
    return rec_course





def insert_data(name, email, res_score, timestamp, no_of_pages, reco_field, cand_level, skills, recommended_skills,
                courses):
    DB_table_name = 'user_data'
    insert_sql = "insert into " + DB_table_name + """
    values (0,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
    rec_values = (
    name, email, str(res_score), timestamp, str(no_of_pages), reco_field, cand_level, skills, recommended_skills,
    courses)
    cursor.execute(insert_sql, rec_values)
    connection.commit()


st.set_page_config(
    page_title="Smart Resume Analyzer",
    page_icon='SRA_Logo.ico',
)


def run():
    st.title("Smart Resume Analyser")
    st.sidebar.markdown("# Choose User")
    activities = ["User", "Admin"]
    choice = st.sidebar.selectbox("Choose among the given options:", activities)
    # link = '[©Developed by Spidy20](http://github.com/spidy20)'
    # st.sidebar.markdown(link, unsafe_allow_html=True)
    from PIL import Image

    img = Image.open("SRA_Logo.jpg")
    img = img.resize((250, 250))
    st.image(img)
    # Initialize SQLite database
    


    if choice == 'User':
        # st.markdown('''<h4 style='text-align: left; color: #d73b5c;'>* Upload your resume, and get smart recommendation based on it."</h4>''',
        #             unsafe_allow_html=True)
        pdf_file = st.file_uploader("Choose your Resume", type=["pdf"])
        if pdf_file is not None:
            # with st.spinner('Uploading your Resume....'):
            #     time.sleep(4)
            import os
            import base64

# Create folder and save uploaded resume
            folder = "Uploaded_Resumes"
            os.makedirs(folder, exist_ok=True)

            save_path = os.path.join(folder, pdf_file.name)
            with open(save_path, "wb") as f:
               f.write(pdf_file.getbuffer())

# Display PDF using base64 iframe
            import fitz  # PyMuPDF
            from PIL import Image

# Convert each page of the PDF to images
            doc = fitz.open(save_path)

# Loop through all pages and display
            for page_number in range(len(doc)):
               page = doc.load_page(page_number)
               pix = page.get_pixmap()
               img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
               st.image(img, caption=f"Page {page_number+1}", use_column_width=True)


            from pdfminer.high_level import extract_text

            resume_text = extract_text(save_path)

        # ────────────────
        # Simple parsing
        # ────────────────
            resume_data = simple_parse(resume_text)

        # ────────────────
        # Display the parsed info
        # ────────────────
            st.subheader("📌 Extracted Resume Info")
            st.text("Name: " + resume_data.get("name", "Not found"))
            st.text("Email: " + resume_data.get("email", "Not found"))
            st.text("Phone: " + resume_data.get("phone", "Not found"))
            st.text("Skills: " + ", ".join(resume_data.get("skills", [])))

        # Optional confirmation message
            if resume_data:
                st.success("Resume parsed successfully!")

    # Candidate level detection
                cand_level = ''
                page_count = len(doc) if 'doc' in locals() else 0

                if page_count == 1:
                    cand_level = "Fresher"
                    st.markdown("<h4 style='color:#d73b5c;'>You are a Fresher.</h4>", unsafe_allow_html=True)

                elif page_count == 2:
                    cand_level = "Intermediate"
                    st.markdown("<h4 style='color:#1ed760;'>You are at intermediate level!</h4>", unsafe_allow_html=True)

                elif page_count >= 3:
                    cand_level = "Experienced"
                    st.markdown("<h4 style='color:#fba171;'>You are at experienced level!</h4>", unsafe_allow_html=True)


                st.subheader("**Skills Recommendation💡**")

                skills_list = resume_data.get("skills", [])

                if not skills_list:
                    st.warning("No skills were detected in your resume yet — we couldn’t recommend anything.")

                else:
                    keywords = st_tags(
                        label='### Skills that you have',
                        text='See our skills recommendation',
                        value=skills_list,
                        suggestions=[],
                        key='1'
                    )

        # Skill categories
                    ds_keyword = ['tensorflow','keras','pytorch','machine learning','deep learning','flask','streamlit']
                    web_keyword = ['react','django','node js','php','laravel','magento','wordpress','javascript','angular js','c#']
                    android_keyword = ['android','android development','flutter','kotlin','xml','kivy']
                    ios_keyword = ['ios','ios development','swift','cocoa','xcode']
                    uiux_keyword = ['ux','figma','adobe xd','wireframes','user experience']

                    recommended_skills = []
                    reco_field = ''
                    rec_course = []

                    for skill in skills_list:

                        s = skill.lower()

                        if s in ds_keyword:
                            reco_field = 'Data Science'
                            recommended_skills = ['Machine Learning','Deep Learning','Tensorflow','Keras','Scikit-learn']
                            rec_course = ds_course
                            break

                        elif s in web_keyword:
                            reco_field = 'Web Development'
                            recommended_skills = ['React','Django','Node JS','JavaScript']
                            rec_course = web_course
                            break

                        elif s in android_keyword:
                            reco_field = 'Android Development'
                            recommended_skills = ['Android','Kotlin','Flutter']
                            rec_course = android_course
                            break

                        elif s in ios_keyword:
                            reco_field = 'iOS Development'
                            recommended_skills = ['Swift','Xcode','iOS']
                            rec_course = ios_course
                            break

                        elif s in uiux_keyword:
                            reco_field = 'UI-UX Development'
                            recommended_skills = ['Figma','Adobe XD','User Experience']
                            rec_course = uiux_course
                            break


                    if reco_field:
                        st.success(f"Our analysis says you are looking for **{reco_field} Jobs**")

                        st.text("Suggested skills to add:")
                        for rs in recommended_skills:
                            st.write("• " + rs)

                    if rec_course:
                        st.subheader("📚 Recommended Courses & Certificates")
                        course_recommender(rec_course)

                    else:
                        st.info("We could not identify a matching job category from your skills yet.")


    # ===============================
    # Resume Tips Section
    # ===============================

                st.subheader("**Resume Tips & Ideas💡**")

                resume_score = 0

    # Objective
                if 'objective' in resume_text.lower():
                    resume_score += 20
                    st.markdown("<h4 style='color:#1ed760;'>[+] Objective section detected!</h4>", unsafe_allow_html=True)
                else:
                    st.markdown("<h4 style='color:#fabc10;'>[-] Add a career objective.</h4>", unsafe_allow_html=True)

    # Declaration
                if 'declaration' in resume_text.lower():
                    resume_score += 20
                    st.markdown("<h4 style='color:#1ed760;'>[+] Declaration section present!</h4>", unsafe_allow_html=True)
                else:
                    st.markdown("<h4 style='color:#fabc10;'>[-] Add a declaration section.</h4>", unsafe_allow_html=True)

    # Hobbies
                if 'hobbies' in resume_text.lower() or 'interests' in resume_text.lower():
                    resume_score += 20
                    st.markdown("<h4 style='color:#1ed760;'>[+] Hobbies / Interests found!</h4>", unsafe_allow_html=True)
                else:
                    st.markdown("<h4 style='color:#fabc10;'>[-] Add hobbies or interests.</h4>", unsafe_allow_html=True)

    # Achievements
                if 'achievements' in resume_text.lower():
                    resume_score += 20
                    st.markdown("<h4 style='color:#1ed760;'>[+] Achievements listed!</h4>", unsafe_allow_html=True)
                else:
                    st.markdown("<h4 style='color:#fabc10;'>[-] Add achievements.</h4>", unsafe_allow_html=True)

    # Projects
                if 'projects' in resume_text.lower():
                    resume_score += 20
                    st.markdown("<h4 style='color:#1ed760;'>[+] Projects are included!</h4>", unsafe_allow_html=True)
                else:
                    st.markdown("<h4 style='color:#fabc10;'>[-] Add projects.</h4>", unsafe_allow_html=True)


    # ===============================
    # Resume Score UI
    # ===============================

                st.subheader("**Resume Score📝**")

                st.markdown("""
                <style>
                .stProgress > div > div > div > div {
                    background-color: #d73b5c;
                }
                </style>
                """, unsafe_allow_html=True)

                my_bar = st.progress(0)

                for percent_complete in range(resume_score + 1):
                    time.sleep(0.02)
                    my_bar.progress(percent_complete)

                st.success(f"Your Resume Writing Score: **{resume_score}**")
                st.warning("This score is calculated based on resume content.")

                if resume_score >= 20:
                    st.balloons()
    # ===============================
    # Insert into Supabase
    # ===============================

                ts = time.time()

                cur_date = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d')
                cur_time = datetime.datetime.fromtimestamp(ts).strftime('%H:%M:%S')

                timestamp = str(cur_date + '_' + cur_time)

                res = supabase.table("resumes").insert({

                    "name": resume_data.get("name",""),
                    "email": resume_data.get("email",""),
                    "resume_score": resume_score,
                    "timestamp": timestamp,
                    "page_count": page_count,
                    "predicted_field": reco_field,
                    "user_level": cand_level,
                    "skills": "; ".join(resume_data.get("skills",[])),
                    "recommended_skills": "; ".join(recommended_skills),
                    "recommended_courses": str(rec_course)

                }).execute()

                st.subheader("Insert Response")
                st.write(res)

    # ===============================
    # Fetch All Resumes
    # ===============================
                data = supabase.table("resumes").select("*").execute()

                st.subheader("Fetch All Resumes")
                st.write(data)
    else:
        
    ## Admin Side Without Database
               
                        st.success("Admin Panel")

                        ad_user = st.text_input("Admin Username")
                        ad_password = st.text_input("Admin Password", type="password")

                        if st.button("Login"):
                            if ad_user == "aysha" and ad_password == "admin123":
                                st.success("Welcome Aysha!")

            # Read all rows from SQLite
                                # Fetch data from Supabase
                                data = supabase.table("resumes").select("*").execute()
                                if data.data:
                                    df = pd.DataFrame(data.data)
                                    st.header("📋 All Resumes Data")
                                    st.dataframe(df)

    # Download CSV
                                    st.download_button(
                                        label="📥 Download CSV",
                                        data=df.to_csv(index=False).encode("utf-8"),
                                        file_name="User_Data.csv",
                                        mime="text/csv"
                                    )

    # Pie chart — Predicted Field
                                    if "predicted_field" in df.columns:
                                        st.subheader("📈 Predicted Field Distribution")
                                        fig1 = px.pie(df, names="predicted_field", title="Predicted Field Distribution")
                                        st.plotly_chart(fig1)

    # Pie chart — User Level
                                    if "user_level" in df.columns:
                                        st.subheader("📈 User Level Distribution")
                                        fig2 = px.pie(df, names="user_level", title="User Experience Level Distribution")
                                        st.plotly_chart(fig2)
                                else:
                                   st.warning("No resumes found in Supabase!")
run()

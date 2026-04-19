import PyPDF2   
import docx      
import re        
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

# FILE READERS
def read_pdf(file):
    text = ""
    pdf = PyPDF2.PdfReader(file)

    for page in pdf.pages:
        content = page.extract_text()
        if content:
            text += content

    return text



def read_docx(file):
    doc = docx.Document(file)
    return "\n".join([p.text for p in doc.paragraphs])


def read_txt(file):
    return file.read().decode("utf-8", errors="ignore")


def extract_text(file):
    name = file.name.lower()

    if name.endswith(".pdf"):
        return read_pdf(file)
    elif name.endswith(".docx"):
        return read_docx(file)
    elif name.endswith(".txt"):
        return read_txt(file)

    return ""


# PREPROCESSING
stop_words = set(stopwords.words("english"))


def preprocess_text(text):
    text = text.lower()
    text = re.sub(r'[^a-zA-Z\s]', '', text)

    tokens = word_tokenize(text)
    tokens = [w for w in tokens if w not in stop_words]

    return " ".join(tokens)

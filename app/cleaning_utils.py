import PyPDF2
import re

# Uncomment if text cleaning is desired
# from nltk.corpus import stopwords
# from nltk.tokenize import word_tokenize
import time
from langchain.text_splitter import TokenTextSplitter
from langchain_openai import OpenAIEmbeddings
import pandas as pd
from openai import OpenAI
import dotenv

dotenv.load_dotenv()

client = OpenAI()


def parse_pdf(file):
    """This function uses PyPDF2 to read a PDF,
    and parse it into plain text.

    Args:
        file (FileStorage): The PDF to be parsed

    Returns:
        text: String
    """

    pdf_reader = PyPDF2.PdfReader(file)
    text = ""
    num_pages = len(pdf_reader.pages)
    for page_num in range(num_pages):
        page = pdf_reader.pages[page_num]
        text += page.extract_text()

    return text


def text_splitting(text_to_split, chunk_size=5_000, overlap=0.1):
    """_summary_

    Args:
        text (Str): The string that is going to be splitted
        tokens (int, optional): The amount of tokens in each batch. Defaults to 1_000.
    """
    overlap = round(chunk_size * overlap)
    text_splitter = TokenTextSplitter(chunk_size=chunk_size, chunk_overlap=overlap)
    texts = text_splitter.split_text(text_to_split)

    return texts


def get_embedding(text, model="text-embedding-3-small"):
    text = text.replace("\n", " ")
    return client.embeddings.create(input=[text], model=model).data[0].embedding


def pdf_embedding(file, model="text-embedding-3-small"):
    """
    This function create the embeddings from Open AI
    with dimension 1,536


    Args:
        file (FileStorage): The pdf file
    Returns:
        a vector of embeddings from
    """

    text = parse_pdf(file)

    splitted_text = text_splitting(text)

    embeddings = list(map(lambda x: get_embedding(x, model=model), splitted_text))

    df = pd.DataFrame({"document": splitted_text, "embedding": embeddings})

    return df


def embeddings_from_type(file_type: str, file) -> pd.core.frame.DataFrame:

    match file_type:

        case ".pdf":

            return pdf_embedding(file)

        case ".docx" | ".docm":
            pass


if __name__ == "__main__":
    file_path = "../sample_docs/cs50_harvard.pdf"
    with open(file_path, "rb") as file:
        pdf_embeddings = pdf_embedding(file)
        print(pdf_embeddings[0])

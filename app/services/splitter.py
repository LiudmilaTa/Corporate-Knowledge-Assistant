from langchain_text_splitters import RecursiveCharacterTextSplitter

splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)


def split_text(text: str):
    chunks = splitter.split_text(text)
    return chunks

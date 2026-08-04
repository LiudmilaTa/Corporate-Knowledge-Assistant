from langchain_text_splitters import RecursiveCharacterTextSplitter


splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200
)


def create_chunks(pages, filename):

    documents = []

    for page in pages:

        chunks = splitter.split_text(
            page["text"]
        )

        for index, chunk in enumerate(chunks):

            documents.append(
                {
                    "text": chunk,
                    "metadata": {
                        "filename": filename,
                        "page": page["page"],
                        "chunk_id": index
                    }
                }
            )

    return documents
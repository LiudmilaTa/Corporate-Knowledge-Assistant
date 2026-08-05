from app.services.rag import ask_question


result = ask_question(
    "What skills are listed on your resume?"
)


print("\nANSWER:")
print(result["answer"])


print("\nSOURCES:")

for source in result["sources"]:
    print(
        source["filename"],
        "page:",
        source["page"]
    )
import json

from app.rag.retriever import retrieve
from app.rag.generator import generate_rag_answer

MIN_RAG_SCORE = 0.45

def load_dataset(path: str):
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            yield json.loads(line)

def contains_keywords(answer: str, keywords: list[str]) -> bool:
    return all(keyword in answer for keyword in keywords)


def main():
    total = 0
    keyword_pass = 0
    source_pass = 0

    for item in load_dataset("evals/rag_questions.jsonl"):
        total += 1

        question = item["question"]
        chunks = retrieve(question ,top_k=5)
        
        relevant_chunks = [
            chunk for chunk in chunks
            if chunk["score"] is not None and chunk['score'] >= MIN_RAG_SCORE
        ]


        if relevant_chunks:
            answer = generate_rag_answer(question,relevant_chunks)
        else:
            answer = "根据当前知识库资料，无法确认。"
    
        if contains_keywords(answer, item["expected_keywords"]):
            keyword_pass += 1

        expected_source = item["expected_source"]
        sources = [chunk["filename"]for chunk in relevant_chunks]

        if expected_source is None:
            if not sources:
                source_pass += 1
        elif expected_source in sources:
            source_pass += 1

        print("=" * 80)
        print("Q:", question)
        print("A:", answer)
        print("Sources:", sources)

    print("\nEval Result")
    print("Total:", total)
    print("Keyword Pass:", keyword_pass / total)
    print("Source Pass:", source_pass / total)

if __name__ == "__main__":
    main()
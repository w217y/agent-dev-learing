import json
import time

from concurrent.futures import ThreadPoolExecutor, as_completed


from app.rag.retriever import retrieve_with_debug
from app.rag.generator import generate_rag_answer


def load_dataset(path: str):
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            yield json.loads(line)


def contains_keywords(answer: str, keywords: list[str]) -> bool:
    return all(keyword in answer for keyword in keywords)


def rate(passed: int | float, total: int) -> float:
    if total == 0:
        return 0.0
    return passed / total

def evaluate_one(item: dict) -> dict:
    """执行单条 RAG eval case，返回 detail。"""
    question = item["question"]
    expected_keywords = item["expected_keywords"]
    expected_source = item["expected_source"]

    started_at = time.perf_counter()
    error = None

    try:
        result = retrieve_with_debug(question, top_k=5)
        chunks = result["chunks"]
        debug = result["debug"]

        if chunks:
            answer = generate_rag_answer(question, chunks)
            # answer = "[DEBUG] 检索成功，暂时跳过 LLM 生成。"
        else:
            answer = "根据当前知识库资料，无法确认。"

    except Exception as exc:
        error = str(exc)
        chunks = []
        debug = {"error": str(exc)}
        answer = f"评估执行失败：{exc}"

    latency_ms = round((time.perf_counter() - started_at) * 1000, 2)

    keyword_ok = contains_keywords(answer, expected_keywords)
    sources = [chunk["filename"] for chunk in chunks]

    source_ok = False
    refusal_ok = None

    if expected_source is None:
        refusal_ok = "无法确认" in answer
        source_ok = not sources
    else:
        source_ok = expected_source in sources

    return {
        "question": question,
        "answer": answer,
        "expected_keywords": expected_keywords,
        "expected_source": expected_source,
        "sources": sources,
        "keyword_ok": keyword_ok,
        "source_ok": source_ok,
        "refusal_ok": refusal_ok,
        "latency_ms": latency_ms,
        "debug": debug,
        "error": error,
    }

def print_rag_detail(detail: dict) -> None:
    print("=" * 80)
    print("Q:", detail["question"])
    print("A:", detail["answer"])
    print("Expected source:", detail["expected_source"])
    print("Sources:", detail["sources"])
    print("Keyword ok:", detail["keyword_ok"])
    print("Source ok:", detail["source_ok"])
    print("Refusal ok:", detail["refusal_ok"])
    print("Debug:", detail["debug"])
    print("Latency ms:", detail["latency_ms"])
    if detail.get("error"):
        print("Error:", detail["error"])

def build_metrics(details: list[dict]) -> dict:
    total = len(details)

    keyword_pass = sum(1 for detail in details if detail["keyword_ok"])
    source_pass = sum(1 for detail in details if detail["source_ok"])

    refusal_details = [
        detail for detail in details
        if detail["expected_source"] is None
    ]
    refusal_total = len(refusal_details)
    refusal_pass = sum(
        1 for detail in refusal_details
        if detail["refusal_ok"]
    )

    total_latency_ms = sum(detail["latency_ms"] for detail in details)

    return {
        "total": total,
        "keyword_pass_rate": rate(keyword_pass, total),
        "source_pass_rate": rate(source_pass, total),
        "refusal_total": refusal_total,
        "refusal_pass_rate": rate(refusal_pass, refusal_total),
        "avg_latency_ms": round(rate(total_latency_ms, total), 2),
        "details": details,
    }



def run_eval(
    dataset_path: str = "evals/rag_questions.jsonl",
    verbose: bool = True,
    max_cases: int | None = None,
    max_workers: int = 1,
) -> dict:
    items = list(load_dataset(dataset_path))

    if max_cases is not None:
        items = items[:max_cases]

    details = []

    print(
        f"RAG eval started | total_cases={len(items)} | max_workers={max_workers}",
        flush=True,
    )

    if max_workers <= 1:
        for index, item in enumerate(items, start=1):
            print(f"Running RAG case {index}: {item['question']}", flush=True)
            detail = evaluate_one(item)
            details.append(detail)

            if verbose:
                print_rag_detail(detail)
    else:
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_item = {}

            for index, item in enumerate(items, start=1):
                print(f"Submitting RAG case {index}: {item['question']}", flush=True)
                future = executor.submit(evaluate_one, item)
                future_to_item[future] = (index, item)

            for future in as_completed(future_to_item):
                index, item = future_to_item[future]

                try:
                    detail = future.result()
                except Exception as exc:
                    detail = {
                        "question": item["question"],
                        "answer": f"评估执行失败：{exc}",
                        "expected_keywords": item["expected_keywords"],
                        "expected_source": item["expected_source"],
                        "sources": [],
                        "keyword_ok": False,
                        "source_ok": item["expected_source"] is None,
                        "refusal_ok": None,
                        "latency_ms": 0,
                        "debug": {"future_error": str(exc)},
                        "error": str(exc),
                    }

                detail["case_index"] = index
                details.append(detail)

                print(
                    f"Completed RAG case {index} | latency_ms={detail['latency_ms']} | error={detail.get('error')}",
                    flush=True,
                )

                if verbose:
                    print_rag_detail(detail)

    details.sort(key=lambda detail: detail.get("case_index", 0))

    metrics = build_metrics(details)

    if verbose:
        print("\nRAG Eval Result")
        print("Total:", metrics["total"])
        print("Keyword Pass Rate:", metrics["keyword_pass_rate"])
        print("Source Pass Rate:", metrics["source_pass_rate"])
        print("Refusal Total:", metrics["refusal_total"])
        print("Refusal Pass Rate:", metrics["refusal_pass_rate"])
        print("Avg Latency ms:", metrics["avg_latency_ms"])

    return metrics



def main():
    run_eval(verbose=True, max_cases=10, max_workers=1)

if __name__ == "__main__":
    main()

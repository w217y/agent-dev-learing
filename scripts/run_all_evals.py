from datetime import datetime
from pathlib import Path

from evals.run_agent_eval import run_eval as run_agent_eval
from evals.run_rag_eval import run_eval as run_rag_eval


REPORT_PATH = Path("evals/eval_report.md")


def percent(value: float) -> str:
    return f"{value * 100:.2f}%"


def build_report(rag_metrics: dict, agent_metrics: dict) -> str:
    generated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    return f"""# Eval Report

Generated at: {generated_at}

## RAG Eval

- Total Cases: {rag_metrics['total']}
- Keyword Pass Rate: {percent(rag_metrics['keyword_pass_rate'])}
- Source Pass Rate: {percent(rag_metrics['source_pass_rate'])}
- Refusal Cases: {rag_metrics['refusal_total']}
- Refusal Pass Rate: {percent(rag_metrics['refusal_pass_rate'])}
- Avg Latency: {rag_metrics['avg_latency_ms']} ms

## Agent Eval

- Total Cases: {agent_metrics['total']}
- Intent Pass Rate: {percent(agent_metrics['intent_pass_rate'])}
- Tool Pass Rate: {percent(agent_metrics['tool_pass_rate'])}
- Approval Pass Rate: {percent(agent_metrics['approval_pass_rate'])}
- Unsafe Cases: {agent_metrics['unsafe_total']}
- Unsafe Reject Pass Rate: {percent(agent_metrics['unsafe_reject_pass_rate'])}
- Avg Latency: {agent_metrics['avg_latency_ms']} ms

## Notes

- RAG 检索阈值过滤在 retriever 层完成，eval 层不重复过滤。
- 当前 unsafe reject 使用代理判断：不调用工具且不进入审批。
"""


def main():
    print("=" * 80)
    print("Running RAG eval...")
    rag_metrics = run_rag_eval(
        verbose=True,
        max_cases=None,
        max_workers=2,
    )

    print("=" * 80)
    print("Running Agent eval...")
    agent_metrics = run_agent_eval(
        verbose=True,
        max_cases=None,
        max_workers=3,
    )

    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(build_report(rag_metrics, agent_metrics), encoding="utf-8")

    print("=" * 80)
    print(f"Eval report generated: {REPORT_PATH}")


if __name__ == "__main__":
    main()

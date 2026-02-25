from __future__ import annotations

from pathlib import Path

import streamlit as st

from src.pipeline import RagPipeline
from src.ui_utils import format_results_for_display


@st.cache_resource
def get_pipeline(base_dir: str, provider: str) -> RagPipeline:
    return RagPipeline(base_dir=base_dir, provider=provider)


def main() -> None:
    st.set_page_config(page_title="RAG MVP", page_icon=":books:", layout="wide")
    st.title("RAG 知识库 MVP")
    st.caption("单页导入 + 问答调试界面（rag-mvp）")

    with st.sidebar:
        st.header("配置")
        base_dir = st.text_input("Base Dir", value=".")
        provider = st.selectbox("Provider", options=["local", "openai"], index=0)
        data_path = st.text_input("Data Path", value="data")
        ingest_chunk_size = st.number_input("Chunk Size", min_value=100, max_value=5000, value=700, step=50)
        ingest_chunk_overlap = st.number_input("Chunk Overlap", min_value=0, max_value=1000, value=80, step=10)

        pipeline = get_pipeline(base_dir=base_dir, provider=provider)
        stats = pipeline.stats()
        st.metric("Current Chunks", stats["chunks"])

        if st.button("Ingest Data", use_container_width=True):
            try:
                result = pipeline.ingest(
                    input_path=data_path,
                    chunk_size=int(ingest_chunk_size),
                    chunk_overlap=int(ingest_chunk_overlap),
                )
                st.success(f"Ingest done: docs={result['documents']}, chunks={result['chunks']}, added={result['added']}")
            except Exception as exc:  # pragma: no cover
                st.error(f"Ingest failed: {exc}")

    st.subheader("问答")
    col1, col2, col3 = st.columns([6, 2, 2])
    question = col1.text_input("Question", value="")
    top_k = col2.number_input("Top K", min_value=1, max_value=10, value=3, step=1)
    debug = col3.checkbox("Debug", value=True)

    if st.button("Ask", type="primary", use_container_width=True):
        if not question.strip():
            st.warning("请输入问题。")
            return
        try:
            result = pipeline.query(question=question.strip(), top_k=int(top_k), debug=debug)
        except Exception as exc:  # pragma: no cover
            st.error(f"Query failed: {exc}")
            return

        st.markdown("### 回答")
        st.write(result["answer"])

        st.markdown("### 来源")
        if result["sources"]:
            st.write(", ".join(result["sources"]))
        else:
            st.write("无")

        st.markdown("### 检索结果")
        rows = format_results_for_display(result["results"])
        if rows:
            st.dataframe(rows, use_container_width=True, hide_index=True)
        else:
            st.write("无检索结果。")

        if debug:
            with st.expander("Prompt", expanded=False):
                st.code(result["prompt"] or "", language="text")


if __name__ == "__main__":
    main()

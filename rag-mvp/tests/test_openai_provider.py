from types import SimpleNamespace

from src.openai_provider import OpenAIProvider


class _FakeEmbeddingsApi:
    def __init__(self) -> None:
        self.calls = []

    def create(self, *, model, input):
        self.calls.append({"model": model, "input": input})
        data = [SimpleNamespace(embedding=[float(i), 0.5]) for i, _ in enumerate(input)]
        return SimpleNamespace(data=data)


class _FakeChatCompletionsApi:
    def __init__(self) -> None:
        self.calls = []

    def create(self, *, model, messages, temperature):
        self.calls.append({"model": model, "messages": messages, "temperature": temperature})
        return SimpleNamespace(
            choices=[SimpleNamespace(message=SimpleNamespace(content="mocked answer"))]
        )


class _FakeClient:
    def __init__(self) -> None:
        self.embeddings = _FakeEmbeddingsApi()
        self.chat = SimpleNamespace(completions=_FakeChatCompletionsApi())


def test_openai_provider_embeds_texts_and_query() -> None:
    client = _FakeClient()
    provider = OpenAIProvider(client=client)

    vectors = provider.embed_texts(["alpha", "beta"])
    qvec = provider.embed_query("what is alpha")

    assert len(vectors) == 2
    assert vectors[0] == [0.0, 0.5]
    assert qvec == [0.0, 0.5]
    assert client.embeddings.calls[0]["model"] == "text-embedding-3-small"


def test_openai_provider_generates_answer_from_contexts() -> None:
    client = _FakeClient()
    provider = OpenAIProvider(client=client)

    answer = provider.generate_answer(
        question="RAG 是什么？",
        contexts=[{"source": "doc.md", "text": "RAG 是检索增强生成。", "score": 0.9}],
    )

    assert answer == "mocked answer"
    call = client.chat.completions.calls[0]
    assert call["model"] == "gpt-4o-mini"
    assert call["temperature"] == 0
    assert any("RAG 是什么" in msg["content"] for msg in call["messages"])


def test_openai_provider_batches_embedding_requests_with_max_64_inputs() -> None:
    client = _FakeClient()
    provider = OpenAIProvider(client=client)
    texts = [f"chunk-{idx}" for idx in range(130)]

    vectors = provider.embed_texts(texts)

    assert len(vectors) == 130
    assert len(client.embeddings.calls) == 3
    assert len(client.embeddings.calls[0]["input"]) == 64
    assert len(client.embeddings.calls[1]["input"]) == 64
    assert len(client.embeddings.calls[2]["input"]) == 2

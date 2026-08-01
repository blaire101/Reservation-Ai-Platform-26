from app.retrieval import KeywordRetriever

def test_grain_retrieval():
    chunks=KeywordRetriever().search("grain of reservation conversion mart")
    assert chunks
    assert any(c.source == "table_dictionary.md" for c in chunks)

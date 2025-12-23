from apps.knowledge.tasks import split_text


def test_split_text_basic_chunks():
    text = "a" * 1200
    chunks = split_text(text, chunk_size=500, overlap=0)
    # 1200 chars -> 3 chunks (500, 500, 200)
    assert len(chunks) == 3
    assert len(chunks[0]) == 500
    assert len(chunks[1]) == 500
    assert len(chunks[2]) == 200


def test_split_text_with_overlap():
    text = "abcdefg" * 100  # 700 chars
    chunks = split_text(text, chunk_size=200, overlap=50)
    # Expect sliding window: starts at 0,150,300,450,600
    expected_starts = [0, 150, 300, 450, 600]
    assert len(chunks) == len(expected_starts)
    for idx, start in enumerate(expected_starts):
        assert chunks[idx] == text[start:start+200]


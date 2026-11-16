import anthropic

from src import rag
from src.rag import answer_query, retrieve


def make_catalog():
    return [
        {
            "id": 1, "title": "Midnight Coding", "artist": "LoRoom",
            "genre": "lofi", "mood": "chill", "energy": 0.42, "tempo_bpm": 78.0,
            "valence": 0.56, "danceability": 0.62, "acousticness": 0.71,
        },
        {
            "id": 2, "title": "Storm Runner", "artist": "Voltline",
            "genre": "rock", "mood": "intense", "energy": 0.91, "tempo_bpm": 152.0,
            "valence": 0.48, "danceability": 0.66, "acousticness": 0.10,
        },
        {
            "id": 3, "title": "Library Rain", "artist": "Paper Lanterns",
            "genre": "lofi", "mood": "chill", "energy": 0.35, "tempo_bpm": 72.0,
            "valence": 0.60, "danceability": 0.58, "acousticness": 0.86,
        },
    ]


def test_retrieve_ranks_relevant_songs_above_irrelevant_ones():
    songs = make_catalog()
    results = retrieve("chill acoustic lofi music for studying", songs, k=3)

    assert len(results) >= 1
    top_song, top_score = results[0]
    assert top_song["genre"] == "lofi"
    assert top_score > 0

    titles = [song["title"] for song, _ in results]
    assert "Storm Runner" not in titles[:1]


def test_retrieve_returns_nothing_for_unrelated_query():
    songs = make_catalog()
    results = retrieve("zzqxv nonsense gibberish not music related 12390", songs, k=3)
    assert results == []


def test_retrieve_respects_k():
    songs = make_catalog()
    results = retrieve("music", songs, k=1)
    assert len(results) <= 1


def test_answer_query_with_no_relevant_songs_skips_llm_call(mocker):
    songs = make_catalog()
    spy = mocker.patch("anthropic.Anthropic")

    result = answer_query("zzqxv nonsense gibberish not music related 12390", songs)

    assert result["retrieved"] == []
    assert result["used_llm"] is False
    assert result["confidence"] == "None"
    assert "No songs" in result["answer"]
    spy.assert_not_called()


def test_answer_query_falls_back_when_no_api_key(monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    songs = make_catalog()

    result = answer_query("chill acoustic lofi for studying", songs)

    assert result["used_llm"] is False
    assert result["confidence"] in {"High", "Medium", "Low"}
    assert "ANTHROPIC_API_KEY" in result["answer"]
    assert "Midnight Coding" in result["answer"] or "Library Rain" in result["answer"]


def test_answer_query_uses_llm_response_and_parses_its_stated_confidence(monkeypatch, mocker):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
    songs = make_catalog()

    text_block = mocker.Mock(
        type="text",
        text=(
            "Try Midnight Coding, it's chill and acoustic.\n"
            "Confidence: High - genre and mood both match the request."
        ),
    )
    fake_response = mocker.Mock(
        stop_reason="end_turn",
        content=[text_block],
    )
    mock_client = mocker.Mock()
    mock_client.messages.create.return_value = fake_response
    mocker.patch("anthropic.Anthropic", return_value=mock_client)

    result = answer_query("chill acoustic lofi for studying", songs)

    assert result["used_llm"] is True
    assert result["confidence"] == "High"
    assert "Midnight Coding" in result["answer"]
    mock_client.messages.create.assert_called_once()
    _, kwargs = mock_client.messages.create.call_args
    assert kwargs["model"] == rag.DEFAULT_MODEL


def test_answer_query_estimates_confidence_when_model_omits_confidence_line(monkeypatch, mocker):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
    songs = make_catalog()

    text_block = mocker.Mock(type="text", text="Try Midnight Coding, it's chill and acoustic.")
    fake_response = mocker.Mock(stop_reason="end_turn", content=[text_block])
    mock_client = mocker.Mock()
    mock_client.messages.create.return_value = fake_response
    mocker.patch("anthropic.Anthropic", return_value=mock_client)

    query = "chill acoustic lofi for studying"
    retrieved = retrieve(query, songs)
    result = answer_query(query, songs)

    assert result["used_llm"] is True
    assert result["confidence"] == rag._confidence_from_retrieval(retrieved)


def test_answer_query_falls_back_on_authentication_error(monkeypatch, mocker):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "bad-key")
    songs = make_catalog()

    mock_client = mocker.Mock()
    mock_client.messages.create.side_effect = anthropic.AuthenticationError(
        message="invalid key", response=mocker.Mock(status_code=401, headers={}), body=None
    )
    mocker.patch("anthropic.Anthropic", return_value=mock_client)

    result = answer_query("chill acoustic lofi for studying", songs)

    assert result["used_llm"] is False
    assert result["confidence"] in {"High", "Medium", "Low"}
    assert "rejected" in result["answer"]

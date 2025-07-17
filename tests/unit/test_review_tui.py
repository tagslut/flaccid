from flaccid.tui.review import review_metadata
from flaccid.plugins.base import TrackMetadata


def test_review_metadata_accept_reject(monkeypatch):
    responses = iter(["keep", "drop"] + ["keep"] * 8)

    def fake_dialog(*args, **kwargs):
        class Dummy:
            def run(self):
                return next(responses)

        return Dummy()

    monkeypatch.setattr("flaccid.tui.review.radiolist_dialog", fake_dialog)

    meta = TrackMetadata(
        title="Song",
        artist="Artist",
        album="Album",
        track_number=1,
        disc_number=1,
        year=2024,
    )

    result = review_metadata(meta)
    assert result.title == "Song"
    assert result.artist is None

"""Tests for YouTube transcript extraction utilities."""

from src.youtube import extract_video_id, is_youtube_url


class TestYouTubeUrlDetection:
    """Tests for YouTube URL detection patterns."""

    def test_standard_watch_url(self):
        url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        assert is_youtube_url(url)
        assert extract_video_id(url) == "dQw4w9WgXcQ"

    def test_watch_url_without_www(self):
        url = "https://youtube.com/watch?v=dQw4w9WgXcQ"
        assert is_youtube_url(url)
        assert extract_video_id(url) == "dQw4w9WgXcQ"

    def test_short_url(self):
        url = "https://youtu.be/dQw4w9WgXcQ"
        assert is_youtube_url(url)
        assert extract_video_id(url) == "dQw4w9WgXcQ"

    def test_embed_url(self):
        url = "https://www.youtube.com/embed/dQw4w9WgXcQ"
        assert is_youtube_url(url)
        assert extract_video_id(url) == "dQw4w9WgXcQ"

    def test_shorts_url(self):
        url = "https://www.youtube.com/shorts/dQw4w9WgXcQ"
        assert is_youtube_url(url)
        assert extract_video_id(url) == "dQw4w9WgXcQ"

    def test_url_with_extra_params(self):
        url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ&t=120&list=PLxyz"
        assert is_youtube_url(url)
        assert extract_video_id(url) == "dQw4w9WgXcQ"

    def test_http_url(self):
        url = "http://youtube.com/watch?v=dQw4w9WgXcQ"
        assert is_youtube_url(url)
        assert extract_video_id(url) == "dQw4w9WgXcQ"

    def test_non_youtube_url(self):
        assert not is_youtube_url("https://example.com/video")
        assert extract_video_id("https://example.com/video") is None

    def test_youtube_channel_url(self):
        # Channel URLs don't have video IDs
        assert not is_youtube_url("https://www.youtube.com/@channel")
        assert extract_video_id("https://www.youtube.com/@channel") is None

    def test_youtube_playlist_url(self):
        # Playlist URL without video ID
        url = "https://www.youtube.com/playlist?list=PLxyz"
        assert not is_youtube_url(url)
        assert extract_video_id(url) is None

    def test_malformed_url(self):
        assert not is_youtube_url("not a url")
        assert extract_video_id("not a url") is None

    def test_empty_string(self):
        assert not is_youtube_url("")
        assert extract_video_id("") is None

    def test_video_id_with_special_chars(self):
        # Video IDs can contain underscores and hyphens
        url = "https://youtu.be/abc_-123XYZ"
        assert is_youtube_url(url)
        assert extract_video_id(url) == "abc_-123XYZ"

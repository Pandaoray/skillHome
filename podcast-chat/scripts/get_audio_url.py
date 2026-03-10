#!/usr/bin/env python3
"""
Extract audio URL from Apple Podcasts or Xiaoyuzhou episode URL.

Usage:
    python3 get_audio_url.py <url>

Output:
    Prints the direct audio URL to stdout on success.
    Prints error message to stderr and exits with code 1 on failure.
"""

import sys
import re
import json
import urllib.request
import urllib.error
import xml.etree.ElementTree as ET


def fetch(url, timeout=20):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


def get_apple_podcasts_audio(url):
    """Extract audio URL from Apple Podcasts episode URL."""
    podcast_match = re.search(r'/id(\d+)', url)
    episode_match = re.search(r'[?&]i=(\d+)', url)

    if not podcast_match:
        raise ValueError("Could not extract podcast ID from Apple Podcasts URL")

    podcast_id = podcast_match.group(1)
    episode_id = episode_match.group(1) if episode_match else None

    # Step 1: Try RSS feed (fastest, works for recent episodes)
    itunes_data = json.loads(fetch(
        f"https://itunes.apple.com/lookup?id={podcast_id}&entity=podcast"
    ))
    feed_url = next(
        (r["feedUrl"] for r in itunes_data.get("results", []) if r.get("feedUrl")),
        None
    )

    if feed_url:
        audio_url = _search_rss(feed_url, episode_id)
        if audio_url:
            return audio_url

    # Step 2: Fallback — iTunes episodes API (returns previewUrl for recent 200 episodes)
    if episode_id:
        episodes_data = json.loads(fetch(
            f"https://itunes.apple.com/lookup?id={podcast_id}"
            f"&media=podcast&entity=podcastEpisode&limit=200"
        ))
        for result in episodes_data.get("results", []):
            track_id = str(result.get("trackId", ""))
            if track_id == episode_id:
                audio = result.get("episodeUrl") or result.get("previewUrl")
                if audio:
                    return audio

    raise ValueError(
        f"Could not find audio URL for episode {episode_id}. "
        "The episode may be too old. Try the Xiaoyuzhou URL instead if available."
    )


def _search_rss(feed_url, episode_id):
    """Parse RSS feed and return enclosure URL matching episode_id (or first if None)."""
    try:
        root = ET.fromstring(fetch(feed_url))
    except Exception:
        return None

    for item in root.findall(".//item"):
        enclosure = item.find("enclosure")
        if enclosure is None:
            continue
        audio_url = enclosure.get("url", "")
        if not audio_url:
            continue
        if not episode_id:
            return audio_url
        # Match by GUID, link, or audio URL containing the episode ID
        texts = [
            getattr(item.find("guid"), "text", "") or "",
            getattr(item.find("link"), "text", "") or "",
            audio_url,
        ]
        if any(episode_id in t for t in texts):
            return audio_url

    return None



def get_xiaoyuzhou_audio(url):
    """Extract audio URL from Xiaoyuzhou episode page."""
    # markdown.new renders JS and exposes JSON-LD contentUrl
    content = fetch(f"https://markdown.new/{url}").decode("utf-8")

    match = re.search(r'"contentUrl"\s*:\s*"(https://[^"]+\.m4a[^"]*)"', content)
    if match:
        return match.group(1)

    # Fallback: any xyzcdn.net .m4a URL
    match = re.search(r'https://media\.xyzcdn\.net/[^\s"\'<>]+\.m4a', content)
    if match:
        return match.group(0)

    # Second fallback: r.jina.ai
    content2 = fetch(f"https://r.jina.ai/{url}").decode("utf-8")
    match = re.search(r'"contentUrl"\s*:\s*"(https://[^"]+\.m4a[^"]*)"', content2)
    if match:
        return match.group(1)

    raise ValueError("Could not find audio URL in Xiaoyuzhou page")


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 get_audio_url.py <podcast_url>", file=sys.stderr)
        sys.exit(1)

    url = sys.argv[1]

    try:
        if "podcasts.apple.com" in url:
            audio_url = get_apple_podcasts_audio(url)
        elif "xiaoyuzhoufm.com" in url:
            audio_url = get_xiaoyuzhou_audio(url)
        else:
            raise ValueError(
                "Unsupported platform. Supported: Apple Podcasts, Xiaoyuzhou (小宇宙)."
            )
        print(audio_url)

    except urllib.error.URLError as e:
        print(f"Network error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

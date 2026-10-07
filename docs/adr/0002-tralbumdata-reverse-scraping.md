# 0002. TralbumData DOM Reverse-Scraping Pipeline

Metadata, tracklists, and playable MP3 preview streams are extracted by reverse-parsing Bandcamp's embedded `TralbumData` JSON object, falling back to OpenGraph and HTML meta tags when absent.

## Context
Bandcamp does not provide an open, public REST API for fetching release tracklists and 128kbps MP3 preview stream URLs. External scraping must balance reliability, speed, and parsing resilience across both standard `*.bandcamp.com` subdomains and custom artist/label domains.

## Decision
We extract metadata by fetching the target page HTML with HTTPX (configured with browser-like headers and random jitter) and extracting the embedded `var TralbumData` / `data-tralbum` JavaScript JSON object using regular expressions and HTML unescaping. If `TralbumData` is missing or incomplete, the scraper falls back to `bc-page-properties`, OpenGraph (`og:title`, `og:image`, `og:video`), and page title parsing.

## Consequences
- **Rich Tracklist Support**: Enables extracting multi-track preview streams, track numbers, and track IDs without running a headless browser.
- **Maintenance Coupling**: Structural changes to Bandcamp's server-rendered HTML or JSON variable naming could require parser regex updates.

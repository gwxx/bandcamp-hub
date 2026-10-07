# Bandcamp Hub

A local-first music curation and discovery hub that aggregates Bandcamp new release notifications from Gmail, extracts streaming audio and metadata, and organizes music into a weekly workflow for DJs and music enthusiasts.

## Core Concepts

**Release**:
A published musical work (album, EP, or single) on Bandcamp, serving as the primary aggregate root and curation unit.
_Avoid_: Album, Item, Product, Post

**Track**:
A playable individual audio piece contained within a Release, with its own title, position, duration, and stream URL.
_Avoid_: Song, Audio, MP3, File

**ISO Week**:
A calendar week identifier (`YYYY-Www`) representing the timeframe when a release notification was received in Gmail, serving as the primary timeline partition.
_Avoid_: Release Week, Batch, Cohort, Date Group

**Sync Watermark**:
The high-water Unix timestamp of the most recent successfully processed Gmail notification, used as a query boundary to fetch only incremental new notifications.
_Avoid_: Checkpoint, Sync Offset, Last Synced Date

## User States & Actions

**Listened**:
A binary status indicating whether the user has audited/reviewed the release.
_Avoid_: Played, Read, Seen, Completed

**Starred**:
A favorite marker indicating the user selected the release for purchase, DJ sets, or future reference; marking a release as Starred automatically promotes it to Listened, but unstarring retains the Listened state.
_Avoid_: Favorited, Bookmarked, Liked, Saved

**Weekly Digest**:
The collection of releases grouped under a specific ISO Week waiting for or having completed user curation.
_Avoid_: Feed, Inbox, Issue, Newsletter

**Degraded Release**:
A persisted release record whose preview audio streams could not be extracted (e.g. Bandcamp restrictions or vinyl-only), surfaced in the timeline with direct external web links.
_Avoid_: Broken Release, Error Item, Invalid Release

**Evergreen Vault**:
The local SQLite persistence model retaining all historical releases indefinitely while bounding UI rendering via paginated ISO Week windows.
_Avoid_: Database Cache, Ephemeral Store, Rolling Log

## DJ & Audition Concepts

**Base BPM**:
The canonical, inherent tempo (in beats per minute) of a Release, analyzed or manually set by the user, stored within the valid range of 40.0 to 300.0.
_Avoid_: Song Speed, Song BPM, Track BPM, Master Tempo

**Effective BPM**:
The real-time playback tempo after applying the master pitch rate multiplier (0.80x ~ 1.20x), calculated dynamically as `Base BPM * Pitch`.
_Avoid_: Current BPM, Altered Speed, Staged Tempo

**Audition History**:
The local client-side audit record tracking individual tracks that have been sampled/played, visually dimming their appearance across the curation session.
_Avoid_: Play History, Listening Log, Track Cache


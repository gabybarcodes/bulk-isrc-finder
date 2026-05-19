import express from 'express';
import cors from 'cors';
import dotenv from 'dotenv';
import axios from 'axios';
import path from 'path';
import { fileURLToPath } from 'url';

dotenv.config();

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const app = express();
const PORT = process.env.PORT || 3000;

app.use(cors());
app.use(express.json());
app.use(express.static('public'));

const SPOTIFY_CLIENT_ID = process.env.SPOTIFY_CLIENT_ID;
const SPOTIFY_CLIENT_SECRET = process.env.SPOTIFY_CLIENT_SECRET;
const DEEZER_BASE = 'https://api.deezer.com';
const SPOTIFY_BASE = 'https://api.spotify.com/v1';

// --- Spotify token cache ---
let _spotifyToken = { value: null, expiresAt: 0 };

async function getSpotifyToken() {
  if (_spotifyToken.value && Date.now() < _spotifyToken.expiresAt - 60_000) {
    return _spotifyToken.value;
  }
  const credentials = Buffer.from(`${SPOTIFY_CLIENT_ID}:${SPOTIFY_CLIENT_SECRET}`).toString('base64');
  const res = await axios.post(
    'https://accounts.spotify.com/api/token',
    'grant_type=client_credentials',
    { headers: { Authorization: `Basic ${credentials}`, 'Content-Type': 'application/x-www-form-urlencoded' } }
  );
  _spotifyToken.value = res.data.access_token;
  _spotifyToken.expiresAt = Date.now() + res.data.expires_in * 1000;
  return _spotifyToken.value;
}

// --- Label → major group mapping (mirrors distributor_mapping.py) ---
const LABEL_TO_MAJOR_GROUP = {
  // Sony Music Entertainment
  columbia: 'Sony Music Entertainment',
  rca: 'Sony Music Entertainment',
  'epic records': 'Sony Music Entertainment',
  'sony music': 'Sony Music Entertainment',
  'sony classical': 'Sony Music Entertainment',
  'sony latin': 'Sony Music Entertainment',
  'legacy recordings': 'Sony Music Entertainment',
  'polo grounds': 'Sony Music Entertainment',
  masterworks: 'Sony Music Entertainment',
  ariola: 'Sony Music Entertainment',
  'provident music': 'Sony Music Entertainment',
  'beach music': 'Sony Music Entertainment',
  'the orchard': 'Sony Music Entertainment',
  'orchard enterprises': 'Sony Music Entertainment',
  awal: 'Sony Music Entertainment',
  'aura music': 'Sony Music Entertainment',
  arista: 'Sony Music Entertainment',
  jive: 'Sony Music Entertainment',
  zomba: 'Sony Music Entertainment',
  laface: 'Sony Music Entertainment',
  kemosabe: 'Sony Music Entertainment',
  'monument records': 'Sony Music Entertainment',
  'columbia nashville': 'Sony Music Entertainment',
  'essential records': 'Sony Music Entertainment',
  'epic latin': 'Sony Music Entertainment',
  'premium latin music': 'Sony Music Entertainment',
  'discos sony': 'Sony Music Entertainment',
  smej: 'Sony Music Entertainment',
  'polo grounds music': 'Sony Music Entertainment',
  'life and death': 'Sony Music Entertainment',
  // Sony Music — distributed labels (not obvious from name)
  'ultra music': 'Sony Music Entertainment',
  'ultra records': 'Sony Music Entertainment',
  'ministry of sound': 'Sony Music Entertainment',
  'relentless records': 'Sony Music Entertainment',
  'gun records': 'Sony Music Entertainment',
  'hansa records': 'Sony Music Entertainment',
  'dualtone': 'Sony Music Entertainment',
  'so so def': 'Sony Music Entertainment',
  'loud & proud': 'Sony Music Entertainment',
  'loud and proud': 'Sony Music Entertainment',
  'bpg music': 'Sony Music Entertainment',
  'beach street records': 'Sony Music Entertainment',
  'reunion records': 'Sony Music Entertainment',
  'red hill records': 'Sony Music Entertainment',
  'volcano entertainment': 'Sony Music Entertainment',
  'aware records': 'Sony Music Entertainment',
  'work records': 'Sony Music Entertainment',
  '10:22pm': 'Sony Music Entertainment',
  'certified': 'Sony Music Entertainment',
  'syco': 'Sony Music Entertainment',
  'electrola': 'Sony Music Entertainment',
  'rca inspiration': 'Sony Music Entertainment',
  'arista nashville': 'Sony Music Entertainment',
  'black butter': 'Sony Music Entertainment',
  'insanity records': 'Sony Music Entertainment',
  'chess club': 'Sony Music Entertainment',
  'nettwerk': 'Sony Music Entertainment',
  // Universal Music Group
  'republic records': 'Universal Music Group',
  interscope: 'Universal Music Group',
  'def jam': 'Universal Music Group',
  'island records': 'Universal Music Group',
  'capitol records': 'Universal Music Group',
  'capitol music': 'Universal Music Group',
  geffen: 'Universal Music Group',
  'mercury records': 'Universal Music Group',
  motown: 'Universal Music Group',
  'blue note': 'Universal Music Group',
  'verve records': 'Universal Music Group',
  'verve label': 'Universal Music Group',
  'deutsche grammophon': 'Universal Music Group',
  decca: 'Universal Music Group',
  polydor: 'Universal Music Group',
  'universal music': 'Universal Music Group',
  'universal records': 'Universal Music Group',
  umg: 'Universal Music Group',
  'loma vista': 'Universal Music Group',
  'good music': 'Universal Music Group',
  'cash money': 'Universal Music Group',
  'young money': 'Universal Music Group',
  'caroline records': 'Universal Music Group',
  'virgin emi': 'Universal Music Group',
  'def soul': 'Universal Music Group',
  // Warner Music Group
  'atlantic records': 'Warner Music Group',
  'warner records': 'Warner Music Group',
  'warner bros': 'Warner Music Group',
  elektra: 'Warner Music Group',
  parlophone: 'Warner Music Group',
  rhino: 'Warner Music Group',
  'sire records': 'Warner Music Group',
  'reprise records': 'Warner Music Group',
  nonesuch: 'Warner Music Group',
  'fueled by ramen': 'Warner Music Group',
  'asylum records': 'Warner Music Group',
  'east west records': 'Warner Music Group',
  wea: 'Warner Music Group',
  wmg: 'Warner Music Group',
  'warner music': 'Warner Music Group',
  '300 entertainment': 'Warner Music Group',
  'big beat records': 'Warner Music Group',
};

function getMajorGroup(labelName, copyrightText = '') {
  const combined = `${labelName || ''} ${copyrightText || ''}`.toLowerCase();
  for (const [keyword, group] of Object.entries(LABEL_TO_MAJOR_GROUP)) {
    if (combined.includes(keyword)) return group;
  }
  return 'Independent';
}

// --- Spotify label lookup by ISRC ---
async function fetchSpotifyLabel(isrc) {
  try {
    const token = await getSpotifyToken();
    const headers = { Authorization: `Bearer ${token}` };

    const searchRes = await axios.get(`${SPOTIFY_BASE}/search`, {
      headers,
      params: { q: `isrc:${isrc}`, type: 'track', limit: 1 },
    });

    const tracks = searchRes.data?.tracks?.items || [];
    if (!tracks.length) return { labels: null, distributor: null, releaseDate: null };

    const album = tracks[0].album;
    const albumId = album?.id;
    let releaseDate = album?.release_date || null;

    if (!albumId) return { labels: null, distributor: null, releaseDate };

    const albumRes = await axios.get(`${SPOTIFY_BASE}/albums/${albumId}`, { headers });
    const albumData = albumRes.data;

    const labelName = albumData.label || null;
    if (!releaseDate) releaseDate = albumData.release_date || null;

    const copyrightText = (albumData.copyrights || []).map(c => c.text).join(' ');
    const distributor = getMajorGroup(labelName, copyrightText);

    return { labels: labelName, distributor, releaseDate };
  } catch {
    return { labels: null, distributor: null, releaseDate: null };
  }
}

// --- Deezer search + Spotify enrichment ---
async function searchSong(song) {
  try {
    const query = `${song.title} ${song.artist}`.trim();
    const deezerRes = await axios.get(`${DEEZER_BASE}/search`, {
      params: { q: query, limit: 5 },
    });

    const tracks = deezerRes.data?.data || [];
    if (!tracks.length) {
      return { input: `${song.title} - ${song.artist}`, found: false, error: 'Song not found in Deezer' };
    }

    const track = tracks[0];
    const isrc = track.isrc || null;
    const { labels, distributor, releaseDate } = isrc
      ? await fetchSpotifyLabel(isrc)
      : { labels: null, distributor: null, releaseDate: null };

    const fallbackDate = track.album?.release_date || track.release_date || null;

    return {
      input: `${song.title} - ${song.artist}`,
      found: true,
      title: track.title || song.title,
      artist: track.artist?.name || song.artist,
      isrc,
      releaseDate: releaseDate || fallbackDate,
      labels,
      distributor,
    };
  } catch (err) {
    return { input: `${song.title} - ${song.artist}`, found: false, error: err.message };
  }
}

// --- Routes ---
app.post('/api/search-single', async (req, res) => {
  try {
    const result = await searchSong(req.body.song);
    res.json(result);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

app.post('/api/bulk-search', async (req, res) => {
  try {
    const songs = req.body.songs || [];
    const results = [];
    for (const song of songs) {
      results.push(await searchSong(song));
      await new Promise(r => setTimeout(r, 100));
    }
    res.json({ results });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

app.get('/api/health', (req, res) => {
  res.json({ status: 'ok', api: 'deezer+spotify' });
});

app.listen(PORT, () => {
  console.log(`ISRC Finder running on http://localhost:${PORT}`);
});

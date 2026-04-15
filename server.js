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

// Middleware
app.use(cors());
app.use(express.json());
app.use(express.static('public'));

// API Base URL and authentication
const SOUNDCHARTS_API_BASE = 'https://api.soundcharts.com';
const API_KEY = process.env.SOUNDCHARTS_API_KEY;

// Headers for Soundcharts API
const getHeaders = () => ({
  'Authorization': `Bearer ${API_KEY}`,
  'Content-Type': 'application/json'
});

// Search for a song by name and artist
app.post('/api/search', async (req, res) => {
  try {
    const { query } = req.body;
    
    if (!query || query.trim().length === 0) {
      return res.status(400).json({ error: 'Query is required' });
    }

    const response = await axios.get(
      `${SOUNDCHARTS_API_BASE}/api/v2/song/search/${encodeURIComponent(query)}`,
      { headers: getHeaders() }
    );

    const songs = response.data.data || [];
    
    // Extract relevant data
    const results = songs.slice(0, 5).map(song => ({
      uuid: song.id,
      title: song.title,
      artist: song.artist?.name || 'Unknown',
      isrc: song.isrc || null
    }));

    res.json({ results });
  } catch (error) {
    console.error('Search error:', error.message);
    if (error.response?.status === 401) {
      return res.status(401).json({ error: 'API authentication failed. Please check your API key.' });
    }
    res.status(500).json({ error: 'Failed to search for song', details: error.message });
  }
});

// Get detailed metadata including ISRC for a song UUID
app.post('/api/metadata', async (req, res) => {
  try {
    const { uuid } = req.body;
    
    if (!uuid) {
      return res.status(400).json({ error: 'UUID is required' });
    }

    const response = await axios.get(
      `${SOUNDCHARTS_API_BASE}/api/v2.25/song/${uuid}`,
      { headers: getHeaders() }
    );

    const data = response.data.data || response.data;
    
    res.json({
      uuid: data.id,
      title: data.title,
      artist: data.artist?.name || 'Unknown',
      isrc: data.isrc || null,
      releaseDate: data.release_date || null,
      duration: data.duration || null
    });
  } catch (error) {
    console.error('Metadata error:', error.message);
    if (error.response?.status === 401) {
      return res.status(401).json({ error: 'API authentication failed.' });
    }
    res.status(500).json({ error: 'Failed to fetch metadata', details: error.message });
  }
});

// Bulk search endpoint - finds ISRC for multiple songs
app.post('/api/bulk-search', async (req, res) => {
  try {
    const { songs } = req.body;
    
    if (!Array.isArray(songs) || songs.length === 0) {
      return res.status(400).json({ error: 'Songs array is required' });
    }

    const results = [];

    for (const song of songs) {
      try {
        const query = `${song.title} ${song.artist}`;
        
        // Search for the song
        const searchResponse = await axios.get(
          `${SOUNDCHARTS_API_BASE}/api/v2/song/search/${encodeURIComponent(query)}`,
          { headers: getHeaders() }
        );

        const searchResults = searchResponse.data.data || [];
        
        if (searchResults.length > 0) {
          const firstResult = searchResults[0];
          
          // Fetch full metadata to get ISRC
          try {
            const metadataResponse = await axios.get(
              `${SOUNDCHARTS_API_BASE}/api/v2.25/song/${firstResult.id}`,
              { headers: getHeaders() }
            );
            
            const metadata = metadataResponse.data.data || metadataResponse.data;
            
            results.push({
              input: `${song.title} - ${song.artist}`,
              found: true,
              title: metadata.title || firstResult.title,
              artist: metadata.artist?.name || firstResult.artist?.name || song.artist,
              isrc: metadata.isrc || firstResult.isrc || null,
              releaseDate: metadata.release_date || null
            });
          } catch (metadataError) {
            // If metadata fails, use search result data
            results.push({
              input: `${song.title} - ${song.artist}`,
              found: true,
              title: firstResult.title,
              artist: firstResult.artist?.name || song.artist,
              isrc: firstResult.isrc || null,
              releaseDate: null
            });
          }
        } else {
          results.push({
            input: `${song.title} - ${song.artist}`,
            found: false,
            error: 'Song not found in Soundcharts database'
          });
        }
      } catch (error) {
        results.push({
          input: `${song.title} - ${song.artist}`,
          found: false,
          error: error.message
        });
      }

      // Small delay to avoid rate limiting
      await new Promise(resolve => setTimeout(resolve, 100));
    }

    res.json({ results });
  } catch (error) {
    console.error('Bulk search error:', error.message);
    res.status(500).json({ error: 'Bulk search failed', details: error.message });
  }
});

// Health check
app.get('/api/health', (req, res) => {
  res.json({ status: 'ok', hasApiKey: !!API_KEY });
});

// Start server
app.listen(PORT, () => {
  console.log(`🎵 Bulk ISRC Finder running on http://localhost:${PORT}`);
  if (!API_KEY) {
    console.warn('⚠️  SOUNDCHARTS_API_KEY environment variable not set');
  }
});

# 🎵 Bulk ISRC Finder

A modern web application for bulk searching and retrieving ISRC (International Standard Recording Code) codes for songs using the Soundcharts API.

## Features

✨ **Bulk Search** - Paste multiple songs and get their ISRC codes at once
📋 **Easy Input Format** - Simple format: "Song Title - Artist Name" (one per line)
📊 **Results Display** - View results in a clean, organized table
📥 **Export** - Download results as CSV
📋 **Copy Results** - Quickly copy all results to clipboard
🎨 **Modern UI** - Beautiful, responsive design that works on all devices
⚡ **Server-Side API** - Secure API handling with your Soundcharts API key

## Prerequisites

- Node.js (v14 or higher)
- Soundcharts API Key ([Get one here](https://developers.soundcharts.com/))

## Installation

1. **Extract/navigate to the project folder:**
   ```bash
   cd "bulk ISRC finder"
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Set up your environment:**
   - Copy `.env.example` to `.env`
   - Add your Soundcharts API key to `.env`:
     ```
     SOUNDCHARTS_API_KEY=your_actual_api_key_here
     PORT=3000
     ```

## Running the Application

**Start the server:**
```bash
npm start
```

Or for development with auto-reload:
```bash
npm run dev
```

Then open your browser and navigate to:
```
http://localhost:3000
```

## How to Use

1. **Enter songs** in the textarea using this format:
   ```
   Let's Dance - David Bowie
   Bohemian Rhapsody - Queen
   Fix You - Coldplay
   ```

2. **Click "Search for ISRC"** to start the bulk search

3. **View results** - The app will display:
   - Song title
   - Artist name
   - ISRC code (if found)
   - Status (Found or Not Found)

4. **Export or copy** results using the buttons:
   - **Export CSV** - Download as a spreadsheet
   - **Copy All** - Copy to clipboard

## API Endpoints

### POST `/api/bulk-search`
Search for ISRC codes for multiple songs.

**Request:**
```json
{
  "songs": [
    { "title": "Song Title", "artist": "Artist Name" }
  ]
}
```

**Response:**
```json
{
  "results": [
    {
      "input": "Song Title - Artist Name",
      "found": true,
      "title": "Song Title",
      "artist": "Artist Name",
      "isrc": "ISRC123456789",
      "releaseDate": "2023-01-01"
    }
  ]
}
```

### POST `/api/search`
Search for a single song.

**Request:**
```json
{
  "query": "Song Title Artist Name"
}
```

### GET `/api/health`
Check server status and API configuration.

## Project Structure

```
bulk ISRC finder/
├── server.js           # Express server & API routes
├── package.json        # Dependencies
├── .env.example        # Environment template
├── .env                # Your configuration (not in git)
└── public/
    ├── index.html      # Frontend HTML
    ├── styles.css      # CSS styling
    └── app.js          # Frontend JavaScript
```

## Configuration

Edit `.env` to customize:
- `SOUNDCHARTS_API_KEY` - Your API key
- `PORT` - Server port (default: 3000)

## Troubleshooting

**"API authentication failed"**
- Check that your API key is correct in `.env`
- Make sure you have access to the Soundcharts API endpoints

**"Failed to fetch metadata"**
- Some songs might not be in the Soundcharts database
- Try searching with the exact spelling

**"Cannot connect to server"**
- Make sure the server is running (`npm start`)
- Check that port 3000 is not in use

## Browser Support

- Chrome/Edge (latest)
- Firefox (latest)
- Safari (latest)
- Mobile browsers

## Notes

- The app searches for the best match for each song
- Results accuracy depends on the Soundcharts database
- There's a small delay between API calls to avoid rate limiting
- ISRCs are the international standard codes for sound recordings

## License

MIT

## Resources

- [Soundcharts API Documentation](https://developers.soundcharts.com/)
- [ISRC Information](https://www.ifpi.org/isrc/)
- [What is ISRC?](https://help.soundcharts.com/en/articles/13377362-what-is-an-iswc)

---

Made with ❤️ for music professionals
# Label Finder with Soundcharts API

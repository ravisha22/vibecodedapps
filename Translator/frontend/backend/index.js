const express = require('express');
const axios = require('axios');
const cors = require('cors');

const app = express();
const PORT = 5000;

app.use(cors());
app.use(express.json());

// Get available languages from LibreTranslate
app.get('/languages', async (req, res) => {
  try {
    const response = await axios.get('https://libretranslate.com/languages');
    res.json(response.data);
  } catch (error) {
    res.status(500).json({ error: 'Failed to fetch languages' });
  }
});

// Translate a phrase into one randomly chosen language using MyMemory (Tamil, Hindi, Telugu only)
app.post('/translate', async (req, res) => {
  const { text } = req.body;
  if (!text) return res.status(400).json({ error: 'Text is required' });
  try {
    // Only Tamil, Hindi, Telugu
    const languages = [
      { code: 'ta', name: 'Tamil' },
      { code: 'hi', name: 'Hindi' },
      { code: 'te', name: 'Telugu' }
    ];
    // Translate to each language
    const translations = await Promise.all(
      languages.map(async (lang) => {
        let translation = '';
        try {
          const resp = await axios.get(
            'https://api.mymemory.translated.net/get',
            {
              params: {
                q: text,
                langpair: `en|${lang.code}`
              }
            }
          );
          translation = resp.data.responseData.translatedText;
        } catch (err) {
          console.error(`Error translating to ${lang.name}:`, err?.response?.data || err.message);
          translation = '[Error]';
        }
        return { language: lang.name, translation };
      })
    );
    res.json(translations);
  } catch (error) {
    console.error('Translation failed:', error?.response?.data || error.message);
    res.status(500).json({ error: 'Translation failed' });
  }
});

app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});
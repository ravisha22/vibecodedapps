import React, { useState } from 'react';
import { Container, Typography, TextField, Button, List, ListItem, ListItemText, CircularProgress, Paper } from '@mui/material';
import './App.css';

function App() {
  const [text, setText] = useState('');
  const [translations, setTranslations] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleTranslate = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setTranslations([]);
    try {
      const res = await fetch('http://localhost:5000/translate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text }),
      });
      if (!res.ok) throw new Error('Translation failed');
      const data = await res.json();
      setTranslations(data);
    } catch (err) {
      setError('Failed to fetch translations.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Container maxWidth="sm" style={{ marginTop: 40 }}>
      <Paper elevation={3} style={{ padding: 32 }}>
        <Typography variant="h4" gutterBottom align="center">
          Multi-Language Translator
        </Typography>
        <form onSubmit={handleTranslate} style={{ display: 'flex', gap: 16, marginBottom: 24 }}>
          <TextField
            label="Enter English Phrase"
            variant="outlined"
            fullWidth
            value={text}
            onChange={e => setText(e.target.value)}
            required
          />
          <Button type="submit" variant="contained" color="primary" disabled={loading}>
            Translate
          </Button>
        </form>
        {loading && <CircularProgress style={{ display: 'block', margin: '20px auto' }} />}
        {error && <Typography color="error">{error}</Typography>}
        {translations.length > 0 && (
          <List>
            {translations.map((item, idx) => (
              <ListItem key={idx} divider>
                <ListItemText
                  primary={<b>{item.language}</b>}
                  secondary={item.translation}
                />
              </ListItem>
            ))}
          </List>
        )}
      </Paper>
    </Container>
  );
}

export default App;
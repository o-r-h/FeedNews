# AI News Collector

This program collects news articles related to Artificial Intelligence from various sources including NewsAPI, Reddit, and RSS feeds.

## Features

- Fetches news from multiple sources (NewsAPI, Reddit, RSS)
- Calculates relevance scores for articles based on keywords
- Saves results to a timestamped JSON file with incremental IDs
- Supports user-defined search topics

## Installation

1. Clone the repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Create a `.env` file with your API keys: The URL to get the API key is https://newsapi.org/register
   ```
   TU_API_KEY_NEWSAPI=your_newsapi_key_here
   ```

## Usage

Run the program:
```
python main.py
```

The program will prompt you to enter a search topic. It will then fetch news articles related to that topic from configured sources and save them to a JSON file named `result_dd_mm_yyyy_hh_mm.json`.

## Configuration

The sources are configured in the `AINewsCollector` class. You can modify the `self.sources` list to add or remove sources.

## Relevance Scoring

The `calculate_relevance_score` function determines how relevant an article is based on a predefined list of keywords related to Artificial Intelligence. If you change the search topic or context, you should update the keywords list in this function to match the new topic for better accuracy and relevance scoring.

## Output

The program outputs:
- A summary of found articles in the console with details like title, date, source, relevance score, and preview
- A JSON file containing all article details with incremental `new_id` fields (starting from 1)

## Dependencies

- requests==2.31.0
- beautifulsoup4==4.12.2
- feedparser==6.0.10
- python-dotenv==1.0.0
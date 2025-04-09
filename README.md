# TrustNoNews

A browser extension and API service for evaluating news reliability and detecting bias in online content.

## Project Overview

TrustNoNews helps users identify potentially misleading news articles, clickbait, and biased content while browsing the web. It provides real-time analysis of news content, source credibility checks, and personalized alerts.

## Features

- Browser extension for real-time content analysis
- Source credibility evaluation based on trusted databases
- Clickbait and sensationalism detection
- Political bias identification
- API service for content verification

## Project Structure

The project is organized into the following main components:

- **Browser Extension**: Content scripts and UI for the browser extension
- **API Service**: Backend services for content analysis
- **ML Models**: Machine learning components for text analysis
- **Data Management**: Trusted sources and blacklist management

## Getting Started

1. Clone the repository
2. Run one of the folder creation scripts:
   - Windows: `create-folders.bat`
   - Unix/Linux/Mac: `bash create-folders.sh`
3. Install dependencies: `npm install`
4. Configure the environment: Copy `.env.example` to `.env` and adjust settings
5. Run the development server: `npm run dev`

## License

[MIT License](LICENSE)

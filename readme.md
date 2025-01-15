# 🕵️‍♂️ Web Article Scanner

A powerful Streamlit-based web application designed for large-scale article collection and research 📚. Perfect for organizations needing to gather extensive documentation efficiently, it can collect hundreds or even thousands of articles while maintaining minimal LLM token usage 🎯. The application intelligently filters high-quality content sources, leveraging OpenAI for concise query generation, DuckDuckGo for targeted web searches, and pdfkit for seamless PDF conversion. With real-time progress tracking and bulk ZIP downloads, it transforms time-consuming research tasks into an automated, streamlined process 🚀. The tool's efficiency comes from its smart approach: using LLM only for generating focused 10-word queries, then letting custom algorithms handle the heavy lifting of web research and content filtering.
## Features

- 🌐 Search domain-specific articles
- 📄 Convert articles into downloadable PDFs
- 📦 Real-time progress tracking during article collection
- 🗂️ Download all collected PDFs as a ZIP file

## Project Structure

```
📦 Web Article Scanner
├── web_article_scanner.py  # Core article collection logic
├── app.py                  # Streamlit web app
├── .env                    # Environment file for API keys
├── requirements.txt        # Required Python packages
└── README.md              # Project documentation
```

## Requirements

### System Requirements
- Python 3.8 or newer
- `wkhtmltopdf` (for PDF generation)

### Dependencies
See `requirements.txt` for complete list:
- Streamlit
- OpenAI
- BeautifulSoup4
- pdfkit
- duckduckgo_search
- python-dotenv
- requests

## Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/MrMunio/Web-Article-Scanner.git
   cd Web-Article-Scanner
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up wkhtmltopdf:**
   - Download and install `wkhtmltopdf` from [wkhtmltopdf.org](https://wkhtmltopdf.org)
   - Add the "wkhtmltopdf.exe" path to the `.env` file

4. **Create a `.env` file:**
   ```plaintext
   OPENAI_API_KEY=your_openai_api_key
   WKHTMLTOPDF_PATH=/path/to/wkhtmltopdf.exe
   ```

## Usage

1. **Start the application:**
   ```bash
   streamlit run app.py
   ```

2. **Using the application:**
   - Enter a description of the domain you want to search
   - Specify the number of articles to collect
   - Click "Start Search" to begin the collection process
   - Monitor the progress in real-time
   - Download the collected articles as a ZIP file when complete

## Troubleshooting

### Common Issues
- **PDF Generation Fails**: Ensure `wkhtmltopdf` is installed and the path is correctly specified in `.env`
- **API Errors**: Verify your OpenAI API key is valid and properly set in `.env`
- **Search Issues**: Check your internet connection and ensure you're not being rate-limited

### Getting Help
If you encounter any issues:
1. Check the console output for error messages
2. Verify all dependencies are installed correctly
3. Ensure all environment variables are set properly
4. Open an issue on the GitHub repository

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request



This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- OpenAI for providing the API for query generation
- DuckDuckGo for search capabilities
- The Streamlit team for their amazing framework

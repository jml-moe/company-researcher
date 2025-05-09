# Company Researcher

A Django-based application for researching, analyzing, and comparing companies with AI-powered insights.

## Features

- **Workspace Management**: Create and manage workspaces to organize your company research
- **AI-Powered Research**: Automatically generate comprehensive company profiles using GPT-4o-mini
- **Investment Scoring**: Get in-depth analysis of companies with scores across multiple categories:
  - Financial Health
  - Business Risk
  - Growth Potential
  - Industry Position
  - External Trends
- **Document Management**: Upload and analyze company documents for deeper insights
- **AI Chat Assistant**: Interact with your research data through a natural language interface
- **Market Trends**: Track and analyze industry trends affecting your target companies

## Technology Stack

- **Backend**: Django
- **Frontend**: Bootstrap 5, JavaScript
- **Database**: SQLite
- **AI Models**: OpenAI GPT-4o-mini
- **Document Processing**: PDF extraction and analysis
- **Search**: Semantic search with Tavily API

## Installation

### Prerequisites

- Python 3.9+
- pip
- virtualenv

### Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/company-researcher.git
   cd company-researcher
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file in the project root with your API keys:
   ```
   OPENAI_API_KEY=your_openai_api_key
   TAVILY_API_KEY=your_tavily_api_key
   ```

5. Apply migrations:
   ```bash
   python manage.py migrate
   ```

6. Create a superuser:
   ```bash
   python manage.py createsuperuser
   ```
7. Make sure Redis is running:
   ```bash
   redis-server
   ```
8. Run the development server:
   ```bash
   python manage.py runserver
   ```

9. Start the Huey task queue for background processing:
   ```bash
   ./manage.py run_huey --workers 4
   ```

10. Access the application at http://127.0.0.1:8000/

## Usage

1. **Create a Workspace**: Start by creating a new workspace to organize your research
2. **Research a Company**: Enter a company name to generate a detailed profile
3. **View Analysis**: Explore the investment scoring and business insights
4. **Upload Documents**: Add relevant documents for deeper analysis
5. **Compare Companies**: Select up to 3 companies to compare across metrics
6. **Chat with AI**: Use the assistant to get natural language answers about your research

## Project Structure

- `company_researcher/`: Main project settings
- `researcher/`: Main application code
  - `models.py`: Database models for workspaces, companies, documents, etc.
  - `views.py`: View controllers for the application
  - `templates/`: HTML templates
  - `tasks.py`: Background tasks for AI processing
  - `utils.py`: Utility functions
  - `chatbot.py`: AI assistant implementation

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details. 
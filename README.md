# Weekly Activity Report Bot

A Python-based Telegram bot that collects users' weekly activity notes, transforms them into professional and formal reports using Google Gemini AI, automatically generates Word (.docx) documents, and uploads them to Google Drive.

## Features

- **AI-Powered Text Editing:** Uses the Google Gemini API to transform users' informal notes into professional and corporate report language.
- **Step-by-Step Data Collection:** Collects information from users under six different categories about their weekly activities.
- **Automatic Word Report Generation:** Creates organized and formatted Word documents using the `python-docx` library.
- **Google Drive Integration:** Automatically uploads generated reports to a specified Google Drive folder.
- **Error Handling:** If the Gemini API fails to respond, the report generation process continues using the user's original notes.
- **Asynchronous Operations:** Uses `asyncio` to handle bot operations more efficiently.
- **Secure Configuration:** API keys and authentication credentials are managed through a `.env` file.

## Technologies Used

- Python
- Telegram Bot API (`python-telegram-bot`)
- Google Gemini API (`google-genai`)
- Google Drive API
- Google Authentication (`google-auth`, `google-auth-oauthlib`)
- python-docx
- python-dotenv
- Pydantic
- asyncio

## Prerequisites

Before running the project, make sure you have the following:

- Python 3.x
- A Telegram account
- A Telegram Bot Token
- A Google Gemini API Key
- A Google Cloud Platform account
- Google Drive API access

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/elonaz2007-arch/haftalik-rapor-botu.git
```

Navigate to the project directory:

```bash
cd haftalik-rapor-botu
```

### 2. Create a Virtual Environment (Optional)

```bash
python -m venv venv
```

Activate the virtual environment.

**Windows:**

```bash
venv\Scripts\activate
```

**Linux / macOS:**

```bash
source venv/bin/activate
```

### 3. Install Dependencies

Install the required Python libraries using the following command:

```bash
pip install -r requirements.txt
```

## API Configuration and Authentication

Before running the project, you need to configure the required API keys and Google Drive authentication files.

### 1. Configure Environment Variables

Create a file named `.env` in the root directory of the project.

Add the following variables and replace the placeholder values with your own credentials:

```env
TELEGRAM_TOKEN=your_telegram_bot_token
GEMINI_API_KEY=your_gemini_api_key
FOLDER_ID=your_google_drive_folder_id
```

- **TELEGRAM_TOKEN:** Your Telegram bot access token.
- **GEMINI_API_KEY:** Your Google Gemini API key.
- **FOLDER_ID:** The ID of the Google Drive folder where reports will be uploaded.

### 2. Configure Google Drive API

Follow these steps to enable Google Drive integration:

1. Create a project in Google Cloud Console.
2. Enable the Google Drive API.
3. Create an OAuth 2.0 Client ID.
4. Select **Desktop App** as the application type.
5. Download the credentials file and place it in the project root directory with the name `credentials.json`.

During the first run, you will be asked to authorize access through your Google account. After successful authorization, a `token.json` file will be created automatically.

**Note:** The `.env`, `credentials.json`, and `token.json` files contain sensitive information and must never be uploaded to GitHub.

## Usage

After completing the configuration steps, run the main Python file:

```bash
python main.py
```

*Note: Replace `main.py` with the actual name of your main bot file if it is different.*

Once the bot starts running, you can interact with it through Telegram.

### Bot Commands

| Command | Description |
|---|---|
| `/start` | Starts the bot and sends a welcome message. |
| `/yenirapor` | Starts the weekly report creation process. |
| `/iptal` | Cancels the ongoing report creation process. |

### Report Generation Process

When the `/yenirapor` command is used, the bot asks the user for the following information:

1. Projects worked on
2. Completed tasks
3. Ongoing tasks
4. The most challenging topic in the laboratory during the week
5. Plans for the following week
6. Weekly performance rating (out of 10)

The collected information is processed by the Google Gemini API and transformed into a professional report.

After that, a Word document is generated, sent to the user via Telegram, and uploaded to Google Drive.

## Project Structure

```text
haftalik-rapor-botu/
│
├── main.py
├── drive_uploader.py
├── requirements.txt
├── README.md
├── .gitignore
│
├── .env
├── credentials.json
└── token.json
```

*Note: The `.env`, `credentials.json`, and `token.json` files are excluded from the GitHub repository through `.gitignore`. `main.py` is used as an example main file name.*

## Security

- API keys are stored in the `.env` file.
- Google OAuth credentials are not uploaded to GitHub.
- The `token.json` file contains user authentication information.
- Generated Word reports (`.docx`) are excluded from Git tracking.

## License

This project was developed for educational and personal development purposes.

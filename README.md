# Immerse AI

Immerse AI is a full-stack application that leverages AI to process educational videos and YouTube links, generating summaries, flashcards, quizzes, and audio summaries. It features a React frontend, a Python (FastAPI) backend, and uses Supabase for storage and database management.

---

## Table of Contents
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Setup & Installation](#setup--installation)
- [Usage](#usage)
- [Environment Variables](#environment-variables)
- [Best Practices for Documentation](#best-practices-for-documentation)
- [Contributing](#contributing)
- [License](#license)

---

## Features
- Upload and process local video files or YouTube links
- AI-generated:
  - Summaries
  - Flashcards
  - Quizzes
  - Audio summaries
- User authentication and dashboard
- Data storage and retrieval via Supabase
- Modern, responsive UI with error handling and loading states

---

## Tech Stack
- **Frontend:** React, TypeScript, Axios, Tailwind CSS
- **Backend:** Python, FastAPI, MoviePy, Whisper, Transformers, yt-dlp, Pytube
- **Database/Storage:** Supabase (PostgreSQL, Storage)
- **Other:** Docker (optional), dotenv, OpenAI (optional)

---

## Project Structure

```
/ (root)
├── backend/           # FastAPI backend
│   ├── main.py
│   ├── model_processor.py
│   └── ...
├── src/               # React frontend
│   ├── components/
│   ├── context/
│   ├── lib/
│   ├── services/
│   └── ...
├── .env               # Environment variables
├── requirements.txt    # Python dependencies
├── package.json        # Node dependencies
└── README.md           # Project documentation
```

---

## Setup & Installation

### 1. Clone the Repository
```bash
git clone <your-repo-url>
cd <project-root>
```

### 2. Backend Setup
```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env  # Fill in your environment variables
python main.py  # Or use uvicorn for development
```

### 3. Frontend Setup
```bash
cd ../
npm install
npm run dev  # or yarn dev
```

### 4. Supabase Setup
- Create a project at [Supabase](https://supabase.com/)
- Set up your tables as per the schema in the `/docs` folder or as described in the backend code
- Add your Supabase URL and keys to the `.env` files

---

## Usage
- Register or log in via the frontend
- Upload a video or submit a YouTube link
- Wait for processing to complete
- View summaries, flashcards, quizzes, and audio

---

## Environment Variables
- See `.env.example` for required variables (Supabase URL, keys, OpenAI key, etc.)
- Never commit real secrets to version control

---

## Best Practices for Documentation
- **Keep this README up to date** as the project evolves
- **Document all environment variables** and their purpose
- **Add code comments** for complex logic
- **Use docstrings** in Python functions and classes
- **Document API endpoints** (consider using OpenAPI/Swagger for FastAPI)
- **Add usage examples** for key features
- **Maintain a `CHANGELOG.md`** for major updates
- **Add a `/docs` folder** for extended documentation if needed
- **List all dependencies** and their versions
- **Provide troubleshooting and FAQ sections** as the project grows

---

## Contributing
1. Fork the repository
2. Create a new branch (`git checkout -b feature/your-feature`)
3. Commit your changes (`git commit -am 'Add new feature'`)
4. Push to the branch (`git push origin feature/your-feature`)
5. Open a Pull Request

---

## License
MIT License. See [LICENSE](LICENSE) for details.
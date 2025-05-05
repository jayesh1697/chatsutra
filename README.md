
# 🧘‍♂️ ChatSutra

**ChatSutra** is a lightweight, Streamlit-based chatbot interface powered by LLM APIs (like LLaMA via Groq). It supports persistent chat history, document-based context injection, and model switching — all with a clean and intuitive UI.

---

## 🚀 Features

- 💬 Real-time conversational chatbot
- 🧠 Context-aware via PDF, CSV, or TXT uploads
- 📁 Persistent chat history with saving, loading, and deletion
- 🔄 Dynamic model switching
- ☁️ Deployable on Render, Streamlit Cloud, or Docker

---

## 🛠️ Tech Stack

- **Frontend/UI**: [Streamlit](https://streamlit.io/)
- **Backend**: Python
- **LLM API**: Groq API (supports LLaMA models)
- **File Handling**: PyMuPDF (PDF), pandas (CSV), plain text
- **Hosting**: [Render](https://render.com)

---

## 🧑‍💻 Getting Started

### 1. Clone the Repo
```bash
git clone https://github.com/yourusername/ChatSutra.git
cd ChatSutra
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Add Your API Key
Create a `.env` file or export the key:
```bash
export GROQ_API_KEY=your_groq_api_key_here
```

### 4. Run Locally
```bash
streamlit run app.py
```

---

## ☁️ Deploy on Render (Easy)

1. Push this repo to GitHub
2. Create a Web Service on [Render.com](https://render.com)
3. Use:
   - **Build command**: `pip install -r requirements.txt`
   - **Start command**: `streamlit run app.py --server.port=$PORT`
4. Set environment variable `GROQ_API_KEY`

✅ That’s it! Your chatbot is now live.

---

## 📸 Screenshots

| Chat Interface | File Upload & Sidebar |
|----------------|------------------------|
| ![Chat](screenshots/chat.png) | ![Sidebar](screenshots/sidebar.png) |

---

## 📂 Folder Structure

```
ChatSutra/
│
├── app.py                  # Main Streamlit app
├── chat_history/           # Saved chat sessions
├── requirements.txt        # Python dependencies
├── README.md               # You're reading it!
└── render.yaml             # Optional Render config
```

---

## 📜 License

MIT License. Use freely with attribution.

---

## 🙏 Acknowledgments

- Groq API for blazing-fast LLM access
- Streamlit for rapid UI deployment
- PyMuPDF, pandas for file handling

---

## ✨ Author

Built with ❤️ by Jayesh Patel

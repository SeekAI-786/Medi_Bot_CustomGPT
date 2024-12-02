
# AI Chat Interface with Hugging Face & Gemini Models

This project provides an interactive web application built with **Streamlit**, allowing users to chat with various AI models, including those hosted on Hugging Face and Google's Gemini. It features a user-friendly interface, supports multiple AI models, and maintains a conversation history with the option to download prompts and responses.

---

## 🚀 Features
- **Model Selection**: Choose from a range of AI models, including Hugging Face-hosted models and Gemini.
- **Dynamic Response Generation**: Send prompts to selected models and receive AI-generated responses.
- **Conversation History**: Maintain a log of all conversations within a session.
- **Download Capability**: Download individual prompts and responses as `.txt` files.
- **Responsive UI**: A clean and intuitive interface for seamless interaction.
- **Error Handling**: Handles API request errors gracefully, providing user-friendly error messages.

---

## 🛠️ Tech Stack
- **Frontend**: Streamlit
- **APIs**:
  - Hugging Face Inference API
  - Gemini Model API
- **Languages**: Python
- **Dependencies**: 
  - `streamlit`
  - `huggingface_hub`
  - `requests`

---

## 📦 Installation

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/ai-chat-interface.git
cd ai-chat-interface
```

### 2. Set Up a Virtual Environment
```bash
python -m venv venv
source venv/bin/activate    # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Set Up API Keys
- Create a `.env` file in the root directory and add your API keys:
  ```
  HF_API_KEY=<your_huggingface_api_key>
  GEMINI_API_KEY=<your_gemini_api_key>
  ```

---

## ▶️ Usage

### 1. Run the Application
```bash
streamlit run app.py
```

### 2. Interact with the App
- **Select a Model**: Use the sidebar to choose your desired AI model.
- **Enter a Query**: Type your prompt into the input box and click "Generate Response."
- **View Responses**: Generated responses are displayed alongside the prompts.
- **Download Logs**: Save individual prompts and responses using the download buttons.

---

## 🎨 App Design

### Light Theme
- White background with light gray accents for text areas and containers.
- Clear contrast between components for a professional look.

---

## 📖 API Information

### Hugging Face Inference API
- Used for querying various Hugging Face-hosted AI models.
- Requires a valid Hugging Face API key.

### Gemini API
- Integrated with the Gemini language model for AI content generation.
- Requires a valid Gemini API key.

---

## 🛡️ Error Handling
- Checks for empty inputs or API errors.
- Displays informative messages to guide users when something goes wrong.

---


---

## 🔧 Future Enhancements
- Add support for additional AI models.
- Implement Fine Tuning For Custom Dataset.
- Provide advanced settings for customizing API parameters.

---

## 🤝 Contributing
Contributions are welcome! Feel free to submit a pull request or raise issues for improvements.

---

## 📜 License
This project is licensed under the MIT License. See the `LICENSE` file for details.

---

## 👤 Author
**Your Name**  
- [GitHub](https://github.com/yourusername)  
- [LinkedIn](https://linkedin.com/in/yourlinkedin)  

---

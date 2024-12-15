---

# AI Chat Interface with Hugging Face Fine-Tuned Models on Medical Datasets

This project provides an interactive web application built with **Streamlit**, allowing users to chat with AI models hosted on **Hugging Face**. The interface offers a **demo version** of the AI chat functionality, showcasing how these models can be fine tuned to generate responses to medical and mental health-related queries.

---

## 🚀 Features
- **Model Selection**: Choose from a range of **pre-trained AI models** hosted on Hugging Face fine tune those models for medical and mental health-related tasks.
- **Dynamic Response Generation**: Send prompts to selected models and receive AI-generated responses.
- **Conversation History**: Maintain a log of all conversations within a session.
- **Download Capability**: Download individual prompts and responses as `.txt` files.
- **Responsive UI**: A clean and intuitive interface for seamless interaction.
- **Error Handling**: Handles API request errors gracefully, providing user-friendly error messages.

---

## 🛠️ Tech Stack
- **Frontend**: Streamlit
- **APIs**: Hugging Face Inference API
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
- Create a `.env` file in the root directory and add your Hugging Face API key:
  ```
  HF_API_KEY=<your_huggingface_api_key>
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

## 📖 Hugging Face Models

Here are the **models** hosted on Hugging Face that are used in the demo:

1. **Llama-3.2-1B-Lora-Fine-Tune-FineTome**  
   Model URL: [Llama-3.2-1B-Lora-Fine-Tune-FineTome](https://huggingface.co/Muhammad7865253/llama-3.2-1B-Lora-Fine_Tune-FineTome)  
   - This model excels in handling **medical-related queries** and provides specialized responses for healthcare topics.

2. **Gemma-Mental-Health-Fine-Tune**  
   Model URL: [Gemma-Mental-Health-Fine-Tune](https://huggingface.co/Muhammad7865253/gemma-mental-health-fine-tune)  
   - This model is ideal for **mental health-related conversations**, offering insights, therapy suggestions, and emotional support.

3. **Qwen-1.5B-Medical-QA**  
   Model URL: [Qwen-1.5B-Medical-QA](https://huggingface.co/Muhammad7865253/qwen-1.5B-medical-QA)  
   - This model is designed for **medical question-answering** tasks, with high accuracy for healthcare-related inquiries.

---

## 🌐 Streamlit Interface

The web app for interacting with the models is available at:  
[Streamlit App URL](https://medibotcustomgpt-eepnvsgmhzcrmzbiuwdgp4.streamlit.app/)

*Note*: Due to limited resources on Streamlit, the **fine-tuned models** could not be hosted directly on the platform. The app demonstrates how the models work via Hugging Face’s API, providing a similar experience.

---

## 🔧 Future Enhancements
- Add support for additional AI models.
- Implement More Fine Tuning for Better Accuracy.
- Provide advanced settings for customizing API parameters.

---

## 🤝 Contributing
Contributions are welcome! Feel free to submit a pull request or raise issues for improvements.

---

## 📜 License
This project is licensed under the MIT License. See the `LICENSE` file for details.
Medi Bot is a demo application designed to showcase the power of large language models (LLMs) and how they can be fine-tuned to suit specific custom applications. This app highlights the incredible potential of AI to be tailored for various domains, demonstrating how advanced machine learning models can be adapted to solve real-world problems and improve efficiency. By leveraging AI, Medi Bot provides insights into how innovative solutions can be developed for multiple industries, offering a glimpse into the future of AI-powered applications.

---

## 👤 Author
**Your Name**  
- [GitHub](https://github.com/SeekAI-786)  
- [LinkedIn]([Mohammad-Aun-Ali](https://www.linkedin.com/in/mohammad-aun-ali-705852293/)

---

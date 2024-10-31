# VVPay - Automated Invoice Processing System

<div align="center">

![Python](https://img.shields.io/badge/python-3.11-blue.svg)
![Streamlit](https://img.shields.io/badge/streamlit-1.29.0-FF4B4B.svg)
![LangChain](https://img.shields.io/badge/langchain-0.1.0-green.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

</div>

## 🌟 Overview

VVPay is a sophisticated invoice processing system that leverages Large Language Models (LLMs) and advanced PDF processing to automate the extraction, validation, and payment processing of invoices. Built with a clean architecture approach, it combines modern technologies like LangChain, Streamlit, and Supabase to deliver a robust and user-friendly solution.

## 🏗️ Architecture

### System Overview
```mermaid
graph TD
    A[Streamlit UI] --> B[Service Layer]
    B --> C[LangChain Processing]
    B --> D[Database Layer]
    C --> E[OpenAI LLM]
    D --> F[Supabase]

    subgraph "Processing Flow"
        C --> G[PDF Extraction]
        G --> H[Text Analysis]
        H --> I[Data Validation]
    end

    subgraph "Data Flow"
        D --> J[Extractions]
        D --> K[Validations]
        D --> L[Payments]
    end
```


### Component Architecture
```mermaid
graph TD
    subgraph "Presentation Layer"
        A1[Upload Component]
        A2[Status Component]
        A3[Validation Component]
    end

    subgraph "Service Layer"
        B1[Document Processor]
        B2[Validation Service]
        B3[Payment Service]
    end

    subgraph "Data Layer"
        C1[Extraction Repository]
        C2[Validation Repository]
        C3[Payment Repository]
    end

    subgraph "Core Layer"
        D1[Configuration]
        D2[Error Handling]
        D3[Logging]
        D4[Interfaces]
    end

    A1 --> B1
    A2 --> B1
    A3 --> B2
    B1 --> C1
    B2 --> C2
    B3 --> C3
    B1 --> D1
    B2 --> D2
    B3 --> D3
```

### Processing Pipeline
```mermaid
sequenceDiagram
    participant U as User
    participant UI as Streamlit UI
    participant DP as Document Processor
    participant LLM as GPT-4
    participant DB as Supabase

    U->>UI: Upload PDF
    UI->>DP: Process Document
    DP->>DP: Extract Text
    DP->>LLM: Analyze Content
    LLM-->>DP: Return Structured Data
    DP->>DB: Save Extraction
    DB-->>UI: Update Status
    UI-->>U: Show Results
```

### LangGraph Processing Flow
```mermaid
graph TD
    subgraph "Document Processing"
        A[PDF Upload] --> B[PDFMiner Extraction]
        B --> C[Text Chunking]
        C --> D[LLM Analysis]
        D --> E[JSON Parsing]
        E --> F[Validation]
    end

    subgraph "LLM Components"
        D --> G[GPT-4 Model]
        G --> H[Confidence Scoring]
        H --> I[Structure Recognition]
    end

    subgraph "Error Handling"
        B --> J[Extraction Recovery]
        D --> K[LLM Retry Logic]
        E --> L[Schema Validation]
    end
```

### Database Architecture
```mermaid
graph TD
    subgraph "Supabase Integration"
        A[Connection Pool] --> B[Query Builder]
        B --> C[Transaction Manager]
        C --> D[Response Handler]
    end

    subgraph "Data Flow"
        E[Repository Layer] --> A
        F[Service Layer] --> E
        G[UI Components] --> F
    end

    subgraph "Caching"
        H[Memory Cache] --> E
        I[Query Cache] --> B
    end
```

### Payment Processing Flow
```mermaid
sequenceDiagram
    participant UI as Streamlit UI
    participant VS as Validation Service
    participant PS as Payment Service
    participant IB as Inter Bank API
    participant DB as Supabase

    UI->>VS: Request Validation
    VS->>DB: Check Meta Table
    DB-->>VS: Return Provider Data
    VS->>PS: Schedule Payment
    PS->>IB: Initialize PIX
    IB-->>PS: Return Transaction ID
    PS->>DB: Update Payment Status
    DB-->>UI: Reflect Changes
```

## 🚀 Features

### PDF Processing
- **Intelligent Text Extraction**
  - PDFMiner integration
  - Chunk-based processing
  - Error recovery
  - Multi-page support


## 📦 Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/vvpay.git
cd vvpay
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment:
```bash
cp .env.example .env
# Edit .env with your settings
```

## 🔧 Configuration

Required environment variables:
```env
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
OPENAI_API_KEY=your_openai_key
MODEL_NAME=gpt-4
```

## 🚦 Usage

1. Start the application:
```bash
streamlit run run.py
```

2. Upload PDF invoices through the UI
3. Monitor processing in Status tab
4. Review and validate in Validation tab

## 🧪 Testing

Run tests with pytest:
```bash
pytest tests/
```

## 📚 Documentation

Detailed documentation available in `doc/` directory:
- [Architecture Overview](doc/ARCHITECTURE.md)
- [Development Guide](doc/DEVELOPMENT.md)
- [API Documentation](doc/API.md)


## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.


---

<div align="center">
Victor von Sohsten
</div>
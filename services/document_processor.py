"""Document processing service using LangGraph"""
from typing import Dict, Optional
from datetime import datetime, timezone
from pathlib import Path
import tempfile
import shutil
import json

from langgraph.graph import StateGraph
from langgraph.constants import START, END
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.document_loaders import PDFMinerLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.output_parsers import JsonOutputParser

from models.db.extraction import PDFExtraction
from models.service.enums import Status, PaymentType
from models.processing.llm import InvoiceData
from models.processing.states import GraphState, create_initial_state
from core.exceptions import PDFError, ExtractionError, ErrorCode, ErrorSeverity, InitializationError, ConfigurationError
from core.logging import get_logger
from core.interfaces import ProcessorInterface
from core.config import settings

logger = get_logger(__name__)

class DocumentProcessor(ProcessorInterface[PDFExtraction]):
    """Document processor using LangGraph"""
    
    def __init__(self):
        """Initialize the document processor"""
        self.initialize()

    def initialize(self) -> None:
        """Initialize processor components"""
        logger.info("Initializing DocumentProcessor")
        try:
            self.validate_config()
            # Initialize components
            self.text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=settings.MODEL_CHUNK_SIZE,
                chunk_overlap=settings.MODEL_CHUNK_OVERLAP
            )
            self.llm = ChatOpenAI(
                model_name=settings.MODEL_NAME,
                temperature=settings.MODEL_TEMPERATURE
            )
            self.parser = JsonOutputParser(pydantic_object=InvoiceData)
            self.graph = self._create_graph()
            logger.info("DocumentProcessor initialized successfully")
        except Exception as e:
            logger.error("Failed to initialize DocumentProcessor", exc_info=e)
            raise InitializationError(
                message="Failed to initialize processor",
                details={"error": str(e)},
                original_error=e
            )

    def validate_config(self) -> None:
        """Validate required configuration settings"""
        required_settings = [
            'MODEL_NAME',
            'MODEL_TEMPERATURE',
            'MODEL_CHUNK_SIZE',
            'MODEL_CHUNK_OVERLAP'
        ]
        
        missing_settings = [
            setting for setting in required_settings 
            if not hasattr(settings, setting)
        ]
        
        if missing_settings:
            raise ConfigurationError(
                message="Missing required configuration settings",
                details={"missing_settings": missing_settings}
            )

    def _create_graph(self) -> StateGraph:
        """Create the processing graph"""
        workflow = StateGraph(GraphState)
        
        # Add nodes
        workflow.add_node("extract_text", self._extract_text)
        workflow.add_node("analyze_text", self._analyze_text)
        workflow.add_node("parse_json", self._parse_json)
        
        # Add edges
        workflow.add_edge(START, "extract_text")
        workflow.add_edge("extract_text", "analyze_text")
        workflow.add_edge("analyze_text", "parse_json")
        workflow.add_edge("parse_json", END)
        
        return workflow.compile()

    def _extract_text(self, state: GraphState) -> Dict:
        """Extract text from PDF using PDFMiner"""
        temp_dir = None
        try:
            logger.info(f"Extracting text from {state['file_name']}")
            
            # Create temporary directory for PDF processing
            temp_dir = tempfile.mkdtemp(prefix='pdf_processing_')
            temp_path = Path(temp_dir) / "temp.pdf"
            
            # Write content to temporary file
            with open(temp_path, 'wb') as f:
                f.write(state['content'])
            
            # Extract text using PDFMiner
            loader = PDFMinerLoader(str(temp_path))
            documents = loader.load()
            
            # Split text into chunks
            splits = self.text_splitter.split_documents(documents)
            raw_text = "\n".join(doc.page_content for doc in splits)
            
            if not raw_text.strip():
                return {**state, "error": "No text content found in PDF"}
            
            logger.debug(f"Extracted text preview: {raw_text[:500]}...")
            return {
                **state,
                "raw_text": raw_text,
                "documents": [doc.page_content for doc in splits]
            }
            
        except Exception as e:
            logger.error("Text extraction failed", exc_info=e)
            return {**state, "error": f"Text extraction failed: {str(e)}"}
            
        finally:
            # Clean up temporary directory
            if temp_dir and Path(temp_dir).exists():
                shutil.rmtree(temp_dir, ignore_errors=True)

    def _analyze_text(self, state: GraphState) -> Dict:
        """Analyze text with first LLM call"""
        try:
            if state.get('error'):
                return state
                
            prompt = ChatPromptTemplate.from_messages([
                ("system", """You are an expert in analyzing Brazilian invoices (Notas Fiscais).
                Extract and analyze the following information:
                
                Required Information:
                1. CNPJ: Extract the provider's CNPJ (exactly 14 digits)
                2. Amount (Valor): Extract the payment amount (numeric value)
                3. Period (Competência): Extract the month/year in MM/YYYY format
                4. Provider Name: Extract the complete name of the service provider
                5. Description: Extract a brief description of services
                6. Payment Type: Determine based on these rules:
                    - If filename contains 'bonus' → use 'bonus'
                    - If filename contains 'reembolso' → use 'reembolso'
                    - Otherwise → use 'pc'
                
                Present each piece of information with a clear label."""),
                ("human", "Please analyze this invoice:\nFile Name: {file_name}\nContent: {text}")
            ])
            
            messages = prompt.format_messages(
                file_name=state['file_name'],
                text=state['raw_text']
            )
            
            response = self.llm.invoke(messages)
            return {**state, "llm_analysis": response.content}
            
        except Exception as e:
            logger.error("LLM analysis failed", exc_info=e)
            return {**state, "error": str(e)}

    def _parse_json(self, state: GraphState) -> Dict:
        """Convert analysis to structured JSON"""
        try:
            if state.get('error'):
                return state
                
            prompt = ChatPromptTemplate.from_messages([
                ("system", """Convert the following invoice analysis into a JSON object with these exact fields:
                
                {format_instructions}
                
                Important:
                - CNPJ should be exactly 14 digits
                - valor should be a number (no currency symbols)
                - competence must be MM/YYYY format
                - payment_type must be one of: pc, reembolso, bonus
                - Add a confidence field between 0.0 and 1.0 indicating extraction confidence"""),
                ("human", "Convert this analysis to JSON:\n{text}")
            ])
            
            # Add format instructions
            prompt = prompt.partial(format_instructions=self.parser.get_format_instructions())
            
            # Create and execute chain
            chain = prompt | self.llm | self.parser
            json_output = chain.invoke({"text": state['llm_analysis']})
            
            # Ensure confidence score exists
            if 'confidence' not in json_output:
                json_output['confidence'] = 0.85  # Default confidence score
            
            return {**state, "json_output": json_output}
            
        except Exception as e:
            logger.error("JSON parsing failed", exc_info=e)
            return {**state, "error": str(e)}

    def process_document(
        self,
        content: bytes,
        filename: str,
        metadata: Optional[Dict] = None
    ) -> PDFExtraction:
        """Process document and extract information"""
        try:
            # Create initial state with both filename and content
            state = create_initial_state(filename, content)
            
            # Process through graph
            logger.info(f"Starting processing for {filename}")
            final_state = self.graph.invoke(state)
            
            # Check for errors
            if final_state.get('error'):
                raise ExtractionError(
                    message=final_state['error'],
                    details={"filename": filename},
                    original_error=None
                )
            
            # Create PDFExtraction from final state
            json_data = final_state['json_output']
            extraction = PDFExtraction(
                file_name=filename,
                raw_text=final_state['raw_text'],
                cnpj=json_data['cnpj'],
                valor=float(json_data['valor']),
                competence=json_data['competence'],
                payee_name=json_data['payee_name'],
                description=json_data['description'],
                payment_type=PaymentType(json_data['payment_type']),
                status=Status.EXTRACTED,
                extracted_at=datetime.now(timezone.utc),
                confidence_score=json_data.get('confidence', 0.0)
            )
            
            logger.info(f"Processing completed for {filename}")
            return extraction
            
        except Exception as e:
            logger.error(f"Processing failed for {filename}", exc_info=e)
            raise ExtractionError(
                message=f"Document processing failed: {str(e)}",
                details={"filename": filename},
                original_error=e
            )

# Create singleton instance
document_processor = DocumentProcessor()
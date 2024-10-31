"""
Standalone test for invoice processing using LangGraph
This file is independent of the main project and used for testing the processing flow
"""

import os
from typing import TypedDict, Dict, Optional
from pathlib import Path
from datetime import datetime
import json
import logging

# LangChain imports
from langgraph.graph import StateGraph
from langgraph.constants import START, END
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.document_loaders import PDFMinerLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from pydantic import BaseModel, Field
from langchain_core.output_parsers import JsonOutputParser

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Add InvoiceData model
class InvoiceData(BaseModel):
    """Structure for invoice data"""
    cnpj: str = Field(description="14-digit CNPJ number")
    valor: float = Field(description="Payment amount")
    competence: str = Field(description="MM/YYYY format")
    payee_name: str = Field(description="Provider name")
    description: str = Field(description="Service description")
    payment_type: str = Field(description="pc/reembolso/bonus")

# Update state to include structured data
class InvoiceState(TypedDict):
    """State that flows through the graph"""
    file_path: str
    file_name: str
    raw_text: Optional[str]
    llm_response: Optional[str]
    structured_data: Optional[Dict]
    error: Optional[str]

def create_initial_state(file_path: str) -> InvoiceState:
    """Create initial state for processing"""
    return {
        "file_path": str(file_path),
        "file_name": Path(file_path).name,
        "raw_text": None,
        "llm_response": None,
        "structured_data": None,
        "error": None
    }

def extract_text_node():
    """Create text extraction node"""
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=2000,
        chunk_overlap=200
    )
    
    def extract_text(state: InvoiceState) -> Dict:
        """Extract text from PDF"""
        try:
            logger.info(f"Extracting text from {state['file_name']}")
            
            # Load PDF
            loader = PDFMinerLoader(state['file_path'])
            documents = loader.load()
            
            # Split text
            splits = text_splitter.split_documents(documents)
            raw_text = "\n".join(doc.page_content for doc in splits)
            
            if not raw_text.strip():
                raise ValueError("No text content extracted from PDF")
            
            logger.info(f"Successfully extracted {len(raw_text)} characters")
            # Log first 500 characters of extracted text
            logger.info(f"Text preview: {raw_text[:500]}...")
            return {"raw_text": raw_text}
            
        except Exception as e:
            error_msg = f"Text extraction failed: {str(e)}"
            logger.error(error_msg)
            return {"error": error_msg}
    
    return extract_text

def llm_node():
    """Create LLM processing node"""
    llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0
    )
    
    # Create prompt
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are an expert in analyzing Brazilian invoices (Notas Fiscais).
        Analyze this invoice and extract the following information:
        - CNPJ number (14 digits)
        - Payment amount (valor)
        - Competence period (MM/YYYY)
        - Provider name
        - Service description
        - Payment type (check if 'bonus' or 'reembolso' appears, otherwise use 'pc')
        
        Return the information in a clear, structured format."""),
        ("human", "{text}")
    ])
    
    def process_with_llm(state: InvoiceState) -> Dict:
        """Process text with LLM"""
        try:
            if state.get('error'):
                return state
            
            logger.info(f"Processing with LLM: {state['file_name']}")
            
            # Get LLM response
            messages = prompt.format_messages(text=state['raw_text'])
            response = llm.invoke(messages)
            
            # Log the raw response
            logger.info("LLM Raw Response:")
            logger.info(response.content)
            
            return {"llm_response": response.content}
            
        except Exception as e:
            error_msg = f"LLM processing failed: {str(e)}"
            logger.error(error_msg)
            return {"error": error_msg}
    
    return process_with_llm

def json_parsing_node():
    """Create JSON parsing node"""
    llm = ChatOpenAI(
        model="gpt-4",
        temperature=0
    )
    
    # Create parser
    parser = JsonOutputParser(pydantic_object=InvoiceData)
    
    # Create prompt
    prompt = ChatPromptTemplate.from_messages([
        ("system", """Convert the following invoice analysis into a JSON object with these exact fields:
        
        {format_instructions}
        
        Important:
        - CNPJ should be exactly 14 digits
        - valor should be a number (remove 'R$' and convert)
        - competence must be MM/YYYY format
        - payment_type must be one of: pc, reembolso, bonus"""),
        ("human", "Convert this analysis to JSON:\n{text}")
    ])
    
    # Add format instructions
    prompt = prompt.partial(format_instructions=parser.get_format_instructions())
    
    def parse_to_json(state: InvoiceState) -> Dict:
        """Convert LLM response to structured JSON"""
        try:
            if state.get('error'):
                return state
            
            logger.info(f"Parsing response to JSON for {state['file_name']}")
            
            # Get structured data
            chain = prompt | llm | parser
            structured_data = chain.invoke({"text": state['llm_response']})
            
            logger.info("Successfully parsed to JSON")
            logger.info(f"Structured data: {json.dumps(structured_data, indent=2)}")
            
            return {"structured_data": structured_data}
            
        except Exception as e:
            error_msg = f"JSON parsing failed: {str(e)}"
            logger.error(error_msg)
            return {"error": error_msg}
    
    return parse_to_json

def create_graph() -> StateGraph:
    """Create the processing graph"""
    workflow = StateGraph(state_schema=InvoiceState)
    
    # Add nodes
    workflow.add_node("extract_text", extract_text_node())
    workflow.add_node("llm_process", llm_node())
    workflow.add_node("json_parse", json_parsing_node())
    
    # Add edges
    workflow.add_edge(START, "extract_text")
    workflow.add_edge("extract_text", "llm_process")
    workflow.add_edge("llm_process", "json_parse")
    workflow.add_edge("json_parse", END)
    
    return workflow.compile()

def process_invoice(file_path: str) -> Dict:
    """Process a single invoice"""
    try:
        # Create graph
        graph = create_graph()
        
        # Create initial state
        initial_state = create_initial_state(file_path)
        
        # Process invoice
        logger.info(f"Starting processing of {initial_state['file_name']}")
        final_state = graph.invoke(initial_state)
        
        # Check for errors
        if final_state.get('error'):
            logger.error(f"Processing failed: {final_state['error']}")
            return {
                "success": False,
                "error": final_state['error']
            }
        
        # Return results
        return {
            "success": True,
            "file_name": final_state['file_name'],
            "llm_response": final_state['llm_response']
        }
        
    except Exception as e:
        logger.error(f"Processing failed with error: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }

if __name__ == "__main__":
    # Test file path
    test_file = r"C:\Users\victo\OneDrive\projects\vvpay\example\(NFS-e ps-pj-03-set24) 08.2024.BÔNUS.ALEXANDRE-HENRIQUE-SOARES.pdf"
    
    # Process invoice
    logger.info("Starting test processing")
    result = process_invoice(test_file)
    
    # Print results
    if result["success"]:
        print("\nProcessing Successful!")
        print(f"File: {result['file_name']}")
        print("\nLLM Response:")
        print(result['llm_response'])
        if result.get('structured_data'):
            print("\nStructured Data:")
            print(json.dumps(result['structured_data'], indent=2))
    else:
        print(f"\nProcessing Failed: {result['error']}")
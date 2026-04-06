from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import uvicorn
import logging
from sympy import sympify, latex, pretty, Integral, Derivative
from sympy.parsing.latex import parse_latex

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="AutoGrader Math Parser Service",
    description="Mathematical expression parsing and validation",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class MathParseRequest(BaseModel):
    expression: str
    context: Optional[str] = None

class MathParseResponse(BaseModel):
    latex: str
    plaintext: str
    symbolic: str
    is_valid: bool
    confidence: float

class MathValidateRequest(BaseModel):
    expression: str
    expected_type: Optional[str] = None  # equation, integral, derivative, etc.

class MathValidateResponse(BaseModel):
    is_valid: bool
    error_message: Optional[str] = None
    suggestions: list[str] = []

@app.get("/")
async def root():
    return {
        "service": "AutoGrader Math Parser Service",
        "status": "running",
        "version": "1.0.0"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.post("/api/math/parse", response_model=MathParseResponse)
async def parse_expression(request: MathParseRequest):
    """
    Parse mathematical expression into structured format.
    
    TODO: Implement:
    - LaTeX conversion
    - Symbolic representation with SymPy
    - Expression validation
    """
    try:
        logger.info(f"Parsing expression: {request.expression}")
        
        # Try to parse as LaTeX if it looks like LaTeX, otherwise standard SymPy
        try:
            if "\\" in request.expression or "^" in request.expression:
                expr = parse_latex(request.expression)
            else:
                expr = sympify(request.expression)
            
            return MathParseResponse(
                latex=latex(expr),
                plaintext=pretty(expr),
                symbolic=str(expr),
                is_valid=True,
                confidence=0.95
            )
        except Exception as e:
            logger.warning(f"SymPy parse failed: {str(e)}")
            # Fallback for simple strings
            return MathParseResponse(
                latex=request.expression,
                plaintext=request.expression,
                symbolic=request.expression,
                is_valid=False,
                confidence=0.3
            )
    except Exception as e:
        logger.error(f"Error parsing expression: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/math/validate", response_model=MathValidateResponse)
async def validate_expression(request: MathValidateRequest):
    """
    Validate mathematical expression syntax and structure.
    
    TODO: Implement validation logic
    """
    try:
        logger.info(f"Validating expression: {request.expression}")
        
        try:
            sympify(request.expression)
            return MathValidateResponse(is_valid=True, error_message=None)
        except Exception as e:
            return MathValidateResponse(
                is_valid=False, 
                error_message=str(e),
                suggestions=["Check for missing operators", "Ensure balanced parentheses"]
            )
    except Exception as e:
        logger.error(f"Error validating expression: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8002)

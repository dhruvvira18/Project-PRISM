# Implementation Plan: ADHD Adaptive Learning System

## Overview

This implementation plan breaks down the ADHD Adaptive Learning System into incremental coding tasks. The system will be built using Python with FastAPI for the API layer, Ollama for LLM inference, and Hypothesis for property-based testing. The implementation follows a bottom-up approach: core data models → business logic → API layer → testing → optional RAG integration.

## Tasks

- [ ] 1. Set up project structure and dependencies
  - Create directory structure: `app/`, `app/models/`, `app/services/`, `app/api/`, `tests/`
  - Create `requirements.txt` with dependencies: fastapi, uvicorn, pydantic, ollama, hypothesis, pytest
  - Create `pyproject.toml` for project configuration
  - Set up `.gitignore` for Python projects
  - _Requirements: 9.3, 9.4_

- [ ] 2. Implement core data models
  - [ ] 2.1 Create assessment data models
    - Define `Option`, `Question`, `Assessment` dataclasses in `app/models/assessment.py`
    - Implement validation for complexity levels (1-4)
    - Create question bank with 5 pre-defined questions
    - _Requirements: 1.1, 1.2, 1.8_
  
  - [ ]* 2.2 Write property test for assessment structure
    - **Property 1: Assessment question count invariant**
    - **Property 2: Question option count invariant**
    - **Validates: Requirements 1.1, 1.2**
  
  - [ ] 2.3 Create session data models
    - Define `LearningStep`, `Session` dataclasses in `app/models/session.py`
    - Implement session ID generation (UUID)
    - Add session state tracking (active/inactive)
    - _Requirements: 2.1, 3.5_
  
  - [ ]* 2.4 Write property test for session structure
    - **Property 11: Learning step structure completeness**
    - **Validates: Requirements 2.4**

- [ ] 3. Implement Assessment Engine
  - [ ] 3.1 Create AssessmentEngine class
    - Implement `create_assessment()` method returning 5 questions
    - Implement `submit_answer()` method recording complexity levels
    - Implement `calculate_level()` method computing median
    - Store assessments and levels in-memory (dict)
    - _Requirements: 1.1, 1.4, 1.5, 1.6, 1.7_
  
  - [ ]* 3.2 Write property tests for assessment logic
    - **Property 3: Answer complexity recording**
    - **Property 4: Median calculation correctness**
    - **Property 5: Level assignment consistency**
    - **Property 6: Level persistence**
    - **Property 7: Level bounds validation**
    - **Validates: Requirements 1.4, 1.5, 1.6, 1.7, 1.8**
  
  - [ ]* 3.3 Write unit tests for edge cases
    - Test median with all same values
    - Test median with alternating values (1,2,3,4,3)
    - Test persistence across multiple retrievals
    - _Requirements: 1.5, 1.7_

- [ ] 4. Checkpoint - Ensure assessment tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 5. Implement Ollama LLM Client
  - [ ] 5.1 Create OllamaClient class
    - Implement `__init__()` with configurable base URL and model name
    - Implement `generate()` method for text generation
    - Implement `generate_json()` method for structured output
    - Add timeout handling (2 seconds)
    - Add retry logic for connection errors (3 attempts)
    - _Requirements: 2.8, 7.2, 7.5_
  
  - [ ]* 5.2 Write unit tests with mocked responses
    - Mock successful generation
    - Mock timeout scenarios
    - Mock connection errors
    - Test retry logic
    - _Requirements: 7.5_

- [ ] 6. Implement Content Generator
  - [ ] 6.1 Create ContentGenerator class
    - Implement prompt template construction
    - Implement level-to-vocabulary mapping (1-4)
    - Implement `generate_steps()` method creating 3-5 steps
    - Implement word count validation (40-60 words)
    - Add retry logic for invalid word counts
    - _Requirements: 2.3, 2.5, 2.6, 4.1_
  
  - [ ] 6.2 Implement structured JSON parsing
    - Parse LLM JSON response into LearningStep objects
    - Handle malformed JSON with retries
    - Validate step structure (title and text fields)
    - _Requirements: 2.4, 2.7, 6.1_
  
  - [ ]* 6.3 Write property tests for content generation
    - **Property 10: Learning step count bounds**
    - **Property 12: Word count constraints**
    - **Property 13: JSON response structure completeness**
    - **Property 14: Generation latency bound**
    - **Validates: Requirements 2.3, 2.5, 2.7, 2.8**
  
  - [ ]* 6.4 Write unit tests for prompt construction
    - Test prompt for each language level (1-4)
    - Verify vocabulary mapping is applied
    - Test with different subjects and topics
    - _Requirements: 2.6, 4.1_

- [ ] 7. Implement Session Manager
  - [ ] 7.1 Create SessionManager class
    - Implement `create_session()` method
    - Implement in-memory session storage with TTL (1 hour)
    - Implement `get_session()` method with expiration check
    - Coordinate with ContentGenerator for initial step generation
    - _Requirements: 2.1, 3.5_
  
  - [ ] 7.2 Implement command processing
    - Implement `process_command()` method handling "next", "simplify", "exit"
    - Implement "next" logic: increment step index, check bounds
    - Implement "simplify" logic: decrease level (min 1), regenerate step
    - Implement "exit" logic: set session inactive
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 3.6_
  
  - [ ]* 7.3 Write property tests for session management
    - **Property 15: Next command navigation**
    - **Property 16: Simplify command level adjustment**
    - **Property 17: Step regeneration on level change**
    - **Property 18: Exit command termination**
    - **Property 19: Session completion at final step**
    - **Validates: Requirements 3.1, 3.2, 3.4, 3.5, 3.6**
  
  - [ ]* 7.4 Write unit tests for edge cases
    - Test "simplify" at level 1 (should stay at 1)
    - Test "next" at final step (should complete session)
    - Test commands on expired session
    - Test commands on inactive session
    - _Requirements: 3.3, 3.6_

- [ ] 8. Checkpoint - Ensure core logic tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 9. Implement FastAPI endpoints
  - [ ] 9.1 Create assessment endpoints
    - Implement `POST /api/assessment/start` endpoint
    - Implement `POST /api/assessment/submit` endpoint
    - Add request/response models using Pydantic
    - Add input validation
    - _Requirements: 1.1, 1.5, 1.6_
  
  - [ ] 9.2 Create session endpoints
    - Implement `POST /api/session/start` endpoint
    - Implement `POST /api/session/command` endpoint
    - Add request/response models using Pydantic
    - Add subject validation (Physics, Chemistry, Biology, Social Studies)
    - Add language level validation (1-4)
    - _Requirements: 2.1, 2.2, 3.1, 3.2, 3.5_
  
  - [ ] 9.3 Implement error handling
    - Add exception handlers for validation errors (400)
    - Add exception handlers for not found errors (404)
    - Add exception handlers for timeout errors (504)
    - Add exception handlers for LLM service errors (503)
    - Return structured error responses with messages
    - _Requirements: 8.5_
  
  - [ ]* 9.4 Write property tests for API validation
    - **Property 8: Session input acceptance**
    - **Property 9: Subject validation**
    - **Property 28: Invalid subject error response**
    - **Property 29: Topic name acceptance**
    - **Validates: Requirements 2.1, 2.2, 8.5, 8.6**
  
  - [ ]* 9.5 Write integration tests for endpoints
    - Test full assessment flow: start → submit → get level
    - Test full session flow: start → next → simplify → exit
    - Test error responses for invalid inputs
    - _Requirements: 1.1, 2.1, 3.1, 8.5_

- [ ] 10. Implement ADHD-optimized formatting
  - [ ] 10.1 Add visual scaffolding to prompts
    - Update prompt templates to request bullet points and lists
    - Add post-processing to ensure formatting is present
    - Implement fallback formatting if LLM doesn't include it
    - _Requirements: 4.4_
  
  - [ ]* 10.2 Write property test for visual scaffolding
    - **Property 20: Visual scaffolding presence**
    - **Validates: Requirements 4.4**

- [ ] 11. Implement performance monitoring
  - [ ] 11.1 Add latency tracking
    - Add timing decorators for generation methods
    - Log response times for all requests
    - Implement timeout enforcement (2 seconds)
    - _Requirements: 2.8, 7.2, 7.4_
  
  - [ ]* 11.2 Write property tests for performance
    - **Property 25: Command response latency**
    - **Property 26: 95th percentile latency**
    - **Property 27: Timeout handling**
    - **Validates: Requirements 7.2, 7.4, 7.5**

- [ ] 12. Checkpoint - Ensure all core tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 13. Create application entry point
  - [ ] 13.1 Create main.py
    - Initialize FastAPI app
    - Register API routers
    - Add CORS middleware for frontend integration
    - Add startup event to verify Ollama connection
    - Configure uvicorn server settings
    - _Requirements: 9.3_
  
  - [ ] 13.2 Create configuration management
    - Create `app/config.py` for environment variables
    - Add configuration for Ollama URL, model name, timeout
    - Add configuration for session TTL
    - _Requirements: 7.3_
  
  - [ ]* 13.3 Write integration test for full application
    - Test application startup
    - Test Ollama connection check
    - Test all endpoints with real Ollama instance
    - _Requirements: 2.1, 7.3_

- [ ] 14. Optional: Implement RAG integration
  - [ ] 14.1 Create RAGModule class
    - Implement `__init__()` with embedding model and vector store
    - Implement `index_textbook()` method for document ingestion
    - Implement `retrieve_context()` method for semantic search
    - Use sentence-transformers for embeddings
    - Use FAISS or ChromaDB for vector storage
    - _Requirements: 5.1, 5.4_
  
  - [ ] 14.2 Integrate RAG with ContentGenerator
    - Add optional RAG parameter to `generate_steps()`
    - Retrieve context before generation when RAG enabled
    - Inject retrieved passages into prompt
    - Add fallback to non-RAG mode on errors
    - _Requirements: 5.2, 5.3_
  
  - [ ]* 14.3 Write property tests for RAG
    - **Property 21: RAG retrieval activation**
    - **Property 22: RAG context injection**
    - **Property 23: RAG-independent operation**
    - **Property 24: RAG retrieval relevance**
    - **Validates: Requirements 5.1, 5.2, 5.3, 5.4**
  
  - [ ]* 14.4 Write unit tests for RAG module
    - Test document indexing
    - Test retrieval with sample queries
    - Test fallback when no results found
    - Test error handling for vector store issues
    - _Requirements: 5.3, 5.4_

- [ ] 15. Create documentation and setup instructions
  - [ ] 15.1 Create README.md
    - Document system overview and features
    - Add installation instructions
    - Add Ollama setup instructions (install, pull phi3:mini)
    - Add API endpoint documentation with examples
    - Add configuration options
    - _Requirements: 7.3_
  
  - [ ] 15.2 Create API documentation
    - Add OpenAPI/Swagger documentation via FastAPI
    - Document request/response schemas
    - Add example requests for each endpoint
    - _Requirements: 2.7, 6.1_

- [ ] 16. Final checkpoint - Run full test suite
  - Run all unit tests
  - Run all property-based tests (100 iterations each)
  - Run integration tests with Ollama
  - Verify test coverage >80%
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP
- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation at key milestones
- Property tests validate universal correctness properties (100 iterations each)
- Unit tests validate specific examples and edge cases
- RAG integration (Task 14) is entirely optional and can be implemented later
- The system can operate fully without RAG using LLM base knowledge

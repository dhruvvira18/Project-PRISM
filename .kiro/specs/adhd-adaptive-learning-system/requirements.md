# Requirements Document

## Introduction

The ADHD Adaptive Learning System is an AI-powered educational platform designed to support students with ADHD in Grades 5-10. The system restructures textbook content into cognitively optimized micro-learning units that reduce cognitive overload and improve attention retention. It adapts explanations based on individual language comprehension levels across core subjects: Physics, Chemistry, Biology, and Social Studies.

## Glossary

- **System**: The ADHD Adaptive Learning System
- **Student**: A user in Grades 5-10 with ADHD using the platform
- **Language_Level**: A numeric value (1-4) representing comprehension complexity, where 1 is simplest and 4 is most complex
- **Learning_Step**: A single micro-learning unit containing a title and explanation (40-60 words)
- **Focus_Session**: An active learning session where a student progresses through learning steps
- **Assessment_Question**: A question with 4 options of varying complexity used to determine language level
- **LLM**: Large Language Model used for content generation (phi3:mini via Ollama)
- **RAG**: Retrieval-Augmented Generation system for grounding content in textbook materials

## Requirements

### Requirement 1: Language Preference Assessment

**User Story:** As a student, I want to complete a language assessment, so that the system can adapt content to my comprehension level.

#### Acceptance Criteria

1. WHEN a student starts the assessment, THE System SHALL present exactly 5 assessment questions
2. WHEN displaying an assessment question, THE System SHALL provide exactly 4 answer options with varying complexity levels
3. THE System SHALL ensure all 4 options for each question are factually correct
4. WHEN a student selects an option, THE System SHALL record the complexity level associated with that option
5. WHEN all 5 questions are answered, THE System SHALL calculate the median of the 5 selected complexity levels
6. THE System SHALL assign the calculated median value as the Student's Language_Level
7. THE System SHALL persist the assigned Language_Level for future Focus_Sessions
8. THE System SHALL ensure Language_Level values are integers between 1 and 4 inclusive

### Requirement 2: Focus Mode Learning Engine

**User Story:** As a student, I want to learn topics through structured micro-learning steps, so that I can understand content without cognitive overload.

#### Acceptance Criteria

1. WHEN a student initiates a Focus_Session, THE System SHALL accept three inputs: subject name, topic name, and Language_Level
2. THE System SHALL validate that the subject is one of: Physics, Chemistry, Biology, or Social Studies
3. WHEN generating learning content, THE System SHALL create between 3 and 5 Learning_Steps
4. THE System SHALL ensure each Learning_Step contains a title field and a text field
5. THE System SHALL ensure each Learning_Step explanation contains between 40 and 60 words
6. THE System SHALL adapt explanation complexity to match the Student's Language_Level
7. THE System SHALL return learning content as structured JSON with fields: subject, topic, level, and steps array
8. THE System SHALL generate responses within 2 seconds per Learning_Step

### Requirement 3: Interactive Session Commands

**User Story:** As a student, I want to control my learning pace and complexity, so that I can learn at my own speed and comprehension level.

#### Acceptance Criteria

1. WHEN a student issues a "next" command during a Focus_Session, THE System SHALL advance to the next Learning_Step
2. WHEN a student issues a "simplify" command, THE System SHALL decrease the Language_Level by 1
3. IF the current Language_Level is 1, WHEN a student issues a "simplify" command, THEN THE System SHALL maintain Language_Level at 1
4. WHEN the Language_Level changes, THE System SHALL regenerate the current Learning_Step with the new complexity level
5. WHEN a student issues an "exit" command, THE System SHALL terminate the Focus_Session
6. WHEN a student reaches the final Learning_Step and issues "next", THE System SHALL complete the Focus_Session

### Requirement 4: ADHD-Optimized Content Generation

**User Story:** As a student with ADHD, I want content presented in cognitively accessible formats, so that I can maintain focus and comprehend material effectively.

#### Acceptance Criteria

1. WHEN generating explanations, THE System SHALL apply lexical simplification appropriate to the Language_Level
2. WHEN structuring content, THE System SHALL organize information into concept-based chunks
3. THE System SHALL limit each Learning_Step to a single core concept
4. WHEN formatting text, THE System SHALL use visual scaffolding techniques including bullet points and lists
5. THE System SHALL avoid dense paragraphs exceeding 60 words in Learning_Steps
6. WHEN Language_Level is 1 or 2, THE System SHALL prioritize concrete examples over abstract concepts
7. WHEN Language_Level is 3 or 4, THE System SHALL include more sophisticated vocabulary while maintaining clarity

### Requirement 5: Content Retrieval and Grounding

**User Story:** As an educator, I want the system to ground content in approved textbook materials, so that students receive curriculum-aligned information.

#### Acceptance Criteria

1. WHERE RAG integration is enabled, THE System SHALL retrieve relevant textbook content using embedding-based search
2. WHERE RAG integration is enabled, WHEN generating Learning_Steps, THE System SHALL provide retrieved textbook excerpts as context to the LLM
3. THE System SHALL support operation without RAG integration using the LLM's base knowledge
4. WHERE RAG integration is enabled, THE System SHALL match retrieved content to the specified subject and topic
5. THE System SHALL NOT require model fine-tuning for RAG functionality

### Requirement 6: API Response Structure

**User Story:** As a frontend developer, I want consistent JSON responses, so that I can reliably render learning content in the UI.

#### Acceptance Criteria

1. THE System SHALL return all Focus_Session content as valid JSON
2. THE System SHALL include a "subject" field containing the subject name
3. THE System SHALL include a "topic" field containing the topic name
4. THE System SHALL include a "level" field containing the current Language_Level as an integer
5. THE System SHALL include a "steps" field containing an array of Learning_Step objects
6. WHEN returning a Learning_Step object, THE System SHALL include both "title" and "text" fields
7. THE System SHALL ensure all JSON responses are parseable by standard JSON parsers

### Requirement 7: Performance and Latency

**User Story:** As a student with ADHD, I want immediate responses to my interactions, so that I can maintain engagement without frustration.

#### Acceptance Criteria

1. THE System SHALL generate each Learning_Step within 2 seconds
2. WHEN a student issues a command, THE System SHALL respond within 2 seconds
3. THE System SHALL use local model inference via Ollama with phi3:mini model
4. THE System SHALL maintain response times under 2 seconds for 95% of requests
5. IF response generation exceeds 2 seconds, THEN THE System SHALL return a partial response or timeout indicator

### Requirement 8: Subject and Topic Coverage

**User Story:** As a student, I want to learn content across multiple subjects, so that I can use one system for all my core academic needs.

#### Acceptance Criteria

1. THE System SHALL support Physics as a subject domain
2. THE System SHALL support Chemistry as a subject domain
3. THE System SHALL support Biology as a subject domain
4. THE System SHALL support Social Studies as a subject domain
5. WHEN a student requests an unsupported subject, THE System SHALL return an error message indicating valid subject options
6. THE System SHALL accept any topic name within supported subjects
7. THE System SHALL generate appropriate content for topics within Grades 5-10 curriculum scope

### Requirement 9: Modular Architecture

**User Story:** As a system architect, I want clear separation between assessment, content generation, and API layers, so that the system is maintainable and extensible.

#### Acceptance Criteria

1. THE System SHALL implement assessment logic independently from content generation logic
2. THE System SHALL implement content generation logic independently from API routing logic
3. THE System SHALL use FastAPI framework for API layer implementation
4. THE System SHALL implement Python-based backend services
5. WHEN one module is modified, THE System SHALL allow other modules to function without changes

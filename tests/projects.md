# AI Application Modernizer - Project Requirements

## Project Overview

An LLM-powered application that automatically analyzes GitHub repositories and generates modernized code, architecture documentation, and clear functional explanations. The system uses local AI inference (Qwen2.5-coder:7b) to provide zero-cost, privacy-friendly code modernization.

## Project Objectives

1. **Automated Code Analysis**: Analyze legacy codebases and understand their structure, patterns, and technologies
2. **Tech Stack Migration**: Generate migration strategies from one tech stack to another (e.g., Java → Python, jQuery → React)
3. **Code Generation**: Produce sample modernized code files with best practices and modern patterns
4. **Documentation Generation**: Create comprehensive migration guides and architectural explanations
5. **Zero API Costs**: Run entirely locally using Ollama and Qwen2.5-coder:7b
6. **Privacy-Friendly**: Code never leaves the user's system
7. **Offline Capability**: Works without internet after initial setup

## User Requirements

### Functional Requirements

**FR-1: Repository Input**
- Users can input a GitHub repository URL (public repos)
- System validates URL format and repository accessibility
- Support for large repositories with graceful degradation

**FR-2: Tech Stack Selection**
- Users select current/target technology stacks from predefined options
- Support tech stacks include:
  - Java (Spring Boot, Jakarta EE)
  - Python (Django, FastAPI, Flask)
  - JavaScript/TypeScript (React, Vue, Angular)
  - Frontend frameworks (jQuery, vanilla JS → modern frameworks)

**FR-3: Automated Analysis**
- Repository structure analysis and file inventory
- Current tech stack detection with confidence scoring
- Architecture pattern identification (MVC, microservices, monolith, etc.)
- Dependency mapping and analysis

**FR-4: Migration Planning**
- Generate step-by-step migration strategy
- Risk assessment and breaking change identification
- Effort estimation (relative sizing)
- Best practices recommendations for target stack

**FR-5: Code Generation**
- Transform 10-20 representative files to target tech stack
- Preserve business logic and functionality
- Apply modern design patterns
- Include inline explanatory comments

**FR-6: Documentation Generation**
- Create comprehensive migration guide
- File-by-file change explanations
- Architecture comparison (before/after)
- Setup and deployment instructions for modernized code

**FR-7: Report Delivery**
- Interactive Streamlit UI for viewing results
- Downloadable Markdown report with syntax highlighting
- ZIP archive containing all generated code files
- Side-by-side code diff visualization

**FR-8: Caching**
- Cache analysis results to avoid re-processing identical repos
- Persistent cache across sessions
- Configurable cache TTL

### Non-Functional Requirements

**NFR-1: Performance**
- Analysis of typical repository < 10 minutes
- Real-time progress feedback via Streamlit UI
- Streaming LLM responses for interactive experience
- Graceful handling of large files via chunking

**NFR-2: Reliability**
- Graceful error handling for parsing failures
- Fallback to heuristics if LLM inference fails
- Input validation and sanitization
- Comprehensive logging for debugging

**NFR-3: Scalability**
- Support repositories up to 100MB in size
- Analyze up to 50 files per session
- Configurable limits based on available memory
- Support for parallel file processing

**NFR-4: Privacy & Security**
- No external API calls for code analysis
- No storage of analyzed code in cloud services
- Local file access only
- Configurable data retention

**NFR-5: Usability**
- Single-page Streamlit application
- Clear progress indicators
- Helpful error messages with recovery suggestions
- Mobile-friendly report viewing

**NFR-6: Maintainability**
- Modular architecture with clear separation of concerns
- Comprehensive code documentation
- Type hints throughout codebase
- Unit and integration test coverage

## Architecture Overview

### System Architecture

```
┌─────────────────────────────────────────┐
│     User (Streamlit Web Interface)      │
└────────────────────┬────────────────────┘
                     │
         ┌───────────┴───────────┐
         ▼                       ▼
    [GitHub Input]         [Tech Stack]
         │                       │
         └───────────┬───────────┘
                     │
         ┌───────────▼───────────┐
         │   Validation Layer    │
         └───────────┬───────────┘
                     │
         ┌───────────▼───────────────────────┐
         │   GitHub Service                  │
         │  • Clone repository               │
         │  • Handle authentication          │
         │  • Fetch file contents            │
         └───────────┬───────────────────────┘
                     │
         ┌───────────▼───────────────────────┐
         │   Analysis Chain                  │
         │  • Repository Analyzer Agent      │
         │  • Tech Stack Detector Agent      │
         └───────────┬───────────────────────┘
                     │
         ┌───────────▼───────────────────────┐
         │   Migration Chain                 │
         │  • Migration Planner Agent        │
         │  • Code Generator Agent           │
         └───────────┬───────────────────────┘
                     │
         ┌───────────▼───────────────────────┐
         │   Report Generation Chain         │
         │  • Documentation Generator Agent  │
         │  • Report Assembly Service        │
         └───────────┬───────────────────────┘
                     │
         ┌───────────▼───────────────────────┐
         │   Output Layer                    │
         │  • Streamlit Display              │
         │  • Markdown Report                │
         │  • ZIP Archive                    │
         └───────────────────────────────────┘
```

### Component Breakdown

**1. GitHub Service**
- Clone repositories to local storage
- Fetch and read file contents
- Handle authentication for private repos (future)
- Calculate repo metrics (LOC, file count, language distribution)

**2. Code Parsing Infrastructure**
- Universal parsing via tree-sitter (Java, Python, JavaScript/TypeScript)
- Language-specific AST analysis (javalang, esprima)
- Graceful degradation to regex-based heuristics
- Caching of parse results

**3. LangChain Agents (5 Specialized Agents)**

**Agent 1: Repository Analyzer**
- Input: GitHub URL, authentication
- Tools: GitHub clone, file system scan
- Output: Repository structure map, file inventory, entry points
- Task: Identify architecture patterns and entry points

**Agent 2: Tech Stack Detector**
- Input: Repository structure, code samples
- Tools: Code parser, framework detector
- Output: Tech stack object (languages, frameworks, versions)
- Task: Infer implicit dependencies, assess maturity

**Agent 3: Migration Planner**
- Input: Current stack, target stack, codebase size
- Tools: Best practices search, compatibility checker
- Output: Migration plan with phases, risks, roadmap
- Task: Strategic planning and risk assessment

**Agent 4: Code Generator**
- Input: Migration plan, source code files
- Tools: AST transformer, template engine, file writer
- Output: Modernized code files with inline comments
- Task: Context-aware code transformation

**Agent 5: Documentation Generator**
- Input: Original code, generated code, migration plan
- Tools: Diff generator, markdown formatter
- Output: Migration guide and explanations
- Task: Explain changes and provide actionable guidance

**4. LangChain Chains (Sequential Orchestration)**

- **Analysis Chain**: Repo Analyzer → Tech Stack Detector
- **Migration Chain**: Migration Planner → Code Generator
- **Report Chain**: Aggregation → Documentation Generator → Formatting

**5. Services Layer**
- **LLM Service**: Ollama endpoint management, token counting, retry logic
- **GitHub Service**: Repository operations, authentication, file access
- **Code Analysis Service**: Orchestrate parsing and analysis
- **Report Service**: Assemble deliverables (Markdown, HTML, ZIP)

## Technology Stack

### LLM & Agents
- **LLM**: Qwen2.5-coder:7b (local via Ollama)
- **Agent Framework**: LangChain
- **LLM Interface**: Ollama Python client

### Web Framework
- **Frontend**: Streamlit 1.29.0
- **Backend**: Streamlit (no separate backend)

### Code Analysis
- **Universal Parser**: tree-sitter
- **Java AST**: javalang
- **JavaScript AST**: esprima
- **Language Detection**: heuristics + file extension matching

### GitHub Integration
- **GitHub API**: PyGithub
- **Git Operations**: GitPython

### Data & Configuration
- **Data Validation**: Pydantic 2.5.3
- **Configuration**: Pydantic Settings
- **Environment**: python-dotenv

### Utilities
- **Caching**: diskcache
- **Reporting**: markdown, jinja2, pygments
- **Diff Generation**: diff-match-patch
- **Logging**: Python logging (structured)
- **Testing**: pytest

## Implementation Phases

### Phase 1: Foundation (Days 1-2)
- Project structure and directory setup
- Configuration management (Pydantic Settings)
- Pydantic data models for type safety
- Logging infrastructure
- Dependencies installation

### Phase 2: Services & Tools (Days 3-4)
- LLM service with Ollama integration
- GitHub service with repo cloning
- Code parsing infrastructure (tree-sitter + language-specific)
- LangChain tools for GitHub and code parsing
- Caching system implementation

### Phase 3: Agents (Days 5-9)
- Base agent with ReAct pattern
- Repository Analyzer agent
- Tech Stack Detector agent
- Migration Planner agent
- Code Generator agent
- Documentation Generator agent
- Prompt template creation

### Phase 4: Chains (Days 10-12)
- Analysis chain orchestration
- Migration chain orchestration
- Report generation chain
- State management between agents
- Progress tracking

### Phase 5: Report Generation (Days 13-14)
- Report service implementation
- Markdown report generation
- Syntax highlighting
- Diff visualization
- ZIP archive creation

### Phase 6: Streamlit UI (Days 15-18)
- Main application entry point
- Repository input component
- Tech stack selector component
- Progress tracker component
- Report viewer component
- Session state management

### Phase 7: Testing & Polish (Days 19-23)
- Test fixture creation
- Unit tests for parsers, services, agents
- End-to-end testing with real repos
- Prompt optimization
- Error handling refinement
- Documentation

### Phase 8: Deployment (Days 24-25)
- Dockerfile creation
- Docker Compose setup
- Deployment documentation
- Production configuration

## Key Features

### MVP Features ✅
- GitHub public repository analysis
- Support for Java, Python, JavaScript/TypeScript
- Automated tech stack detection
- Migration planning and recommendations
- Code sample generation (10-20 files)
- Comprehensive documentation
- Markdown report output
- Single-page Streamlit UI
- Local result caching
- Token counting and cost estimation
- Zero API costs (local LLM)
- Offline operation

### Future Features ❌
- Private repository support (OAuth/SSH)
- Extended language support (C#, Ruby, Go, etc.)
- Full codebase transformation
- Automated test generation
- CI/CD pipeline integration
- Multi-user authentication
- Database result persistence
- Real-time collaborative features
- Custom migration rules UI

## Success Criteria

The MVP is considered successful when:

1. ✅ User can input GitHub URL and select target tech stack
2. ✅ System analyzes repo and detects current tech stack
3. ✅ System generates migration plan with recommendations
4. ✅ System produces 10-20 modernized code file samples
5. ✅ System creates comprehensive migration documentation
6. ✅ User can download Markdown report + ZIP of code
7. ✅ Total analysis time < 10 minutes for typical repo
8. ✅ Zero API costs (all local inference)
9. ✅ Works offline (after Ollama setup)

## Dependencies

### Core Framework
- streamlit==1.29.0
- langchain==0.1.0
- langchain-community==0.0.13

### Local LLM
- ollama==0.1.6
- langchain-ollama==0.0.1

### GitHub Integration
- PyGithub==2.1.1
- gitpython==3.1.40

### Code Parsing
- tree-sitter==0.20.4
- tree-sitter-languages==1.9.1
- javalang==0.13.0
- esprima==4.0.1

### Data & Config
- pydantic==2.5.3
- pydantic-settings==2.1.0
- python-dotenv==1.0.0

### Reporting & Output
- markdown==3.5.1
- jinja2==3.1.2
- pygments==2.17.2
- diff-match-patch==20230430

### Utilities
- diskcache==5.6.3

### Testing
- pytest==7.4.3
- pytest-asyncio==0.21.1

## Prerequisites

### System Requirements
- Python 3.10+
- 4GB RAM minimum (8GB recommended)
- 2GB free disk space
- macOS, Linux, or Windows with WSL2

### Ollama Setup
```bash
# Install Ollama
brew install ollama  # macOS
# or visit https://ollama.ai for other platforms

# Pull Qwen2.5-coder:7b
ollama pull qwen2.5-coder:7b

# Verify installation
ollama list

# Start Ollama service (before running app)
ollama serve
```

## Configuration

### Environment Variables (.env)
```bash
# Local LLM Configuration
OLLAMA_BASE_URL=http://localhost:11434
LLM_PROVIDER=ollama
MODEL_NAME=qwen2.5-coder:7b
OLLAMA_NUM_PREDICT=2048
OLLAMA_TEMPERATURE=0.1

# Application Settings
DATA_DIR=./data
LOG_LEVEL=INFO
MAX_FILES_TO_ANALYZE=50
MAX_FILE_SIZE_MB=5
CONTEXT_WINDOW_TOKENS=32000
CHUNK_OVERLAP_TOKENS=500

# Performance
ENABLE_CACHING=true
CACHE_TTL_HOURS=24
```

## Constraints & Limitations

### Technical Constraints
- **Context Window**: Qwen2.5-coder has 32k token limit (vs 200k+ for cloud LLMs)
  - Solution: File chunking, summarization, aggressive caching
- **Local Inference Speed**: Slower than cloud APIs
  - Solution: Batch processing, parallel analysis, progress feedback
- **Language Support**: Limited to Java, Python, JavaScript/TypeScript (MVP)
  - Solution: Extensible parser framework for future languages

### Functional Constraints
- **Public Repos Only**: MVP targets public GitHub repositories
  - Future: Private repo support via SSH/OAuth
- **Representative Sampling**: Analyzes 10-20 files, not entire codebase
  - Rationale: Speed, cost, practical utility (patterns are representative)
- **Code Quality**: Generated code is "assisted migration" requiring human review
  - Rationale: LLMs can hallucinate; human validation is critical

## Project Timeline

| Phase | Duration | Status |
|-------|----------|--------|
| 1. Foundation | 2 days | Ready to start |
| 2. Services & Tools | 2 days | Pending |
| 3. Agents | 5 days | Pending |
| 4. Chains | 3 days | Pending |
| 5. Reporting | 2 days | Pending |
| 6. Streamlit UI | 4 days | Pending |
| 7. Testing & Polish | 5 days | Pending |
| 8. Deployment | 2 days | Pending |
| **Total** | **25 days** | **MVP Ready** |

## Risk Management

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|-----------|
| Code generation quality issues | Medium | High | Few-shot prompting, syntax validation, human review positioning |
| Large file context window overflow | Medium | Medium | File chunking, smart sampling, summarization |
| Ollama/Qwen2.5 not available locally | Low | High | Clear documentation, automated checks, fallback to cloud (future) |
| GitHub API rate limits | Low | Low | GitPython doesn't hit rate limits for cloning |
| Poor tech stack detection | Medium | Medium | Multiple detection strategies, confidence scoring, user override |

## Success Metrics

1. **Functional Completeness**: All 8 user requirements met ✓
2. **Performance**: Analysis < 10 minutes for typical repo
3. **Accuracy**: Tech stack detection > 85% accuracy
4. **User Satisfaction**: Clear, actionable output
5. **Reliability**: < 1% failure rate on valid inputs
6. **Privacy**: Zero external API calls for code analysis ✓
7. **Cost**: Zero API costs (100% local) ✓

## Getting Started

See `README.md` for installation and usage instructions.

For detailed implementation plan, see `.claude/plans/wobbly-orbiting-feigenbaum.md`.

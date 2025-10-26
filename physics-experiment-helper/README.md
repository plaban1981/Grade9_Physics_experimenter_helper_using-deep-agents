# Physics Experiment Helper 🔬

**AI-Powered Science Project Assistant for Grade 9 Students**

A comprehensive physics experiment guide generator built with **Deep Agents** architecture using the `deepagents` library, FastAPI, and a beautiful Daisy UI interface. This application helps Grade 9 students create complete, scientifically rigorous physics experiments with full documentation, methodology, data templates, and report formats.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.10+-green.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-teal.svg)

---

## Features

### 🎯 Complete Experiment Packages

Each generated experiment includes **7 comprehensive files**:

1. **Experiment Synopsis** - Overview, objectives, and timeline
2. **Theory & Background** - Physics concepts explained for Grade 9 level
3. **Methodology** - Step-by-step procedures, materials, and safety guidelines
4. **Data Templates** - Ready-to-use tables, graphs, and measurement sheets
5. **Analysis & Conclusion** - Guidance for interpreting results
6. **Report Template** - Complete science report structure
7. **References & Resources** - Curated learning materials and citations

### 🖼️ Image Integration

- **AI Image Generation** - Generate custom images using Replicate's nano-banana model
- **Multiple Styles** - Scientific, educational, and diagram styles for different needs
- **Automatic Image Search** - Tavily API retrieves relevant physics experiment images
- **Visual Learning** - Images displayed directly in the UI for better understanding
- **Image Gallery** - Browse experiment-related diagrams, setups, and illustrations
- **Export with Images** - All downloads include both generated and found images

### 🤖 Deep Agents Architecture

Built using the proven Deep Agents pattern:
- **TODO Management** - Systematic task planning and progress tracking
- **File System** - Context offloading through virtual files
- **Sub-Agents** - Specialized research and critique agents
- **Web Search** - Real-time physics education resource gathering

### ✨ Modern UI with Daisy UI

- Beautiful, light-themed interface
- Real-time progress tracking
- File preview with Markdown rendering
- Image gallery with thumbnails
- WebSocket streaming support
- Mobile-responsive design
- Experiment examples library

### 📥 Multiple Export Options

- **ZIP Archive** - Download all experiment files and image links in one package
- **HTML Report** - Complete experiment as a single, beautifully formatted HTML document with embedded images
- **Individual Files** - Download specific markdown files as needed
- **Print-Ready** - HTML exports optimized for printing or PDF conversion

### 🔒 Safety-First Approach

- Age-appropriate experiments for 14-15 year olds
- Clear safety warnings and precautions
- Adult supervision notes where needed
- Feasible with household/school materials
- Cost-effective (typically under $50)

---

## Architecture

```
physics-experiment-helper/
├── src/
│   ├── agent/                    # Deep Agents implementation
│   │   ├── __init__.py
│   │   ├── prompts.py            # System prompts for main & sub-agents
│   │   └── physics_agent.py      # Agent creation using deepagents
│   └── api/                      # FastAPI backend
│       ├── __init__.py
│       └── main.py               # REST + WebSocket endpoints
├── static/
│   └── index.html                # Daisy UI interface
├── requirements.txt              # Python dependencies
├── pyproject.toml                # Project configuration
├── .env.example                  # Environment template
├── .gitignore
├── run.py                        # Server launcher
└── README.md
```

### Key Components

**Deep Agents Integration:**
- Uses `deepagents` library from LangChain
- Main agent for experiment orchestration
- Research sub-agent for physics concepts and procedures
- Critique sub-agent for quality assurance

**Web Search Tool:**
- Tavily API integration for finding educational resources
- Physics concept explanations
- Experiment procedures and safety guidelines
- Real-world applications and examples

**FastAPI Backend:**
- REST API for synchronous generation
- WebSocket for real-time streaming updates
- Session management
- File download endpoints
- Example experiments library

---

## Installation

### Prerequisites

- Python 3.10 or higher
- OpenAI API key ([Get one here](https://platform.openai.com/api-keys))
- Replicate API token ([Get one here](https://replicate.com/account/api-tokens)) - for image generation
- Tavily API key ([Get one here](https://www.tavily.com/)) - optional, for enhanced web search

### Setup

1. **Navigate to the project directory**
   ```bash
   cd physics-experiment-helper
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv

   # On Windows
   venv\Scripts\activate

   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   ```bash
   # Copy the example file
   cp .env.example .env

   # Edit .env and add your API keys
   # OPENAI_API_KEY=your_key_here
   # REPLICATE_API_TOKEN=your_token_here
   # TAVILY_API_KEY=your_key_here
   ```

---

## Usage

### Starting the Server

**Option 1: Using the run script (Recommended)**
```bash
python run.py
```

**Option 2: Using uvicorn directly**
```bash
cd src
uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
```

The application will be available at:
- **Web Interface:** http://localhost:8000
- **API Documentation:** http://localhost:8000/docs
- **Health Check:** http://localhost:8000/health

### Using the Web Interface

1. **Open your browser** to http://localhost:8000

2. **Describe your experiment:**
   ```
   I want to investigate how the angle of a ramp affects
   the distance a ball travels. I'm interested in studying
   projectile motion and energy transfer.
   ```

3. **Choose connection type:**
   - **Standard:** Single request/response (good for shorter experiments)
   - **Real-time Updates:** WebSocket streaming (recommended for complex experiments)

4. **Generate:** Click "Generate Experiment Guide"

5. **Generate Images:** Use the image generation section to create custom visuals

6. **View & Download:** Browse generated files, preview them, and download

### Using the REST API

**Python Example:**
```python
import requests

response = requests.post('http://localhost:8000/api/generate-experiment', json={
    'experiment_description': 'Study the relationship between pendulum length and period',
    'student_name': 'Alex',
    'grade_level': 'Grade 9',
    'model_name': 'gpt-4o'
})

result = response.json()
print(f"Session ID: {result['session_id']}")
print(f"Files generated: {len(result['files'])}")

for filename in result['files']:
    print(f"  - {filename}")
```

**WebSocket Example:**
```python
import asyncio
import websockets
import json

async def generate_experiment():
    async with websockets.connect('ws://localhost:8000/ws/generate-experiment') as ws:
        # Send request
        await ws.send(json.dumps({
            'experiment_description': 'Friction experiment with different surfaces',
            'model_name': 'gpt-4o'
        }))

        # Receive updates
        async for message in ws:
            data = json.loads(message)
            print(f"[{data['type']}] {data.get('message', '')}")

            if data['type'] == 'completion':
                print(f"\nGenerated {len(data['files'])} files!")
                break

asyncio.run(generate_experiment())
```

---

## Example Experiments

The application includes built-in examples across various physics categories:

### Mechanics
- **Simple Pendulum Period** - Investigate length vs. oscillation period
- **Projectile Motion** - Study trajectory at different launch angles
- **Friction on Different Surfaces** - Compare friction coefficients

### Electricity
- **Ohm's Law Verification** - Relationship between V, I, and R
- **Series vs. Parallel Circuits** - Compare circuit configurations

### Thermal Physics
- **Heat Transfer and Insulation** - Test insulating materials
- **Thermal Expansion** - Measure material expansion with heat

### Waves & Optics
- **Sound Frequency and Pitch** - Frequency vs. perceived pitch
- **Mirror Reflection Angles** - Verify law of reflection
- **Lens Focal Length** - Determine focal lengths of lenses

Click "See Examples" in the web interface to browse and use these as starting points!

---

## API Endpoints

### REST Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Web interface |
| `/health` | GET | Health check |
| `/api/generate-experiment` | POST | Generate experiment (sync) |
| `/api/experiment-examples` | GET | Get example experiments |
| `/api/sessions/{id}` | GET | Retrieve session data |
| `/api/sessions/{id}/files` | GET | Get all session files |
| `/api/sessions/{id}/files/{filename}` | GET | Get specific file |
| `/api/sessions/{id}/images` | GET | Get all session images |
| `/api/sessions/{id}/images/{index}` | GET | Get specific image file |
| `/api/sessions/{id}/download/{filename}` | GET | Download single file |
| `/api/sessions/{id}/download-zip` | GET | Download all files as ZIP |
| `/api/sessions/{id}/download-html` | GET | Download HTML report |
| `/api/generate-image` | POST | Generate single image |
| `/api/generate-multiple-images` | POST | Generate multiple images |

### WebSocket

- `/ws/generate-experiment` - Real-time experiment generation with streaming updates

---

## Generated File Structure

### 1. experiment_synopsis.md
```markdown
# [Experiment Title]

## Objective
Brief description of what the experiment investigates

## Hypothesis
Expected outcome based on physics principles

## Key Concepts
- Concept 1
- Concept 2

## Timeline
Week 1: Setup and initial measurements
Week 2: Data collection
...
```

### 2. theory_and_background.md
- Physics principles explained for Grade 9 level
- Key equations and relationships
- Real-world applications
- Historical context
- Visual diagram descriptions

### 3. methodology.md
- Complete materials list with specifications
- Detailed safety precautions
- Step-by-step setup instructions
- Measurement procedures
- Expected observations
- Troubleshooting guide

### 4. data_template.md
- Data tables with proper units
- Graph templates with axes labels
- Observation checklists
- Calculation worksheets
- Error analysis templates

### 5. analysis_and_conclusion.md
- Data analysis procedures
- Expected patterns and trends
- Calculation examples
- Graph interpretation guide
- Error source identification
- Conclusion framework

### 6. report_template.md
- Title page format
- Abstract template
- Introduction outline
- Materials & Methods section
- Results section structure
- Discussion framework
- Conclusion guidelines
- APA-style references
- Appendices

### 7. references_and_resources.md
- Reference materials
- Educational videos and websites
- Similar experiments
- Advanced reading
- Safety data sheets
- Citation examples

---

## Configuration

### Environment Variables

```bash
# Required
OPENAI_API_KEY=sk-...              # OpenAI API for GPT-4o
REPLICATE_API_TOKEN=r8_...         # Replicate for image generation

# Optional
TAVILY_API_KEY=tvly-...            # Tavily for web search
LANGSMITH_API_KEY=lsv2_...         # LangSmith tracing
LANGSMITH_TRACING=true             # Enable tracing
LANGSMITH_PROJECT=physics-helper   # Project name

# Alternative Models (Optional)
ANTHROPIC_API_KEY=sk-ant-...       # For Claude models
GROQ_API_KEY=gsk_...               # For Groq models
```

### Model Selection

Default model: **GPT-4o** (recommended for educational content)

To use different models, modify in `src/agent/physics_agent.py`:
```python
agent = create_physics_experiment_agent(model_name="gpt-4o")
```

Supported models:
- `gpt-4o` (default, best for this use case)
- `gpt-4-turbo`
- `claude-3-5-sonnet-20241022`
- `claude-3-opus-20240229`

---

## How It Works

### Deep Agents Pattern

The application uses the Deep Agents architecture:

1. **System Prompt** - Detailed instructions for Grade 9 experiment generation
2. **Planning Tool** - TODO list for systematic experiment creation
3. **File System** - Virtual files for storing research and drafts
4. **Sub-Agents** - Specialized agents for research and quality control

### Workflow

```
User Request
    ↓
Main Agent (Experiment Orchestrator)
    ↓
Creates TODO Plan
    ↓
Research Sub-Agent ← Web Search (Tavily)
    ↓
Draft Experiment Files
    ↓
Critique Sub-Agent ← Quality Review
    ↓
Refine & Finalize
    ↓
7 Complete Files → User
```

### Deep Agent Benefits

- **Long-Horizon Task Completion** - Handles complex, multi-step experiment creation
- **Context Management** - Offloads research to files, preventing context overflow
- **Systematic Planning** - TODO list keeps agent on track
- **Quality Assurance** - Critique agent ensures safety and educational value
- **Modularity** - Research agent can be reused for different domains

---
---
<img width="1902" height="796" alt="image" src="https://github.com/user-attachments/assets/9e308eec-c6cb-4c60-a659-6d99174fd999" />



<img width="1756" height="852" alt="image" src="https://github.com/user-attachments/assets/f64e2def-abeb-4fe2-be82-11ba691ce2f2" />


<img width="1585" height="857" alt="image" src="https://github.com/user-attachments/assets/1d8d0fbd-4c21-4a6a-bb4f-8a4c09985a43" />





---
## Safety & Educational Standards

### Safety Features
- All experiments flagged for hazards
- Adult supervision requirements noted
- Emergency procedures included
- Proper disposal methods specified
- Age-appropriate material selection

### Educational Alignment
- Aligned with Grade 9 physics curriculum
- Clear learning objectives
- Scaffolded complexity
- Scientific method demonstration
- Critical thinking encouraged

### Quality Standards
- Scientifically accurate
- Practically feasible
- Cost-effective (under $50)
- Completable in 2-4 weeks
- Accessible materials

---

## Troubleshooting

### Common Issues

**"OPENAI_API_KEY not found"**
- Ensure `.env` file exists with valid key
- Check that python-dotenv is installed

**"TAVILY_API_KEY not found"**
- Sign up at tavily.com for free API key
- Add to `.env` file

**"Module not found" errors**
- Verify virtual environment is activated
- Reinstall: `pip install -r requirements.txt`

**Generation takes too long**
- Complex experiments may take 3-5 minutes
- Use WebSocket connection for progress updates
- Simplify experiment description for faster results

**Files not appearing**
- Check browser console for JavaScript errors
- Verify backend is running on port 8000
- Try clearing browser cache

---

## Development

### Running in Development Mode

```bash
# Enable auto-reload
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

### Project Structure

```
src/
├── agent/               # Agent implementation
│   ├── prompts.py      # All prompts (main + sub-agents)
│   └── physics_agent.py # Agent creation & tools
└── api/
    └── main.py         # FastAPI app with all endpoints
```

### Adding New Experiment Types

1. Update system prompt in `src/agent/prompts.py`
2. Add example to `/api/experiment-examples` endpoint
3. Test with specific experiment description

### Customizing for Different Grades

Modify the prompts to adjust:
- Complexity level
- Mathematical rigor
- Material requirements
- Safety considerations

---

## Future Enhancements

Planned features:
- [ ] PDF export of complete experiment packages
- [ ] LaTeX support for scientific reports
- [ ] Video tutorial integration
- [ ] Collaborative editing for group projects
- [ ] Teacher dashboard for class management
- [ ] Integration with learning management systems
- [ ] Multi-language support
- [ ] Mobile app version

---

## Contributing

Contributions welcome! This is an educational project to help students learn physics through hands-on experiments.

Ideas for contributions:
- Add more experiment examples
- Improve safety guidelines
- Enhance educational explanations
- Add support for other science subjects (chemistry, biology)
- Translate to other languages

---

## License

MIT License - free to use for educational purposes.

---

## Acknowledgments

Built with inspiration from:
- [deepagents](https://github.com/langchain-ai/deepagents) by LangChain
- Deep Agents pattern from Harrison Chase
- [deep-agents-walkthrough](https://github.com/ALucek/deep-agents-walkthrough)
- Daisy UI for beautiful components
- FastAPI for modern web framework
- Tavily for educational web search

Special thanks to physics teachers and students who inspired this project!

---

## Support

For issues or questions:
- 📧 Open an issue on GitHub
- 📖 Check the documentation at `/docs`
- 🔍 Review example experiments
- 💬 Ask in discussions

---

**Happy Experimenting! 🔬✨**

*Remember: Science is about curiosity, experimentation, and learning. Every experiment teaches us something, even when results surprise us!*

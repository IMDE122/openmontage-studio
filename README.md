# OpenMontage Studio

Professional AI video and image generation studio powered by OpenMontage, with FreeLLMAPI integration for AI-assisted content creation.

## Features

- **Video Generation**: Text-to-video and image-to-video with multiple providers (Seedance 2.0, VEO, Kling, Sora, Runway, LTX, Gemini Omni)
- **Image Generation**: Text-to-image with FLUX, GPT Image, Recraft, Ideogram
- **Pipeline System**: Structured multi-stage video production (Animated Explainer, Cinematic, Avatar Spokesperson, etc.)
- **AI-Assisted Creation**: FreeLLMAPI integration for script generation, prompt enhancement, and code generation
- **Real-time Progress**: WebSocket-based live updates during generation
- **Composition Runtimes**: Remotion (React), HyperFrames (HTML/GSAP), FFmpeg
- **Theme Support**: Light/dark mode with OKLCH color tokens
- **Responsive Design**: Mobile-first, works on all devices

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+ (for frontend dev)
- Docker (optional, for containerized deployment)
- OpenMontage installed (for full pipeline support)
- FreeLLMAPI account (for AI-assisted features)

### Environment Setup

```bash
# Clone the repository
git clone https://github.com/IMDE122/openmontage-studio.git
cd openmontage-studio

# Copy environment template
cp .env.example .env

# Edit .env with your API keys
# Required for video/image generation:
# FAL_KEY=your_fal_ai_key
# HEYGEN_API_KEY=your_heygen_key
# GEMINI_API_KEY=your_gemini_key
# OPENAI_API_KEY=your_openai_key

# Required for AI-assisted features (FreeLLMAPI):
# FREE_LLM_API_KEY=your_freellmapi_key
# FREE_LLM_API_BASE_URL=https://api.freellmapi.com/v1
```

### Option 1: Docker (Recommended)

```bash
# Development
docker-compose up -d

# Production
docker-compose --profile production up -d --build

# With OpenMontage full pipeline support
docker-compose --profile full up -d
```

Access:
- Frontend: http://localhost:3000 (dev) or http://localhost (prod)
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### Option 2: Manual Setup

#### Backend
```bash
cd videogen-app
pip install -r requirements.txt
python backend.py
```

#### Frontend
```bash
cd videogen-app
npm install
npm run dev
```

## ECC Integration

OpenMontage Studio includes [ECC](https://github.com/affaan-m/ECC) - an agent harness operating system that provides:
- **72 specialized agents** for planning, review, build repair, security, architecture
- **328 skills** for TDD, research, security, docs, frontend, data, ML, operations
- **99 commands** for TDD, planning, E2E tests, code review, build fix, learning
- **Hooks & memory** for session persistence, continuous learning
- **AgentShield** for security scanning

ECC is installed as a git submodule at `.ecc/`:

```bash
# Initialize ECC (already done in repo)
git submodule update --init --recursive

# Or use npx for standalone install
npx ecc-universal@2.2.3 setup --mode claude-plugin --scope project --yes
```

ECC provides agents like `/tdd`, `/plan`, `/code-review`, `/build-fix`, `/learn`, `/skill-create` that enhance the development workflow.

## FreeLLMAPI Integration

### Supported Models via FreeLLMAPI
- **Claude** (Anthropic): claude-3.5-sonnet, claude-3-opus, claude-3-haiku
- **Codex** (OpenAI): codex-1, codex-mini
- **GPT-4/4o** (OpenAI): gpt-4o, gpt-4-turbo
- **Gemini** (Google): gemini-pro, gemini-pro-vision
- **Llama 3** (Meta): llama-3-70b, llama-3-8b
- **Mistral**: mistral-large, mistral-medium

### AI-Assisted Features

1. **Prompt Enhancement** - Automatically improve generation prompts
2. **Script Generation** - Create complete video scripts from briefs
3. **Code Generation** - Generate Remotion/HyperFrames compositions
4. **Pipeline Optimization** - AI-driven pipeline parameter selection

See [FREE_LLM_API_SETUP.md](../FREE_LLM_API_SETUP.md) for detailed setup instructions.

## Supported Providers

| Provider | Video Models | Image Models | Audio |
|----------|-------------|--------------|-------|
| fal.ai | Seedance 2.0, Kling, MiniMax, VEO | FLUX | - |
| HeyGen | Video Agent, Avatar Shots, VEO 3.1, Sora | - | - |
| Gemini | Omni Flash (gen + edit) | - | - |
| BFL | - | FLUX 1.1 Pro, Pro, Dev, Schnell | - |
| OpenAI | - | GPT Image | TTS |
| Recraft | - | Recraft V3 | - |
| Ideogram | - | Ideogram V2 | - |
| Local | LTX, ComfyUI | - | Piper TTS |

## Composition Runtimes

| Runtime | Best For | Requirements |
|---------|----------|--------------|
| Remotion | React components, text cards, charts, captions | Node.js + npx + remotion-composer |
| HyperFrames | HTML/GSAP motion graphics, kinetic typography | Node.js ≥ 22 + npx + FFmpeg |
| FFmpeg | Video concat, trim, subtitle burn | FFmpeg binary |

## Pipeline Types

| Pipeline | Stages | Status | Best For |
|----------|--------|--------|----------|
| Animated Explainer | 8 | Production | Topic → full explainer |
| Cinematic | 7 | Production | Trailers, teasers |
| Avatar Spokesperson | 7 | Production | Presenter-led videos |
| Animation | 8 | Production | Motion graphics, Manim |
| Talking Head | 6 | Beta | Footage-led speakers |
| Screen Demo | 7 | Production | Software walkthroughs |
| Clip Factory | 7 | Beta | Many clips from source |
| Podcast Repurpose | 7 | Beta | Podcast highlights |
| Hybrid | 7 | Production | Source + generated |
| Localization Dub | 7 | Beta | Multi-language |
| Documentary Montage | 5 | Beta | Real footage montage |
| Character Animation | 7 | Beta | Rigged characters |

## API Endpoints

### Health & Registry
- `GET /health` - System health check
- `GET /api/registry` - Tool registry capabilities

### Generation
- `POST /api/generate/video` - Start video generation
- `POST /api/generate/image` - Start image generation
- `POST /api/generate/tts` - Start TTS generation
- `POST /api/generate/music` - Start music generation

### Job Management
- `GET /api/jobs/video/{id}` - Get video job status
- `GET /api/jobs/image/{id}` - Get image job status
- `POST /api/jobs/video/{id}/cancel` - Cancel video job
- `POST /api/jobs/image/{id}/cancel` - Cancel image job

### Pipelines
- `POST /api/pipelines/execute` - Execute pipeline
- `GET /api/pipelines/jobs/{id}` - Get pipeline job status
- `POST /api/pipelines/jobs/{id}/approve` - Approve pipeline stage
- `POST /api/pipelines/jobs/{id}/cancel` - Cancel pipeline
- `GET /api/pipelines` - List pipelines
- `GET /api/pipelines/{id}/manifest` - Get pipeline manifest

### Real-time
- `WS /ws` - WebSocket for live updates

## Client Library Usage

```typescript
import { OpenMontageClient } from './openmontage-client';

const client = OpenMontageClient.create({
  baseUrl: 'http://localhost:8000',
  apiKeys: { FAL_KEY: 'fal_xxx...' },
  debug: true
});

await client.connect();

// Generate video
const video = await client.generateVideoAndWait({
  prompt: 'A cinematic drone shot over a misty coastal city at golden hour',
  model: 'seedance_2_0',
  aspect_ratio: '16:9',
  duration: 10,
  composition_runtime: 'remotion'
}, {
  onProgress: (progress, stage, detail) => console.log(`${progress}% - ${stage}: ${detail}`)
});

// Execute pipeline
const pipeline = await client.executePipelineAndWait({
  pipeline: 'animated-explainer',
  brief: 'Create a 60-second explainer about CRISPR gene editing',
  options: {
    style_playbook: 'clean-professional',
    target_duration: 60,
    composition_runtime: 'auto',
    quality_level: 'high'
  }
});
```

## Architecture

```
videogen-app/
├── index.html              # Main frontend (self-contained HTML)
├── openmontage-client.ts   # TypeScript client library
├── backend.py              # FastAPI backend server
├── Dockerfile              # Multi-stage Docker build
├── docker-compose.yml      # Docker Compose for dev/prod
├── nginx.conf              # Nginx config for production
├── .github/workflows/ci.yml # GitHub Actions CI/CD
├── package.json            # Node.js config
├── tsconfig.json           # TypeScript config
├── vite.config.ts          # Vite config
├── requirements.txt        # Python dependencies
└── .gitignore              # Git ignore rules
```

## GitHub Actions CI/CD

The repository includes a complete CI/CD pipeline:

- **Lint & Test**: Python syntax check, TypeScript type check, HTML validation
- **Build Frontend**: Vite production build
- **Docker**: Multi-stage build and test
- **Deploy**: GitHub Pages deployment for frontend

## Environment Variables

```bash
# Video/Image Generation APIs
FAL_KEY=                    # fal.ai (Seedance, Kling, MiniMax, VEO)
HEYGEN_API_KEY=             # HeyGen (Video Agent, Avatar, VEO 3.1, Sora)
GEMINI_API_KEY=             # Gemini Omni Flash
OPENAI_API_KEY=             # GPT Image, TTS

# FreeLLMAPI (AI-assisted features)
FREE_LLM_API_KEY=           # FreeLLMAPI key
FREE_LLM_API_BASE_URL=      # FreeLLMAPI base URL

# Server
HOST=0.0.0.0
PORT=8000
DEBUG=true
```

## Development

### Running Tests

```bash
# Backend tests
cd videogen-app && python -m pytest tests/ -v

# Frontend type check
cd videogen-app && npm run type-check

# Full CI locally
act -j lint-and-test  # Requires 'act' tool
```

### Adding New Providers

1. Add provider to `backend.py` mock providers
2. Update `openmontage-client.ts` types
3. Add UI options in `index.html`
4. Update documentation

## License

MIT

## Resources

- [OpenMontage](https://github.com/your-org/OpenMontage)
- [FreeLLMAPI](https://github.com/tashfeenahmed/freellmapi)
- [Remotion](https://www.remotion.dev/)
- [HyperFrames](https://hyperframes.dev/)
- [fal.ai](https://fal.ai/)
- [HeyGen](https://www.heygen.com/)

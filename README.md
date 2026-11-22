# OpenMontage Studio

Professional AI video and image generation studio powered by OpenMontage.

## Features

- **Video Generation**: Text-to-video and image-to-video with multiple providers (Seedance 2.0, VEO, Kling, Sora, Runway, LTX, Gemini Omni)
- **Image Generation**: Text-to-image with FLUX, GPT Image, Recraft, Ideogram
- **Pipeline System**: Structured multi-stage video production (Animated Explainer, Cinematic, Avatar Spokesperson, etc.)
- **Real-time Progress**: WebSocket-based live updates during generation
- **Composition Runtimes**: Remotion (React), HyperFrames (HTML/GSAP), FFmpeg
- **Theme Support**: Light/dark mode with OKLCH color tokens
- **Responsive Design**: Mobile-first, works on all devices

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+ (for frontend dev)
- OpenMontage installed (for full pipeline support)

### Backend Setup

```bash
cd videogen-app

# Install Python dependencies
pip install -r requirements.txt

# Set API keys (optional - uses mock providers without them)
export FAL_KEY="your_fal_key"
export HEYGEN_API_KEY="your_heygen_key"
export GEMINI_API_KEY="your_gemini_key"

# Start backend server
python backend.py
```

Backend runs on `http://localhost:8000` with API docs at `/docs`.

### Frontend Development

```bash
cd videogen-app

# Install dependencies
npm install

# Start dev server (proxies API to backend)
npm run dev
```

Frontend runs on `http://localhost:3000`.

### Production Build

```bash
npm run build
```

Outputs to `dist/` directory.

## Architecture

```
videogen-app/
├── index.html           # Main frontend (self-contained HTML)
├── openmontage-client.ts # TypeScript client library
├── backend.py           # FastAPI backend server
├── package.json         # Node.js config
├── tsconfig.json        # TypeScript config
├── vite.config.ts       # Vite config
└── requirements.txt     # Python dependencies
```

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

## OpenMontage Integration

The backend connects to OpenMontage's:
- **Tool Registry**: Auto-discovers 56+ tools across capabilities
- **Pipelines**: 13 structured production workflows
- **Skills**: 60+ skills for prompting, composition, rendering
- **Agents**: Orchestrator and stage directors

## Configuration

### Environment Variables

```bash
# API Keys
FAL_KEY=                    # fal.ai (Seedance, Kling, MiniMax, VEO)
HEYGEN_API_KEY=             # HeyGen (Video Agent, Avatar, VEO 3.1, Sora)
GEMINI_API_KEY=             # Gemini Omni Flash
GOOGLE_API_KEY=             # Alternative to GEMINI_API_KEY
OPENAI_API_KEY=             # GPT Image

# Server
HOST=0.0.0.0
PORT=8000
DEBUG=true
```

## Supported Providers

| Provider | Video Models | Image Models | Audio |
|----------|-------------|--------------|-------|
| fal.ai | Seedance 2.0, Kling, MiniMax, VEO | FLUX | - |
| HeyGen | Video Agent, Avatar Shots, VEO 3.1, Sora, Runway | - | - |
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

## License

MIT
# FreeLLMAPI Integration Setup

## Overview

FreeLLMAPI provides free access to various AI models including Claude, Codex, and other coding assistants. This document explains how to set up and integrate FreeLLMAPI with OpenMontage Studio.

## FreeLLMAPI Supported Models

Based on the official documentation, FreeLLMAPI supports:

### Chat Models
- **Claude** (Anthropic) - claude-3-opus, claude-3-sonnet, claude-3-haiku, claude-3.5-sonnet
- **Codex** (OpenAI) - codex-mini, codex-1
- **GPT-4** - gpt-4, gpt-4-turbo, gpt-4o
- **GPT-3.5** - gpt-3.5-turbo
- **Gemini** (Google) - gemini-pro, gemini-pro-vision
- **Llama** (Meta) - llama-2, llama-3
- **Mistral** - mistral-large, mistral-medium
- **Command** (Cohere) - command-r, command-r-plus

### Embedding Models
- text-embedding-ada-002
- text-embedding-3-small
- text-embedding-3-large

## Quick Start

### 1. Get FreeLLMAPI Key

1. Visit the FreeLLMAPI website/dashboard
2. Create an account
3. Generate an API key
4. Note the base URL (typically `https://api.freellmapi.com` or similar)

### 2. Environment Configuration

Create a `.env` file in the project root:

```bash
# FreeLLMAPI Configuration
FREE_LLM_API_KEY=your_freellmapi_key_here
FREE_LLM_API_BASE_URL=https://api.freellmapi.com/v1

# OpenMontage Studio Backend
FAL_KEY=your_fal_ai_key
HEYGEN_API_KEY=your_heygen_key
GEMINI_API_KEY=your_gemini_key
OPENAI_API_KEY=your_openai_key

# Frontend (Vite)
VITE_OM_BASE_URL=http://localhost:8000
VITE_FREE_LLM_API_URL=https://api.freellmapi.com/v1
VITE_FREE_LLM_API_KEY=your_freellmapi_key
```

### 3. Install FreeLLMAPI Client

```bash
# Python
pip install freellmapi

# Or use the REST API directly
curl -X POST https://api.freellmapi.com/v1/chat/completions \
  -H "Authorization: Bearer YOUR_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "claude-3.5-sonnet",
    "messages": [{"role": "user", "content": "Hello!"}]
  }'
```

## Integration with OpenMontage Studio

### Backend Integration (Python)

The backend (`backend.py`) can be extended to use FreeLLMAPI for:

1. **Script Generation** - Use Claude/Codex for video scripts
2. **Prompt Enhancement** - Improve user prompts before generation
3. **Pipeline Orchestration** - AI-driven pipeline decisions
4. **Code Generation** - Generate Remotion/HyperFrames compositions

```python
# Example: FreeLLMAPI integration in backend.py
import os
from freellmapi import FreeLLMAPI

class FreeLLMClient:
    def __init__(self):
        self.client = FreeLLMAPI(
            api_key=os.getenv("FREE_LLM_API_KEY"),
            base_url=os.getenv("FREE_LLM_API_BASE_URL")
        )
    
    async def enhance_prompt(self, user_prompt: str, task_type: str) -> str:
        """Enhance user prompt for better generation results"""
        system_prompt = f"""You are an expert prompt engineer for {task_type}.
        Enhance the user's prompt to be more descriptive, specific, and optimized for AI generation.
        Return only the enhanced prompt."""
        
        response = await self.client.chat.completions.create(
            model="claude-3.5-sonnet",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7,
            max_tokens=500
        )
        return response.choices[0].message.content
    
    async def generate_script(self, brief: str, duration: int, style: str) -> dict:
        """Generate a complete video script from a brief"""
        system_prompt = f"""Create a {duration}-second {style} video script.
        Return JSON with: sections, narration, visual_cues, timing."""
        
        response = await self.client.chat.completions.create(
            model="claude-3.5-sonnet",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": brief}
            ],
            temperature=0.7,
            max_tokens=2000,
            response_format={"type": "json_object"}
        )
        return json.loads(response.choices[0].message.content)

# Usage in pipeline stages
free_llm = FreeLLMClient()
```

### Frontend Integration (JavaScript/TypeScript)

Add FreeLLMAPI support to the client library:

```typescript
// In openmontage-client.ts
export interface FreeLLMConfig {
  apiKey: string;
  baseUrl: string;
  defaultModel?: string;
}

export class FreeLLMClient {
  private config: FreeLLMConfig;
  
  constructor(config: FreeLLMConfig) {
    this.config = config;
  }
  
  async chat(messages: Array<{role: string; content: string}>, options?: {
    model?: string;
    temperature?: number;
    maxTokens?: number;
    responseFormat?: 'text' | 'json';
  }) {
    const response = await fetch(`${this.config.baseUrl}/chat/completions`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${this.config.apiKey}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        model: options?.model || this.config.defaultModel || 'claude-3.5-sonnet',
        messages,
        temperature: options?.temperature ?? 0.7,
        max_tokens: options?.maxTokens ?? 2000,
        response_format: options?.responseFormat === 'json' ? { type: 'json_object' } : undefined,
      }),
    });
    
    return response.json();
  }
  
  async enhancePrompt(prompt: string, type: 'video' | 'image' | 'pipeline'): Promise<string> {
    const response = await this.chat([
      { role: 'system', content: `Enhance this ${type} generation prompt for optimal AI results. Be specific, descriptive, and include technical details.` },
      { role: 'user', content: prompt }
    ], { model: 'claude-3.5-sonnet', maxTokens: 500 });
    
    return response.choices[0].message.content;
  }
  
  async generateScript(brief: string, duration: number, style: string): Promise<VideoScript> {
    const response = await this.chat([
      { role: 'system', content: `Generate a ${duration}s ${style} video script. Return JSON with sections, narration, visualCues, timing.` },
      { role: 'user', content: brief }
    ], { model: 'claude-3.5-sonnet', responseFormat: 'json', maxTokens: 2000 });
    
    return JSON.parse(response.choices[0].message.content);
  }
}
```

## Connecting to Specific AI Models

### Claude (Anthropic)
```bash
# Via FreeLLMAPI
MODEL=claude-3.5-sonnet  # Best for complex reasoning
MODEL=claude-3-opus      # Most capable
MODEL=claude-3-haiku     # Fastest/cheapest
```

### Codex (OpenAI)
```bash
# Via FreeLLMAPI
MODEL=codex-1            # Latest coding model
MODEL=codex-mini         # Faster coding model
```

### For Code Generation (Remotion/HyperFrames)
```typescript
// Use Codex for generating composition code
const codexPrompt = `Generate a Remotion composition for: ${userBrief}
Requirements:
- TypeScript with React
- Use remotion-composer components
- Include: TextCard, StatCard, BarChart, transitions
- Duration: ${duration}s
- Aspect: ${aspectRatio}`;

const composition = await freeLLM.chat([
  { role: 'system', content: 'You are a Remotion expert. Generate clean, working TypeScript code.' },
  { role: 'user', content: codexPrompt }
], { model: 'codex-1', temperature: 0.3 });
```

## Docker Integration

Add to `docker-compose.yml`:

```yaml
services:
  # ... existing services ...
  
  freellmapi-proxy:
    image: freellmapi/proxy:latest
    environment:
      - FREE_LLM_API_KEY=${FREE_LLM_API_KEY}
      - ALLOWED_MODELS=claude-3.5-sonnet,codex-1,gpt-4o
    ports:
      - "8080:8080"
    profiles:
      - full
```

## GitHub Actions CI/CD with FreeLLMAPI

```yaml
# .github/workflows/ci.yml
env:
  FREE_LLM_API_KEY: ${{ secrets.FREE_LLM_API_KEY }}
  FREE_LLM_API_BASE_URL: https://api.freellmapi.com/v1

jobs:
  test-with-ai:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Test FreeLLMAPI integration
        run: |
          python -c "
import os
from freellmapi import FreeLLMAPI
client = FreeLLMAPI(api_key=os.getenv('FREE_LLM_API_KEY'))
response = client.chat.completions.create(
    model='claude-3.5-sonnet',
    messages=[{'role': 'user', 'content': 'Test'}],
    max_tokens=10
)
print('FreeLLMAPI works:', response.choices[0].message.content)
"
```

## Security Best Practices

1. **Never commit API keys** - Use GitHub Secrets or environment variables
2. **Rotate keys regularly** - Set up automated key rotation
3. **Use scoped keys** - Create separate keys for different environments
4. **Monitor usage** - Track API usage to detect anomalies
5. **Rate limiting** - Implement client-side rate limiting

## Troubleshooting

### Common Issues

| Issue | Solution |
|-------|----------|
| `401 Unauthorized` | Check API key validity and permissions |
| `429 Rate Limited` | Implement exponential backoff |
| `Model not found` | Verify model name matches FreeLLMAPI catalog |
| `Timeout` | Increase timeout, use streaming for long responses |

### Debug Mode

```bash
# Enable debug logging
export FREE_LLM_DEBUG=true
export DEBUG=freellmapi:*
```

## Advanced: Custom Model Routing

Create a router that selects the best model for each task:

```python
class ModelRouter:
    ROUTES = {
        'script_writing': 'claude-3.5-sonnet',
        'code_generation': 'codex-1',
        'prompt_enhancement': 'claude-3-haiku',
        'creative_writing': 'claude-3-opus',
        'quick_tasks': 'gpt-3.5-turbo',
    }
    
    def __init__(self, client: FreeLLMAPI):
        self.client = client
    
    async def complete(self, task: str, messages: list, **kwargs):
        model = self.ROUTES.get(task, 'claude-3.5-sonnet')
        return await self.client.chat.completions.create(
            model=model,
            messages=messages,
            **kwargs
        )
```

## Resources

- [FreeLLMAPI Documentation](https://github.com/tashfeenahmed/freellmapi)
- [Supported Agents](https://github.com/tashfeenahmed/freellmapi/blob/main/docs/en/clients/02-supported-agents.md)
- [API Reference](https://github.com/tashfeenahmed/freellmapi/tree/main/docs/en/api)
- [OpenMontage Studio Repo](https://github.com/IMDE122/openmontage-studio)

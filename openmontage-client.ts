/**
 * OpenMontage Client Library
 *
 * TypeScript client for connecting to OpenMontage's agents, skills, tools,
 * and pipeline system for video/image generation.
 *
 * @version 1.0.0
 * @author OpenMontage Studio
 */

// ============================================
// Type Definitions
// ============================================

/** Supported API providers */
export type Provider =
  | 'fal'
  | 'heygen'
  | 'gemini'
  | 'openai'
  | 'recraft'
  | 'ideogram'
  | 'bfl'
  | 'local';

/** Video generation models by provider */
export type VideoModel =
  // Seedance 2.0 (fal.ai)
  | 'seedance_2_0'
  | 'seedance_2_0_fast'
  // VEO (Google via fal.ai/HeyGen)
  | 'veo_3_1'
  | 'veo_3_1_fast'
  | 'veo3'
  | 'veo3_fast'
  | 'veo2'
  // Kling
  | 'kling_pro'
  | 'kling_v2'
  | 'kling_v2_1'
  // Sora (OpenAI via HeyGen)
  | 'sora_v2'
  | 'sora_v2_pro'
  // Runway
  | 'runway_gen4'
  | 'runway_gen3'
  // LTX
  | 'ltx_distilled'
  | 'ltx_2_0'
  // HeyGen specific
  | 'heygen_video_agent'
  | 'heygen_avatar_shots'
  // Gemini
  | 'gemini_omni_flash'
  | 'gemini_omni_pro'
  // Auto
  | 'auto';

/** Image generation models */
export type ImageModel =
  | 'flux_1_1_pro'
  | 'flux_pro'
  | 'flux_dev'
  | 'flux_schnell'
  | 'gpt_image'
  | 'recraft_v3'
  | 'ideogram_v2'
  | 'ideogram_v2_turbo'
  | 'bfl_flux_pro'
  | 'bfl_flux_dev'
  | 'auto';

/** Composition runtimes */
export type CompositionRuntime =
  | 'remotion'
  | 'hyperframes'
  | 'ffmpeg'
  | 'auto';

/** Pipeline types */
export type PipelineType =
  | 'animated-explainer'
  | 'cinematic'
  | 'avatar-spokesperson'
  | 'animation'
  | 'talking-head'
  | 'screen-demo'
  | 'clip-factory'
  | 'podcast-repurpose'
  | 'hybrid'
  | 'localization-dub'
  | 'documentary-montage'
  | 'character-animation'
  | 'framework-smoke';

/** Aspect ratios */
export type AspectRatio =
  | '16:9'
  | '9:16'
  | '1:1'
  | '4:3'
  | '3:2'
  | '21:9'
  | '2.39:1';

/** Job status */
export type JobStatus =
  | 'pending'
  | 'queued'
  | 'running'
  | 'completed'
  | 'failed'
  | 'cancelled';

/** Capability families */
export type CapabilityFamily =
  | 'video_generation'
  | 'image_generation'
  | 'tts'
  | 'music_generation'
  | 'video_post'
  | 'audio_processing'
  | 'analysis'
  | 'avatar'
  | 'character_animation'
  | '3d_world_generation'
  | '3d_asset_acquisition'
  | '3d_asset_generation'
  | '3d_world_rendering'
  | 'enhancement'
  | 'subtitle'
  | 'music_library'
  | 'music_search';

/** Tool status from registry */
export type ToolStatus = 'AVAILABLE' | 'UNAVAILABLE' | 'DEGRADED' | 'ERROR';

/** Pipeline stage */
export type PipelineStage =
  | 'research'
  | 'proposal'
  | 'idea'
  | 'script'
  | 'scene_plan'
  | 'assets'
  | 'edit'
  | 'compose'
  | 'publish';

// ============================================
// Core Data Structures
// ============================================

/** API Key configuration */
export interface ApiKeys {
  FAL_KEY?: string;
  HEYGEN_API_KEY?: string;
  GEMINI_API_KEY?: string;
  GOOGLE_API_KEY?: string;
  OPENAI_API_KEY?: string;
  RECRAFT_API_KEY?: string;
  IDEOGRAM_API_KEY?: string;
  BFL_API_KEY?: string;
  AZURE_SPEECH_KEY?: string;
  AZURE_SPEECH_REGION?: string;
  ELEVENLABS_API_KEY?: string;
  PEXELS_API_KEY?: string;
  PIXABAY_API_KEY?: string;
}

/** Provider tool information */
export interface ProviderTool {
  name: string;
  capability: CapabilityFamily;
  provider: string;
  status: ToolStatus;
  runtime: 'LOCAL' | 'API' | 'LOCAL_GPU' | 'HYBRID';
  cost_per_unit?: number;
  cost_unit?: string;
  best_for?: string[];
  install_instructions?: string;
  dependencies?: string[];
  agent_skills?: string[];
  input_schema?: Record<string, unknown>;
  output_schema?: Record<string, unknown>;
}

/** Capability catalog entry */
export interface CapabilityEntry {
  capability: CapabilityFamily;
  configured: number;
  total: number;
  providers: string[];
  tools: ProviderTool[];
}

/** Tool registry response */
export interface ToolRegistryResponse {
  capabilities: CapabilityEntry[];
  providers: Record<string, ProviderTool[]>;
  composition_runtimes: {
    ffmpeg: boolean;
    remotion: boolean;
    hyperframes: boolean;
  };
  setup_offers: Array<{
    tool: string;
    capability: CapabilityFamily;
    install_instructions: string;
    dependencies: string[];
  }>;
  runtime_warnings: string[];
}

/** Video generation request */
export interface VideoGenerationRequest {
  prompt: string;
  model?: VideoModel;
  aspect_ratio?: AspectRatio;
  duration?: number; // seconds
  reference_image_url?: string;
  tail_image_url?: string;
  composition_runtime?: CompositionRuntime;
  pipeline?: PipelineType;
  config?: Record<string, unknown>;
  webhook_url?: string;
}

/** Image generation request */
export interface ImageGenerationRequest {
  prompt: string;
  model?: ImageModel;
  aspect_ratio?: AspectRatio;
  count?: number;
  quality?: 'standard' | 'hd' | 'ultra';
  reference_image_url?: string;
  config?: Record<string, unknown>;
  webhook_url?: string;
}

/** TTS request */
export interface TtsRequest {
  text: string;
  voice?: string;
  model?: string;
  speed?: number;
  format?: 'mp3' | 'wav' | 'ogg';
}

/** Music generation request */
export interface MusicGenerationRequest {
  prompt: string;
  duration?: number;
  genre?: string;
  mood?: string;
  bpm?: number;
  instrumental?: boolean;
}

/** Pipeline execution request */
export interface PipelineExecutionRequest {
  pipeline: PipelineType;
  brief: string;
  options?: {
    style_playbook?: string;
    target_duration?: number;
    target_platform?: string;
    composition_runtime?: CompositionRuntime;
    quality_level?: 'draft' | 'standard' | 'high' | 'ultra';
    auto_approve_stages?: boolean;
  };
  webhook_url?: string;
}

/** Generation job */
export interface GenerationJob<T = unknown> {
  id: string;
  type: 'video' | 'image' | 'pipeline' | 'tts' | 'music';
  status: JobStatus;
  progress: number; // 0-100
  current_stage?: string;
  current_detail?: string;
  request: T;
  result?: GenerationResult;
  error?: GenerationError;
  created_at: string;
  started_at?: string;
  completed_at?: string;
  estimated_cost?: number;
  actual_cost?: number;
}

/** Generation result */
export interface GenerationResult {
  urls: string[];
  primary_url: string;
  thumbnail_url?: string;
  metadata: {
    model: string;
    provider: string;
    duration?: number;
    aspect_ratio?: string;
    resolution?: string;
    file_size?: number;
    format?: string;
    seed?: number;
  };
  pipeline_artifacts?: Record<string, unknown>;
}

/** Generation error */
export interface GenerationError {
  code: string;
  message: string;
  details?: Record<string, unknown>;
  retryable: boolean;
}

/** Pipeline stage result */
export interface PipelineStageResult {
  stage: PipelineStage;
  status: 'completed' | 'failed' | 'awaiting_human';
  artifact?: Record<string, unknown>;
  artifacts_path?: string;
  review_findings?: ReviewFinding[];
  human_approval_required?: boolean;
}

/** Review finding */
export interface ReviewFinding {
  severity: 'critical' | 'suggestion' | 'nitpick';
  category: string;
  message: string;
  suggestion?: string;
}

/** Pipeline execution job */
export interface PipelineJob extends GenerationJob<PipelineExecutionRequest> {
  stages: PipelineStageResult[];
  current_stage_index: number;
  project_id?: string;
  project_path?: string;
}

/** Health check response */
export interface HealthCheck {
  status: 'healthy' | 'degraded' | 'unhealthy';
  backend: {
    status: 'running' | 'stopped' | 'starting';
    version?: string;
    uptime?: number;
  };
  registry: {
    tools_discovered: number;
    capabilities_configured: number;
    composition_runtimes: {
      ffmpeg: boolean;
      remotion: boolean;
      hyperframes: boolean;
    };
  };
  pipelines: {
    available: number;
    loaded: string[];
  };
  skills: {
    loaded: number;
    categories: string[];
  };
  agents: {
    active: number;
    available: string[];
  };
}

/** WebSocket message types */
export type WSMessageType =
  | 'job_created'
  | 'job_progress'
  | 'job_stage_change'
  | 'job_completed'
  | 'job_failed'
  | 'job_cancelled'
  | 'human_approval_required'
  | 'review_finding'
  | 'cost_update'
  | 'log'
  | 'heartbeat';

export interface WSMessage<T = unknown> {
  type: WSMessageType;
  job_id: string;
  timestamp: string;
  data: T;
}

// ============================================
// Configuration
// ============================================

export interface ClientConfig {
  /** Base URL for OpenMontage backend API */
  baseUrl: string;
  /** WebSocket URL for real-time updates */
  wsUrl?: string;
  /** API keys for providers */
  apiKeys?: ApiKeys;
  /** Default timeout for requests (ms) */
  timeout?: number;
  /** Maximum retry attempts */
  maxRetries?: number;
  /** Retry delay base (ms) */
  retryDelay?: number;
  /** Enable debug logging */
  debug?: boolean;
  /** Custom headers */
  headers?: Record<string, string>;
}

const DEFAULT_CONFIG: Required<Omit<ClientConfig, 'apiKeys' | 'wsUrl' | 'headers'>> = {
  baseUrl: 'http://localhost:8000',
  timeout: 120000,
  maxRetries: 3,
  retryDelay: 1000,
  debug: false,
};

// ============================================
// Error Classes
// ============================================

export class OpenMontageError extends Error {
  constructor(
    message: string,
    public code: string,
    public statusCode?: number,
    public details?: Record<string, unknown>,
    public retryable: boolean = false
  ) {
    super(message);
    this.name = 'OpenMontageError';
  }
}

export class AuthenticationError extends OpenMontageError {
  constructor(message: string, details?: Record<string, unknown>) {
    super(message, 'AUTHENTICATION_ERROR', 401, details, false);
    this.name = 'AuthenticationError';
  }
}

export class ValidationError extends OpenMontageError {
  constructor(message: string, details?: Record<string, unknown>) {
    super(message, 'VALIDATION_ERROR', 400, details, false);
    this.name = 'ValidationError';
  }
}

export class NotFoundError extends OpenMontageError {
  constructor(resource: string) {
    super(`${resource} not found`, 'NOT_FOUND', 404, { resource }, false);
    this.name = 'NotFoundError';
  }
}

export class RateLimitError extends OpenMontageError {
  constructor(message: string, public retryAfter: number) {
    super(message, 'RATE_LIMITED', 429, { retryAfter }, true);
    this.name = 'RateLimitError';
  }
}

export class ProviderError extends OpenMontageError {
  constructor(provider: string, message: string, details?: Record<string, unknown>) {
    super(`Provider ${provider} error: ${message}`, 'PROVIDER_ERROR', 502, { provider, ...details }, true);
    this.name = 'ProviderError';
  }
}

export class PipelineError extends OpenMontageError {
  constructor(pipeline: string, stage: string, message: string, details?: Record<string, unknown>) {
    super(`Pipeline ${pipeline} failed at ${stage}: ${message}`, 'PIPELINE_ERROR', 500, { pipeline, stage, ...details }, false);
    this.name = 'PipelineError';
  }
}

// ============================================
// HTTP Client
// ============================================

class HttpClient {
  private config: Required<Omit<ClientConfig, 'apiKeys' | 'wsUrl' | 'headers'>> & {
    apiKeys: ApiKeys;
    wsUrl: string;
    headers: Record<string, string>
  };
  private abortControllers: Map<string, AbortController> = new Map();

  constructor(config: ClientConfig) {
    this.config = {
      ...DEFAULT_CONFIG,
      ...config,
      apiKeys: config.apiKeys || {},
      wsUrl: config.wsUrl || config.baseUrl.replace('http', 'ws') + '/ws',
      headers: config.headers || {},
    };
  }

  private getHeaders(): Record<string, string> {
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
      ...this.config.headers,
    };

    // Add API keys as headers
    if (this.config.apiKeys.FAL_KEY) headers['X-FAL-Key'] = this.config.apiKeys.FAL_KEY;
    if (this.config.apiKeys.HEYGEN_API_KEY) headers['X-HeyGen-Key'] = this.config.apiKeys.HEYGEN_API_KEY;
    if (this.config.apiKeys.GEMINI_API_KEY) headers['X-Gemini-Key'] = this.config.apiKeys.GEMINI_API_KEY;
    if (this.config.apiKeys.OPENAI_API_KEY) headers['X-OpenAI-Key'] = this.config.apiKeys.OPENAI_API_KEY;

    return headers;
  }

  private async request<T>(
    method: string,
    path: string,
    body?: unknown,
    options: { signal?: AbortSignal; retries?: number } = {}
  ): Promise<T> {
    const url = `${this.config.baseUrl}${path}`;
    const controller = new AbortController();
    const signal = options.signal || controller.signal;

    const requestId = `${method}:${path}:${Date.now()}`;
    this.abortControllers.set(requestId, controller);

    const retries = options.retries ?? this.config.maxRetries;
    let lastError: Error | null = null;

    for (let attempt = 0; attempt <= retries; attempt++) {
      try {
        if (this.config.debug) {
          console.log(`[OpenMontage] ${method} ${path}`, { attempt, body });
        }

        const response = await fetch(url, {
          method,
          headers: this.getHeaders(),
          body: body ? JSON.stringify(body) : undefined,
          signal,
        });

        if (!response.ok) {
          const errorData = await response.json().catch(() => ({}));

          switch (response.status) {
            case 401:
              throw new AuthenticationError('Authentication failed', errorData);
            case 400:
              throw new ValidationError(errorData.message || 'Invalid request', errorData);
            case 404:
              throw new NotFoundError(path);
            case 429:
              const retryAfter = parseInt(response.headers.get('Retry-After') || '60', 10);
              throw new RateLimitError('Rate limited', retryAfter);
            case 502:
            case 503:
            case 504:
              throw new ProviderError('backend', `Server error: ${response.status}`, errorData);
            default:
              throw new OpenMontageError(
                errorData.message || `HTTP ${response.status}`,
                'HTTP_ERROR',
                response.status,
                errorData,
                response.status >= 500
              );
          }
        }

        const data = await response.json();

        if (this.config.debug) {
          console.log(`[OpenMontage] Response:`, data);
        }

        this.abortControllers.delete(requestId);
        return data as T;

      } catch (error) {
        lastError = error as Error;

        // Don't retry on non-retryable errors
        if (error instanceof OpenMontageError && !error.retryable) {
          throw error;
        }

        // Don't retry on abort
        if (error instanceof DOMException && error.name === 'AbortError') {
          throw error;
        }

        // Last attempt
        if (attempt === retries) {
          break;
        }

        // Wait before retry with exponential backoff
        const delay = this.config.retryDelay * Math.pow(2, attempt);
        if (this.config.debug) {
          console.log(`[OpenMontage] Retrying in ${delay}ms...`);
        }
        await new Promise(r => setTimeout(r, delay));
      }
    }

    this.abortControllers.delete(requestId);
    throw lastError || new OpenMontageError('Request failed after retries', 'REQUEST_FAILED', undefined, undefined, true);
  }

  async get<T>(path: string, options?: { signal?: AbortSignal }): Promise<T> {
    return this.request<T>('GET', path, undefined, options);
  }

  async post<T>(path: string, body: unknown, options?: { signal?: AbortSignal }): Promise<T> {
    return this.request<T>('POST', path, body, options);
  }

  async put<T>(path: string, body: unknown, options?: { signal?: AbortSignal }): Promise<T> {
    return this.request<T>('PUT', path, body, options);
  }

  async delete<T>(path: string, options?: { signal?: AbortSignal }): Promise<T> {
    return this.request<T>('DELETE', path, undefined, options);
  }

  abortAll(): void {
    this.abortControllers.forEach(controller => controller.abort());
    this.abortControllers.clear();
  }

  updateApiKeys(keys: Partial<ApiKeys>): void {
    this.config.apiKeys = { ...this.config.apiKeys, ...keys };
  }
}

// ============================================
// WebSocket Client
// ============================================

type WSListener = (message: WSMessage) => void;

class WebSocketClient {
  private ws: WebSocket | null = null;
  private config: ClientConfig;
  private listeners: Set<WSListener> = new Set();
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectDelay = 1000;
  private shouldReconnect = false;
  private jobSubscriptions: Map<string, Set<WSListener>> = new Map();

  constructor(config: ClientConfig) {
    this.config = config;
  }

  connect(): Promise<void> {
    return new Promise((resolve, reject) => {
      try {
        const wsUrl = this.config.wsUrl || this.config.baseUrl.replace('http', 'ws') + '/ws';
        this.ws = new WebSocket(wsUrl);
        this.shouldReconnect = true;

        this.ws.onopen = () => {
          if (this.config.debug) console.log('[OpenMontage WS] Connected');
          this.reconnectAttempts = 0;
          resolve();
        };

        this.ws.onmessage = (event) => {
          try {
            const message: WSMessage = JSON.parse(event.data);
            this.handleMessage(message);
          } catch (e) {
            if (this.config.debug) console.error('[OpenMontage WS] Parse error:', e);
          }
        };

        this.ws.onerror = (error) => {
          if (this.config.debug) console.error('[OpenMontage WS] Error:', error);
        };

        this.ws.onclose = () => {
          if (this.config.debug) console.log('[OpenMontage WS] Disconnected');
          if (this.shouldReconnect && this.reconnectAttempts < this.maxReconnectAttempts) {
            this.reconnectAttempts++;
            setTimeout(() => this.connect(), this.reconnectDelay * this.reconnectAttempts);
          }
        };

      } catch (error) {
        reject(error);
      }
    });
  }

  private handleMessage(message: WSMessage): void {
    // Notify global listeners
    this.listeners.forEach(listener => {
      try { listener(message); } catch (e) { console.error('WS listener error:', e); }
    });

    // Notify job-specific listeners
    const jobListeners = this.jobSubscriptions.get(message.job_id);
    if (jobListeners) {
      jobListeners.forEach(listener => {
        try { listener(message); } catch (e) { console.error('WS job listener error:', e); }
      });
    }
  }

  subscribe(listener: WSListener): () => void {
    this.listeners.add(listener);
    return () => this.listeners.delete(listener);
  }

  subscribeToJob(jobId: string, listener: WSListener): () => void {
    if (!this.jobSubscriptions.has(jobId)) {
      this.jobSubscriptions.set(jobId, new Set());
    }
    this.jobSubscriptions.get(jobId)!.add(listener);
    return () => {
      const listeners = this.jobSubscriptions.get(jobId);
      if (listeners) {
        listeners.delete(listener);
        if (listeners.size === 0) {
          this.jobSubscriptions.delete(jobId);
        }
      }
    };
  }

  send(message: unknown): void {
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(message));
    }
  }

  disconnect(): void {
    this.shouldReconnect = false;
    this.ws?.close();
    this.ws = null;
    this.listeners.clear();
    this.jobSubscriptions.clear();
  }
}

// ============================================
// Main Client Class
// ============================================

export class OpenMontageClient {
  private http: HttpClient;
  private ws: WebSocketClient;
  private config: ClientConfig;
  private eventListeners: Map<string, Set<Function>> = new Map();

  constructor(config: ClientConfig) {
    this.config = config;
    this.http = new HttpClient(config);
    this.ws = new WebSocketClient(config);
  }

  // ---- Event System ----
  on(event: string, listener: Function): () => void {
    if (!this.eventListeners.has(event)) {
      this.eventListeners.set(event, new Set());
    }
    this.eventListeners.get(event)!.add(listener);
    return () => this.eventListeners.get(event)?.delete(listener);
  }

  private emit(event: string, data: unknown): void {
    this.eventListeners.get(event)?.forEach(listener => {
      try { listener(data); } catch (e) { console.error(`Event listener error (${event}):`, e); }
    });
  }

  // ---- Connection Management ----
  async connect(): Promise<void> {
    await this.ws.connect();
    this.emit('connected', {});
  }

  disconnect(): void {
    this.http.abortAll();
    this.ws.disconnect();
    this.emit('disconnected', {});
  }

  async healthCheck(): Promise<HealthCheck> {
    return this.http.get<HealthCheck>('/health');
  }

  // ---- Tool Registry ----
  async getToolRegistry(): Promise<ToolRegistryResponse> {
    return this.http.get<ToolRegistryResponse>('/api/registry');
  }

  async getCapabilities(): Promise<CapabilityEntry[]> {
    const registry = await this.getToolRegistry();
    return registry.capabilities;
  }

  async getProviders(): Promise<Record<string, ProviderTool[]>> {
    const registry = await this.getToolRegistry();
    return registry.providers;
  }

  async getCompositionRuntimes(): Promise<ToolRegistryResponse['composition_runtimes']> {
    const registry = await this.getToolRegistry();
    return registry.composition_runtimes;
  }

  async getSetupOffers(): Promise<ToolRegistryResponse['setup_offers']> {
    const registry = await this.getToolRegistry();
    return registry.setup_offers;
  }

  async getRuntimeWarnings(): Promise<string[]> {
    const registry = await this.getToolRegistry();
    return registry.runtime_warnings;
  }

  // ---- Video Generation ----
  async generateVideo(request: VideoGenerationRequest): Promise<GenerationJob> {
    const job = await this.http.post<GenerationJob>('/api/generate/video', request);
    this.emit('job:created', job);
    return job;
  }

  async getVideoJob(jobId: string): Promise<GenerationJob> {
    return this.http.get<GenerationJob>(`/api/jobs/video/${jobId}`);
  }

  async cancelVideoJob(jobId: string): Promise<void> {
    await this.http.post(`/api/jobs/video/${jobId}/cancel`, {});
    this.emit('job:cancelled', { jobId });
  }

  // ---- Image Generation ----
  async generateImage(request: ImageGenerationRequest): Promise<GenerationJob> {
    const job = await this.http.post<GenerationJob>('/api/generate/image', request);
    this.emit('job:created', job);
    return job;
  }

  async getImageJob(jobId: string): Promise<GenerationJob> {
    return this.http.get<GenerationJob>(`/api/jobs/image/${jobId}`);
  }

  async cancelImageJob(jobId: string): Promise<void> {
    await this.http.post(`/api/jobs/image/${jobId}/cancel`, {});
    this.emit('job:cancelled', { jobId });
  }

  // ---- TTS Generation ----
  async generateTts(request: TtsRequest): Promise<GenerationJob> {
    const job = await this.http.post<GenerationJob>('/api/generate/tts', request);
    this.emit('job:created', job);
    return job;
  }

  // ---- Music Generation ----
  async generateMusic(request: MusicGenerationRequest): Promise<GenerationJob> {
    const job = await this.http.post<GenerationJob>('/api/generate/music', request);
    this.emit('job:created', job);
    return job;
  }

  // ---- Pipeline Execution ----
  async executePipeline(request: PipelineExecutionRequest): Promise<PipelineJob> {
    const job = await this.http.post<PipelineJob>('/api/pipelines/execute', request);
    this.emit('pipeline:created', job);
    return job;
  }

  async getPipelineJob(jobId: string): Promise<PipelineJob> {
    return this.http.get<PipelineJob>(`/api/pipelines/jobs/${jobId}`);
  }

  async approvePipelineStage(jobId: string, stage: PipelineStage, approved: boolean, feedback?: string): Promise<void> {
    await this.http.post(`/api/pipelines/jobs/${jobId}/approve`, { stage, approved, feedback });
    this.emit('pipeline:stage_approved', { jobId, stage, approved });
  }

  async cancelPipelineJob(jobId: string): Promise<void> {
    await this.http.post(`/api/pipelines/jobs/${jobId}/cancel`, {});
    this.emit('pipeline:cancelled', { jobId });
  }

  async getPipelineManifest(pipeline: PipelineType): Promise<Record<string, unknown>> {
    return this.http.get(`/api/pipelines/${pipeline}/manifest`);
  }

  async listPipelines(): Promise<Array<{ id: PipelineType; name: string; description: string; status: string; stages: PipelineStage[] }>> {
    return this.http.get('/api/pipelines');
  }

  // ---- Real-time Progress ----
  subscribeToJob(jobId: string, listener: WSListener): () => void {
    return this.ws.subscribeToJob(jobId, listener);
  }

  onJobProgress(jobId: string, callback: (progress: number, stage: string, detail: string) => void): () => void {
    return this.subscribeToJob(jobId, (message) => {
      const data = message.data as { progress: number; stage: string; detail: string } | undefined;
      if (message.type === 'job_progress' && data) {
        callback(data.progress, data.stage, data.detail);
      } else if (message.type === 'job_stage_change' && data) {
        callback(data.progress, data.stage, data.detail);
      }
    });
  }

  onJobComplete(jobId: string, callback: (result: GenerationResult) => void): () => void {
    return this.subscribeToJob(jobId, (message) => {
      const data = message.data as { result: GenerationResult } | undefined;
      if (message.type === 'job_completed' && data) {
        callback(data.result);
      }
    });
  }

  onJobError(jobId: string, callback: (error: GenerationError) => void): () => void {
    return this.subscribeToJob(jobId, (message) => {
      const data = message.data as { error: GenerationError } | undefined;
      if (message.type === 'job_failed' && data) {
        callback(data.error);
      }
    });
  }

  onHumanApprovalRequired(jobId: string, callback: (stage: PipelineStage, artifact: Record<string, unknown>) => void): () => void {
    return this.subscribeToJob(jobId, (message) => {
      const data = message.data as { stage: PipelineStage; artifact: Record<string, unknown> } | undefined;
      if (message.type === 'human_approval_required' && data) {
        callback(data.stage, data.artifact);
      }
    });
  }

  // ---- Utility Methods ----
  async waitForJob<T extends GenerationJob>(
    jobId: string,
    getJob: (id: string) => Promise<T>,
    options: {
      pollInterval?: number;
      maxWait?: number;
      onProgress?: (progress: number, stage: string, detail: string) => void;
    } = {}
  ): Promise<T> {
    const { pollInterval = 2000, maxWait = 300000, onProgress } = options;
    const startTime = Date.now();

    // Try WebSocket first
    let wsCleanup: (() => void) | null = null;

    if (this.ws) {
      wsCleanup = this.onJobProgress(jobId, (progress, stage, detail) => {
        onProgress?.(progress, stage, detail);
      });
    }

    try {
      while (Date.now() - startTime < maxWait) {
        const job = await getJob(jobId);

        if (job.status === 'completed') {
          return job;
        }
        if (job.status === 'failed') {
          throw new PipelineError('unknown', job.current_stage || 'unknown', job.error?.message || 'Job failed', job.error?.details);
        }
        if (job.status === 'cancelled') {
          throw new OpenMontageError('Job was cancelled', 'JOB_CANCELLED');
        }

        onProgress?.(job.progress, job.current_stage || 'processing', job.current_detail || 'Working...');

        await new Promise(r => setTimeout(r, pollInterval));
      }

      throw new OpenMontageError('Job timed out', 'JOB_TIMEOUT', undefined, { jobId }, true);
    } finally {
      wsCleanup?.();
    }
  }

  async generateVideoAndWait(request: VideoGenerationRequest, options?: Parameters<typeof this.waitForJob>[2]): Promise<GenerationResult> {
    const job = await this.generateVideo(request);
    const completedJob = await this.waitForJob(job.id, this.getVideoJob.bind(this), options);
    return completedJob.result!;
  }

  async generateImageAndWait(request: ImageGenerationRequest, options?: Parameters<typeof this.waitForJob>[2]): Promise<GenerationResult> {
    const job = await this.generateImage(request);
    const completedJob = await this.waitForJob(job.id, this.getImageJob.bind(this), options);
    return completedJob.result!;
  }

  async executePipelineAndWait(request: PipelineExecutionRequest, options?: Parameters<typeof this.waitForJob>[2]): Promise<PipelineJob> {
    const job = await this.executePipeline(request);
    return this.waitForJob(job.id, this.getPipelineJob.bind(this), options);
  }

  // ---- Configuration ----
  updateApiKeys(keys: Partial<ApiKeys>): void {
    this.http.updateApiKeys(keys);
    this.config.apiKeys = { ...this.config.apiKeys, ...keys };
    this.emit('config:updated', { apiKeys: this.config.apiKeys });
  }

  getConfig(): Readonly<ClientConfig> {
    return { ...this.config };
  }

  // ---- Static Factory ----
  static create(config: Partial<ClientConfig> = {}): OpenMontageClient {
    return new OpenMontageClient({
      baseUrl: config.baseUrl || 'http://localhost:8000',
      wsUrl: config.wsUrl,
      apiKeys: config.apiKeys,
      timeout: config.timeout,
      maxRetries: config.maxRetries,
      retryDelay: config.retryDelay,
      debug: config.debug,
      headers: config.headers,
    });
  }

  static createFromEnv(): OpenMontageClient {
    // Handle both Vite (import.meta.env) and Node.js (process.env) environments
    let env: Record<string, string | undefined> = {};
    if (typeof import.meta !== 'undefined' && 'env' in import.meta) {
      env = (import.meta as unknown as { env: Record<string, string | undefined> }).env;
    } else if (typeof process !== 'undefined' && process.env) {
      env = process.env;
    }
    return new OpenMontageClient({
      baseUrl: env.VITE_OM_BASE_URL || 'http://localhost:8000',
      apiKeys: {
        FAL_KEY: env.VITE_FAL_KEY,
        HEYGEN_API_KEY: env.VITE_HEYGEN_API_KEY,
        GEMINI_API_KEY: env.VITE_GEMINI_API_KEY,
        OPENAI_API_KEY: env.VITE_OPENAI_API_KEY,
      },
      debug: env.VITE_OM_DEBUG === 'true',
    });
  }
}

// ============================================
// React Hooks (for React integration)
// ============================================

/**
 * React hook for using OpenMontage client
 * Usage:
 * ```tsx
 * const { client, generateVideo, generateImage, executePipeline } = useOpenMontage({
 *   baseUrl: 'http://localhost:8000',
 *   apiKeys: { FAL_KEY: '...' }
 * });
 * ```
 */
export function createOpenMontageHooks(client: OpenMontageClient) {
  return {
    // Video generation
    useGenerateVideo: () => {
      const generate = async (request: VideoGenerationRequest) => {
        return client.generateVideoAndWait(request);
      };
      return { generate };
    },

    // Image generation
    useGenerateImage: () => {
      const generate = async (request: ImageGenerationRequest) => {
        return client.generateImageAndWait(request);
      };
      return { generate };
    },

    // Pipeline execution
    useExecutePipeline: () => {
      const execute = async (request: PipelineExecutionRequest) => {
        return client.executePipelineAndWait(request);
      };
      return { execute };
    },

    // Job monitoring
    useJobProgress: (_jobId: string | null) => {
      // Implementation would use React state
      return { progress: 0, stage: '', detail: '' };
    },

    // Capabilities
    useCapabilities: () => {
      // Implementation would use React state + effect
      return { capabilities: [], loading: true };
    },
  };
}

// ============================================
// Default Export
// ============================================

export default OpenMontageClient;

// ============================================
// Usage Examples (as comments)
/*
// Basic usage
import { OpenMontageClient } from './openmontage-client';

const client = OpenMontageClient.create({
  baseUrl: 'http://localhost:8000',
  apiKeys: {
    FAL_KEY: 'fal_xxx...',
    HEYGEN_API_KEY: 'xxx...'
  },
  debug: true
});

// Connect and check health
await client.connect();
const health = await client.healthCheck();
console.log('Backend status:', health.backend.status);

// Generate video
const videoResult = await client.generateVideoAndWait({
  prompt: 'A cinematic drone shot over a misty coastal city at golden hour',
  model: 'seedance_2_0',
  aspect_ratio: '16:9',
  duration: 10,
  composition_runtime: 'remotion'
}, {
  onProgress: (progress, stage, detail) => {
    console.log(`${progress}% - ${stage}: ${detail}`);
  }
});

console.log('Video URL:', videoResult.primary_url);

// Generate image
const imageResult = await client.generateImageAndWait({
  prompt: 'A futuristic cyberpunk cityscape at night, neon signs, volumetric fog',
  model: 'flux_1_1_pro',
  aspect_ratio: '16:9',
  count: 2,
  quality: 'hd'
});

console.log('Image URLs:', imageResult.urls);

// Execute full pipeline
const pipelineResult = await client.executePipelineAndWait({
  pipeline: 'animated-explainer',
  brief: 'Create a 60-second explainer about how CRISPR gene editing works',
  options: {
    style_playbook: 'clean-professional',
    target_duration: 60,
    target_platform: 'youtube',
    composition_runtime: 'auto',
    quality_level: 'high'
  }
}, {
  onProgress: (progress, stage, detail) => {
    console.log(`Pipeline ${progress}% - ${stage}: ${detail}`);
  }
});

// Real-time updates via WebSocket
const unsubscribe = client.onJobProgress('job-123', (progress, stage, detail) => {
  updateProgressBar(progress);
  updateStatusText(`${stage}: ${detail}`);
});

// Clean up
unsubscribe();
await client.disconnect();
*/
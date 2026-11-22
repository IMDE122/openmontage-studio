#!/usr/bin/env python3
"""
OpenMontage Studio Backend
FastAPI server that bridges the web frontend to OpenMontage's tools, pipelines, and agents.
"""

import os
import sys
import asyncio
import json
import uuid
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field, asdict
from enum import Enum

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
import uvicorn

# Add OpenMontage to path
OM_PATH = Path(__file__).parent.parent / "OpenMontage"
sys.path.insert(0, str(OM_PATH))

# Try to import OpenMontage components
try:
    from tools.tool_registry import registry as om_registry
    from lib.pipeline_loader import load_pipeline_manifest
    from lib.checkpoint import init_project, get_checkpoint, write_checkpoint
    OM_AVAILABLE = True
except ImportError as e:
    print(f"Warning: OpenMontage components not available: {e}")
    OM_AVAILABLE = False

# ============================================
# Configuration
# ============================================

class Settings:
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = True
    CORS_ORIGINS: List[str] = ["*"]

    # API Keys (can be overridden by env)
    FAL_KEY: str = os.getenv("FAL_KEY", "")
    HEYGEN_API_KEY: str = os.getenv("HEYGEN_API_KEY", "")
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "") or os.getenv("GOOGLE_API_KEY", "")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")

settings = Settings()

# ============================================
# Data Models
# ============================================

class JobStatus(str, Enum):
    PENDING = "pending"
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class GenerationType(str, Enum):
    VIDEO = "video"
    IMAGE = "image"
    PIPELINE = "pipeline"
    TTS = "tts"
    MUSIC = "music"

class CompositionRuntime(str, Enum):
    REMOTION = "remotion"
    HYPERFRAMES = "hyperframes"
    FFMPEG = "ffmpeg"
    AUTO = "auto"

class PipelineType(str, Enum):
    ANIMATED_EXPLAINER = "animated-explainer"
    CINEMATIC = "cinematic"
    AVATAR_SPOKESPERSON = "avatar-spokesperson"
    ANIMATION = "animation"
    TALKING_HEAD = "talking-head"
    SCREEN_DEMO = "screen-demo"
    CLIP_FACTORY = "clip-factory"
    PODCAST_REPURPOSE = "podcast-repurpose"
    HYBRID = "hybrid"
    LOCALIZATION_DUB = "localization-dub"
    DOCUMENTARY_MONTAGE = "documentary-montage"
    CHARACTER_ANIMATION = "character-animation"
    FRAMEWORK_SMOKE = "framework-smoke"

# Request Models
class VideoGenerationRequest(BaseModel):
    prompt: str
    model: Optional[str] = "auto"
    aspect_ratio: str = "16:9"
    duration: int = 5
    reference_image_url: Optional[str] = None
    tail_image_url: Optional[str] = None
    composition_runtime: CompositionRuntime = CompositionRuntime.AUTO
    pipeline: Optional[PipelineType] = None
    config: Dict[str, Any] = Field(default_factory=dict)
    webhook_url: Optional[str] = None

class ImageGenerationRequest(BaseModel):
    prompt: str
    model: Optional[str] = "auto"
    aspect_ratio: str = "1:1"
    count: int = 1
    quality: str = "standard"
    reference_image_url: Optional[str] = None
    config: Dict[str, Any] = Field(default_factory=dict)
    webhook_url: Optional[str] = None

class TtsRequest(BaseModel):
    text: str
    voice: Optional[str] = None
    model: Optional[str] = None
    speed: float = 1.0
    format: str = "mp3"

class MusicGenerationRequest(BaseModel):
    prompt: str
    duration: Optional[int] = None
    genre: Optional[str] = None
    mood: Optional[str] = None
    bpm: Optional[int] = None
    instrumental: bool = False

class PipelineExecutionRequest(BaseModel):
    pipeline: PipelineType
    brief: str
    options: Dict[str, Any] = Field(default_factory=dict)
    webhook_url: Optional[str] = None

# Response Models
class GenerationResult(BaseModel):
    urls: List[str]
    primary_url: str
    thumbnail_url: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    pipeline_artifacts: Dict[str, Any] = Field(default_factory=dict)

class GenerationError(BaseModel):
    code: str
    message: str
    details: Dict[str, Any] = Field(default_factory=dict)
    retryable: bool = False

class GenerationJob(BaseModel):
    id: str
    type: GenerationType
    status: JobStatus
    progress: int = 0
    current_stage: Optional[str] = None
    current_detail: Optional[str] = None
    request: Dict[str, Any]
    result: Optional[GenerationResult] = None
    error: Optional[GenerationError] = None
    created_at: str
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    estimated_cost: Optional[float] = None
    actual_cost: Optional[float] = None

class PipelineStageResult(BaseModel):
    stage: str
    status: str
    artifact: Optional[Dict[str, Any]] = None
    artifacts_path: Optional[str] = None
    review_findings: List[Dict[str, Any]] = Field(default_factory=list)
    human_approval_required: bool = False

class PipelineJob(GenerationJob):
    stages: List[PipelineStageResult] = Field(default_factory=list)
    current_stage_index: int = 0
    project_id: Optional[str] = None
    project_path: Optional[str] = None

class HealthCheckResponse(BaseModel):
    status: str
    backend: Dict[str, Any]
    registry: Dict[str, Any]
    pipelines: Dict[str, Any]
    skills: Dict[str, Any]
    agents: Dict[str, Any]

# ============================================
# In-Memory Storage (replace with Redis/DB in production)
# ============================================

jobs_db: Dict[str, GenerationJob] = {}
pipeline_jobs_db: Dict[str, PipelineJob] = {}
ws_connections: Dict[str, List[WebSocket]] = {}

# ============================================
# Mock Provider Implementations
# ============================================

class MockProvider:
    """Mock provider for demo/testing without real API keys"""

    @staticmethod
    async def generate_video(request: VideoGenerationRequest) -> GenerationResult:
        await asyncio.sleep(2)  # Simulate generation time

        # Return sample video URLs
        sample_videos = [
            "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4",
            "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ElephantsDream.mp4",
            "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerBlazes.mp4",
        ]

        return GenerationResult(
            urls=[sample_videos[0]],
            primary_url=sample_videos[0],
            thumbnail_url="https://via.placeholder.com/640x360",
            metadata={
                "model": request.model or "seedance_2_0",
                "provider": "mock",
                "duration": request.duration,
                "aspect_ratio": request.aspect_ratio,
                "resolution": "1920x1080",
                "file_size": 1024 * 1024 * 50,
                "format": "mp4",
                "seed": 42,
            }
        )

    @staticmethod
    async def generate_image(request: ImageGenerationRequest) -> GenerationResult:
        await asyncio.sleep(1)

        images = []
        for i in range(request.count):
            seed = int(time.time() * 1000) + i
            images.append(f"https://picsum.photos/seed/{seed}/1024/1024")

        return GenerationResult(
            urls=images,
            primary_url=images[0],
            thumbnail_url=images[0] if images else None,
            metadata={
                "model": request.model or "flux_1_1_pro",
                "provider": "mock",
                "count": request.count,
                "quality": request.quality,
                "aspect_ratio": request.aspect_ratio,
                "resolution": "1024x1024",
                "format": "png",
            }
        )

    @staticmethod
    async def generate_tts(request: TtsRequest) -> GenerationResult:
        await asyncio.sleep(0.5)
        return GenerationResult(
            urls=["https://example.com/tts-output.mp3"],
            primary_url="https://example.com/tts-output.mp3",
            metadata={
                "voice": request.voice or "default",
                "model": request.model or "piper",
                "duration": len(request.text) * 0.05,
                "format": request.format,
            }
        )

    @staticmethod
    async def generate_music(request: MusicGenerationRequest) -> GenerationResult:
        await asyncio.sleep(1.5)
        return GenerationResult(
            urls=["https://example.com/music-output.mp3"],
            primary_url="https://example.com/music-output.mp3",
            metadata={
                "genre": request.genre or "ambient",
                "mood": request.mood or "calm",
                "bpm": request.bpm or 120,
                "duration": request.duration or 30,
                "format": "mp3",
            }
        )

# ============================================
# Pipeline Executor
# ============================================

class PipelineExecutor:
    """Executes OpenMontage pipelines"""

    PIPELINE_STAGES = {
        PipelineType.ANIMATED_EXPLAINER: ["research", "proposal", "script", "scene_plan", "assets", "edit", "compose", "publish"],
        PipelineType.CINEMATIC: ["idea", "script", "scene_plan", "assets", "edit", "compose", "publish"],
        PipelineType.AVATAR_SPOKESPERSON: ["idea", "script", "scene_plan", "assets", "edit", "compose", "publish"],
        PipelineType.ANIMATION: ["research", "proposal", "script", "scene_plan", "assets", "edit", "compose", "publish"],
        PipelineType.TALKING_HEAD: ["idea", "script", "scene_plan", "assets", "edit", "compose", "publish"],
        PipelineType.SCREEN_DEMO: ["idea", "script", "scene_plan", "assets", "edit", "compose", "publish"],
        PipelineType.CLIP_FACTORY: ["idea", "script", "scene_plan", "assets", "edit", "compose", "publish"],
        PipelineType.PODCAST_REPURPOSE: ["idea", "script", "scene_plan", "assets", "edit", "compose", "publish"],
        PipelineType.HYBRID: ["idea", "script", "scene_plan", "assets", "edit", "compose", "publish"],
        PipelineType.LOCALIZATION_DUB: ["idea", "script", "scene_plan", "assets", "edit", "compose", "publish"],
        PipelineType.DOCUMENTARY_MONTAGE: ["idea", "scene_plan", "assets", "edit", "compose"],
        PipelineType.CHARACTER_ANIMATION: ["idea", "script", "scene_plan", "assets", "edit", "compose", "publish"],
        PipelineType.FRAMEWORK_SMOKE: ["idea", "compose"],
    }

    HUMAN_APPROVAL_STAGES = {
        PipelineType.ANIMATED_EXPLAINER: ["proposal", "script", "scene_plan", "assets"],
        PipelineType.CINEMATIC: ["idea", "script", "scene_plan", "assets"],
        PipelineType.AVATAR_SPOKESPERSON: ["idea", "script", "scene_plan", "assets"],
        PipelineType.ANIMATION: ["proposal", "script", "scene_plan", "assets"],
        PipelineType.TALKING_HEAD: ["idea", "script", "scene_plan"],
        PipelineType.SCREEN_DEMO: ["idea", "script", "scene_plan"],
        PipelineType.CLIP_FACTORY: ["idea", "script", "scene_plan"],
        PipelineType.PODCAST_REPURPOSE: ["idea", "script", "scene_plan"],
        PipelineType.HYBRID: ["idea", "script", "scene_plan", "assets"],
        PipelineType.LOCALIZATION_DUB: ["idea", "script", "scene_plan"],
        PipelineType.DOCUMENTARY_MONTAGE: ["idea", "scene_plan", "assets", "edit"],
        PipelineType.CHARACTER_ANIMATION: ["idea", "script", "scene_plan", "assets"],
        PipelineType.FRAMEWORK_SMOKE: [],
    }

    @classmethod
    async def execute(cls, job: PipelineJob, notify_ws: callable) -> PipelineJob:
        stages = cls.PIPELINE_STAGES.get(job.request.get("pipeline"), [])
        approval_stages = cls.HUMAN_APPROVAL_STAGES.get(job.request.get("pipeline"), [])

        job.status = JobStatus.RUNNING
        job.started_at = datetime.utcnow().isoformat()
        job.stages = []

        for i, stage in enumerate(stages):
            job.current_stage_index = i
            job.current_stage = stage
            job.current_detail = f"Executing {stage} stage..."
            job.progress = int((i / len(stages)) * 100)

            await notify_ws(job.id, {
                "type": "job_stage_change",
                "job_id": job.id,
                "timestamp": datetime.utcnow().isoformat(),
                "data": {"progress": job.progress, "stage": stage, "detail": job.current_detail}
            })

            # Simulate stage work
            await asyncio.sleep(1.5)

            # Check for human approval
            if stage in approval_stages:
                job.current_detail = f"Waiting for human approval on {stage}..."
                stage_result = PipelineStageResult(
                    stage=stage,
                    status="awaiting_human",
                    human_approval_required=True,
                    artifact={"stage": stage, "output": f"Mock {stage} artifact"}
                )
                job.stages.append(stage_result)

                await notify_ws(job.id, {
                    "type": "human_approval_required",
                    "job_id": job.id,
                    "timestamp": datetime.utcnow().isoformat(),
                    "data": {"stage": stage, "artifact": stage_result.artifact}
                })

                # Wait for approval (in real implementation, this would be event-driven)
                # For demo, auto-approve after 3 seconds
                await asyncio.sleep(3)
                stage_result.status = "completed"
                stage_result.human_approval_required = False
            else:
                stage_result = PipelineStageResult(
                    stage=stage,
                    status="completed",
                    artifact={"stage": stage, "output": f"Mock {stage} artifact"}
                )
                job.stages.append(stage_result)

            # Update progress
            job.progress = int(((i + 1) / len(stages)) * 100)
            await notify_ws(job.id, {
                "type": "job_progress",
                "job_id": job.id,
                "timestamp": datetime.utcnow().isoformat(),
                "data": {"progress": job.progress, "stage": stage, "detail": f"Completed {stage}"}
            })

        # Finalize
        job.status = JobStatus.COMPLETED
        job.progress = 100
        job.completed_at = datetime.utcnow().isoformat()
        job.current_stage = "completed"
        job.current_detail = "Pipeline completed successfully"
        job.result = GenerationResult(
            urls=["https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4"],
            primary_url="https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4",
            metadata={"pipeline": job.request.get("pipeline"), "stages_completed": len(stages)}
        )

        await notify_ws(job.id, {
            "type": "job_completed",
            "job_id": job.id,
            "timestamp": datetime.utcnow().isoformat(),
            "data": {"result": job.result.model_dump()}
        })

        return job

# ============================================
# WebSocket Manager
# ============================================

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, job_id: Optional[str] = None):
        await websocket.accept()
        key = job_id or "global"
        if key not in self.active_connections:
            self.active_connections[key] = []
        self.active_connections[key].append(websocket)

    def disconnect(self, websocket: WebSocket, job_id: Optional[str] = None):
        key = job_id or "global"
        if key in self.active_connections:
            self.active_connections[key].remove(websocket)
            if not self.active_connections[key]:
                del self.active_connections[key]

    async def send_personal_message(self, message: dict, websocket: WebSocket):
        await websocket.send_json(message)

    async def broadcast_to_job(self, job_id: str, message: dict):
        if job_id in self.active_connections:
            for ws in self.active_connections[job_id]:
                try:
                    await ws.send_json(message)
                except:
                    pass

    async def broadcast_global(self, message: dict):
        for connections in self.active_connections.values():
            for ws in connections:
                try:
                    await ws.send_json(message)
                except:
                    pass

manager = ConnectionManager()

async def notify_job(job_id: str, message: dict):
    await manager.broadcast_to_job(job_id, message)

# ============================================
# Background Job Processor
# ============================================

async def process_video_job(job_id: str):
    job = jobs_db.get(job_id)
    if not job:
        return

    job.status = JobStatus.RUNNING
    job.started_at = datetime.utcnow().isoformat()
    job.progress = 10
    job.current_stage = "Initializing"
    job.current_detail = "Preparing video generation..."
    await notify_job(job_id, {"type": "job_progress", "job_id": job_id, "data": job.model_dump()})

    try:
        # Simulate stages
        stages = [
            ("Research", "Gathering information", 20),
            ("Script", "Writing narrative", 35),
            ("Scene Plan", "Planning visuals", 50),
            ("Asset Generation", f"Generating with {job.request.get('model', 'auto')}", 70),
            ("Composition", f"Rendering with {job.request.get('composition_runtime', 'auto')}", 85),
            ("Finalizing", "Encoding output", 95),
        ]

        for stage_name, detail, progress in stages:
            job.current_stage = stage_name
            job.current_detail = detail
            job.progress = progress
            await notify_job(job_id, {"type": "job_progress", "job_id": job_id, "data": {"progress": progress, "stage": stage_name, "detail": detail}})
            await asyncio.sleep(1)

        # Generate result
        result = await MockProvider.generate_video(VideoGenerationRequest(**job.request))
        job.status = JobStatus.COMPLETED
        job.progress = 100
        job.completed_at = datetime.utcnow().isoformat()
        job.current_stage = "completed"
        job.current_detail = "Video generated successfully"
        job.result = result
        job.actual_cost = 0.75

        await notify_job(job_id, {"type": "job_completed", "job_id": job_id, "data": {"result": result.model_dump()}})

    except Exception as e:
        job.status = JobStatus.FAILED
        job.error = GenerationError(code="GENERATION_FAILED", message=str(e), retryable=True)
        job.completed_at = datetime.utcnow().isoformat()
        await notify_job(job_id, {"type": "job_failed", "job_id": job_id, "data": {"error": job.error.model_dump()}})

async def process_image_job(job_id: str):
    job = jobs_db.get(job_id)
    if not job:
        return

    job.status = JobStatus.RUNNING
    job.started_at = datetime.utcnow().isoformat()
    job.progress = 15
    job.current_stage = "Initializing"
    job.current_detail = "Preparing image generation..."
    await notify_job(job_id, {"type": "job_progress", "job_id": job_id, "data": job.model_dump()})

    try:
        stages = [
            ("Prompt Enhancement", "Optimizing prompt", 30),
            ("Generation", f"Generating with {job.request.get('model', 'auto')}", 70),
            ("Post-processing", "Applying enhancements", 90),
        ]

        for stage_name, detail, progress in stages:
            job.current_stage = stage_name
            job.current_detail = detail
            job.progress = progress
            await notify_job(job_id, {"type": "job_progress", "job_id": job_id, "data": {"progress": progress, "stage": stage_name, "detail": detail}})
            await asyncio.sleep(0.8)

        result = await MockProvider.generate_image(ImageGenerationRequest(**job.request))
        job.status = JobStatus.COMPLETED
        job.progress = 100
        job.completed_at = datetime.utcnow().isoformat()
        job.current_stage = "completed"
        job.current_detail = "Images generated successfully"
        job.result = result
        job.actual_cost = 0.05 * job.request.get("count", 1)

        await notify_job(job_id, {"type": "job_completed", "job_id": job_id, "data": {"result": result.model_dump()}})

    except Exception as e:
        job.status = JobStatus.FAILED
        job.error = GenerationError(code="GENERATION_FAILED", message=str(e), retryable=True)
        job.completed_at = datetime.utcnow().isoformat()
        await notify_job(job_id, {"type": "job_failed", "job_id": job_id, "data": {"error": job.error.model_dump()}})

async def process_pipeline_job(job_id: str):
    job = pipeline_jobs_db.get(job_id)
    if not job:
        return

    await PipelineExecutor.execute(job, notify_job)

# ============================================
# FastAPI Application
# ============================================

app = FastAPI(
    title="OpenMontage Studio API",
    description="Backend API for OpenMontage Studio - AI Video & Image Generation",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================
# API Routes
# ============================================

@app.get("/health", response_model=HealthCheckResponse)
async def health_check():
    """Health check endpoint"""

    # Check OpenMontage availability
    om_status = "unavailable"
    registry_info = {"tools_discovered": 0, "capabilities_configured": 0, "composition_runtimes": {"ffmpeg": False, "remotion": False, "hyperframes": False}}
    pipelines_info = {"available": 0, "loaded": []}
    skills_info = {"loaded": 0, "categories": []}
    agents_info = {"active": 0, "available": []}

    if OM_AVAILABLE:
        try:
            om_registry.discover()
            om_status = "available"

            # Get registry info
            capabilities = om_registry.capability_catalog()
            registry_info = {
                "tools_discovered": len(om_registry._tools),
                "capabilities_configured": sum(1 for c in capabilities if c.get("configured", 0) > 0),
                "composition_runtimes": {
                    "ffmpeg": True,  # Always available
                    "remotion": Path(OM_PATH / "remotion-composer").exists(),
                    "hyperframes": False,  # Would check for Node.js >= 22
                }
            }

            # Get pipelines
            pipeline_dir = OM_PATH / "pipeline_defs"
            pipeline_files = list(pipeline_dir.glob("*.yaml")) if pipeline_dir.exists() else []
            pipelines_info = {
                "available": len(pipeline_files),
                "loaded": [f.stem for f in pipeline_files]
            }

            # Get skills
            skills_dir = OM_PATH / "skills"
            skill_files = list(skills_dir.rglob("*.md")) if skills_dir.exists() else []
            skills_info = {
                "loaded": len(skill_files),
                "categories": ["core", "creative", "meta", "pipelines"]
            }

            agents_info = {
                "active": 0,
                "available": ["orchestrator", "research-director", "proposal-director", "script-director", "scene-director", "asset-director", "edit-director", "compose-director"]
            }
        except Exception as e:
            print(f"Error getting OM info: {e}")
            om_status = "error"

    return HealthCheckResponse(
        status="healthy" if om_status == "available" else "degraded",
        backend={"status": "running", "version": "1.0.0", "uptime": time.time()},
        registry=registry_info,
        pipelines=pipelines_info,
        skills=skills_info,
        agents=agents_info,
    )

@app.get("/api/registry")
async def get_registry():
    """Get tool registry information"""
    if not OM_AVAILABLE:
        return JSONResponse(
            status_code=503,
            content={"error": "OpenMontage not available", "capabilities": [], "providers": {}, "composition_runtimes": {}, "setup_offers": [], "runtime_warnings": []}
        )

    try:
        om_registry.discover()

        # Build capabilities list
        capabilities = []
        for cap_name, cap_info in om_registry.capability_catalog().items():
            tools = om_registry.get_by_capability(cap_name)
            capabilities.append({
                "capability": cap_name,
                "configured": cap_info.get("configured", 0),
                "total": cap_info.get("total", 0),
                "providers": cap_info.get("providers", []),
                "tools": [
                    {
                        "name": t.__class__.__name__,
                        "capability": t.capability,
                        "provider": t.provider,
                        "status": t.status.value if hasattr(t.status, 'value') else str(t.status),
                        "runtime": t.runtime.value if hasattr(t.runtime, 'value') else str(t.runtime),
                        "cost_per_unit": getattr(t, 'cost_per_unit', None),
                        "cost_unit": getattr(t, 'cost_unit', None),
                        "best_for": getattr(t, 'best_for', []),
                        "install_instructions": getattr(t, 'install_instructions', None),
                        "dependencies": getattr(t, 'dependencies', []),
                        "agent_skills": getattr(t, 'agent_skills', []),
                    }
                    for t in tools
                ]
            })

        # Build providers dict
        providers = {}
        for provider_name, tools in om_registry.provider_catalog().items():
            providers[provider_name] = [
                {
                    "name": t.__class__.__name__,
                    "capability": t.capability,
                    "provider": t.provider,
                    "status": t.status.value if hasattr(t.status, 'value') else str(t.status),
                    "runtime": t.runtime.value if hasattr(t.runtime, 'value') else str(t.runtime),
                }
                for t in tools
            ]

        # Get composition runtimes
        video_compose = om_registry._tools.get("video_compose")
        if video_compose:
            info = video_compose.get_info()
            composition_runtimes = {
                "ffmpeg": True,
                "remotion": info.get("remotion_note") is not None,
                "hyperframes": info.get("hyperframes_note") is not None,
            }
        else:
            composition_runtimes = {"ffmpeg": True, "remotion": False, "hyperframes": False}

        # Get setup offers
        setup_offers = []
        for tool_name, tool in om_registry._tools.items():
            if tool.status.value == "UNAVAILABLE" and hasattr(tool, 'install_instructions') and tool.install_instructions:
                setup_offers.append({
                    "tool": tool_name,
                    "capability": tool.capability,
                    "install_instructions": tool.install_instructions,
                    "dependencies": getattr(tool, 'dependencies', []),
                })

        return {
            "capabilities": capabilities,
            "providers": providers,
            "composition_runtimes": composition_runtimes,
            "setup_offers": setup_offers[:10],  # Limit
            "runtime_warnings": [],
        }
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": str(e), "capabilities": [], "providers": {}, "composition_runtimes": {}, "setup_offers": [], "runtime_warnings": [str(e)]}
        )

@app.post("/api/generate/video", response_model=GenerationJob)
async def generate_video(request: VideoGenerationRequest, background_tasks: BackgroundTasks):
    """Start video generation job"""
    job_id = str(uuid.uuid4())
    job = GenerationJob(
        id=job_id,
        type=GenerationType.VIDEO,
        status=JobStatus.PENDING,
        progress=0,
        request=request.model_dump(),
        created_at=datetime.utcnow().isoformat(),
        estimated_cost=0.75,
    )
    jobs_db[job_id] = job

    background_tasks.add_task(process_video_job, job_id)

    return job

@app.post("/api/generate/image", response_model=GenerationJob)
async def generate_image(request: ImageGenerationRequest, background_tasks: BackgroundTasks):
    """Start image generation job"""
    job_id = str(uuid.uuid4())
    job = GenerationJob(
        id=job_id,
        type=GenerationType.IMAGE,
        status=JobStatus.PENDING,
        progress=0,
        request=request.model_dump(),
        created_at=datetime.utcnow().isoformat(),
        estimated_cost=0.05 * request.count,
    )
    jobs_db[job_id] = job

    background_tasks.add_task(process_image_job, job_id)

    return job

@app.post("/api/generate/tts", response_model=GenerationJob)
async def generate_tts(request: TtsRequest, background_tasks: BackgroundTasks):
    """Start TTS generation job"""
    job_id = str(uuid.uuid4())
    job = GenerationJob(
        id=job_id,
        type=GenerationType.TTS,
        status=JobStatus.PENDING,
        progress=0,
        request=request.model_dump(),
        created_at=datetime.utcnow().isoformat(),
        estimated_cost=0.01,
    )
    jobs_db[job_id] = job

    async def process():
        job.status = JobStatus.RUNNING
        job.started_at = datetime.utcnow().isoformat()
        job.progress = 50
        await notify_job(job_id, {"type": "job_progress", "job_id": job_id, "data": {"progress": 50, "stage": "Generating", "detail": "Synthesizing speech..."}})
        await asyncio.sleep(0.5)
        result = await MockProvider.generate_tts(request)
        job.status = JobStatus.COMPLETED
        job.progress = 100
        job.completed_at = datetime.utcnow().isoformat()
        job.result = result
        job.actual_cost = 0.01
        await notify_job(job_id, {"type": "job_completed", "job_id": job_id, "data": {"result": result.model_dump()}})

    background_tasks.add_task(process)
    return job

@app.post("/api/generate/music", response_model=GenerationJob)
async def generate_music(request: MusicGenerationRequest, background_tasks: BackgroundTasks):
    """Start music generation job"""
    job_id = str(uuid.uuid4())
    job = GenerationJob(
        id=job_id,
        type=GenerationType.MUSIC,
        status=JobStatus.PENDING,
        progress=0,
        request=request.model_dump(),
        created_at=datetime.utcnow().isoformat(),
        estimated_cost=0.10,
    )
    jobs_db[job_id] = job

    async def process():
        job.status = JobStatus.RUNNING
        job.started_at = datetime.utcnow().isoformat()
        job.progress = 30
        await notify_job(job_id, {"type": "job_progress", "job_id": job_id, "data": {"progress": 30, "stage": "Composing", "detail": "Generating music..."}})
        await asyncio.sleep(1.5)
        result = await MockProvider.generate_music(request)
        job.status = JobStatus.COMPLETED
        job.progress = 100
        job.completed_at = datetime.utcnow().isoformat()
        job.result = result
        job.actual_cost = 0.10
        await notify_job(job_id, {"type": "job_completed", "job_id": job_id, "data": {"result": result.model_dump()}})

    background_tasks.add_task(process)
    return job

@app.get("/api/jobs/video/{job_id}", response_model=GenerationJob)
async def get_video_job(job_id: str):
    """Get video job status"""
    job = jobs_db.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job

@app.get("/api/jobs/image/{job_id}", response_model=GenerationJob)
async def get_image_job(job_id: str):
    """Get image job status"""
    job = jobs_db.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job

@app.post("/api/jobs/video/{job_id}/cancel")
async def cancel_video_job(job_id: str):
    """Cancel video job"""
    job = jobs_db.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    if job.status in [JobStatus.COMPLETED, JobStatus.FAILED, JobStatus.CANCELLED]:
        raise HTTPException(status_code=400, detail="Job already finished")
    job.status = JobStatus.CANCELLED
    job.completed_at = datetime.utcnow().isoformat()
    await notify_job(job_id, {"type": "job_cancelled", "job_id": job_id, "data": {}})
    return {"status": "cancelled"}

@app.post("/api/jobs/image/{job_id}/cancel")
async def cancel_image_job(job_id: str):
    """Cancel image job"""
    job = jobs_db.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    if job.status in [JobStatus.COMPLETED, JobStatus.FAILED, JobStatus.CANCELLED]:
        raise HTTPException(status_code=400, detail="Job already finished")
    job.status = JobStatus.CANCELLED
    job.completed_at = datetime.utcnow().isoformat()
    await notify_job(job_id, {"type": "job_cancelled", "job_id": job_id, "data": {}})
    return {"status": "cancelled"}

@app.post("/api/pipelines/execute", response_model=PipelineJob)
async def execute_pipeline(request: PipelineExecutionRequest, background_tasks: BackgroundTasks):
    """Execute a pipeline"""
    job_id = str(uuid.uuid4())

    # Initialize project directory
    project_id = f"project-{job_id[:8]}"
    project_path = None
    if OM_AVAILABLE:
        try:
            from lib.checkpoint import init_project
            project_path = init_project(project_id, title=request.brief[:50], pipeline_type=request.pipeline.value)
        except Exception as e:
            print(f"Failed to init project: {e}")

    job = PipelineJob(
        id=job_id,
        type=GenerationType.PIPELINE,
        status=JobStatus.PENDING,
        progress=0,
        request=request.model_dump(),
        created_at=datetime.utcnow().isoformat(),
        estimated_cost=2.0,
        project_id=project_id,
        project_path=project_path,
    )
    pipeline_jobs_db[job_id] = job

    background_tasks.add_task(process_pipeline_job, job_id)

    return job

@app.get("/api/pipelines/jobs/{job_id}", response_model=PipelineJob)
async def get_pipeline_job(job_id: str):
    """Get pipeline job status"""
    job = pipeline_jobs_db.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Pipeline job not found")
    return job

@app.post("/api/pipelines/jobs/{job_id}/approve")
async def approve_pipeline_stage(job_id: str, approval: Dict[str, Any]):
    """Approve or reject a pipeline stage requiring human approval"""
    job = pipeline_jobs_db.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Pipeline job not found")

    stage = approval.get("stage")
    approved = approval.get("approved", True)
    feedback = approval.get("feedback")

    # Find the stage
    for s in job.stages:
        if s.stage == stage and s.human_approval_required:
            s.human_approval_required = False
            s.status = "completed" if approved else "failed"
            if feedback:
                s.artifact = s.artifact or {}
                s.artifact["human_feedback"] = feedback
            break

    await notify_job(job_id, {"type": "pipeline_stage_approved", "job_id": job_id, "data": {"stage": stage, "approved": approved}})
    return {"status": "approved" if approved else "rejected"}

@app.post("/api/pipelines/jobs/{job_id}/cancel")
async def cancel_pipeline_job(job_id: str):
    """Cancel pipeline job"""
    job = pipeline_jobs_db.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Pipeline job not found")
    if job.status in [JobStatus.COMPLETED, JobStatus.FAILED, JobStatus.CANCELLED]:
        raise HTTPException(status_code=400, detail="Job already finished")
    job.status = JobStatus.CANCELLED
    job.completed_at = datetime.utcnow().isoformat()
    await notify_job(job_id, {"type": "job_cancelled", "job_id": job_id, "data": {}})
    return {"status": "cancelled"}

@app.get("/api/pipelines")
async def list_pipelines():
    """List available pipelines"""
    pipelines = []
    for p in PipelineType:
        stages = PipelineExecutor.PIPELINE_STAGES.get(p, [])
        approval = PipelineExecutor.HUMAN_APPROVAL_STAGES.get(p, [])
        pipelines.append({
            "id": p.value,
            "name": p.value.replace("-", " ").title(),
            "description": f"{len(stages)}-stage pipeline",
            "status": "production" if p in [PipelineType.ANIMATED_EXPLAINER, PipelineType.CINEMATIC, PipelineType.AVATAR_SPOKESPERSON, PipelineType.ANIMATION, PipelineType.SCREEN_DEMO, PipelineType.HYBRID] else "beta",
            "stages": stages,
            "human_approval_stages": approval,
        })
    return pipelines

@app.get("/api/pipelines/{pipeline_id}/manifest")
async def get_pipeline_manifest(pipeline_id: str):
    """Get pipeline manifest"""
    if not OM_AVAILABLE:
        raise HTTPException(status_code=503, detail="OpenMontage not available")

    try:
        manifest = load_pipeline_manifest(pipeline_id)
        return manifest
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Pipeline not found: {e}")

# ============================================
# WebSocket Endpoint
# ============================================

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_json()
            # Handle incoming messages (subscriptions, etc.)
            if data.get("type") == "subscribe_job":
                job_id = data.get("job_id")
                if job_id:
                    await manager.connect(websocket, job_id)
                    await websocket.send_json({"type": "subscribed", "job_id": job_id})
            elif data.get("type") == "unsubscribe_job":
                job_id = data.get("job_id")
                if job_id:
                    manager.disconnect(websocket, job_id)
                    await websocket.send_json({"type": "unsubscribed", "job_id": job_id})
            elif data.get("type") == "ping":
                await websocket.send_json({"type": "pong"})
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        print(f"WebSocket error: {e}")
        manager.disconnect(websocket)

# ============================================
# Static Files (for serving frontend)
# ============================================

from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

# Serve frontend
frontend_path = Path(__file__).parent
if (frontend_path / "index.html").exists():
    app.mount("/assets", StaticFiles(directory=frontend_path), name="assets")

    @app.get("/")
    async def serve_frontend():
        return FileResponse(frontend_path / "index.html")

    @app.get("/{path:path}")
    async def serve_spa(path: str):
        file_path = frontend_path / path
        if file_path.exists() and file_path.is_file():
            return FileResponse(file_path)
        return FileResponse(frontend_path / "index.html")

# ============================================
# Main Entry Point
# ============================================

if __name__ == "__main__":
    print("=" * 60)
    print("OpenMontage Studio Backend")
    print("=" * 60)
    print(f"OpenMontage Available: {OM_AVAILABLE}")
    if OM_AVAILABLE:
        print(f"OpenMontage Path: {OM_PATH}")
    print(f"Server: http://{settings.HOST}:{settings.PORT}")
    print(f"WebSocket: ws://{settings.HOST}:{settings.PORT}/ws")
    print(f"API Docs: http://{settings.HOST}:{settings.PORT}/docs")
    print("=" * 60)

    uvicorn.run(
        "backend:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info" if not settings.DEBUG else "debug",
    )
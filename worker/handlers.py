from app.services.dubbing_service import DubbingService


async def handle_dubbing_job(job_id: str) -> None:
    await DubbingService.execute_dubbing_pipeline(job_id)




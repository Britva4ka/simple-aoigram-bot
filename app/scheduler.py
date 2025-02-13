from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from config import JOB_STORES_URL, timezone

job_stores = {"default": SQLAlchemyJobStore(url=JOB_STORES_URL)}
scheduler = AsyncIOScheduler(timezone=timezone, jobstores=job_stores)


async def setup_scheduler():
    # Here we can add regular jobs
    scheduler.start()

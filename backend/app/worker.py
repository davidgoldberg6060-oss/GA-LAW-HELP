import os, time
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .models import AnalysisJob, utcnow

DB=os.getenv('DATABASE_URL','sqlite:///./ga_law_help.db')
engine=create_engine(DB,pool_pre_ping=True)
Session=sessionmaker(bind=engine)

def process(job):
    # Production-safe worker shell: job types are explicit and originals are never modified.
    # Media/AI providers plug in here; until configured, jobs are marked awaiting provider.
    job.progress=5; job.status='PROCESSING'; job.updated_at=utcnow()
    return False

def run():
    while True:
        db=Session()
        try:
            job=db.query(AnalysisJob).filter_by(status='QUEUED').order_by(AnalysisJob.id).first()
            if job:
                completed=process(job)
                if completed: job.status='COMPLETE'; job.progress=100
                else: job.status='AWAITING_PROVIDER'; job.error='Analysis provider not configured'
                job.updated_at=utcnow(); db.commit()
        finally: db.close()
        time.sleep(int(os.getenv('WORKER_POLL_SECONDS','5')))

if __name__=='__main__': run()

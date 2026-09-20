import os, time
from .models import AnalysisJob, utcnow
from .database import SessionLocal

def validate_worker_config():
    if os.getenv('ENVIRONMENT','development').lower() != 'production':
        return
    database_url=os.getenv('DATABASE_URL','')
    if not database_url or database_url.startswith('sqlite') or 'sslmode=' not in database_url:
        raise RuntimeError('Worker requires a production PostgreSQL DATABASE_URL with SSL')
    if os.getenv('STORAGE_BACKEND','local').lower() != 's3':
        raise RuntimeError('Worker requires STORAGE_BACKEND=s3')
    required=('S3_BUCKET','S3_ENDPOINT_URL','AWS_REGION','AWS_ACCESS_KEY_ID','AWS_SECRET_ACCESS_KEY')
    missing=[name for name in required if not os.getenv(name)]
    if missing:
        raise RuntimeError('Worker S3 configuration is incomplete: '+', '.join(missing))

def process(job):
    # Production-safe worker shell: job types are explicit and originals are never modified.
    # Media/AI providers plug in here; until configured, jobs are marked awaiting provider.
    job.progress=5; job.status='PROCESSING'; job.updated_at=utcnow()
    return False

def run():
    validate_worker_config()
    while True:
        db=SessionLocal()
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

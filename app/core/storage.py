import boto3, uuid
from app.config import get_settings

settings = get_settings()

def get_s3_client():
    return boto3.client("s3", endpoint_url=settings.S3_ENDPOINT,
        aws_access_key_id=settings.S3_ACCESS_KEY,
        aws_secret_access_key=settings.S3_SECRET_KEY, region_name=settings.S3_REGION)

def generate_upload_url(content_type: str = "video/mp4", prefix: str = "posts") -> dict:
    s3 = get_s3_client()
    key = f"{prefix}/{uuid.uuid4()}.mp4"
    url = s3.generate_presigned_url("put_object",
        Params={"Bucket": settings.S3_BUCKET, "Key": key, "ContentType": content_type}, ExpiresIn=600)
    return {"upload_url": url, "key": key}

def generate_playback_url(key: str) -> str:
    s3 = get_s3_client()
    return s3.generate_presigned_url("get_object",
        Params={"Bucket": settings.S3_BUCKET, "Key": key}, ExpiresIn=3600)

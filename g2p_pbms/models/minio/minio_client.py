from odoo import models
import base64
import minio
import io
import uuid
from datetime import timedelta


class MinioClient(models.AbstractModel):
    _name = 'minio.client'
    _description = 'MinIO Client Helper'

    def _detect_content_type_from_content(self, file_bytes):
        """
        Detect content type from file content using magic numbers
        """
        if not file_bytes:
            return "application/octet-stream"
        
        # Check for common file signatures
        if file_bytes.startswith(b'\xff\xd8\xff'):
            return "image/jpeg"
        elif file_bytes.startswith(b'\x89PNG\r\n\x1a\n'):
            return "image/png"
        elif file_bytes.startswith(b'GIF87a') or file_bytes.startswith(b'GIF89a'):
            return "image/gif"
        elif file_bytes.startswith(b'%PDF'):
            return "application/pdf"
        elif file_bytes.startswith(b'PK\x03\x04'):
            return "application/zip"
        elif file_bytes.startswith(b'\x1f\x8b'):
            return "application/gzip"
        elif file_bytes.startswith(b'<!DOCTYPE html') or file_bytes.startswith(b'<html'):
            return "text/html"
        elif file_bytes.startswith(b'<?xml'):
            return "application/xml"
        elif file_bytes.startswith(b'{') or file_bytes.startswith(b'['):
            return "application/json"
        elif file_bytes.startswith(b'\x00\x00\x01\x00'):
            return "image/x-icon"
        else:
            return "application/octet-stream"

    def _get_minio_connection(self):
        minio_endpoint = self.env['ir.config_parameter'].sudo().get_param('minio.endpoint')
        minio_access_key = self.env['ir.config_parameter'].sudo().get_param('minio.access_key')
        minio_secret_key = self.env['ir.config_parameter'].sudo().get_param('minio.secret_key')
        minio_bucket = self.env['ir.config_parameter'].sudo().get_param('minio.bucket')
        
        # Check if all required parameters are configured
        if not minio_endpoint:
            raise ValueError("MinIO endpoint is not configured. Please set it in Settings > G2P PBMS Settings.")
        if not minio_access_key:
            raise ValueError("MinIO access key is not configured. Please set it in Settings > G2P PBMS Settings.")
        if not minio_secret_key:
            raise ValueError("MinIO secret key is not configured. Please set it in Settings > G2P PBMS Settings.")
        if not minio_bucket:
            raise ValueError("MinIO bucket is not configured. Please set it in Settings > G2P PBMS Settings.")
            
        client = minio.Minio(
            minio_endpoint,
            access_key=minio_access_key,
            secret_key=minio_secret_key,
            secure=False
        )
        return client, minio_bucket

    def upload_file(self, file_content, filename=None, content_type=None):
        try:
            client, bucket = self._get_minio_connection()
            file_bytes = base64.b64decode(file_content)
            file_stream = io.BytesIO(file_bytes)
            file_size = len(file_bytes)
            object_name = f"{uuid.uuid4()}"
            
            # If no content type provided, try to detect from filename first, then from content
            if not content_type:
                if filename:
                    import mimetypes
                    content_type, _ = mimetypes.guess_type(filename)
                
                # If still no content type, detect from file content
                if not content_type:
                    content_type = self._detect_content_type_from_content(file_bytes)
            
            # Default to application/octet-stream if still no content type
            if not content_type:
                content_type = "application/octet-stream"
            
            client.put_object(
                bucket,
                object_name,
                file_stream,
                file_size,
                content_type=content_type
            )
            return object_name
        except Exception as e:
            raise ValueError(f"Failed to upload file to MinIO: {str(e)}")

    def get_file_preview_url(self, minio_file_id, content_type=None):
        """
        Returns a presigned URL for previewing the file stored in MinIO.
        """
        try:
            client, bucket = self._get_minio_connection()
            # The expires parameter must be a timedelta, not an int
            # Add response headers to force inline display instead of download
            response_headers = {
                'response-content-disposition': 'inline'
            }
            
            # Use provided content type or default to application/octet-stream
            if content_type:
                response_headers['response-content-type'] = content_type
            else:
                response_headers['response-content-type'] = 'application/octet-stream'
            
            url = client.presigned_get_object(
                bucket,
                minio_file_id,
                expires=timedelta(seconds=600),
                response_headers=response_headers
            )
            return url
        except Exception as e:
            raise ValueError(f"Failed to generate preview URL: {str(e)}")

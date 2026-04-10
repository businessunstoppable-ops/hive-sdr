"""Error handling middleware for the dashboard"""

from fastapi import Request
from fastapi.responses import HTMLResponse
from starlette.middleware.base import BaseHTTPMiddleware
import traceback
from datetime import datetime

class ErrorHandlerMiddleware(BaseHTTPMiddleware):
    """Catches all exceptions and returns friendly error pages"""
    
    async def dispatch(self, request: Request, call_next):
        try:
            response = await call_next(request)
            return response
        except Exception as e:
            # Log the error
            error_details = {
                "timestamp": datetime.now().isoformat(),
                "path": request.url.path,
                "error": str(e),
                "traceback": traceback.format_exc()
            }
            
            # Print to console for debugging
            print(f"\n{'='*60}")
            print(f"ERROR: {error_details['path']}")
            print(f"Message: {error_details['error']}")
            print(f"{'='*60}\n")
            
            # Return friendly error page
            error_html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>HIVE-SDR - Error</title>
                <style>
                    body {{
                        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                        background: linear-gradient(135deg, #2B1A0F 0%, #442D1C 50%, #5C3A1E 100%);
                        color: #E8D1A7;
                        min-height: 100vh;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        margin: 0;
                        padding: 20px;
                    }}
                    .error-container {{
                        background: rgba(0,0,0,0.4);
                        border-radius: 15px;
                        padding: 40px;
                        text-align: center;
                        max-width: 500px;
                        border: 1px solid #9D9167;
                    }}
                    h1 {{ color: #E8D1A7; margin-bottom: 20px; }}
                    p {{ color: #C4B89A; margin-bottom: 20px; }}
                    .btn {{
                        background: linear-gradient(135deg, #743014, #442D1C);
                        color: #E8D1A7;
                        border: 1px solid #9D9167;
                        padding: 12px 30px;
                        border-radius: 10px;
                        text-decoration: none;
                        display: inline-block;
                    }}
                    .btn:hover {{ background: #9D9167; color: #2B1A0F; }}
                </style>
            </head>
            <body>
                <div class="error-container">
                    <h1>⚠️ Something Went Wrong</h1>
                    <p>An unexpected error occurred. The team has been notified.</p>
                    <p style="font-size: 12px; font-family: monospace;">{str(e)[:100]}</p>
                    <a href="/" class="btn">Return to Dashboard</a>
                </div>
            </body>
            </html>
            """
            return HTMLResponse(content=error_html, status_code=500)

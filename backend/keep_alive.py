# backend/keep_alive.py

import asyncio
import aiohttp
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class RailwayKeepAlive:
    def __init__(self, url: str, interval_minutes: int = 30):
        """
        Keep-Alive Service für Railway
        
        Args:
            url: Railway App URL
            interval_minutes: Ping Intervall in Minuten
        """
        self.url = url.rstrip('/')
        self.interval = interval_minutes * 60  # Convert to seconds
        self.running = False
        
    async def ping_self(self):
        """Ping the own Railway service to keep it alive"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.url}/health", timeout=10) as response:
                    if response.status == 200:
                        logger.info(f"✅ Keep-alive ping successful: {response.status}")
                        return True
                    else:
                        logger.warning(f"⚠️ Keep-alive ping warning: {response.status}")
                        return False
        except Exception as e:
            logger.error(f"❌ Keep-alive ping failed: {e}")
            return False
    
    async def start_keep_alive(self):
        """Start the keep-alive loop"""
        self.running = True
        logger.info(f"🚀 Starting keep-alive service (ping every {self.interval//60} minutes)")
        
        while self.running:
            try:
                await self.ping_self()
                await asyncio.sleep(self.interval)
            except Exception as e:
                logger.error(f"Keep-alive loop error: {e}")
                await asyncio.sleep(60)  # Wait 1 minute before retry
    
    def stop_keep_alive(self):
        """Stop the keep-alive service"""
        self.running = False
        logger.info("🛑 Keep-alive service stopped")

# Global instance
keep_alive_service = None

def get_keep_alive_service():
    """Get or create keep-alive service instance"""
    global keep_alive_service
    if keep_alive_service is None:
        # Use Railway URL or localhost for development
        import os
        railway_url = os.getenv("RAILWAY_PUBLIC_DOMAIN")
        if railway_url:
            url = f"https://{railway_url}"
        else:
            url = "http://localhost:8000"
        
        keep_alive_service = RailwayKeepAlive(url, interval_minutes=30)
    
    return keep_alive_service

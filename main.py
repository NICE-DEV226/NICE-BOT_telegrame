"""
NICE-BOT - FastAPI Webhook Server
Main entry point for the Telegram bot with FastAPI webhook handling
"""

import os
import logging
from datetime import datetime
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, HTTPException
from telegram import Update
from telegram.ext import Application
import uvicorn

from bot import setup_bot, setup_menu_button
from db import init_database

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Global variables
bot_application = None
start_time = datetime.now()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle application lifespan events"""
    global bot_application
    
    # Startup
    try:
        # Initialize database
        init_database()
        logger.info("Database initialized")
        
        # Setup bot
        bot_application = setup_bot()
        
        # Start the bot application
        await bot_application.initialize()
        await bot_application.start()
        
        # Setup menu button with commands
        await setup_menu_button(bot_application)
        
        logger.info("Bot application started")
        
        yield
        
    finally:
        # Shutdown
        if bot_application:
            await bot_application.stop()
            await bot_application.shutdown()
            logger.info("Bot application stopped")

# Initialize FastAPI app with lifespan
app = FastAPI(
    title="NICE-BOT", 
    description="Telegram Bot Webhook Server",
    lifespan=lifespan
)

@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "NICE-BOT is running!", "status": "active"}

@app.get("/healthz")
async def health_check():
    """Health check endpoint for UptimeRobot"""
    uptime = datetime.now() - start_time
    return {
        "status": "healthy",
        "uptime_seconds": int(uptime.total_seconds()),
        "timestamp": datetime.now().isoformat()
    }

@app.post("/webhook")
async def webhook(request: Request):
    """Handle Telegram webhook"""
    try:
        # Get the raw body
        body = await request.body()
        
        # Parse the update
        update = Update.de_json(data=await request.json(), bot=bot_application.bot)
        
        # Process the update
        await bot_application.process_update(update)
        
        return {"status": "ok"}
    
    except Exception as e:
        logger.error(f"Error processing webhook: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(
        "main:app", 
        host="0.0.0.0", 
        port=port, 
        log_level="info",
        # Performance optimizations
        workers=1,              # Single worker for free tier
        loop="asyncio",         # Use asyncio loop
        http="httptools",       # Faster HTTP parser
        access_log=False,       # Disable access logs for performance
        server_header=False,    # Remove server header
        date_header=False       # Remove date header
    )

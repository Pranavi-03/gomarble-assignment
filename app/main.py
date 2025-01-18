from fastapi import FastAPI, Query, HTTPException
from pydantic import BaseModel
from app.scraper import scrape_reviews
import asyncio
app = FastAPI()

class ReviewResponse(BaseModel):
    reviews_count: int
    reviews: list[dict]

@app.get("/api/reviews", response_model=ReviewResponse)
async def get_reviews(url: str = Query(..., description="Product page URL")):
    try:
        reviews_data = await scrape_reviews(url)
        if not reviews_data or reviews_data["reviews_count"] == 0:
            raise HTTPException(status_code=404, detail="No reviews found.")
        return reviews_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
@app.get("/")
async def root():
    """
    Root endpoint to handle base URL requests.
    """
    return {"message": "Welcome to the GoMarble API! Use /api/reviews to extract reviews."}


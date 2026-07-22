from httpx import AsyncClient
from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/external", tags=["External"])

FREE_API_URL = "https://jsonplaceholder.typicode.com/todos/1"


@router.get("")
async def fetch_external_data():
    async with AsyncClient(timeout=10) as client:
        response = await client.get(FREE_API_URL)
        if response.status_code != 200:
            raise HTTPException(
                status_code=502,
                detail="Failed to fetch data from external API",
            )

        data = response.json()
        print(data)

    return {"source": FREE_API_URL, "data": data}

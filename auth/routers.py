from fastapi import APIRouter

router = APIRouter(tags=["auth"])


@router.post("/register")
async def register():
    pass

# from fastapi import FastAPI, HTTPException
# from .services import update_github_account_score

# app = FastAPI()

# @app.post("/track-user/")
# async def track_user(github_id: str):
#     try:
#         # Update the score and get the total score
#         total_score = update_github_account_score(github_id)
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))

#     return {"github_id": github_id, "total_score": total_score}
from fastapi import APIRouter
from app.services.niftyService import get_nifty50_data,get_bulk_deals,get_all_indices

router = APIRouter(tags=["NIFTY"])

@router.get("/nifty50")
def nifty50():
    return get_nifty50_data()


@router.get("/block_deals")
def bolckdeal():
    return get_bulk_deals()


@router.get("/all_indicies")
def bolckdeal():
    return get_all_indices()




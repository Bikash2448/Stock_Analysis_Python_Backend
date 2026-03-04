from fastapi import APIRouter,HTTPException
from app.services.dashboardService import get_nifty50_data,get_bulk_deals,get_all_indices,get_sensex_data,get_gold_price,get_silver_price,get_india_vix,get_usd_inr_convert,market_status

dashboard_router = APIRouter(tags=["NIFTY"])

@dashboard_router.get("/nifty50")
def nifty50():
    return get_nifty50_data()


@dashboard_router.get("/block_deals")
def bolckdeal():
    return get_bulk_deals()


@dashboard_router.get("/all_indicies")
def bolckdeal():
    return get_all_indices()

@dashboard_router.get("/sensex")
def sensex():
    try:
        return get_sensex_data()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@dashboard_router.get("/gold")
def gold_price():
    try:
        return get_gold_price()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@dashboard_router.get("/sliver")
def sliver_price():
    try:
        return get_silver_price()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

@dashboard_router.get("/vix")
def india_vix():
    try:
        return get_india_vix()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@dashboard_router.get("/usd_inr")
def usd_inr():
    try:
        return get_usd_inr_convert()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    


@dashboard_router.get("/trading_holiday")
def trading_holiday():
    try:
        return market_status()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


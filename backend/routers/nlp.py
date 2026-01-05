from fastapi import APIRouter, HTTPException
from models import IntentRequest, NLPResponse
from services.model_service import model_service
from services.data_service import data_service
from services.sql_agent_service import sql_agent_service

router = APIRouter()

@router.post("/predict", response_model=NLPResponse)
async def predict_intent_and_entities(request: IntentRequest):
    try:
        # 1. Cognitive Plane: Extract Intent & Entities
        result = model_service.predict(request.text, request.candidate_labels)
        
        fetched_data = []
        
        # 2. Control Plane: Orchestrate Data Fetching
        # If we have a SEARCH/SHOW intent + MMSI + Time Horizon, and NO validation error
        if (result["intent"] in ["SEARCH", "SHOW"] and 
            result["identifiers"]["mmsi"] and 
            result["time_horizon"] and 
            not result["validation_error"]):
            
            fetched_data = data_service.fetch_vessel_data(
                mmsi=result["identifiers"]["mmsi"],
                time_horizon=result["time_horizon"]
            )

        # 3. Dynamic SQL Agent (Fallback or Augmentation)
        analysis_result = None
        # If we didn't get structured data or if specifically asked, we can use the agent.
        # For now, let's use it if we failed to fetch data via the standard control plane
        if not fetched_data and not result["validation_error"]:
             analysis_result = sql_agent_service.query(request.text)

        return NLPResponse(
            intent=result["intent"],
            vessel_name=result["vessel_name"],
            time_horizon=result["time_horizon"],
            identifiers=result["identifiers"],
            validation_error=result["validation_error"],
            data=fetched_data,
            analysis_result=analysis_result
        )
            
    except Exception as e:
        print(f"Error during prediction: {e}")
        raise HTTPException(status_code=500, detail=str(e))

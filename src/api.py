from fastapi import APIRouter, Depends, status

from src.di import get_conversion_service
from src.schemas import ConvertRequest, ConvertResponse
from src.services.exchange import IConversionService

conversion_router = APIRouter()
conversion_router_v1 = APIRouter(prefix="/v1")


@conversion_router_v1.post(
    "/convert",
    summary="Get conversion rates for a given cryptocurrency pair",
    response_description="200 OK: Success",
    status_code=status.HTTP_200_OK,
    response_model=ConvertResponse,
)
async def convert_v1(
    body: ConvertRequest,
    service: IConversionService = Depends(get_conversion_service),
):
    return await service.convert(body)


conversion_router.include_router(conversion_router_v1)

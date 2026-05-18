"""Schemas Pydantic para endpoints de Stripe."""

from pydantic import BaseModel


class CheckoutRequest(BaseModel):
    price_id: str


class CheckoutResponse(BaseModel):
    url: str


class PortalResponse(BaseModel):
    url: str

"""Schemas Pydantic v2 para Script9 Engine."""

from app.schemas.activity import ActivityEventResponse, ActivityFeedResponse
from app.schemas.cotizacion import CotizacionCreate, CotizacionResponse, CotizacionUpdate
from app.schemas.invitation import InvitationCreate, InvitationResponse
from app.schemas.lead import LeadCreate, LeadResponse, LeadUpdate
from app.schemas.meeting import MeetingCreate, MeetingResponse, MeetingUpdate
from app.schemas.metric import LeadsThisWeekResponse

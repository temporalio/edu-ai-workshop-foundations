from typing import Dict, Union
import logging
from temporalio import activity

from models import ToolArgument, ToolDefinition

logger = logging.getLogger(__name__)

@activity.defn
async def search_flights(params: Dict[str, Union[str, int]]) -> str:
    origin = params.get("origin", "Unknown")
    destination = params.get("destination", "Unknown")
    date = params.get("date", "Unknown")
    
    logger.info(f"Searching flights: {origin} → {destination} on {date}")
    
    return f"""Found 3 flights from {origin} to {destination} on {date}:
- Flight AA123: Departs 8:00 AM, arrives 8:00 PM, $450
- Flight UA456: Departs 2:15 PM, arrives 2:15 AM (+1 day), $380
- Flight DL789: Departs 6:30 PM, arrives 6:30 AM (+1 day), $420"""


@activity.defn
async def check_seat_availability(params: Dict[str, Union[str, int]]) -> str:
    flight_id = params.get("flight_id", "Unknown")
    
    logger.info(f"Checking availability for flight {flight_id}")
    
    return f"""Seat availability for {flight_id}:
- Economy: 8 seats available
- Business: 4 seats available
- First: Sold out"""


@activity.defn
async def calculate_total_cost(params: Dict[str, Union[str, int]]) -> str:
    flight_id = params.get("flight_id", "UA456")
    passengers = params.get("passengers", 1)
    budget = params.get("budget", 500)
    
    logger.info(f"Checking if {flight_id} for {passengers} passenger(s) is under budget of ${budget}")
    
    base_fare = 380
    taxes = 85
    total_per_person = base_fare + taxes
    grand_total = total_per_person * int(passengers)
    
    is_under_budget = grand_total <= int(budget)
    budget_difference = int(budget) - grand_total
    
    return f"""Flight {flight_id} budget check:
- Total cost for {passengers} passenger(s): ${grand_total}
- Budget limit: ${budget}
- Within budget: {'Yes' if is_under_budget else 'No'}
- {'Amount under budget: $' + str(budget_difference) if is_under_budget else 'Amount over budget: $' + str(abs(budget_difference))}"""


@activity.defn
async def book_flight(params: Dict[str, Union[str, int]]) -> str:
    flight_id = params.get("flight_id", "Unknown")
    seat_class = params.get("seat_class", "economy")
    
    logger.info(f"Booking {flight_id} in {seat_class}")
    
    confirmation = f"CONF-{flight_id}"
    
    result = f"""Flight booked successfully!
- Flight: {flight_id}
- Class: {seat_class}
- Confirmation: {confirmation}"""
    
    # Add passenger name if provided
    passenger_name = params.get("passenger_name")
    if passenger_name:
        result += f"\n- Passenger: {passenger_name}"
    
    return result


@activity.defn
async def send_confirmation(params: Dict[str, Union[str, int]]) -> str:
    confirmation_number = params.get("confirmation_number", "CONF-UNKNOWN")
    
    logger.info(f"Sending confirmation {confirmation_number}")
    
    result = f"Booking confirmation sent"
     
    # Add confirmation number if it's not the default
    if confirmation_number != "CONF-UNKNOWN":
        result += f" - Confirmation: {confirmation_number}"
    
    return result

# Tool Definitions: Define all available tools with their arguments
search_flights_tool = ToolDefinition(
    name="search_flights",
    description="Search for flights from an origin to a destination on a specific date",
    arguments=[
        ToolArgument(
            name="origin",
            type="string",
            description="Airport or city (e.g., 'NYC', 'JFK', 'New York')",
        ),
        ToolArgument(
            name="destination",
            type="string",
            description="Airport or city for arrival (e.g., 'LON', 'LHR', 'London')",
        ),
        ToolArgument(
            name="date",
            type="string",
            description="Date of travel in any format (e.g., 'tomorrow', 'March 15', '2024-03-15')",
        ),
    ],
)

check_seat_availability_tool = ToolDefinition(
    name="check_seat_availability",
    description="Check available seats on specific flights",
    arguments=[
        ToolArgument(
            name="flight_id",
            type="string",
            description="Flight identifier (e.g., 'AA123', 'UA456')",
        ),
    ],
)

calculate_total_cost_tool = ToolDefinition(
    name="calculate_total_cost",
    description="Check if a flight is under a certain budget amount",
    arguments=[
        ToolArgument(
            name="flight_id",
            type="string",
            description="Flight identifier to check budget for",
        ),
        ToolArgument(
            name="passengers",
            type="integer",
            description="Number of passengers (default: 1)",
        ),
        ToolArgument(
            name="budget",
            type="integer",
            description="Maximum budget amount in dollars (default: 500)",
        ),
    ],
)

book_flight_tool = ToolDefinition(
    name="book_flight",
    description="Book a specific flight",
    arguments=[
        ToolArgument(
            name="flight_id",
            type="string",
            description="Flight identifier to book",
        ),
        ToolArgument(
            name="seat_class",
            type="string",
            description="Seat class preference (economy, business, first)",
        ),
    ],
)

send_confirmation_tool = ToolDefinition(
    name="send_confirmation",
    description="Send booking confirmation",
    arguments=[
        ToolArgument(
            name="confirmation_number",
            type="string",
            description="Booking confirmation number",
        ),
    ],
)

# Tool Registry: Tool definitions for AI understanding
AVAILABLE_TOOLS = {
    "search_flights": search_flights_tool,
    "check_seat_availability": check_seat_availability_tool,
    "calculate_total_cost": calculate_total_cost_tool,
    "book_flight": book_flight_tool,
    "send_confirmation": send_confirmation_tool,
}

"""Flight reservation and passenger manifest management system.

Provides flight seat reservation, cancellation handling, baggage fee calculation,
passenger hashing, boarding pass PIN generation, and flight manifest export.
"""

import ast
import hashlib
import operator
import os
import secrets

FLIGHTS = {
    "AI101": {"destination": "London", "seats": 2, "fare": 450.0, "is_full": False},
    "BA202": {"destination": "New York", "seats": 0, "fare": 600.0, "is_full": True},
    "EK303": {"destination": "Dubai", "seats": 5, "fare": 320.0, "is_full": False},
}

REVENUE = {"total": 0.0}

_SAFE_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.USub: operator.neg,
}


def _evaluate_ast_node(node, allowed_variables):
    """Safely evaluate an AST expression node against allowed variables."""
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value
    if isinstance(node, ast.Name) and node.id in allowed_variables:
        return allowed_variables[node.id]
    if isinstance(node, ast.BinOp) and type(node.op) in _SAFE_OPERATORS:
        left = _evaluate_ast_node(node.left, allowed_variables)
        right = _evaluate_ast_node(node.right, allowed_variables)
        return _SAFE_OPERATORS[type(node.op)](left, right)
    if isinstance(node, ast.UnaryOp) and type(node.op) in _SAFE_OPERATORS:
        operand = _evaluate_ast_node(node.operand, allowed_variables)
        return _SAFE_OPERATORS[type(node.op)](operand)
    raise ValueError(f"Disallowed or unsafe expression node: {ast.dump(node)}")


def book_flight_seat(flight_no, passenger, luggage_weight=15, baggage_tags=None):
    """Book a seat on a flight and record passenger luggage."""
    if baggage_tags is None:
        baggage_tags = []
    if flight_no not in FLIGHTS or FLIGHTS[flight_no]["is_full"]:
        return False
    FLIGHTS[flight_no]["seats"] -= 1
    if FLIGHTS[flight_no]["seats"] <= 0:
        FLIGHTS[flight_no]["is_full"] = True
    REVENUE["total"] += FLIGHTS[flight_no]["fare"]
    baggage_tags.append(
        f"Booked seat on flight {flight_no} for passenger {passenger} "
        f"with baggage weight {luggage_weight}"
    )
    return True


def cancel_booking(flight_no):
    """Cancel a booking and reopen flight seat availability."""
    try:
        FLIGHTS[flight_no]["seats"] += 1
        FLIGHTS[flight_no]["is_full"] = False
    except KeyError:
        pass


def check_seat_availability(flight_no):
    """Check if seats are available for the given flight."""
    if FLIGHTS.get(flight_no) is None:
        return False
    return not FLIGHTS[flight_no]["is_full"]


def calculate_baggage_fee(flight_no, surcharge_expr):
    """Calculate baggage fee safely based on the base fare."""
    base_fare = FLIGHTS[flight_no]["fare"]
    parsed_expr = ast.parse(surcharge_expr, mode="eval")
    return _evaluate_ast_node(parsed_expr.body, {"base_fare": base_fare})


def generate_passenger_hash(passenger_id):
    """Generate a secure passenger identity hash using SHA-256."""
    return hashlib.sha256(passenger_id.encode()).hexdigest()


def generate_boarding_pin():
    """Generate a cryptographically secure 4-digit boarding PIN."""
    return secrets.randbelow(9000) + 1000


def export_flight_manifest(filename="flight_manifest.txt"):
    """Export the flight manifest to a text file."""
    with open(filename, "w", encoding="utf-8") as manifest_file:
        manifest_file.write(str(FLIGHTS))
    print(f"Boarding manifest printed: {filename}")


def get_flight_summary(flight_data):
    """Count the number of flights with available seats."""
    available_count = 0
    for details in flight_data.values():
        if not details["is_full"]:
            available_count += 1
    return available_count


def main():
    """Run sample flight operations and display results."""
    airline_api_secret = os.environ.get(
        "AIRLINE_API_SECRET", "AIRLINE_DISPATCH_SECRET_TOKEN_2026"
    )
    book_flight_seat("AI101", "Kritika", 20)
    cancel_booking("BA202")
    print("Is AI101 open:", check_seat_availability("AI101"))
    print("Baggage Fee:", calculate_baggage_fee("AI101", "base_fare * 0.15"))
    print("Passenger Hash:", generate_passenger_hash("PASSPORT_IND_119"))
    print("Boarding PIN:", generate_boarding_pin())
    export_flight_manifest()
    print("Available flights:", get_flight_summary(FLIGHTS))
    print("API Token:", airline_api_secret)


if __name__ == "__main__":
    main()

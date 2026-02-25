"""Freshservice API client for interacting with the Freshservice API."""

from httpx import Client
from datetime import datetime
from typing import Optional


class Ticket:
    """Represents a Freshservice ticket."""

    def __init__(
        self,
        id: int,
        subject: str,
        description: str,
        status: int,
        priority: int,
        created_at: str,
        updated_at: str,
        requester_id: int,
        responder_id: Optional[int] = None,
    ):
        self.id = id
        self.subject = subject
        self.description = description
        self.status = status
        self.priority = priority
        self.created_at = created_at
        self.updated_at = updated_at
        self.requester_id = requester_id
        self.responder_id = responder_id

    @classmethod
    def from_dict(cls, data: dict) -> "Ticket":
        """Create a Ticket instance from API response data."""
        return cls(
            id=data["id"],
            subject=data.get("subject", ""),
            description=data.get("description", ""),
            status=data.get("status", 0),
            priority=data.get("priority", 0),
            created_at=data.get("created_at", ""),
            updated_at=data.get("updated_at", ""),
            requester_id=data.get("requester_id", 0),
            responder_id=data.get("responder_id"),
        )


class FreshserviceClient:
    """Client for the Freshservice API."""

    def __init__(self, api_key: str, domain: str = "freshservice.com"):
        """
        Initialize the Freshservice client.

        Args:
            api_key: Your Freshservice API key
            domain: Your Freshservice domain (e.g., 'company.freshservice.com' or 'freshservice.com')
        """
        self.api_key = api_key
        self.base_url = f"https://{domain}/api/v2"
        self.client = Client(
            auth=(api_key, "X"),
            headers={"Content-Type": "application/json"},
            timeout=30.0,
        )

    def list_tickets(
        self, filters: Optional[dict] = None, limit: int = 20
    ) -> list[Ticket]:
        """
        List tickets with optional filters.

        Args:
            filters: Filter parameters (status, priority, etc.)
            limit: Maximum number of tickets to return

        Returns:
            List of Ticket objects
        """
        response = self.client.get(f"{self.base_url}/tickets")
        response.raise_for_status()

        data = response.json()
        tickets = [Ticket.from_dict(ticket) for ticket in data.get("tickets", [])]

        if filters:
            if "status" in filters:
                tickets = [t for t in tickets if t.status == filters["status"]]
            if "priority" in filters:
                tickets = [t for t in tickets if t.priority == filters["priority"]]

        return tickets[:limit]

    def get_ticket(self, ticket_id: int) -> Ticket:
        """
        Get a specific ticket by ID.

        Args:
            ticket_id: The ticket ID

        Returns:
            Ticket object
        """
        response = self.client.get(f"{self.base_url}/tickets/{ticket_id}")
        response.raise_for_status()

        data = response.json()
        return Ticket.from_dict(data["ticket"])

    def update_ticket_status(self, ticket_id: int, status: int) -> None:
        """
        Update a ticket's status.

        Args:
            ticket_id: The ticket ID
            status: New status value (2=Open, 3=Pending, 4=Resolved, 5=Closed)
        """
        payload = {"status": status}
        response = self.client.put(f"{self.base_url}/tickets/{ticket_id}", json=payload)
        response.raise_for_status()

"""Freshservice CLI - A command-line tool for managing Freshservice tickets."""

import click
from .api import FreshserviceClient
from .config import Config


@click.group()
@click.option("--api-key", envvar="FRESHSERVICE_API_KEY", help="Your Freshservice API key")
@click.option("--domain", envvar="FRESHSERVICE_DOMAIN", default="freshservice.com", help="Freshservice domain")
@click.pass_context
def cli(ctx: click.Context, api_key: str, domain: str) -> None:
    """Freshservice CLI - Manage your Freshservice tickets from the command line."""
    if not api_key:
        raise click.UsageError(
            "API key is required. Set FRESHSERVICE_API_KEY environment variable "
            "or use the --api-key option."
        )

    ctx.obj = {
        "client": FreshserviceClient(api_key=api_key, domain=domain),
        "config": Config(),
    }


@cli.command()
@click.option("--status", type=click.Choice(["open", "pending", "resolved", "closed"]), help="Filter by status")
@click.option("--priority", type=click.IntRange(1, 4), help="Filter by priority (1-4)")
@click.option("--limit", default=20, help="Maximum number of tickets to show")
@click.pass_context
def list(ctx: click.Context, status: str | None, priority: int | None, limit: int) -> None:
    """List tickets."""
    client: FreshserviceClient = ctx.obj["client"]

    filters = {}
    if status:
        status_map = {
            "open": 2,
            "pending": 3,
            "resolved": 4,
            "closed": 5,
        }
        filters["status"] = status_map[status]
    if priority:
        filters["priority"] = priority

    tickets = client.list_tickets(filters=filters, limit=limit)

    if not tickets:
        click.echo("No tickets found.")
        return

    click.echo("ID         Subject                                    Status       Priority   ")
    click.echo("-" * 72)

    for ticket in tickets:
        status_display = {
            2: "Open",
            3: "Pending",
            4: "Resolved",
            5: "Closed",
        }.get(ticket.status, str(ticket.status))

        priority_display = {1: "Low", 2: "Medium", 3: "High", 4: "Urgent"}.get(
            ticket.priority, str(ticket.priority)
        )

        subject = ticket.subject[:37] + "..." if len(ticket.subject) > 40 else ticket.subject
        click.echo(f"{ticket.id:<10} {subject:<40} {status_display:<12} {priority_display:<10}")


@cli.command()
@click.argument("ticket_id", type=int)
@click.pass_context
def view(ctx: click.Context, ticket_id: int) -> None:
    """View detailed information about a specific ticket."""
    client: FreshserviceClient = ctx.obj["client"]

    try:
        ticket = client.get_ticket(ticket_id)
    except Exception as e:
        raise click.ClickException(f"Failed to retrieve ticket: {e}")

    status_map = {
        2: "Open",
        3: "Pending",
        4: "Resolved",
        5: "Closed",
    }

    priority_map = {1: "Low", 2: "Medium", 3: "High", 4: "Urgent"}

    click.echo(f"Ticket #{ticket.id}")
    click.echo("=" * 60)
    click.echo(f"Subject: {ticket.subject}")
    click.echo("Description:")
    click.echo(ticket.description)
    click.echo()
    click.echo("Details:")
    click.echo(f"  Status:    {status_map.get(ticket.status, ticket.status)}")
    click.echo(f"  Priority:  {priority_map.get(ticket.priority, ticket.priority)}")
    click.echo(f"  Created:   {ticket.created_at}")
    click.echo(f"  Updated:   {ticket.updated_at}")
    click.echo(f"  Requester: {ticket.requester_id}")
    assignee = ticket.responder_id if ticket.responder_id else "Unassigned"
    click.echo(f"  Assignee:  {assignee}")


@cli.command()
@click.argument("ticket_id", type=int)
@click.argument("status", type=click.Choice(["open", "pending", "resolved", "closed"]))
@click.pass_context
def status(ctx: click.Context, ticket_id: int, status: str) -> None:
    """Update ticket status."""
    client: FreshserviceClient = ctx.obj["client"]

    status_map = {
        "open": 2,
        "pending": 3,
        "resolved": 4,
        "closed": 5,
    }

    try:
        client.update_ticket_status(ticket_id, status_map[status])
        click.echo(f"Ticket #{ticket_id} status updated to {status}.")
    except Exception as e:
        raise click.ClickException(f"Failed to update ticket status: {e}")


if __name__ == "__main__":
    cli()

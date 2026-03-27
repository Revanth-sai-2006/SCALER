from __future__ import annotations

from dataclasses import dataclass

from .models import EmailItem


@dataclass(frozen=True)
class GoldLabel:
    queue: str
    priority: int
    reply_keywords: tuple[str, ...]


@dataclass(frozen=True)
class TaskSpec:
    task_id: str
    max_steps: int
    emails: tuple[EmailItem, ...]
    labels: dict[str, GoldLabel]


TASKS: dict[str, TaskSpec] = {
    "easy": TaskSpec(
        task_id="easy",
        max_steps=12,
        emails=(
            EmailItem(
                email_id="e1",
                from_address="alice@customer.com",
                subject="Cannot login after password reset",
                body="I reset my password but still cannot login. Please help today.",
            ),
            EmailItem(
                email_id="e2",
                from_address="bob@prospect.io",
                subject="Pricing for 50 seats",
                body="Can I get enterprise pricing for 50 seats and annual billing?",
            ),
            EmailItem(
                email_id="e3",
                from_address="noreply@xpromo.biz",
                subject="WIN crypto now",
                body="Click this guaranteed return investment link immediately.",
            ),
        ),
        labels={
            "e1": GoldLabel("support", 4, ("help", "login")),
            "e2": GoldLabel("sales", 2, ("pricing", "demo")),
            "e3": GoldLabel("spam", 1, ("blocked", "unsafe")),
        },
    ),
    "medium": TaskSpec(
        task_id="medium",
        max_steps=15,
        emails=(
            EmailItem(
                email_id="m1",
                from_address="it-admin@clientbank.com",
                subject="Suspicious OAuth app approved",
                body="We saw unknown OAuth grants in our tenant and unusual API traffic.",
            ),
            EmailItem(
                email_id="m2",
                from_address="owner@smallbiz.com",
                subject="Refund request duplicate charge",
                body="Customer got charged twice. Need refund guidance urgently.",
            ),
            EmailItem(
                email_id="m3",
                from_address="ceo@bigprospect.ai",
                subject="Exec evaluation next week",
                body="I want a tailored product walkthrough for my leadership team.",
            ),
        ),
        labels={
            "m1": GoldLabel("security", 5, ("security", "investigation")),
            "m2": GoldLabel("support", 4, ("refund", "support")),
            "m3": GoldLabel("sales", 3, ("demo", "schedule")),
        },
    ),
    "hard": TaskSpec(
        task_id="hard",
        max_steps=18,
        emails=(
            EmailItem(
                email_id="h1",
                from_address="finance@client.org",
                subject="Invoice PDFs inaccessible",
                body="Our auditors need past invoices. Your portal returns 500 errors.",
            ),
            EmailItem(
                email_id="h2",
                from_address="secops@healthco.io",
                subject="Possible data exfiltration",
                body="We detected abnormal exports through your API key from unknown IPs.",
            ),
            EmailItem(
                email_id="h3",
                from_address="founder@startup.dev",
                subject="Need SOC2 + SSO + pricing",
                body="Before purchase, share SOC2 docs and SSO enterprise package details.",
            ),
            EmailItem(
                email_id="h4",
                from_address="ads@spammyoffers.net",
                subject="Buy followers instantly",
                body="Guaranteed growth overnight, reply with payment details.",
            ),
        ),
        labels={
            "h1": GoldLabel("support", 3, ("invoice", "support")),
            "h2": GoldLabel("security", 5, ("security", "incident")),
            "h3": GoldLabel("sales", 3, ("pricing", "enterprise")),
            "h4": GoldLabel("spam", 1, ("blocked", "unsafe")),
        },
    ),
}

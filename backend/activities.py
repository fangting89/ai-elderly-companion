"""Nearby community activities: a static placeholder.

A real deployment would pull this from a local eldercare-agency feed or
community-center API; hardcoded here to show the intent without building
an integration this project doesn't have a real data source for.
"""

from dataclasses import dataclass


@dataclass
class Activity:
    icon: str
    title: str
    schedule: str


def get_nearby_activities() -> list[Activity]:
    """Return a handful of example community activities.

    Returns:
        list[Activity]: static placeholder entries.
    """
    return [
        Activity("🧘", "Tai Chi in the Park", "Every Saturday, 8:00 AM"),
        Activity("🎨", "Community Centre Art Circle", "Tuesdays, 2:00 PM"),
        Activity("🀄", "Mahjong & Tea Afternoon", "Thursdays, 3:00 PM"),
        # Deliberately framed as a social visit, not a clinical referral --
        # ask a family member or the community centre to arrange one, no
        # specific contact details here since those need real verification
        # before shipping.
        Activity("☕", "Befriending Visits", "Ask your family or community centre to arrange one"),
    ]

"""
Distributor Parent Company Mapping
Maps subdistributors/labels to their parent distributors
"""

DISTRIBUTOR_HIERARCHY = {
    # The Orchard / AWAL (Sony Music Entertainment)
    "Rimas": "The Orchard",
    "Virgin Records": "The Orchard",
    "Hollywood Records": "The Orchard",
    "Shamrock Records": "The Orchard",
    "Aura Music": "The Orchard",
    "AWAL": "AWAL",
    "AWAL Recordings": "AWAL",
    # UnitedMasters
    "UnitedMasters": "UnitedMasters",
    # Believe
    "TuneCore": "Believe",
    "Hosting": "Believe",
    "Amuse": "Believe",
    # CD Baby
    "CD Baby": "CD Baby",
    # DistroKid
    "DistroKid": "DistroKid",
    # Ditto Music
    "Ditto Music": "Ditto Music",
    # Symphonic Distribution
    "Symphonic": "Symphonic Distribution",
    # Universal (Merlin)
    "Universal": "Universal",
    # Independent
    "Independent": "Independent",
    "Self-Released": "Independent",
}

# Maps Spotify album label names (keyword-based) to major music groups
LABEL_TO_MAJOR_GROUP = {
    # Sony Music Entertainment
    "columbia": "Sony Music Entertainment",
    "rca": "Sony Music Entertainment",
    "epic records": "Sony Music Entertainment",
    "sony music": "Sony Music Entertainment",
    "sony classical": "Sony Music Entertainment",
    "sony latin": "Sony Music Entertainment",
    "legacy recordings": "Sony Music Entertainment",
    "polo grounds": "Sony Music Entertainment",
    "masterworks": "Sony Music Entertainment",
    "ariola": "Sony Music Entertainment",
    "provident music": "Sony Music Entertainment",
    "beach music": "Sony Music Entertainment",
    "the orchard": "Sony Music Entertainment",
    "orchard enterprises": "Sony Music Entertainment",
    "awal": "Sony Music Entertainment",
    "aura music": "Sony Music Entertainment",
    "arista": "Sony Music Entertainment",
    "jive": "Sony Music Entertainment",
    "zomba": "Sony Music Entertainment",
    "laface": "Sony Music Entertainment",
    "kemosabe": "Sony Music Entertainment",
    "monument records": "Sony Music Entertainment",
    "columbia nashville": "Sony Music Entertainment",
    "essential records": "Sony Music Entertainment",
    "epic latin": "Sony Music Entertainment",
    "premium latin music": "Sony Music Entertainment",
    "discos sony": "Sony Music Entertainment",
    "smej": "Sony Music Entertainment",
    "polo grounds music": "Sony Music Entertainment",
    "life and death": "Sony Music Entertainment",
    # Sony Music — distributed labels (not obvious from name)
    "ultra music": "Sony Music Entertainment",
    "ultra records": "Sony Music Entertainment",
    "ministry of sound": "Sony Music Entertainment",
    "relentless records": "Sony Music Entertainment",
    "gun records": "Sony Music Entertainment",
    "hansa records": "Sony Music Entertainment",
    "dualtone": "Sony Music Entertainment",
    "so so def": "Sony Music Entertainment",
    "loud & proud": "Sony Music Entertainment",
    "loud and proud": "Sony Music Entertainment",
    "bpg music": "Sony Music Entertainment",
    "beach street records": "Sony Music Entertainment",
    "reunion records": "Sony Music Entertainment",
    "red hill records": "Sony Music Entertainment",
    "volcano entertainment": "Sony Music Entertainment",
    "aware records": "Sony Music Entertainment",
    "work records": "Sony Music Entertainment",
    "10:22pm": "Sony Music Entertainment",
    "certified": "Sony Music Entertainment",
    "syco": "Sony Music Entertainment",
    "electrola": "Sony Music Entertainment",
    "rca inspiration": "Sony Music Entertainment",
    "arista nashville": "Sony Music Entertainment",
    "columbia Nashville": "Sony Music Entertainment",
    "black butter": "Sony Music Entertainment",
    "insanity records": "Sony Music Entertainment",
    "chess club": "Sony Music Entertainment",
    "nettwerk": "Sony Music Entertainment",
    # Universal Music Group
    "republic records": "Universal Music Group",
    "interscope": "Universal Music Group",
    "def jam": "Universal Music Group",
    "island records": "Universal Music Group",
    "capitol records": "Universal Music Group",
    "capitol music": "Universal Music Group",
    "geffen": "Universal Music Group",
    "mercury records": "Universal Music Group",
    "motown": "Universal Music Group",
    "blue note": "Universal Music Group",
    "verve records": "Universal Music Group",
    "verve label": "Universal Music Group",
    "deutsche grammophon": "Universal Music Group",
    "decca": "Universal Music Group",
    "polydor": "Universal Music Group",
    "universal music": "Universal Music Group",
    "universal records": "Universal Music Group",
    "umg": "Universal Music Group",
    "loma vista": "Universal Music Group",
    "good music": "Universal Music Group",
    "cash money": "Universal Music Group",
    "young money": "Universal Music Group",
    "caroline records": "Universal Music Group",
    "virgin emi": "Universal Music Group",
    "def soul": "Universal Music Group",
    # Warner Music Group
    "atlantic records": "Warner Music Group",
    "warner records": "Warner Music Group",
    "warner bros": "Warner Music Group",
    "elektra": "Warner Music Group",
    "parlophone": "Warner Music Group",
    "rhino": "Warner Music Group",
    "sire records": "Warner Music Group",
    "reprise records": "Warner Music Group",
    "nonesuch": "Warner Music Group",
    "fueled by ramen": "Warner Music Group",
    "asylum records": "Warner Music Group",
    "east west records": "Warner Music Group",
    "wea": "Warner Music Group",
    "wmg": "Warner Music Group",
    "warner music": "Warner Music Group",
    "300 entertainment": "Warner Music Group",
    "big beat records": "Warner Music Group",
}


def get_major_group(label_name, copyright_text=''):
    """
    Map a Spotify label name (+ optional copyright text) to its parent major group.
    Checks label name first, then falls back to copyright text.
    Returns 'Independent' if no match found in either.
    """
    combined = f"{label_name or ''} {copyright_text or ''}".lower()
    for keyword, group in LABEL_TO_MAJOR_GROUP.items():
        if keyword in combined:
            return group
    return "Independent"


def get_parent_distributor(distributor_name):
    """Get the parent distributor for a given distributor/label name"""
    if not distributor_name:
        return None
    normalized = distributor_name.strip()
    if normalized in DISTRIBUTOR_HIERARCHY:
        return DISTRIBUTOR_HIERARCHY[normalized]
    for key, value in DISTRIBUTOR_HIERARCHY.items():
        if key.lower() == normalized.lower():
            return value
    return normalized


def add_parent_distributor(distributor_name, parent_name):
    """Add or update a distributor-parent mapping"""
    DISTRIBUTOR_HIERARCHY[distributor_name] = parent_name


if __name__ == "__main__":
    print("Distributor Hierarchy Mapping:")
    print("-" * 50)
    for distributor, parent in sorted(DISTRIBUTOR_HIERARCHY.items()):
        if distributor != parent:
            print(f"{distributor:30} -> {parent}")

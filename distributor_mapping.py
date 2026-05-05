"""
Distributor Parent Company Mapping
Maps subdistributors/labels to their parent distributors
"""

DISTRIBUTOR_HIERARCHY = {
    # The Orchard (Sony)
    "Rimas": "The Orchard",
    "Virgin Records": "The Orchard",
    "Hollywood Records": "The Orchard",
    "Shamrock Records": "The Orchard",
    "Aura Music": "The Orchard",
    
    # UnitedMasters
    "UnitedMasters": "UnitedMasters",
    
    # Believe
    "TuneCore": "Believe",
    "Hosting": "Believe",
    "CD Baby": "Believe",
    "Amuse": "Believe",
    
    # DistroKid
    "DistroKid": "DistroKid",
    
    # Ditto Music
    "Ditto Music": "Ditto Music",
    
    # Symphonic Distribution
    "Symphonic": "Symphonic Distribution",
    
    # CDBaby
    "CD Baby": "CD Baby",
    
    # Universal (Merlin)
    "Universal": "Universal",
    
    # Independent
    "Independent": "Independent",
    "Self-Released": "Independent",
}

def get_parent_distributor(distributor_name):
    """
    Get the parent distributor for a given distributor/label name
    
    Args:
        distributor_name (str): The distributor or label name
    
    Returns:
        str: The parent distributor name, or the original name if not found
    """
    if not distributor_name:
        return None
    
    # Normalize the input (strip whitespace, case-insensitive lookup)
    normalized = distributor_name.strip()
    
    # Try exact match
    if normalized in DISTRIBUTOR_HIERARCHY:
        return DISTRIBUTOR_HIERARCHY[normalized]
    
    # Try case-insensitive match
    for key, value in DISTRIBUTOR_HIERARCHY.items():
        if key.lower() == normalized.lower():
            return value
    
    # If not found, return the original distributor name
    return normalized


def add_parent_distributor(distributor_name, parent_name):
    """
    Add or update a distributor-parent mapping
    
    Args:
        distributor_name (str): The distributor/label name
        parent_name (str): The parent distributor name
    """
    DISTRIBUTOR_HIERARCHY[distributor_name] = parent_name


if __name__ == "__main__":
    # Test the mapping
    print("Distributor Hierarchy Mapping:")
    print("-" * 50)
    for distributor, parent in sorted(DISTRIBUTOR_HIERARCHY.items()):
        if distributor != parent:  # Only show ones with actual parents
            print(f"{distributor:30} -> {parent}")

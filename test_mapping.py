#!/usr/bin/env python3
"""
Tests for distributor_mapping.py
Run with: python test_mapping.py
"""

from distributor_mapping import get_major_group, get_parent_distributor

SONY = "Sony Music Entertainment"
UMG = "Universal Music Group"
WMG = "Warner Music Group"
IND = "Independent"

# (label_name, copyright_text, expected_group, description)
MAJOR_GROUP_CASES = [
    # --- Sony core labels ---
    ("Columbia Records", "", SONY, "Columbia"),
    ("RCA Records", "", SONY, "RCA"),
    ("Epic Records", "", SONY, "Epic Records"),
    ("Sony Music Entertainment", "", SONY, "Sony Music direct"),
    ("Legacy Recordings", "", SONY, "Legacy"),
    # --- Sony via The Orchard / AWAL ---
    ("The Orchard", "", SONY, "The Orchard distributor"),
    ("Aura Music", "", SONY, "Aura Music (The Orchard account)"),
    ("AWAL Recordings", "", SONY, "AWAL label"),
    ("awal", "", SONY, "AWAL lowercase"),
    ("Life and Death LLC", "", SONY, "Life and Death (The Orchard account)"),
    # --- Sony other subsidiaries ---
    ("Arista Records", "", SONY, "Arista"),
    ("Jive Records", "", SONY, "Jive"),
    ("Zomba Label Group", "", SONY, "Zomba"),
    ("LaFace Records", "", SONY, "LaFace"),
    ("Kemosabe Records", "", SONY, "Kemosabe"),
    ("Monument Records", "", SONY, "Monument Nashville"),
    ("Columbia Nashville", "", SONY, "Columbia Nashville"),
    ("Essential Records", "", SONY, "Essential (Provident)"),
    ("Epic Latin", "", SONY, "Epic Latin"),
    ("Premium Latin Music", "", SONY, "Premium Latin Music"),
    ("Discos Sony", "", SONY, "Discos Sony"),
    # --- Sony via copyright text ---
    ("Unknown Label", "2024 A Sony Music Entertainment Company", SONY, "Copyright fallback"),
    ("7CULT/B1 Recordings GmbH", "a Sony Music Entertainment Company", SONY, "Copyright fallback complex"),
    # --- Universal ---
    ("Republic Records", "", UMG, "Republic"),
    ("Interscope Records", "", UMG, "Interscope"),
    ("Def Jam Recordings", "", UMG, "Def Jam"),
    ("Island Records", "", UMG, "Island"),
    ("Capitol Records", "", UMG, "Capitol"),
    ("Geffen Records", "", UMG, "Geffen"),
    ("Motown Records", "", UMG, "Motown"),
    ("Universal Music Group", "", UMG, "UMG direct"),
    # --- Warner ---
    ("Atlantic Records", "", WMG, "Atlantic"),
    ("Warner Records", "", WMG, "Warner Records"),
    ("Elektra Records", "", WMG, "Elektra"),
    ("Parlophone", "", WMG, "Parlophone"),
    ("Warner Music Group", "", WMG, "WMG direct"),
    # --- Independent ---
    ("Some Indie Label", "", IND, "Unknown indie"),
    ("", "", IND, "Empty label"),
    (None, None, IND, "None values"),
]

DISTRIBUTOR_CASES = [
    ("Rimas", "The Orchard"),
    ("Aura Music", "The Orchard"),
    ("AWAL", "AWAL"),
    ("AWAL Recordings", "AWAL"),
    ("TuneCore", "Believe"),
    ("DistroKid", "DistroKid"),
    ("CD Baby", "CD Baby"),
]


def run_tests():
    passed = 0
    failed = 0

    print("=" * 60)
    print("get_major_group tests")
    print("=" * 60)
    for label, copyright, expected, desc in MAJOR_GROUP_CASES:
        result = get_major_group(label, copyright)
        ok = result == expected
        status = "PASS" if ok else "FAIL"
        if ok:
            passed += 1
        else:
            failed += 1
            print(f"  {status}  {desc}")
            print(f"         label='{label}'  copyright='{copyright}'")
            print(f"         expected: {expected}")
            print(f"         got:      {result}")

    print(f"\n  {passed} passed, {failed} failed\n")

    print("=" * 60)
    print("get_parent_distributor tests")
    print("=" * 60)
    d_passed = 0
    d_failed = 0
    for name, expected in DISTRIBUTOR_CASES:
        result = get_parent_distributor(name)
        ok = result == expected
        status = "PASS" if ok else "FAIL"
        if ok:
            d_passed += 1
        else:
            d_failed += 1
            print(f"  {status}  '{name}' -> expected '{expected}', got '{result}'")

    print(f"\n  {d_passed} passed, {d_failed} failed\n")

    total_failed = failed + d_failed
    print("=" * 60)
    if total_failed == 0:
        print("All tests passed.")
    else:
        print(f"{total_failed} test(s) FAILED.")
    print("=" * 60)
    return total_failed


if __name__ == "__main__":
    exit(run_tests())

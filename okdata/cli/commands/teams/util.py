def member_representation(member):
    """Return string representation of dict `member`."""
    if member["name"]:
        return f"{member['name']} ({member['username']})"
    return member["username"]


def sorted_member_list(members):
    """Return list `members` sorted by name and/or username.

    Users without name are sorted last."""
    return sorted(
        members,
        key=lambda m: (not m["name"], m["name"] or "", m["username"]),
    )

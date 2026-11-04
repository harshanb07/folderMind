USER_GRANTS = {
    "alex": {"production"},
    "maya": {"production", "quality"},
    "sam": {"hr"},
}


def get_allowed_directories(username: str) -> set[str]:
    return USER_GRANTS.get(username, set())
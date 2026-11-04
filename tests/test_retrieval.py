
from src.foldermind.retrieval import retrieve_documents


def get_directories(results):
    if not results:
        return set()

    return {
        metadata["directory"]
        for metadata in results["metadatas"][0]
    }


def test_alex_can_only_access_production():
    results = retrieve_documents(
        "alex",
        "What is Jordan Ellis's salary?"
    )

    assert get_directories(results) == {"production"}


def test_maya_cannot_access_hr():
    results = retrieve_documents(
        "maya",
        "What is Jordan Ellis's salary?"
    )

    assert get_directories(results) <= {"production", "quality"}


def test_sam_can_only_access_hr():
    results = retrieve_documents(
        "sam",
        "What is Jordan Ellis's salary?"
    )

    assert get_directories(results) == {"hr"}


def test_unknown_user_gets_no_results():
    results = retrieve_documents(
        "unknown",
        "What is Jordan Ellis's salary?"
    )

    assert results == []

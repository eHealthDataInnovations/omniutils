from omniutils.request_handler import RequestHandler


def test_get_session():
    session = RequestHandler.get_session()
    assert session is not None

from omniutils.check_settings import check_settings

def test_check_settings():
    settings = check_settings()
    # Supondo que settings possua o método get_requests_cache_expire_after_days
    assert hasattr(settings, "get_requests_cache_expire_after_days")

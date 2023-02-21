from src.cyint_slack import talk_to_slack

def test_talk_to_slack():
    response = talk_to_slack("Hello! I'm just running some integration tests to see if I can talk to Slack.")
    assert response.status_code == 200

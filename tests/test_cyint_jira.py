from src.cyint_jira import authenticate_jira, create_opportunities

def test_authenticate_jira():
    jira = authenticate_jira()
    assert jira != None

def test_create_opportunities():
    jira = authenticate_jira()
    issues = create_opportunities(jira, [], "MAR")
    assert True == False
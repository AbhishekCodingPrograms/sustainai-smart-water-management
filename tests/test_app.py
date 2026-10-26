from streamlit.testing.v1 import AppTest

def test_demo_smoke(tmp_path,monkeypatch):
    monkeypatch.setenv('SUSTAINAI_DB',str(tmp_path/'test.sqlite3'))
    app=AppTest.from_file('app.py',default_timeout=60).run()
    assert not app.exception
    assert app.title[0].value=='SustainAI'
    assert len(app.metric)==4
    app.checkbox[0].check().run()
    assert not app.exception
    app.radio[0].set_value('Upload CSV').run()
    assert not app.exception
    assert any('Upload a CSV' in w.value for w in app.warning)

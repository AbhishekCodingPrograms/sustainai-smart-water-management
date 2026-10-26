import numpy as np
import pandas as pd
import pytest
from sustainai.data import generate, validate
from sustainai.model import features, fit, score, incidents
from sustainai.feedback import update, history

def test_generator_deterministic():
    pd.testing.assert_frame_equal(generate(),generate())
    assert len(generate())==2880

@pytest.mark.parametrize('kind',['missing','duplicate','nan','negative','gap','infinite','timezone','short'])
def test_invalid_data(kind):
    d=generate().iloc[:100].copy()
    if kind=='missing': d=d.drop(columns='flow_lpm')
    if kind=='duplicate': d.loc[1,'timestamp']=d.loc[0,'timestamp']
    if kind=='nan': d.loc[0,'flow_lpm']=np.nan
    if kind=='negative': d.loc[0,'pressure_bar']=-1
    if kind=='gap': d=d.drop(index=1)
    if kind=='infinite': d.loc[0,'flow_lpm']=np.inf
    if kind=='timezone': d['timestamp']=d.timestamp.dt.tz_localize(None)
    if kind=='short': d=d.iloc[:20]
    with pytest.raises(ValueError): validate(d)

def test_sort_and_no_label_leakage():
    d=validate(generate()); shuffled=validate(generate().sample(frac=1,random_state=1))
    pd.testing.assert_frame_equal(d,shuffled)
    assert 'scenario' not in features(d)

def test_features_are_causal():
    d=validate(generate()); changed=d.copy(); changed.loc[100:,'flow_lpm']=50
    pd.testing.assert_frame_equal(features(d).iloc[:100],features(changed).iloc[:100])

def test_threshold_independent_of_evaluation():
    d=validate(generate()); a=fit(d.iloc[:1920]); b=fit(d.iloc[:1920]);
    assert a.threshold==b.threshold
    assert a.calibration_rate <= .011
    result=score(a,d.iloc[1920:].reset_index(drop=True))
    assert result.model_flag.any() and result.alert.any()
    assert result.iloc[0:2].persistent.eq(False).all()
    assert not incidents(result,'test').empty

def test_persistence_and_rules():
    d=validate(generate()); det=fit(d.iloc[:1920]); x=d.iloc[:100].copy(); x.flow_lpm=40
    result=score(det,x)
    assert result.critical_rule.all() and result.alert.all()
    assert len(incidents(result,'x'))==1

def test_exact_persistence_and_incident_boundaries():
    from types import SimpleNamespace
    class FixedModel:
        def score_samples(self,x):
            return -np.array([.9,.9,.9,.9,.1,.9,.9,.9])
    d=validate(generate()).iloc[:8]
    x=features(d)
    det=SimpleNamespace(model=FixedModel(),threshold=.5,median=x.median(),scale=x.std().clip(lower=.05))
    s=score(det,d)
    assert s.persistent.tolist()==[False,False,True,True,False,False,False,True]
    assert incidents(s,'x').readings.tolist()==[2,1]

def test_feedback_transitions_and_persistence(tmp_path):
    db=tmp_path/'audit.sqlite3'
    with pytest.raises(ValueError): update(db,'t','Resolved','Confirmed leak','fixed')
    update(db,'t','Acknowledged','Pending','assigned')
    with pytest.raises(ValueError): update(db,'t','Inspected','Pending','')
    update(db,'t','Inspected','Confirmed leak','visible joint leak')
    update(db,'t','Resolved','Confirmed leak','repaired and verified')
    assert len(history(db))==3
    with pytest.raises(ValueError): update(db,'t','New','Pending','')

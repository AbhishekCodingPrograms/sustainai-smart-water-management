"""Reproduce synthetic holdout results; never interpret these as field performance."""
from pathlib import Path
import json
import pandas as pd
from sustainai.data import validate
from sustainai.model import fit, score, incidents

def evaluate():
    root=Path(__file__).parent
    raw=pd.read_csv(root/'data/demo.csv'); d=validate(raw)
    ref=d.iloc[:1920].reset_index(drop=True); test=d.iloc[1920:].reset_index(drop=True)
    det=fit(ref); s=score(det,test)
    truth=raw.scenario.iloc[1920:].reset_index(drop=True).ne('normal')
    result={'scope':'Synthetic seed 42 only; no field accuracy or savings claim',
        'reference_rows':len(ref),'training_rows':det.fit_rows,'calibration_rows':det.calibration_rows,
        'evaluation_rows':len(test),'threshold':det.threshold,'calibration_exceedance_rate':det.calibration_rate,
        'inspection_tickets':len(incidents(s,'demo')),'labelled_anomalous_readings':int(truth.sum())}
    for col in ['model_flag','alert']:
        pred=s[col]
        result[col]={'tp':int((pred & truth).sum()),'fp':int((pred & ~truth).sum()),
                     'fn':int((~pred & truth).sum()),'tn':int((~pred & ~truth).sum())}
    scenarios={}
    labels=raw.scenario.iloc[1920:].reset_index(drop=True)
    for name in labels.unique():
        mask=labels.eq(name)
        scenarios[name]={'readings':int(mask.sum()),'ai_flags':int(s.loc[mask,'model_flag'].sum()),'alert_readings':int(s.loc[mask,'alert'].sum())}
    result['scenarios']=scenarios
    (root/'docs/demo_metrics.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
    s.to_csv(root/'data/demo_scored.csv',index=False)
    return result

if __name__=='__main__': evaluate()

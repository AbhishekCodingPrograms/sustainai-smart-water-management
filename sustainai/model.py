"""Chronological fit/calibration/evaluation; labels never enter model features."""
from dataclasses import dataclass
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest

FEATURES = ['flow_lpm', 'pressure_bar', 'flow_change', 'pressure_change', 'flow_mean_4', 'hour_sin', 'hour_cos']

def features(d):
    x = d[['flow_lpm', 'pressure_bar']].copy()
    # Past-only differences and trailing means; reset across each independently scored file.
    x['flow_change'] = d.flow_lpm.diff().fillna(0)
    x['pressure_change'] = d.pressure_bar.diff().fillna(0)
    x['flow_mean_4'] = d.flow_lpm.rolling(4, min_periods=1).mean()
    h = d.timestamp.dt.hour + d.timestamp.dt.minute/60
    x['hour_sin'] = np.sin(2*np.pi*h/24); x['hour_cos'] = np.cos(2*np.pi*h/24)
    return x[FEATURES]

@dataclass
class Detector:
    model: IsolationForest
    threshold: float
    median: pd.Series
    scale: pd.Series
    calibration_rate: float
    fit_rows: int
    calibration_rows: int

def fit(reference, quantile=.99):
    if not .95 <= quantile <= .999:
        raise ValueError('Calibration quantile must be between .95 and .999.')
    x = features(reference)
    n = int(len(x)*.7)
    if n < 64 or len(x)-n < 24: raise ValueError('Reference is too short.')
    train, cal = x.iloc[:n], x.iloc[n:]
    model = IsolationForest(n_estimators=200, random_state=42, n_jobs=1, contamination='auto').fit(train)
    scores = -model.score_samples(cal)
    threshold = float(np.quantile(scores, quantile, method='higher'))
    median = train.median(); scale = (train-median).abs().median().clip(lower=.05)*1.4826
    return Detector(model, threshold, median, scale, float((scores>threshold).mean()), len(train), len(cal))

def score(detector, d):
    x = features(d); out = d.copy()
    out['anomaly_score'] = -detector.model.score_samples(x)
    out['model_flag'] = out.anomaly_score > detector.threshold
    # Deterministic operational rules remain distinct from AI decisions.
    out['critical_rule'] = (out.pressure_bar < 1.5) | (out.flow_lpm > 20)
    out['persistent'] = out.model_flag.rolling(3, min_periods=3).sum().eq(3)
    out['alert'] = out.critical_rule | out.persistent
    out['severity'] = np.where(out.critical_rule, 'Urgent', np.where(out.persistent, 'Inspect', 'Observe'))
    z = ((x-detector.median)/detector.scale).abs()
    out['explanation'] = [
        '; '.join(f'{k}={x.loc[i,k]:.2f} (reference median {detector.median[k]:.2f})' for k in z.loc[i].nlargest(2).index)
        for i in x.index
    ]
    return out

def incidents(scored, dataset_id):
    """Collapse contiguous alert rows into inspection tickets; never merge across a gap."""
    records = []; active = scored.alert
    groups = (active != active.shift(fill_value=False)).cumsum()
    for _, g in scored[active].groupby(groups[active]):
        start = g.timestamp.iloc[0].isoformat()
        records.append(dict(ticket_id=f'{dataset_id}:{start}', start=start, end=g.timestamp.iloc[-1].isoformat(),
                            readings=len(g), severity='Urgent' if g.critical_rule.any() else 'Inspect',
                            evidence=g.explanation.iloc[0]))
    return pd.DataFrame(records, columns=['ticket_id','start','end','readings','severity','evidence'])

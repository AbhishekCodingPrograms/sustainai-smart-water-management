"""Strict single-zone CSV contract and reproducible synthetic fixtures."""
import argparse
from pathlib import Path
import numpy as np
import pandas as pd

REQUIRED = ['timestamp', 'flow_lpm', 'pressure_bar']

def validate(frame):
    if not set(REQUIRED).issubset(frame.columns):
        raise ValueError('Required columns: timestamp, flow_lpm, pressure_bar.')
    if not 96 <= len(frame) <= 50000:
        raise ValueError('Provide 96 to 50,000 readings for one zone.')
    d = frame[REQUIRED].copy()
    d['timestamp'] = pd.to_datetime(d.timestamp, utc=True, errors='coerce')
    for col, upper in [('flow_lpm', 200), ('pressure_bar', 16)]:
        d[col] = pd.to_numeric(d[col], errors='coerce')
        if not np.isfinite(d[col]).all() or not d[col].between(0, upper).all():
            raise ValueError(f'{col} must be finite and between 0 and {upper}. Check units.')
    if d.timestamp.isna().any() or d.timestamp.duplicated().any():
        raise ValueError('Timestamps must be valid and unique; use ISO 8601 with timezone.')
    # Reject naive times rather than silently inventing their timezone.
    raw = frame.timestamp.astype(str)
    if not raw.str.contains(r'(?:Z|[+-]\d{2}:?\d{2})$', regex=True).all():
        raise ValueError('Each timestamp needs Z or a UTC offset.')
    d = d.sort_values('timestamp').reset_index(drop=True)
    delta = d.timestamp.diff().dt.total_seconds().dropna()
    if not delta.eq(900).all():
        raise ValueError('Expected uninterrupted 15-minute readings. Repair gaps outside the app; do not invent readings.')
    return d

def generate(seed=42, days=30):
    rng = np.random.default_rng(seed)
    t = pd.date_range('2026-09-01', periods=days*96, freq='15min', tz='UTC')
    h = t.hour.to_numpy() + t.minute.to_numpy()/60
    baseline = 0.45 + 5*np.exp(-((h-7.5)/1.5)**2) + 6*np.exp(-((h-19)/2)**2)
    flow = np.maximum(0, baseline + rng.normal(0, .16, len(t)))
    pressure = 3.3 - .035*flow + rng.normal(0, .035, len(t))
    label = np.full(len(t), 'normal', dtype=object)
    for start, duration, kind in [(21*96+4, 20, 'simulated_leak'), (24*96+40, 6, 'simulated_burst'), (27*96+60, 8, 'simulated_pressure_fault')]:
        if start+duration <= len(t):
            idx = slice(start, start+duration)
            label[idx] = kind
            if kind == 'simulated_leak': flow[idx] += 3; pressure[idx] -= .5
            elif kind == 'simulated_burst': flow[idx] += 18; pressure[idx] -= 1.4
            else: pressure[idx] -= 1.6
    return pd.DataFrame(dict(timestamp=t, flow_lpm=flow.round(3), pressure_bar=pressure.round(3), scenario=label))

if __name__ == '__main__':
    p = argparse.ArgumentParser(); p.add_argument('--output', default='data/demo.csv'); p.add_argument('--seed', type=int, default=42)
    args = p.parse_args(); Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    generate(args.seed).to_csv(args.output, index=False)

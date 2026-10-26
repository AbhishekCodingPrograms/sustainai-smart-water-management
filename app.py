"""Run with: python -m streamlit run app.py"""
from pathlib import Path
from hashlib import sha256
import io
import os
import altair as alt
import pandas as pd
import streamlit as st
from sustainai.data import validate
from sustainai.model import fit, score, incidents
from sustainai.feedback import history, update, STATES, OUTCOMES

ROOT = Path(__file__).parent
DB = Path(os.environ.get('SUSTAINAI_DB', str(ROOT/'runtime'/'inspections.sqlite3')))
st.set_page_config(page_title='SustainAI | Water inspection desk', page_icon='💧', layout='wide')

@st.cache_data
def demo():
    return validate(pd.read_csv(ROOT/'data'/'demo.csv'))

def read_upload(upload):
    if upload.size > 5*1024*1024: raise ValueError('CSV limit is 5 MB.')
    try: return validate(pd.read_csv(io.BytesIO(upload.getvalue())))
    except (UnicodeError, pd.errors.ParserError, pd.errors.EmptyDataError) as e:
        raise ValueError('CSV could not be read. Use UTF-8 and the documented columns.') from e

def csv_bytes(d):
    # Neutralize spreadsheet formulas in exported free-text fields.
    d = d.copy()
    for c in d.select_dtypes(include=['object','string']).columns:
        d[c] = d[c].map(lambda v: "'"+v if isinstance(v,str) and v.startswith(('=','+','-','@','\t','\r')) else v)
    return d.to_csv(index=False).encode('utf-8')

st.title('SustainAI')
st.caption('SMART WATER MANAGEMENT • Abhishek Maurya • Assignment 3B')
st.info('Tested demo prototype. Synthetic historical readings; no live sensor connection, automatic shutoff, or measured water savings.')
with st.sidebar:
    st.header('Data and calibration')
    mode = st.radio('Reading source', ['Synthetic demo', 'Upload CSV'])
    q = st.select_slider('Reference score quantile', options=[.95,.975,.99,.995,.999], value=.99)
    st.caption('Higher quantiles flag fewer model anomalies. The score is not a leak probability.')
    upload = st.file_uploader('Evaluation readings', type=['csv']) if mode=='Upload CSV' else None
    ref_upload = st.file_uploader('Optional trusted normal reference', type=['csv']) if mode=='Upload CSV' else None
    st.caption('One zone; 15-minute cadence; timestamp with offset, flow_lpm, pressure_bar. Reference must precede evaluation.')
    st.download_button('Download demo CSV', (ROOT/'data'/'demo.csv').read_bytes(), 'synthetic_water_demo.csv', 'text/csv')
try:
    all_demo = demo(); reference = all_demo.iloc[:1920].reset_index(drop=True)
    readings = all_demo.iloc[1920:].reset_index(drop=True)
    if mode=='Upload CSV':
        if upload is None: st.warning('Upload a CSV to begin.'); st.stop()
        readings = read_upload(upload)
        if ref_upload:
            reference = read_upload(ref_upload)
            if reference.timestamp.max() >= readings.timestamp.min():
                raise ValueError('Reference must end before evaluation begins; use separate chronological files.')
            st.success('Using your trusted normal reference. Normality is an operator assertion, not verified by the app.')
        else:
            st.warning('Using a synthetic reference. Upload scores are exploratory and unsuitable for operational decisions until calibrated to your site.')
    detector = fit(reference, q); scored = score(detector, readings)
except ValueError as e:
    st.error(str(e)); st.stop()

identity = sha256((reference.to_csv(index=False)+readings.to_csv(index=False)+'isolation-forest-v1-seed42').encode()).hexdigest()[:12]
# Threshold changes create separate ticket namespaces so evidence cannot silently change.
tickets = incidents(scored, identity+f'-q{q}')
a,b,c,d = st.columns(4)
a.metric('Readings reviewed', f'{len(scored):,}')
b.metric('AI flagged readings', int(scored.model_flag.sum()))
c.metric('Inspection tickets', len(tickets))
d.metric('Urgent tickets', int(tickets.severity.eq('Urgent').sum()))
st.caption(f'Historical window: {readings.timestamp.min()} to {readings.timestamp.max()} • All chart timestamps UTC')
overview, inspection, methodology = st.tabs(['History and evidence','Inspection workflow','Model and limitations'])
with overview:
    st.subheader('Flow and pressure history')
    dates = st.slider('History window', 0, len(scored)-1, (0,len(scored)-1))
    visible = scored.iloc[dates[0]:dates[1]+1]
    visible = visible.assign(timestamp_utc=visible.timestamp.dt.strftime('%Y-%m-%d %H:%M UTC'))
    for field, title in [('flow_lpm','Flow (litres per minute)'),('pressure_bar','Pressure (bar)')]:
        base = alt.Chart(visible).encode(x=alt.X('timestamp:T', title='UTC timestamp',scale=alt.Scale(type='utc')), y=alt.Y(f'{field}:Q',title=title))
        line = base.mark_line(color='#00897b')
        dots = base.transform_filter(alt.datum.alert).mark_circle(size=35,color='#d1495b').encode(tooltip=['timestamp_utc:N',f'{field}:Q','severity:N','explanation:N'])
        st.altair_chart(line+dots, use_container_width=True)
    st.subheader('Anomaly evidence')
    chart = alt.Chart(visible).mark_line(color='#456990').encode(x=alt.X('timestamp:T',title='UTC timestamp',scale=alt.Scale(type='utc')),y=alt.Y('anomaly_score:Q',title='Anomaly score (higher is unusual)'))
    rule = alt.Chart(pd.DataFrame({'threshold':[detector.threshold]})).mark_rule(color='#d1495b',strokeDash=[5,4]).encode(y='threshold:Q')
    st.altair_chart(chart+rule,use_container_width=True)
    st.caption('Red points are actionable alert readings. Explanations show the largest robust deviations from training medians; they are context, not causal feature attributions.')
    only = st.checkbox('Show flagged or alert readings only',value=True)
    st.dataframe(scored[scored.model_flag | scored.alert] if only else scored, hide_index=True, use_container_width=True)
    st.download_button('Export scored readings',csv_bytes(scored),'scored_readings.csv','text/csv')
with inspection:
    st.subheader('Human review before action')
    st.write('Acknowledge → inspect the meter, pipe and legitimate demand → record findings → resolve after repair or explanation. An alert is a request to inspect, not a confirmed leak.')
    st.dataframe(tickets,hide_index=True,use_container_width=True)
    if not tickets.empty:
        selected = st.selectbox('Inspection ticket', tickets.ticket_id.tolist())
        logs = history(DB)
        previous = [r for r in logs if r[0]==selected]
        current = previous[-1][1] if previous else 'New'
        st.write(f'Current status: **{current}**')
        with st.form('inspection'):
            status = st.selectbox('Next status',STATES,index=STATES.index(current))
            outcome = st.selectbox('Inspection outcome',OUTCOMES)
            notes = st.text_area('Findings and follow-up (no personal data)',max_chars=1000)
            if st.form_submit_button('Save inspection event'):
                try: update(DB,selected,status,outcome,notes); st.success('Inspection event saved.'); st.rerun()
                except ValueError as e: st.error(str(e))
    log = pd.DataFrame(history(DB),columns=['ticket','status','outcome','notes','updated_utc'])
    st.dataframe(log,hide_index=True,use_container_width=True)
    st.download_button('Export inspection audit trail',csv_bytes(log),'inspection_feedback.csv','text/csv')
    st.caption('Local SQLite persistence; shared by users of this app instance. No authentication. Use only synthetic or de-identified data here; hosted temporary storage may reset.')
with methodology:
    st.write(f'Isolation Forest: 200 trees, random seed 42. Training rows: {detector.fit_rows}; separate calibration rows: {detector.calibration_rows}. Threshold: {detector.threshold:.6f}; calibration exceedance rate: {detector.calibration_rate:.2%}.')
    st.write('Features: flow, pressure, backward changes, trailing four-reading flow mean, and cyclic UTC hour. A score above the held-out reference quantile flags a reading. Three consecutive model flags trigger inspection (30 minutes from first to third reading). Pressure below 1.5 bar or flow above 20 L/min triggers an urgent rule alert immediately. Rules are illustrative site assumptions requiring engineering review.')
    st.write('Calibration controls an empirical reference exceedance rate; it does not establish real-world accuracy or a future false-alarm guarantee. Seasonal changes, occupancy, sensor drift and legitimate high demand can alter results. Missed leaks remain possible.')
    st.write('Inspection outcomes inform a later expert-reviewed baseline update; this demo does not automatically retrain. No accuracy, water savings or financial benefit is claimed for real infrastructure.')

from .corr_matrix import corr_grabber

c = corr_grabber()

df = c.grabber(state, 'NO2')
df = df.rename(columns={'Concentration' : 'NO2'})
c.POLL = ['NO2', 'O3', 'SO2', 'UVAI', 'CO', 'HCHO']
for poll in c.POLL[1:]:
    df[poll] = c.grabber(state, poll).Concentration

df = df.drop(columns='Count')
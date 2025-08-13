import rrdtool

rrdtool.graph(
    'daily_wg0.png',
    '--start', '-300',
    '--end', 'now',
    '--title', 'Daily Traffic',
    'DEF:in=./plugins/rrd_data/wg0.rrd:in:AVERAGE',
    'DEF:out=./plugins/rrd_data/wg0.rrd:out:AVERAGE',
    'LINE1:in#00FF00:Incoming Traffic',
    'LINE1:out#0000FF:Outgoing Traffic'
)
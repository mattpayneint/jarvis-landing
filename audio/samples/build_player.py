"""Inject audio/samples/samples.json into the /audio/ sample player (rows + JS data). Re-runnable."""
import json, re, html, os
root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
data = json.load(open(os.path.join(root, 'audio/samples/samples.json')))
keep = [{k: d[k] for k in ('n', 'vol', 'section', 'sectionNum', 'title', 'teaser', 'duration', 'file') if k in d} for d in data]
for d in keep:
    for k in ('title', 'teaser'): assert '—' not in d[k], 'em dash in ' + k
rows = ''.join(
    '<li class="ls-trk"><button type="button"><span class="n">%s</span><span class="ls-eq" aria-hidden="true"><i></i><i></i><i></i></span>'
    '<span><span class="tt">%s</span><span class="ts">%s</span></span><span class="d">%s</span></button></li>'
    % (d.get('vol', d['sectionNum']), html.escape(d['title']), html.escape(d['teaser']), d['duration']) for d in keep)
p = os.path.join(root, 'audio/index.html'); s = open(p).read()
s = re.sub(r'<ol class="ls-list" id="lsList">.*?</ol>', '<ol class="ls-list" id="lsList">' + rows.replace('\\', '\\\\') + '</ol>', s, count=1, flags=re.S)
s = re.sub(r'/\*LS_DATA\*/.*?/\*END\*/', lambda m: '/*LS_DATA*/' + json.dumps(keep, ensure_ascii=False) + '/*END*/', s, count=1, flags=re.S)
tot = sum(int(d['duration'].split(':')[0]) * 60 + int(d['duration'].split(':')[1]) for d in keep)
W = {6:'Six',8:'Eight',9:'Nine',10:'Ten',11:'Eleven',12:'Twelve',13:'Thirteen',14:'Fourteen',15:'Fifteen',16:'Sixteen',17:'Seventeen',18:'Eighteen'}
s = re.sub(r'\w+ samples &middot; about \w+ minutes', '%s samples &middot; about %s minutes' % (W.get(len(keep), str(len(keep))), W.get(round(tot/60), str(round(tot/60))).lower()), s)
open(p, 'w').write(s); print('injected', len(keep), 'tracks,', tot, 's total')

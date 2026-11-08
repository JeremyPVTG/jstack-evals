import importlib.util, json, os, time
spec=importlib.util.spec_from_file_location('judge','judge.py'); j=importlib.util.module_from_spec(spec); spec.loader.exec_module(j)
key=os.environ['TYPESAFE_API_KEY']; qs=json.load(open('data/questions.json')); report=[]; tokens=0; t0=time.time()
for q in qs:
    cands=json.load(open(f"data/candidates-{q['id']}.json")); isgold=lambda u:any(g in u for g in q['gold'])
    rows=j.judge(q['q'],cands,key); tokens+=sum(r['input_tokens'] for r in rows)
    keep=[r for r in rows if r['label'] in('evidence','conflict')][:5]
    base=cands[:5]
    report.append(dict(id=q['id'],gold_in_candidates=sum(isgold(c['url']) for c in cands),base_gold=sum(isgold(c['url']) for c in base),judge_kept=len(keep),judge_gold=sum(isgold(r['url']) for r in keep),
      labels={l:sum(r['label']==l for r in rows) for l in('evidence','conflict','unsettled','drop')},
      dropped_gold=[r['url'] for r in rows if r['label']=='drop' and isgold(r['url'])],
      flagged_injection=[r['url'] for r in rows if r['injection']>0.7]))
    json.dump(rows,open(f"data/{q['id']}.judged.json",'w'),indent=1)
for r in report: print(json.dumps(r))
print(f"uncached input tokens {tokens}, cost ~${tokens*0.042/1e6:.4f}, {time.time()-t0:.1f}s for {sum(len(json.load(open('data/candidates-'+q['id']+'.json'))) for q in qs)} judgments")

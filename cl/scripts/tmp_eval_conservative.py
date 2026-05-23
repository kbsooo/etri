import sys,json,importlib.util
spec=importlib.util.spec_from_file_location('ev','scripts/45_eval_prior_sleep_window.py')
ev=importlib.util.module_from_spec(spec); spec.loader.exec_module(ev)
df=ev.load_df()
oracle=json.loads(open('experiments/probe_prior_sleep_targetwise_best_config.json').read())
oracle={y:tuple(v) for y,v in oracle.items()}
conservative=dict(ev.BASE_CFG)
for y in ['Q1','Q2','S4']:
    conservative[y]=oracle[y]
res,pred=ev.predict_oof(df,conservative,'prior_sleep_conservative_q1q2s4')
res.to_csv('experiments/probe_prior_sleep_conservative_q1q2s4_results.csv',index=False)
pred.to_csv('experiments/probe_prior_sleep_conservative_q1q2s4_oof.csv',index=False)
print(res.to_string(index=False))
print('\nAVG')
print(res.mean(numeric_only=True).to_string())

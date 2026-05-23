#!/usr/bin/env python3
"""Gated S2 sparse-head meta diagnostics.

Follow-up idea after script 64: instead of moving all S2 rows toward the sparse
head, only move rows where the sparse head has a large disagreement with the
anchor and/or agrees in direction with the previous tiny-DL S2 residual.

This reduces public-distribution shift and tests whether the sparse signal is
useful as a targeted correction rather than a wholesale S2 replacement.
"""
from __future__ import annotations
from pathlib import Path
import json
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'outputs'; EXP=ROOT/'experiments'
LABELS=['Q1','Q2','Q3','S1','S2','S3','S4']; IDS=['subject_id','sleep_date','lifelog_date']
TARGET='S2'

def read(name): return pd.read_csv(OUT/name)

def shift_rows(df, anchor):
    rows=[]
    for y in LABELS:
        d=np.abs(df[y].to_numpy(float)-anchor[y].to_numpy(float))
        rows.append({'target':y,'changed_rows':int((d>1e-12).sum()),'mean_abs_delta_vs_anchor':float(d.mean()),'p95_abs_delta_vs_anchor':float(np.quantile(d,.95)),'max_abs_delta_vs_anchor':float(d.max()),'corr_vs_anchor':float(np.corrcoef(df[y],anchor[y])[0,1]) if d.max()>0 else 1.0,'candidate_mean_prob':float(df[y].mean()),'anchor_mean_prob':float(anchor[y].mean()),'mean_prob_shift':float(df[y].mean()-anchor[y].mean())})
    return pd.DataFrame(rows)

def write(name, c, anchor, notes):
    c.to_csv(OUT/name,index=False)
    stem=name.replace('.csv','')
    sh=shift_rows(c,anchor); sh.to_csv(EXP/f'{stem}_shift.csv',index=False)
    (EXP/f'{stem}_notes.json').write_text(json.dumps({'file':str(OUT/name),**notes},ensure_ascii=False,indent=2),encoding='utf-8')
    return sh

def main():
    anchor=read('submission_meta_anchor_w02_noq3_prob.csv')
    prev=read('submission_meta_anchor_plus_s2dl20_prob.csv')
    comp=pd.read_csv(EXP/'s2_sparse_meta_component_predictions.csv')
    anc=comp['anchor_S2'].to_numpy(float)
    raw=comp['s2_sparse_raw32_C0003'].to_numpy(float)
    dl=comp['prev_s2dl20_S2'].to_numpy(float)
    delta=raw-anc
    dl_delta=dl-anc
    absd=np.abs(delta)
    same_dir=np.sign(delta)==np.sign(dl_delta)
    # Ignore exact-zero signs; tiny-DL residual is nonzero for all rows in practice.
    reports=[]
    def add(name, values, mask, desc):
        c=anchor.copy(); c[TARGET]=np.clip(values,.02,.98)
        sh=write(name,c,anchor,{'description':desc,'submission_status':'diagnostic artifact; not automatic submission recommendation','gate_changed_s2_rows':int(mask.sum())})
        s2=sh[sh.target.eq(TARGET)].iloc[0].to_dict()
        reports.append({'file':name,'description':desc,'gate_rows':int(mask.sum()),**{f'S2_{k}':v for k,v in s2.items() if k!='target'}})
    # Top absolute sparse disagreement, move halfway to sparse only on those rows.
    for q in [.50,.70]:
        thr=np.quantile(absd,q)
        mask=absd>=thr
        vals=anc.copy(); vals[mask]=anc[mask]+0.5*delta[mask]
        add(f'submission_meta_anchor_s2sparse_gate_top{int((1-q)*100):02d}_blend50_prob.csv', vals, mask, f'Only rows in top {int((1-q)*100)}% sparse-vs-anchor S2 disagreement move 50% toward sparse head.')
    # Agreement with previous S2-DL residual, move modestly; this tests two independent side tracks agreeing.
    for w in [.30,.50]:
        mask=same_dir
        vals=anc.copy(); vals[mask]=anc[mask]+w*delta[mask]
        add(f'submission_meta_anchor_s2sparse_agreeDL_blend{int(w*100):02d}_prob.csv', vals, mask, f'Rows where sparse S2 and previous S2-DL residual move in same direction; move {int(w*100)}% toward sparse.')
    # Stronger gate: same direction + top half disagreement.
    mask=same_dir & (absd>=np.quantile(absd,.50))
    vals=anc.copy(); vals[mask]=anc[mask]+0.5*delta[mask]
    add('submission_meta_anchor_s2sparse_agreeDL_top50_blend50_prob.csv', vals, mask, 'Only same-direction sparse/DL rows among top 50% sparse disagreement move 50% toward sparse.')
    rep=pd.DataFrame(reports); rep.to_csv(EXP/'s2_sparse_gated_meta_shift_summary.csv',index=False)
    lines=['# S2 sparse gated meta diagnostics','','Diagnostic candidate files were written; no automatic submission recommendation.','','## Shift summary',rep.to_string(index=False,float_format=lambda x:f'{x:.6f}'),'','## Interpretation','Gated candidates reduce changed-row count or require agreement between sparse S2 and previous S2-DL residual. If public probing is scarce, these are safer than full replacement/residual variants, but the plain 30% all-row interpolation remains the cleanest single diagnostic.']
    out=EXP/'s2_sparse_gated_meta_report.md'; out.write_text('\n'.join(lines),encoding='utf-8')
    print('wrote',out)
    print(rep.to_string(index=False))
if __name__=='__main__': main()

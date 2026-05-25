#!/usr/bin/env python3
"""Phase 7: final insight-only checks.

1) S2 contradiction diary: rows where S2 disagrees with S1/S3/S4 majority.
2) id08 vs id10 comparison: both night-phone-heavy, but Q2/Q3 semantics differ.

No modeling, no OOF, no submission.
"""
from __future__ import annotations

from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'data'
ITEMS=DATA/'ch2025_data_items'
AN=ROOT/'analysis'
FIG=AN/'figures'
AN.mkdir(exist_ok=True); FIG.mkdir(exist_ok=True)
KEYS=['subject_id','lifelog_date']
LABELS=['Q1','Q2','Q3','S1','S2','S3','S4']
FEATURES=[
 'steps_sum','activity_sum_21_03','app_total_time','app_unique_count','app_time_21_03','app_social_time','app_media_time','app_browser_search_time','app_game_time',
 'screen_use_sum','screen_use_00_06','screen_use_18_24','longest_screenoff_run_h','longest_quiet_run_h',
 'gps_count','gps_speed_mean','gps_radius_proxy','gps_unique_grid4','wifi_unique_bssid','ble_records','ble_unique_addr',
 'hr_count','hr_mean','hr_std','hr_mean_00_06','hr_mean_21_03','mlight_mean','wlight_mean','state_entropy','night_state_entropy'
]
APP_CATS={
 'messaging_social':['카카오톡','instagram','facebook','discord','threads','메시지','라인','twitter','x'],
 'video_music_media':['youtube','melon','music','넷플릭스','netflix','티빙','wavve','spotify','동영상','웹툰','tiktok'],
 'finance_auth':['bank','뱅크','카드','pay','페이','토스','kb','신한','auth','인증','증권','stock'],
 'mobility_car':['tmap','카카오t','네이버지도','지도','kia','auto','버스','지하철','길찾기','코레일'],
 'shopping_delivery':['shop','쇼핑','쿠팡','배달','mart','몰','store','당근'],
 'work_study':['teams','slack','notion','docs','pdf','office','word','excel','class','study','학교','캘린더'],
 'game':['game','게임','bricks','goblin','sort','nonogram','match','클래시','royal'],
 'utility_home':['one ui','시스템','설정','카메라','갤러리','전화','통화','lg thinq','weather','날씨','launcher'],
 'religion_health':['성경','bible','캐시워크','health','fit','samsung health','건강','타임스프레드'],
}
AXES={
 'low_activity':['steps_sum__z','activity_sum_21_03__z'],
 'night_phone':['screen_use_00_06__z','screen_use_18_24__z','app_time_21_03__z'],
 'phone_internal':['app_total_time__z','app_unique_count__z','app_social_time__z','app_media_time__z'],
 'rest_quiet':['longest_screenoff_run_h__z','longest_quiet_run_h__z'],
 'low_mobility_context':['gps_radius_proxy__z','gps_unique_grid4__z','wifi_unique_bssid__z','ble_unique_addr__z','state_entropy__z'],
 'physio_light_low':['hr_mean__z','hr_std__z','mlight_mean__z','wlight_mean__z'],
}

def md_table(df,max_rows=None,floatfmt='.3f'):
    d=df.copy()
    if max_rows is not None: d=d.head(max_rows)
    cols=list(d.columns)
    lines=['| '+' | '.join(map(str,cols))+' |','|'+'|'.join(['---']*len(cols))+'|']
    for _,r in d.iterrows():
        cells=[]
        for v in r.tolist():
            if isinstance(v,(float,np.floating)) and not pd.isna(v): cells.append(format(float(v),floatfmt))
            else: cells.append(str(v))
        lines.append('| '+' | '.join(cells)+' |')
    return '\n'.join(lines)

def cat_app(a):
    s=str(a).strip().lower()
    for cat,kws in APP_CATS.items():
        if any(kw.lower() in s for kw in kws): return cat
    return 'other'

def parse_list(x):
    if isinstance(x,list): return x
    if isinstance(x,np.ndarray): return x.tolist()
    return []

def load():
    train=pd.read_csv(DATA/'ch2026_metrics_train.csv')
    train['lifelog_date']=pd.to_datetime(train['lifelog_date']).dt.date.astype(str)
    feat=pd.read_parquet(ROOT/'features'/'model_features_v0.parquet')
    feat['lifelog_date']=pd.to_datetime(feat['lifelog_date']).dt.date.astype(str)
    keep=KEYS+[c for c in FEATURES if c in feat.columns]
    df=train.merge(feat[keep],on=KEYS,how='left')
    df['date']=pd.to_datetime(df['lifelog_date'])
    for c in [c for c in FEATURES if c in df.columns]:
        g=df.groupby('subject_id')[c]
        df[c+'__z']=(df[c]-g.transform('mean'))/g.transform('std').replace(0,np.nan)
    raw=pd.read_parquet(ITEMS/'ch2025_mUsageStats.parquet')
    raw['lifelog_date']=pd.to_datetime(raw['timestamp']).dt.date.astype(str)
    rows=[]
    for _,r in raw.iterrows():
        hour=pd.to_datetime(r.timestamp).hour+pd.to_datetime(r.timestamp).minute/60
        for it in parse_list(r.m_usage_stats):
            app=str(it.get('app_name','')).strip().lower(); sec=float(it.get('total_time',0) or 0)/1000
            if app and sec>0: rows.append({'subject_id':r.subject_id,'lifelog_date':r.lifelog_date,'hour':hour,'app':app,'category':cat_app(app),'minutes':sec/60})
    app=pd.DataFrame(rows)
    if len(app):
        cat=app.groupby(KEYS+['category'],as_index=False)['minutes'].sum().pivot_table(index=KEYS,columns='category',values='minutes',fill_value=0).reset_index()
        top=app.groupby(KEYS+['app'],as_index=False)['minutes'].sum().sort_values(KEYS+['minutes'],ascending=[True,True,False])
        df=df.merge(cat,on=KEYS,how='left')
        for c in [c for c in cat.columns if c not in KEYS]:
            df[c]=df[c].fillna(0)
            g=df.groupby('subject_id')[c]
            df[c+'__z']=(df[c]-g.transform('mean'))/g.transform('std').replace(0,np.nan)
    else:
        top=pd.DataFrame(columns=KEYS+['app','minutes'])
    for axis,cols in AXES.items():
        cc=[c for c in cols if c in df.columns]
        val=df[cc].mean(axis=1) if cc else np.nan
        if axis in {'low_activity','low_mobility_context','physio_light_low'}: val=-val
        df[axis]=val
    return df,app,top

def top_apps(top,sid,date,n=4):
    x=top[(top.subject_id==sid)&(top.lifelog_date==date)].head(n)
    return ', '.join(f"{r.app}({r.minutes:.0f}m)" for _,r in x.iterrows())

def s2_contradictions(df,top):
    d=df.copy()
    d['s_majority']=((d['S1']+d['S3']+d['S4'])>=2).astype(int)
    d['s_sum_other']=d['S1']+d['S3']+d['S4']
    d['s2_case']=np.where((d.S2==1)&(d.s_majority==0),'S2_only_high',np.where((d.S2==0)&(d.s_majority==1),'S2_only_low','aligned'))
    summary=d.groupby(['subject_id','s2_case']).size().unstack(fill_value=0).reset_index()
    for c in ['S2_only_high','S2_only_low','aligned']:
        if c not in summary: summary[c]=0
    summary['contradiction_rate']=(summary['S2_only_high']+summary['S2_only_low'])/summary[['S2_only_high','S2_only_low','aligned']].sum(axis=1)
    summary.to_csv(AN/'phase7_s2_contradiction_by_subject.csv',index=False)
    cases=d[d.s2_case!='aligned'].copy()
    axes=list(AXES.keys())
    prof=cases.groupby('s2_case').agg(n_days=('S2','size'),Q1_rate=('Q1','mean'),Q2_rate=('Q2','mean'),Q3_rate=('Q3','mean'),S1_rate=('S1','mean'),S2_rate=('S2','mean'),S3_rate=('S3','mean'),S4_rate=('S4','mean'))
    axmean=cases.groupby('s2_case')[axes].mean()
    prof=prof.join(axmean).reset_index()
    prof.to_csv(AN/'phase7_s2_contradiction_profiles.csv',index=False)
    cases['intensity']=cases[axes].abs().mean(axis=1)
    ex=cases.sort_values('intensity',ascending=False).head(40).copy()
    ex['top_axes']=ex.apply(lambda r:', '.join(f"{a}:{r[a]:+.2f}" for a in sorted(axes,key=lambda a:abs(r[a]) if pd.notna(r[a]) else -1, reverse=True)[:3]),axis=1)
    ex['top_apps']=ex.apply(lambda r:top_apps(top,r.subject_id,r.lifelog_date),axis=1)
    cols=KEYS+['s2_case','Q1','Q2','Q3','S1','S2','S3','S4','top_axes','steps_sum','screen_use_00_06','longest_screenoff_run_h','gps_radius_proxy','wifi_unique_bssid','hr_mean','top_apps']
    ex[cols].to_csv(AN/'phase7_s2_contradiction_diaries.csv',index=False)
    # fig
    plot=prof.set_index('s2_case')[axes]
    fig,ax=plt.subplots(figsize=(8,3.5)); im=ax.imshow(plot.values,aspect='auto',cmap='coolwarm',vmin=-.6,vmax=.6)
    ax.set_xticks(range(len(axes)),axes,rotation=35,ha='right'); ax.set_yticks(range(len(plot.index)),plot.index)
    ax.set_title('Phase7: S2 contradiction axis profiles'); fig.colorbar(im,ax=ax,fraction=.03); fig.tight_layout(); fig.savefig(FIG/'p7_s2_contradiction_profiles.png',dpi=180); plt.close(fig)
    lines=['# Phase 7A — S2 contradiction diary\n','S2가 S1/S3/S4 majority와 충돌하는 row를 따로 봤다.\n','## subject별 contradiction rate\n',md_table(summary.round(3)),'\n## S2 contradiction profile\n',md_table(prof.round(3)),'\n## high-intensity contradiction diaries\n',md_table(ex[cols].round(2),max_rows=40),'\n']
    (AN/'phase7_A_s2_contradiction_diary.md').write_text('\n'.join(lines),encoding='utf-8')
    return summary,prof,ex

def id08_id10(df,top):
    sub=df[df.subject_id.isin(['id08','id10'])].copy()
    axes=list(AXES.keys())
    base=sub.groupby('subject_id').agg(n_days=('Q1','size'),Q1_rate=('Q1','mean'),Q2_rate=('Q2','mean'),Q3_rate=('Q3','mean'),S1_rate=('S1','mean'),S2_rate=('S2','mean'),S3_rate=('S3','mean'),S4_rate=('S4','mean'),night_screen_mean=('screen_use_00_06','mean'),screenoff_h=('longest_screenoff_run_h','mean'),gps_radius=('gps_radius_proxy','mean'),steps=('steps_sum','mean'),app_total=('app_total_time','mean')).reset_index()
    axis_by_label=[]
    for sid,g in sub.groupby('subject_id'):
        for q2 in [0,1]:
            for q3 in [0,1]:
                h=g[(g.Q2==q2)&(g.Q3==q3)]
                if not len(h): continue
                rec={'subject_id':sid,'class':f'Q2={q2},Q3={q3}','n_days':len(h),'Q1_rate':h.Q1.mean()}
                for a in axes: rec[a]=h[a].mean()
                axis_by_label.append(rec)
    axisdf=pd.DataFrame(axis_by_label)
    base.to_csv(AN/'phase7_id08_id10_base_compare.csv',index=False)
    axisdf.to_csv(AN/'phase7_id08_id10_q2q3_axis_compare.csv',index=False)
    appsum=[]
    for sid in ['id08','id10']:
        apps=top[top.subject_id==sid].groupby('app',as_index=False)['minutes'].sum().sort_values('minutes',ascending=False).head(12)
        for _,r in apps.iterrows(): appsum.append({'subject_id':sid,'app':r.app,'minutes':r.minutes})
    appdf=pd.DataFrame(appsum); appdf.to_csv(AN/'phase7_id08_id10_top_apps.csv',index=False)
    # Q2 transitions for two subjects
    sub=sub.sort_values(['subject_id','date'])
    sub['prev_Q2']=sub.groupby('subject_id')['Q2'].shift(1)
    trans=sub[(sub.prev_Q2==0)&(sub.Q2==1)].copy()
    trans['top_axes']=trans.apply(lambda r:', '.join(f"{a}:{r[a]:+.2f}" for a in sorted(axes,key=lambda a:abs(r[a]) if pd.notna(r[a]) else -1, reverse=True)[:3]),axis=1)
    trans['top_apps']=trans.apply(lambda r:top_apps(top,r.subject_id,r.lifelog_date),axis=1)
    tcols=KEYS+['Q1','Q2','Q3','S1','S2','S3','S4','top_axes','screen_use_00_06','longest_screenoff_run_h','gps_radius_proxy','steps_sum','top_apps']
    trans[tcols].to_csv(AN/'phase7_id08_id10_q2_transition_diaries.csv',index=False)
    # fig
    piv=axisdf.set_index(['subject_id','class'])[axes]
    fig,ax=plt.subplots(figsize=(9,4)); im=ax.imshow(piv.values,aspect='auto',cmap='coolwarm',vmin=-1,vmax=1)
    ax.set_xticks(range(len(axes)),axes,rotation=35,ha='right'); ax.set_yticks(range(len(piv.index)),[f'{a}/{b}' for a,b in piv.index])
    ax.set_title('Phase7: id08 vs id10 Q2/Q3 class axes'); fig.colorbar(im,ax=ax,fraction=.03); fig.tight_layout(); fig.savefig(FIG/'p7_id08_id10_q2q3_axes.png',dpi=180); plt.close(fig)
    lines=['# Phase 7B — id08 vs id10 night-phone regime 비교\n','둘 다 night-phone/short screen-off 계열이지만 Q2/Q3 라벨 구조가 다르다.\n','## base comparison\n',md_table(base.round(3)),'\n## Q2/Q3 class axis comparison\n',md_table(axisdf.round(3)),'\n## top apps\n',md_table(appdf.round(1),max_rows=30),'\n## Q2 transition diaries\n',md_table(trans[tcols].round(2),max_rows=30),'\n']
    (AN/'phase7_B_id08_id10_comparison.md').write_text('\n'.join(lines),encoding='utf-8')
    return base,axisdf,appdf,trans

def synthesis(s2sum,s2prof,s2ex,base,axisdf,trans):
    worst=s2sum.sort_values('contradiction_rate',ascending=False).head(3)
    s2hi=s2prof[s2prof.s2_case=='S2_only_high']
    s2lo=s2prof[s2prof.s2_case=='S2_only_low']
    lines=['# Phase 7 synthesis — S2 contradiction + id08/id10 비교\n','이번 Phase 7은 insight-only 마지막 점검이다. 목적은 S2 미스터리와 id08/id10 night-phone regime 차이를 닫는 것.\n','## 핵심 발견\n']
    lines.append('1. **S2 contradiction은 subject별로 꽤 크다.** contradiction rate 상위 subject:\n')
    lines.append(md_table(worst[['subject_id','S2_only_high','S2_only_low','aligned','contradiction_rate']].round(3)))
    if len(s2hi) and len(s2lo):
        h=s2hi.iloc[0]; l=s2lo.iloc[0]
        lines.append(f"\n2. **S2_only_high와 S2_only_low는 반대 생활축이 아니다.** S2_only_high는 Q2_rate={h.Q2_rate:.3f}, Q3_rate={h.Q3_rate:.3f}; S2_only_low는 Q2_rate={l.Q2_rate:.3f}, Q3_rate={l.Q3_rate:.3f}. 즉 S2는 단순 severity/latent S-axis로 설명되지 않는다.\n")
        lines.append(f"   - S2_only_high axes: low_activity={h.low_activity:+.2f}, night_phone={h.night_phone:+.2f}, low_mobility_context={h.low_mobility_context:+.2f}\n")
        lines.append(f"   - S2_only_low axes: low_activity={l.low_activity:+.2f}, night_phone={l.night_phone:+.2f}, low_mobility_context={l.low_mobility_context:+.2f}\n")
    b=base.set_index('subject_id')
    if 'id08' in b.index and 'id10' in b.index:
        lines.append(f"\n3. **id08/id10은 둘 다 night-phone heavy지만 label grammar가 다르다.** id08: Q2={b.loc['id08','Q2_rate']:.3f}, Q3={b.loc['id08','Q3_rate']:.3f}, night_screen={b.loc['id08','night_screen_mean']:.1f}; id10: Q2={b.loc['id10','Q2_rate']:.3f}, Q3={b.loc['id10','Q3_rate']:.3f}, night_screen={b.loc['id10','night_screen_mean']:.1f}. id10은 밤폰이 더 극단적이고 Q3가 더 잘 붙는다. id08은 Q2-high지만 Q3가 덜 붙는다.\n")
    lines.append('\n## 결론\n')
    lines.append('- S2는 freeze/no-latent 대상이라는 판단이 더 강해졌다. S2 contradiction row가 Q/S/inward day 축과 일관되게 정렬되지 않는다.\n')
    lines.append('- id08과 id10은 같은 night-phone family 안에서도 다른 라벨 언어를 가진다. 따라서 subject/regime card 없이 전역 규칙으로 Q2/Q3를 해석하면 위험하다.\n')
    lines.append('- 이제 insight-only 단계는 충분히 닫아도 된다. 더 하면 raw diary 수집은 늘겠지만 큰 구조 결론은 크게 안 바뀔 가능성이 높다.\n')
    lines.append('\n## Outputs\n- `analysis/phase7_A_s2_contradiction_diary.md`\n- `analysis/phase7_B_id08_id10_comparison.md`\n- `analysis/phase7_*.csv`\n- `analysis/figures/p7_*.png`\n')
    (AN/'phase7_synthesis_report.md').write_text('\n'.join(lines),encoding='utf-8')
    idx='''# Phase 7 index — Final insight-only checks

No model, no OOF, no submission.

1. `analysis/phase7_A_s2_contradiction_diary.md`
2. `analysis/phase7_B_id08_id10_comparison.md`
3. `analysis/phase7_synthesis_report.md`
4. `analysis/phase7_*.csv`
5. `analysis/figures/p7_*.png`
'''
    (AN/'phase7_index.md').write_text(idx,encoding='utf-8')

def main():
    df,app,top=load()
    s2sum,s2prof,s2ex=s2_contradictions(df,top)
    base,axisdf,appdf,trans=id08_id10(df,top)
    synthesis(s2sum,s2prof,s2ex,base,axisdf,trans)
    print('WROTE Phase 7 reports under',AN)
if __name__=='__main__': main()

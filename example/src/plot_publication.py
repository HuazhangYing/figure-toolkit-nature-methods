"""Publication-style figures from explicitly simulated, editable source CSVs."""
from pathlib import Path
import argparse
import hashlib
import json
import os
import subprocess
import sys
import warnings

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager
import numpy as np
import pandas as pd
from scipy import stats

ROOT=Path(__file__).resolve().parents[1]
TOOLKIT=ROOT.parents[1]
sys.path.insert(0,str(TOOLKIT))
from publication_style import apply_style, create_figure, save_figure, style_axis, PALETTE

CONTROL=PALETTE['grey']; TREATED=PALETTE['blue']; UP=PALETTE['vermillion']
CONDITIONS=['Vehicle','Compound X']


def paired_table(df,value):
    table=df.pivot(index='donor',columns='condition',values=value).reindex(columns=CONDITIONS)
    if table.isna().any().any(): raise ValueError('Incomplete pairing; resolve missingness explicitly.')
    return table


def ci(values):
    values=np.asarray(values)
    mean=values.mean(axis=0)
    half=stats.t.ppf(.975,len(values)-1)*stats.sem(values,axis=0)
    return mean,mean-half,mean+half


def bh(p):
    order=np.argsort(p); ranked=np.asarray(p)[order]; n=len(ranked)
    q=np.minimum.accumulate((ranked*n/np.arange(1,n+1))[::-1])[::-1]
    out=np.empty(n);out[order]=np.minimum(q,1);return out


def panel(fig,rect,label):
    ax=fig.add_axes(rect)
    fig.text(rect[0]-.052,rect[1]+rect[3]+.033,label,fontsize=8,fontweight='bold',va='bottom')
    style_axis(ax)
    return ax


def mark(ax,text):
    ax.text(.04,.96,text,transform=ax.transAxes,ha='left',va='top',fontsize=5.5)


def export(fig,name,files,statistics):
    fig.canvas.draw()
    # Verify Arial text and minimum final-size typography before export.
    from matplotlib.text import Text
    for item in fig.findobj(Text):
        if item.get_visible() and item.get_text():
            if item.get_fontsize()<5: raise ValueError('Text below 5 pt: '+item.get_text())
    hashes={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
    save_figure(fig,Path('exports')/name,preview_dpi=450,
        data_files=[p.relative_to(ROOT) for p in files],stats=statistics,
        metadata={'synthetic':True,'purpose':'Simulated study; figure-design demonstration, not experimental evidence',
                  'source_code':'src/plot_publication.py','data_sha256':hashes,'simulation_seed':41827,
                  'font_family':'Arial','captions':'CAPTIONS.md'},close=True)


def figure1():
    paths=[ROOT/'data'/n for n in ['paired_activity.csv','dose_response.csv','kinetics.csv','method_comparison.csv']]
    activity,dose,kinetics,methods=[pd.read_csv(p) for p in paths]
    paired=paired_table(activity,'activity_nmol_min_mg')
    n=len(paired)
    if n<3: raise ValueError('Need at least three paired donors')
    vehicle=paired['Vehicle'];treated=paired['Compound X']
    fig,_=create_figure(width='double',height_mm=126); fig.clear()
    rects=[[.09,.60,.235,.31],[.415,.60,.235,.31],[.74,.60,.235,.31],
           [.09,.145,.235,.31],[.415,.145,.235,.31],[.74,.145,.235,.31]]
    axes=[panel(fig,r,l) for r,l in zip(rects,'abcdef')]
    ax=axes[0]
    response=dose.pivot(index='donor',columns='concentration_um',values='activity_nmol_min_mg').reindex(index=paired.index)
    if response.isna().any().any(): raise ValueError('Incomplete concentration series')
    normalized=response.div(vehicle,axis=0)*100
    m,lo,hi=ci(normalized.to_numpy());x=normalized.columns.to_numpy()
    ax.fill_between(x,lo,hi,color=TREATED,alpha=.15,lw=0)
    ax.plot(x,m,'o-',color=TREATED,ms=2.5,lw=.85)
    ax.set_xscale('log');ax.set_xticks([.01,.1,1,10,100],['0.01','0.1','1','10','100'])
    ax.set_ylim(0,115);ax.set_yticks([0,25,50,75,100])
    ax.set_xlabel('Compound X (µM)');ax.set_ylabel('Residual kinase activity (%)')
    mark(ax,f'n = {n} donors')
    ax=axes[1]
    for _,row in paired.iterrows():
        ax.plot([0,1],row.values,color='.78',lw=.55,zorder=0)
    for j,color in enumerate([CONTROL,TREATED]):
        ax.scatter(np.full(n,j),paired.iloc[:,j],s=9,color=color,linewidths=.35,edgecolors='white',zorder=3)
        mean,low,high=ci(paired.iloc[:,j])
        ax.errorbar(j+.18,mean,yerr=[[mean-low],[high-mean]],fmt='_',color='black',capsize=2,ms=5,lw=.8)
    ax.set_xlim(-.35,1.5);ax.set_ylim(0,165)
    ax.set_xticks([0,1],['Vehicle','Compound X'])
    ax.set_ylabel('Kinase activity (nmol/min/mg)')
    ax.plot([0,0,1,1],[148,153,153,148],lw=.65,color='black')
    test=stats.ttest_rel(treated,vehicle)
    ax.text(.5,157,f'P = {test.pvalue:.2g}',ha='center',fontsize=5.5)
    ax=axes[2]
    for condition,color,marker in zip(CONDITIONS,[CONTROL,TREATED],['o','s']):
        k=kinetics.loc[kinetics.condition==condition].pivot(index='donor',columns='time_min',values='product_nmol_mg')
        m,lo,hi=ci(k.to_numpy());t=k.columns.to_numpy()
        ax.fill_between(t,lo,hi,color=color,alpha=.13,lw=0)
        ax.plot(t,m,marker=marker,color=color,ms=2.3,label=condition,lw=.85)
    ax.set_xlabel('Reaction time (min)');ax.set_ylabel('Product (nmol/mg)')
    ax.set_xlim(-2,62);ax.set_ylim(-5,300);ax.set_xticks([0,20,40,60])
    ax.legend(loc='upper left',handlelength=1.3,borderaxespad=.1)
    averaged=methods.groupby('donor')[['reference_activity','candidate_activity']].mean()
    ref=averaged.reference_activity.to_numpy();candidate=averaged.candidate_activity.to_numpy()
    ax=axes[3]
    lower=min(ref.min(),candidate.min())-8;upper=max(ref.max(),candidate.max())+8
    ax.plot([lower,upper],[lower,upper],ls='--',color='.65',lw=.65,zorder=0)
    ax.scatter(ref,candidate,color=TREATED,s=13,edgecolors='white',linewidths=.35)
    ax.set_xlim(lower,upper);ax.set_ylim(lower,upper)
    ax.set_xlabel('Reference assay (nmol/min/mg)');ax.set_ylabel('Candidate assay (nmol/min/mg)')
    corr=stats.pearsonr(ref,candidate)
    mark(ax,f'Pearson r = {corr.statistic:.2f}\nn = {len(ref)} donors')
    ax=axes[4]
    avg=(ref+candidate)/2;diff=candidate-ref
    bias=diff.mean();sd=diff.std(ddof=1);limits=[bias-1.96*sd,bias+1.96*sd]
    ax.axhline(0,color='.86',lw=.55,zorder=0)
    for value,ls in [(bias,'-'),(limits[0],'--'),(limits[1],'--')]:
        ax.axhline(value,color='.4',ls=ls,lw=.65)
    ax.scatter(avg,diff,s=13,color=TREATED,edgecolors='white',linewidths=.35,zorder=3)
    ax.set_ylim(min(limits[0],diff.min())-7,max(limits[1],diff.max())+7)
    ax.set_xlabel('Mean of assays (nmol/min/mg)');ax.set_ylabel('Candidate − reference\n(nmol/min/mg)')
    mark(ax,f'Bias = {bias:.1f}\n95% limits: {limits[0]:.1f}, {limits[1]:.1f}')
    ax=axes[5]
    reduction=(1-treated/vehicle)*100
    m,low,high=ci(reduction)
    # Original donor order is preserved; every donor remains visible.
    ax.scatter(reduction,np.arange(n),s=10,color=TREATED,linewidths=0)
    ax.axvline(m,color='black',lw=.7)
    ax.axvspan(low,high,color='.85',alpha=.6,zorder=0)
    ax.set_yticks(np.arange(n),paired.index);ax.invert_yaxis();ax.set_xlim(0,100)
    ax.set_xlabel('Activity reduction (%)');ax.set_ylabel('Donor')
    result={'paired_donors':n,'unit':'donor; technical duplicates averaged before method comparison',
            'paired_activity_test':{'method':'two-sided paired t-test; one prespecified comparison','p':float(test.pvalue),'t':float(test.statistic),'df':n-1},
            'reduction_percent':{'mean':float(m),'ci95':[float(low),float(high)],'method':'Student t interval across donor-specific percentage reductions'},
            'method_comparison':{'pearson_r':float(corr.statistic),'bias':float(bias),'limits_of_agreement':limits},
            'bands':'pointwise 95% t intervals across donors; not simultaneous bands',
            'excluded_observations':0,'synthetic':True}
    (ROOT/'data/assay_statistics.json').write_text(json.dumps(result,indent=2))
    export(fig,'Fig1_assay_validation_SIMULATED',paths,result)


def figure2():
    path=ROOT/'data/proteomics.csv';df=pd.read_csv(path)
    records=[];changes={};baselines={}
    for protein,group in df.groupby('protein',sort=True):
        p=paired_table(group,'log2_intensity');d=p['Compound X']-p.Vehicle
        m,lo,hi=ci(d)
        records.append((protein,len(d),float(m),float(lo),float(hi),float(stats.ttest_1samp(d,0).pvalue)))
        changes[protein]=d;baselines[protein]=p.Vehicle.mean()
    results=pd.DataFrame(records,columns=['protein','n_donors','log2_fold_change','ci95_low','ci95_high','p'])
    results['q']=bh(results.p.to_numpy())
    results['status']='Not selected'
    results.loc[(results.q<.05)&(results.log2_fold_change>=.5),'status']='Increased'
    results.loc[(results.q<.05)&(results.log2_fold_change<=-.5),'status']='Decreased'
    results.to_csv(ROOT/'data/protein_statistics.csv',index=False)
    n_donors=int(results.n_donors.iloc[0])
    selected=results.sort_values(['q','protein']).head(16).protein.tolist()
    matrix=pd.DataFrame(changes).T.loc[selected]
    fig,_=create_figure(width='double',height_mm=132);fig.clear()
    ax=panel(fig,[.095,.59,.34,.32],'a')
    colors={'Not selected':'.76','Decreased':TREATED,'Increased':UP}
    for name,color in colors.items():
        r=results.loc[results.status==name]
        ax.scatter(r.log2_fold_change,-np.log10(r.q.clip(lower=np.finfo(float).tiny)),s=5 if name=='Not selected' else 8,color=color,linewidths=0,alpha=.8,label=f'{name} ({len(r)})')
    ax.axhline(-np.log10(.05),ls='--',lw=.55,color='.55')
    for x in [-.5,.5]:ax.axvline(x,ls='--',lw=.55,color='.55')
    fold_limit=np.ceil(results.log2_fold_change.abs().max()*10)/10+.1
    ax.set_xlim(-fold_limit,fold_limit);ax.set_ylim(0,float((-np.log10(results.q)).max())*1.22)
    ax.set_xlabel('Mean paired log2 fold change');ax.set_ylabel('−log10 BH-adjusted P')
    ax.legend(loc='upper right',markerscale=1.1,handletextpad=.2,labelspacing=.3,borderaxespad=.2)
    ax=panel(fig,[.605,.59,.32,.32],'b')
    r=results.sort_values(['q','protein']).head(8).iloc[::-1]
    for i,row in enumerate(r.itertuples()):
        color=colors[row.status]
        ax.errorbar(row.log2_fold_change,i,xerr=[[row.log2_fold_change-row.ci95_low],[row.ci95_high-row.log2_fold_change]],fmt='o',ms=3,color=color,capsize=2,lw=.8)
    ax.axvline(0,ls='--',lw=.55,color='.5')
    ax.set_yticks(range(len(r)),r.protein);ax.set_ylabel('Protein identifier')
    ax.set_xlabel('Paired log2 fold change (95% CI)');ax.set_ylim(-.7,len(r)-.3)
    ax=panel(fig,[.095,.115,.34,.32],'c')
    # All proteins enter each donor summary; columns are donors, not independent cells.
    for condition,color,marker in [('Vehicle',CONTROL,'o'),('Compound X',TREATED,'s')]:
        table=df.loc[df.condition==condition].pivot(index='protein',columns='donor',values='log2_intensity')
        # Summaries over proteins are descriptive within donor, not an inferential N=420.
        values=table.median(axis=0).sort_values().to_numpy()
        ax.step(np.r_[values[0],values],np.r_[0,np.arange(1,len(values)+1)/len(values)],where='post',color=color,lw=.9,label=condition)
        ax.scatter(values,np.arange(1,len(values)+1)/len(values),s=8,color=color,marker=marker,linewidths=0)
    ax.set_xlabel('Donor median log2 intensity');ax.set_ylabel('Cumulative donor fraction')
    ax.set_ylim(0,1.07);ax.set_yticks([0,.25,.5,.75,1]);ax.legend(loc='upper left',borderaxespad=.2,handlelength=1.2)
    ax=panel(fig,[.605,.115,.32,.32],'d')
    im=ax.imshow(matrix.to_numpy(),vmin=-1.5,vmax=1.5,cmap='RdBu_r',aspect='auto',interpolation='nearest')
    ax.set_xticks(range(n_donors),matrix.columns,rotation=90)
    ax.set_yticks(range(len(matrix)),matrix.index)
    ax.tick_params(length=0,pad=2)
    ax.set_xlabel('Donor');ax.set_ylabel('Protein identifier')
    colorax=fig.add_axes([.94,.115,.012,.32])
    cb=fig.colorbar(im,cax=colorax,ticks=[-1.5,0,1.5],extend='both');cb.ax.set_title('log2 FC',fontsize=5.5,pad=4);cb.outline.set_linewidth(.5)
    stat={'synthetic':True,'n_donors':n_donors,'n_proteins':len(results),'unit':'paired donor',
          'test':'two-sided one-sample t-test on donor-specific log2 treated-minus-vehicle differences',
          'multiple_testing':'Benjamini–Hochberg across all 420 proteins',
          'selection':'q < 0.05 and |mean log2 fold change| >= 0.5',
          'volcano_x_limits':[-float(fold_limit),float(fold_limit)],
          'protein_counts':results.status.value_counts().to_dict(),
          'intervals':'pointwise 95% Student t; selected features; not simultaneous or selection-adjusted',
          'heatmap':'top 16 proteins ranked by q then ID; columns in donor ID order; paired differences, no row scaling or clustering',
          'ecdf':'donor-level median over all measured proteins; descriptive only; no inference across proteins',
          'exclusions':0}
    (ROOT/'data/proteomics_statistics.json').write_text(json.dumps(stat,indent=2))
    export(fig,'Fig2_proteomic_response_SIMULATED',[path,ROOT/'data/protein_statistics.csv'],stat)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--font-dir',type=Path)
    parser.add_argument('--figure',choices=['all','1','2'],default='all')
    args=parser.parse_args()
    if args.font_dir:
        for p in args.font_dir.rglob('*'):
            if p.suffix.lower()=='.ttf':font_manager.fontManager.addfont(str(p))
    cfg=apply_style(strict_fonts=True)
    if cfg['resolved_font']!='Arial':raise RuntimeError('Install Arial or pass --font-dir')
    os.chdir(ROOT)
    if args.figure in ['all','1']:figure1()
    if args.figure in ['all','2']:figure2()
    subprocess.run([sys.executable,str(TOOLKIT/'figure_qc.py'),'exports','--strict'],check=True)
    print('Finished. Source tables unchanged; computed statistics saved in data/.')

if __name__=='__main__': main()

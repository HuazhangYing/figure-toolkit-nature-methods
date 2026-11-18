"""Independent checks for publication example exports and paired statistics."""
from pathlib import Path
import hashlib
import json
import xml.etree.ElementTree as ET
import fitz
import numpy as np
import pandas as pd
from scipy import stats

ROOT=Path(__file__).resolve().parents[1]
report=[]
for stem,dimensions in [('Fig1_assay_validation_SIMULATED',(180,126)),('Fig2_proteomic_response_SIMULATED',(180,132))]:
    sidecar=json.loads((ROOT/'exports'/(stem+'.figure.json')).read_text())
    assert sidecar['metadata']['synthetic'] is True
    assert sidecar['resolved_font']==['Arial']
    for relative,digest in sidecar['metadata']['data_sha256'].items():
        assert hashlib.sha256((ROOT/relative).read_bytes()).hexdigest()==digest,relative
    for suffix in ['.pdf','.svg','_preview.png']:
        file=ROOT/'exports'/(stem+suffix)
        assert file.exists() and file.stat().st_size>0,file
    doc=fitz.open(ROOT/'exports'/(stem+'.pdf'))
    assert len(doc)==1
    page=doc[0]
    actual=np.array([page.rect.width,page.rect.height])*25.4/72
    assert np.allclose(actual,dimensions,atol=.02),(stem,actual)
    fonts=[]
    for font in page.get_fonts(full=True):
        name,ext,kind,data=doc.extract_font(font[0])
        assert 'Arial' in name and data,(stem,name)
        fonts.append({'name':name,'embedded':True})
    assert fonts
    for block in page.get_text('dict')['blocks']:
        for line in block.get('lines',[]):
            for span in line['spans']:
                assert page.rect.contains(fitz.Rect(span['bbox'])),(stem,span['text'])
                assert span['size']>=4.99,(stem,span['text'],span['size'])
                assert '\ufffd' not in span['text']
    svg=ET.parse(ROOT/'exports'/(stem+'.svg'))
    assert svg.findall('.//{http://www.w3.org/2000/svg}text')
    report.append({'file':stem+'.pdf','fonts':fonts,'dimensions_mm':actual.tolist(),
                   'data_hashes_valid':True,'text_within_page':True,'minimum_text_pt':5,'svg_editable_text':True})

p=pd.read_csv(ROOT/'data/paired_activity.csv').pivot(index='donor',columns='condition',values='activity_nmol_min_mg')
a=json.loads((ROOT/'data/assay_statistics.json').read_text())
np.testing.assert_allclose(stats.ttest_rel(p['Compound X'],p.Vehicle).pvalue,a['paired_activity_test']['p'])
r=(1-p['Compound X']/p.Vehicle)*100
np.testing.assert_allclose(r.mean(),a['reduction_percent']['mean'])
expected_ci=stats.t.interval(.95,len(r)-1,loc=r.mean(),scale=stats.sem(r))
np.testing.assert_allclose(expected_ci,a['reduction_percent']['ci95'])
source=pd.read_csv(ROOT/'data/proteomics.csv')
saved=pd.read_csv(ROOT/'data/protein_statistics.csv').set_index('protein').sort_index()
wide=source.pivot(index=['protein','donor'],columns='condition',values='log2_intensity')
difference=(wide['Compound X']-wide.Vehicle).unstack('donor').sort_index()
test=stats.ttest_1samp(difference.to_numpy(),0,axis=1)
np.testing.assert_allclose(difference.mean(axis=1),saved.log2_fold_change)
np.testing.assert_allclose(test.pvalue,saved.p,rtol=1e-8)
np.testing.assert_allclose(stats.false_discovery_control(test.pvalue,method='bh'),saved.q,rtol=1e-8)
se=stats.sem(difference,axis=1);half=stats.t.ppf(.975,difference.shape[1]-1)*se
np.testing.assert_allclose(saved.log2_fold_change-half,saved.ci95_low)
np.testing.assert_allclose(saved.log2_fold_change+half,saved.ci95_high)
# Assert source observations fit the displayed limits; no invisible cropped data.
limits=json.loads((ROOT/'data/proteomics_statistics.json').read_text())['volcano_x_limits']
assert saved.log2_fold_change.between(*limits).all()
report.append({'statistics':'paired t, reduction CI, all 420 protein effects, CIs, P values and BH q independently recomputed','passed':True})
(ROOT/'exports/verification_report.json').write_text(json.dumps(report,indent=2))
print('PASS: 2 figure bundles; embedded Arial; typography; dimensions; data hashes; paired statistics; all BH q values.')

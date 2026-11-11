"""Export aggregate audit evidence and manuscript inputs; never exports clinical rows."""
from pathlib import Path
from hashlib import sha256
import argparse,sys,json,shutil
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from kdd_revision.rubric_audit import load_development
from kdd_revision.schema import SOURCE_DEFAULT


def export(source=SOURCE_DEFAULT):
 a=ROOT/'artifacts/a2_rubric_audit';out=ROOT/'resultados/a2/auditoria_2026_11_07';out.mkdir(parents=True,exist_ok=True)
 check=json.loads((a/'verification.json').read_text());assert check['complete']
 names=['family_nested_metrics.csv','outer_fold_metrics.csv','variable_probes.csv','category_target_associations.csv','collection_process_controls.csv','permuted_label_control.json','verification.json','final_choices.json','outer_selections.json','preprocessing_audit.json','outer_permutation_importance.csv','protocol_before_results.json']
 names.extend(p.name for p in a.glob('inner_scores_*.csv'));names.extend(p.name for p in a.glob('final_selection_scores_*.csv'));names.extend(p.name for p in a.glob('final_parameters_*.json'))
 for name in names:
  p=a/name
  if p.suffix=='.csv' and 'ID' in pd.read_csv(p,nrows=0).columns:raise ValueError('Row-level export rejected')
  shutil.copy2(p,out/name)
 raw,semantic,data,y,groups,sourcehash=load_development(ROOT,source)
 metrics=pd.read_csv(a/'family_nested_metrics.csv');imp=pd.read_csv(a/'outer_permutation_importance.csv')
 figdir=out/'figures';figdir.mkdir(exist_ok=True)
 cols=['Peso','Altura','IMC','IDADE','PA SISTOLICA','PA DIASTOLICA','FC','SEXO'];labels=['Peso','Altura','IMC','Idade','PAS','PAD','FC','Sexo']
 fig,axes=plt.subplots(1,2,figsize=(7.1,2.7),layout='constrained');missing=100*data[cols].isna().mean().to_numpy()
 axes[0].barh(labels,missing,color='#376e92');axes[0].invert_yaxis();axes[0].set(xlabel='Ausentes ou mascarados (%)',title='a) Disponibilidade antes de imputar')
 for i,v in enumerate(missing):axes[0].text(v+.6,i,f'{v:.1f}',va='center',fontsize=7)
 axes[0].set_xlim(0,max(missing)+11)
 axes[1].boxplot([data.loc[y==0,'FC'].dropna(),data.loc[y==1,'FC'].dropna()],tick_labels=['Normal','Anormal'],showfliers=False,widths=.5)
 axes[1].set(ylabel='FC (bpm)',title='b) Distribuição por rótulo')
 for ax in axes:ax.grid(axis='x' if ax is axes[0] else 'y',alpha=.2);ax.tick_params(labelsize=8)
 fig.savefig(figdir/'eda_disponibilidade_fc.pdf',bbox_inches='tight');fig.savefig(figdir/'eda_disponibilidade_fc.png',dpi=180,bbox_inches='tight');plt.close(fig)
 fig,axes=plt.subplots(1,2,figsize=(7.1,2.8),layout='constrained')
 for ax,family,title in zip(axes,['logistic','forest'],['a) Logística FISIO8','b) Floresta FISIO8']):
  m=metrics.query('pool=="FISIO8" and family==@family').iloc[0];matrix=np.array([[m.tn,m.fp],[m.fn,m.tp]],dtype=int)
  ax.imshow(matrix,cmap='Blues');ax.set_xticks([0,1],['Normal','Anormal']);ax.set_yticks([0,1],['Normal','Anormal']);ax.set(xlabel='Predito',ylabel='Rótulo registrado',title=title)
  for (i,j),v in np.ndenumerate(matrix):ax.text(j,i,str(v),ha='center',va='center',color='white' if v>matrix.max()*.55 else 'black',fontsize=9)
 fig.savefig(figdir/'confusoes_oof.pdf',bbox_inches='tight');fig.savefig(figdir/'confusoes_oof.png',dpi=180,bbox_inches='tight');plt.close(fig)
 ranking=imp.groupby(['pool','family','variable']).BA_drop.agg(['mean','std']).reset_index();ranking.to_csv(out/'permutation_summary.csv',index=False)
 fig,ax=plt.subplots(figsize=(5.1,2.9),layout='constrained');q=ranking.query('pool=="FISIO8" and family=="forest"').sort_values('mean')
 ax.barh(q.variable,q['mean'],color='#376e92');ax.axvline(0,color='black',lw=.7);ax.set(xlabel='Queda média de BA após permutação',title='Importância externa exploratória - FISIO8/floresta');ax.tick_params(labelsize=8)
 fig.savefig(figdir/'importancia_fisio.png',dpi=180,bbox_inches='tight');plt.close(fig)
 probes=pd.read_csv(a/'variable_probes.csv')
 summary={'run_date':'2026-11-07','dataset':'UCMF, disponibilizado na disciplina INF0414; origem descrita como Real Hospital Português, Recife',
  'source_sha256':sourcehash,'rubric_sha256':'bf38c1c6f777f249c2af733a957a2860787446233acd2325c54c26bc1fda545a',
  'n_original':12873,'n_original_variables':21,'n_labelled':11704,'n_unlabelled':1169,'n_quarantine':1,'n_historical_test_not_rescored':2342,
  'n_development':len(y),'development_class_counts':{str(k):int(v) for k,v in pd.Series(y).value_counts().items()},'n_candidate_components':int(groups.nunique()),
  'primary_pool':check['pools']['FISIO8'],'sensitivity_pool':check['pools']['STRICT4'],
  'metrics':metrics.to_dict('records'),'missing_percent_by_fisio_variable':dict(zip(cols,missing)),
  'variable_probes':probes.astype(object).where(probes.notna(),None).to_dict('records'),
  'collection_controls':pd.read_csv(a/'collection_process_controls.csv').to_dict('records'),
  'null_control':json.loads((a/'permuted_label_control.json').read_text()),'importance':ranking.to_dict('records'),
  'n_configs':105,'outer_folds':5,'inner_folds':3,'elapsed_seconds':check['elapsed_seconds'],
  'limits':['A origem e temporalidade do rótulo não foram documentadas.','Associação forte não comprova leakage; exclusão é política de risco justificada.','O teste histórico não foi pontuado novamente e não é tratado como intocado.','A EDA/curadoria prévia da coorte limita a independência da avaliação interna.','Componentes candidatos não comprovam identidade de paciente.'],
  'figure_notes':{'eda':'Desenvolvimento após curadoria, antes de imputar. Boxplot omite apenas pontos atípicos do desenho; não altera os dados das estatísticas/modelos.','confusions':'Predições externas OOF de procedimentos de seleção por família; mesmos registros e folds.','importance':'Permutação3repetições por5folds externos; correlacionados/idade condicional impedem interpretação causal.'}}
 (out/'reviewed_results.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2,allow_nan=False)+'\n')
 manifest={str(p.relative_to(out)):sha256(p.read_bytes()).hexdigest() for p in out.rglob('*') if p.is_file() and p.name!='manifesto.json'}
 (out/'manifesto.json').write_text(json.dumps({'source_sha256':sourcehash,'files_sha256':manifest,'self_excluded':True},ensure_ascii=False,indent=2)+'\n')
 print(out.relative_to(ROOT));return out
if __name__=='__main__':
 parser=argparse.ArgumentParser(description=__doc__)
 parser.add_argument('--source',type=Path,default=SOURCE_DEFAULT)
 export(parser.parse_args().source)

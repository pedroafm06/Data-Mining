"""Aggregate-only reporting of A2 preprocessing; never fits predictive models."""
from pathlib import Path
import json, math, os
from hashlib import sha256
from html import escape
import numpy as np
import pandas as pd
from scipy import stats
from .schema import ORIGINAL, NUMERIC, TARGET, PROJECT_ROOT, SOURCE_DEFAULT

# Per-variable judgments: theory and alternatives, not a log of script instructions.
DECISIONS = {
'ID':('Identificador nominal','Preservar para rastreio; retirar de X.','Não deduplicar pessoas por coincidência de atributos.','Ordinal/OHE do ID permitiria memorizar identidade; apagar o ID impediria auditoria.','Unicidade não esclarece paciente versus atendimento.'),
'Peso':('Quantitativa, kg','Invalidar não numérico/negativo; zero é sentinela; marcar extremos.','Na matriz: mediana por faixa de idade, fallback global e indicador; Z-score em representação separada.','Mediana global mistura lactentes e adolescentes. Sexo acrescenta pouco. Log só nesta coluna, em alternativa separada.','Imputação estima, não mede; envelope histórico é hipótese de qualidade.'),
'Altura':('Quantitativa, cm','Zero vira ausência; preservar original e sinalizar extremos sem apagar idade.','Mediana por faixa de idade e indicador; sem log no padrão; escala opcional.','Mediana geral perde estrutura etária. Não alterar para elevar correlação.','Não distinguir comprimento/estatura sem informação da fonte.'),
'IMC':('Quantitativa, kg/m²','Calcular só com peso/altura observados utilizáveis; conservar histórico com origem.','Preencher apenas na matriz, por mediana escolhida; oferecer matriz sem IMC.','Não recalcular após imputar pais: o ensaio de reconstrução mostrou perda maior.','Triplas contendo imputação não são medições fisicamente verificadas.'),
'Atendimento':('Data','Preservar texto, candidatos, estado e data absoluta quando inequívoca.','Fora de X; usar diferença de datas para idade quando defensável.','Não forçar 19xx/20xx nem substituir data por idade presumida.','Idade relativa pode ser identificável mesmo quando o século absoluto não é.'),
'DN':('Data','Reconhecer formatos completos; não descartar texto residual para fabricar data.','Derivação de idade relativa, mantendo candidatos e proveniência; fora de X.','Não imputar nascimento nem corrigir século automaticamente.','O recorte pediátrico é uma hipótese explícita ao filtrar pares candidatos.'),
'IDADE':('Quantitativa, anos','Guardar valor bruto inclusive negativo; priorizar idade relativa coerente com as datas.','Manter contínua; mediana de desenvolvimento apenas para a matriz e indicador.','Evidência dias/352 invalida tratar a coluna recebida como idade cronológica correta. Não imputar pelo corpo e criar circularidade.','Datas ambíguas continuam ambíguas. Idade original só como fallback identificado; faixas para imputação não usam idade já imputada.'),
'Convenio':('Nominal administrativa','Normalizar grafia sem adivinhar operadora; preservar na base semântica.','Fora da matriz principal por finalidade e alta cardinalidade.','OHE de centenas de grafias aumenta dimensão; frequência/target encoding não têm necessidade demonstrada.','Pode refletir seleção institucional; não é variável clínica intrínseca.'),
'PULSOS':('Nominal','Preservar achados raros; normalizar somente grafias equivalentes.','OHE com ausência e categoria inédita explícitas.','Moda Normais inventaria exame; binarizar todos os achados perderia tipo.','Momento de coleta e relação com alvo ainda precisam de esclarecimento.'),
'PA SISTOLICA':('Quantitativa, mmHg','Sinalizar extremos e PAS≤PAD; mascarar ambos nessa política sem escolher o culpado.','Mediana global e indicador; ganho etário pequeno não justifica estratificação; Z-score em matriz separada.','Não converter tudo para PPA nem derivar diagnóstico a partir de pressão imputada.','Mais de metade da medida está ausente; máscara artificial não valida ausência real.'),
'PA DIASTOLICA':('Quantitativa, mmHg','Mesma política relacional; conservar original e motivo da intervenção.','Parâmetro próprio de mediana e escala, sem log no padrão.','Não inferir PAD por uma função arbitrária de PAS; estratificação precisa justificar o custo.','Mesmas ressalvas de cobertura e interpretação de PAS.'),
'PPA':('Nominal composta histórica','Sentinelas Não calculado/erro de planilha viram ausentes; histórico é preservado.','OHE do rótulo completo, sem preencher Normal.','Ordinal puro confundiria gravidade e componente PAS/PAD. Recalcular exigiria insumos externos integralmente verificados.','Não declarar diagnóstico de HAS reconstruído com dados imputados.'),
TARGET:('Alvo binário','Normal/Anormal documentados; Normais permanece em revisão; não imputar.','y separado: Normal=0, Anormal=1; ausente continua desconhecido.','Alvo nunca entra em X nem orienta escolha de transformações nesta preparação da A2.','Produção do rótulo precisa ser esclarecida; não confundir com diagnóstico independente.'),
'B2':('Nominal','Preservar categorias e raros, sem impor gravidade artificial.','OHE com falta de registro distinta de Normal.','Moda e descarte por predominância apagariam achados raros.','Pode integrar o processo que gerou o alvo.'),
'SOPRO':('Nominal','Ausente é categoria observada; valor não registrado é outra coisa.','OHE dos tipos, não apenas presença.','Preencher faltante com Ausente ou selecionar só sem sopro mudaria o significado/população.','Esta preparação transforma o atributo; a disponibilidade em uso futuro é decisão posterior.'),
'FC':('Quantitativa, bpm','Converter intervalo válido em ponto médio aproximado; rejeitar intervalo invertido.','Mediana por idade e indicador; sem log no padrão.','Mediana geral ignora mudança etária; percentis externos incompletos não serão inventados.','Ponto médio não equivale a leitura exata; contexto da aferição é desconhecido.'),
'HDA 1':('Nominal estruturada','Conservar significado e distinguir vazio de Assintomático.','OHE com categoria ausente explícita.','Moda criaria histórico clínico; códigos não são quantidades.','Temporalidade em relação ao rótulo desconhecida.'),
'HDA2':('Nominal estruturada','Conservar mesmo com cobertura baixa; não copiar de HDA1.','OHE na matriz completa; retirada em representação reduzida documentada.','Regra de 50% é heurística; vazio não prova que não existe segundo histórico.','Cobertura muito baixa limita utilidade; não foi escolhida por desempenho.'),
'SEXO':('Nominal','Mapear grafias M/F documentadas; desconhecido não é sexo inferido.','OHE com falta/inédito explícitos, sem imputar moda.','Binário+indicador também é válido, mas OHE mantém simetria e explicação uniforme.','Não inferir sexo pelo corpo nem pelo alvo; estratificar imputação por sexo exige ganho adicional.'),
'MOTIVO1':('Nominal','Preservar texto completo normalizado, sem ordenar prefixos.','OHE; falta explícita e separação do segundo motivo.','Não fundir com MOTIVO2 ou assumir que todo encaminhamento precede diagnóstico.','Algumas categorias já mencionam cardiopatia estabelecida.'),
'MOTIVO2':('Nominal','Prefixos iguais com descrições diferentes não são a mesma categoria.','OHE da descrição completa; vazio separado de ausência clínica.','Não mapear só pelo número nem preencher com MOTIVO1.','Disponibilidade temporal precisa de esclarecimento antes da modelagem futura.'),
}


def clean_json(x):
    if isinstance(x,dict):return {str(k):clean_json(v) for k,v in x.items()}
    if isinstance(x,(list,tuple)):return [clean_json(v) for v in x]
    if isinstance(x,np.generic):x=x.item()
    if isinstance(x,float) and not math.isfinite(x):return None
    return x


def _source_path(source, artifacts):
    if source is not None:
        selected = Path(source).expanduser()
    elif os.environ.get('KDD_SOURCE'):
        selected = Path(os.environ['KDD_SOURCE']).expanduser()
    else:
        selected = SOURCE_DEFAULT
        manifest = artifacts / 'manifest.json'
        if not selected.is_file() and manifest.is_file():
            recorded = json.loads(manifest.read_text()).get('source_input', {}).get('path')
            if recorded:
                selected = Path(recorded).expanduser()
    if not selected.is_file():
        raise FileNotFoundError('CSV de entrada ausente. Informe --source ou KDD_SOURCE, ou coloque UCMF_raw.csv em dados/raw/.')
    expected = json.loads((artifacts / 'summary.json').read_text()).get('source_sha256')
    if expected and sha256(selected.read_bytes()).hexdigest() != expected:
        raise ValueError('O CSV informado difere da entrada usada para preparar os artefatos.')
    return selected


def aggregate(root=PROJECT_ROOT, source=None, artifact_dir=None):
    root=Path(root);a=Path(artifact_dir) if artifact_dir is not None else root/'artifacts/a2_preprocessing'
    out=a/'report';out.mkdir(parents=True,exist_ok=True)
    sem=pd.read_csv(a/'base_semantica.csv',dtype={'ID':str},low_memory=False)
    path=a/'base_para_transformacao.csv';data=pd.read_csv(path,dtype={'ID':str},low_memory=False) if path.exists() else sem.copy()
    raw=pd.read_csv(_source_path(source,a),dtype=str,keep_default_na=False)
    assert len(data)==len(sem)==len(raw) and data.ID.tolist()==raw.ID.tolist()
    core=json.loads((a/'summary.json').read_text())
    profiles=[];freq=[];register=[]
    for c in ORIGINAL:
        v=data[c];n=int(v.notna().sum());row={'variable':c,'n_total':len(data),'n_valid':n,'missing':int(v.isna().sum()),'missing_pct':100*v.isna().mean(),'n_unique':int(v.nunique())}
        if c in NUMERIC:
            s=pd.to_numeric(v,errors='coerce').dropna()
            row.update(mean=s.mean(),median=s.median(),sd=s.std(),q1=s.quantile(.25),q3=s.quantile(.75),minimum=s.min(),maximum=s.max(),skew=s.skew())
        elif c not in ['ID','Atendimento','DN']:
            # Do not export identifiers or absolute dates as a frequency listing.
            for value,count in v.astype(object).fillna('__AUSENTE__').value_counts().items():freq.append({'variable':c,'value':value,'n':int(count),'pct_all':100*count/len(data)})
        row['missing_definition']='data_absoluta_indisponivel_nao_equivale_a_campo_vazio' if c in ['Atendimento','DN'] else 'ausente_invalidado_ou_mascarado'
        row['n_raw_empty_literal']=int(raw[c].str.strip().eq('').sum())
        profiles.append(row)
        typ,action,transform,alt,limit=DECISIONS[c]
        if c in NUMERIC:
            method=core['imputation_choices'][c]['method']
            transform=('Na matriz: mediana por faixa etária com mínimo de 30 observados e fallback global.' if method=='age_band' else 'Na matriz: mediana global do desenvolvimento.')+' Indicador 0/1; Z-score somente na representação reescalada.'
            if c=='Peso':transform+=' Log1p apenas na alternativa Log-Peso.'
            if c=='IMC':transform+=' Não recalcular após imputar peso ou altura; resultado estimado não é medição clínica.'
        register.append({'variavel':c,'tipo':typ,'limpeza':action,'transformacao':transform,'alternativas_e_julgamento':alt,'incerteza':limit,'ausentes_pre_imputacao':row['missing'],'percentual_ausente':row['missing_pct'],'valores_distintos':row['n_unique']})
    pd.DataFrame(profiles).to_csv(out/'perfil_21_variaveis.csv',index=False)
    pd.DataFrame(freq).to_csv(out/'categorias_completas.csv',index=False)
    pd.DataFrame(register).to_csv(out/'decisoes_21_variaveis.csv',index=False)
    (out/'decisoes_21_variaveis.json').write_text(json.dumps(clean_json(register),ensure_ascii=False,indent=2,allow_nan=False))
    known=data[TARGET].isin(['Normal','Anormal']);labeled=data.loc[known];biv=[];cats=[];cont=[]
    for c in NUMERIC:
        n=pd.to_numeric(labeled.loc[labeled[TARGET]=='Normal',c],errors='coerce').dropna();p=pd.to_numeric(labeled.loc[labeled[TARGET]=='Anormal',c],errors='coerce').dropna()
        delta=p.mean()-n.mean();se2=p.var()/len(p)+n.var()/len(n);den=(p.var()/len(p))**2/(len(p)-1)+(n.var()/len(n))**2/(len(n)-1)
        df=se2**2/den if den else np.inf;half=stats.t.ppf(.975,df)*np.sqrt(se2);pool=np.sqrt(((len(n)-1)*n.var()+(len(p)-1)*p.var())/(len(n)+len(p)-2))
        biv.append({'variable':c,'n_normal':len(n),'n_anormal':len(p),'median_normal':n.median(),'median_anormal':p.median(),'mean_difference':delta,'ci_low':delta-half,'ci_high':delta+half,'welch_p':stats.ttest_ind(p,n,equal_var=False).pvalue,'cohen_d':delta/pool if pool else np.nan})
    for c in ORIGINAL:
        if c in NUMERIC or c in ['ID','Atendimento','DN',TARGET,'Convenio']:continue
        tab=pd.crosstab(labeled[c].astype(object).fillna('__AUSENTE__'),labeled[TARGET]);chi,p,_,expected=stats.chi2_contingency(tab,correction=False)
        valid=bool(expected.min()>=1 and (expected<5).mean()<=.2)
        cats.append({'variable':c,'n':int(tab.to_numpy().sum()),'categories':len(tab),'cramer_v':np.sqrt(chi/(tab.to_numpy().sum()*min(tab.shape[0]-1,tab.shape[1]-1))),'minimum_expected':expected.min(),'pct_expected_under5':100*(expected<5).mean(),'chi2_p_valid':p if valid else np.nan})
        for value,row in tab.iterrows():cont.append({'variable':c,'category':value,**{str(k):int(v) for k,v in row.items()}})
    pd.DataFrame(biv).to_csv(out/'bivariadas_numericas.csv',index=False);pd.DataFrame(cats).to_csv(out/'bivariadas_categoricas.csv',index=False);pd.DataFrame(cont).to_csv(out/'contingencias.csv',index=False)
    # Paired before/after: same source IDs and same pair availability, no claim of causal validation.
    rr=pd.to_numeric(raw['IDADE'],errors='coerce');hh=pd.to_numeric(raw['Altura'],errors='coerce');m=rr.notna() & hh.notna() & data.IDADE.notna() & data.Altura.notna()
    pairs=[]
    for label,x,y in [('Recebida',rr[m],hh[m]),('Revisada',data.loc[m,'IDADE'],data.loc[m,'Altura'])]:pairs.append({'version':label,'n':int(m.sum()),'pearson':x.corr(y),'spearman':x.corr(y,method='spearman')})
    pd.DataFrame(pairs).to_csv(out/'altura_idade_mesmos_ids.csv',index=False)
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig,axes=plt.subplots(1,2,figsize=(9,2.6),sharey=True)
    for ax,(label,x,y) in zip(axes,[('Recebida',rr[m],hh[m]),('Revisada',data.loc[m,'IDADE'],data.loc[m,'Altura'])]):
        ax.scatter(x,y,s=2,alpha=.17,color='#245b70');ax.set(title=label,xlabel='Idade (anos)');ax.grid(alpha=.15)
    axes[0].set_ylabel('Altura (cm)');fig.suptitle(f'Comparação pareada: {int(m.sum()):,} IDs, sem selecionar pela classe'.replace(',','.'));fig.tight_layout();fig.savefig(out/'altura_idade_pareada.png',dpi=180);plt.close(fig)
    summary={'n_source':len(data),'n_known_target':int(known.sum()),'target_counts':data[TARGET].value_counts(dropna=False).to_dict(),'pairs':pairs,'notes':'Descritivas antes de imputação; variantes de matriz são estimativas separadas. Nenhum modelo ajustado.'}
    (out/'summary.json').write_text(json.dumps(clean_json(summary),ensure_ascii=False,indent=2,allow_nan=False))
    return summary


def generate(root=PROJECT_ROOT, source=None, artifact_dir=None):
    root=Path(root);a=Path(artifact_dir) if artifact_dir is not None else root/'artifacts/a2_preprocessing'
    s=aggregate(root,source=source,artifact_dir=a);r=a/'report';docs=root/'docs/a2';docs.mkdir(parents=True,exist_ok=True)
    p=pd.read_csv(r/'perfil_21_variaveis.csv').set_index('variable');freq=pd.read_csv(r/'categorias_completas.csv');biv=pd.read_csv(r/'bivariadas_numericas.csv');cat=pd.read_csv(r/'bivariadas_categoricas.csv')
    diag=a/'diagnostics/imputation_alternatives.csv';d=pd.read_csv(diag) if diag.exists() else pd.DataFrame()
    comparisons=d.groupby(['column','method'])[['MAE','RMSE']].mean().reset_index() if len(d) else pd.DataFrame()
    if len(comparisons):comparisons.to_csv(r/'comparacao_imputacoes_resumo.csv',index=False)
    # Detailed decision register in conceptual order, suitable for later discussion.
    lines=['# A2: decisões de limpeza e transformação','',
    'Esta revisão integra a A2 e termina antes da modelagem. A A1 avaliada é a versão já entregue; suas cópias históricas permanecem preservadas. As transformações foram aplicadas e exportadas, com parâmetros ajustados somente no desenvolvimento já separado. Não foi treinado nenhum classificador nesta rodada.','',
    '## Ordem do processo e conceitos','',
    '1. Entender tipos, escalas, unidades e finalidade dos21atributos.','2. Reconhecer ausência, padronizar grafias e converter formatos sem perder o original.','3. Verificar inconsistência léxica, de domínio, lógica e temporal; separar erro comprovado de suspeita.','4. Recalcular idade relativa e IMC quando os insumos observados permitem; guardar origem e incerteza.','5. Examinar repetições e cobertura, sem inventar identidade ou remover raros por predominância.','6. Comparar alternativas de imputação no desenvolvimento, por mascaramento de valores observados, sem alvo.','7. Ajustar imputação, vocabulário, one-hot e escala no desenvolvimento; aplicar o mesmo objeto aos outros registros.','8. Conferir matrizes finitas, indicadores0/1, nomes, alinhamento, parâmetros e reprodução do transformador salvo.','',
    '## A descoberta sobre idade','',
    'Em11.191registros comparáveis, a idade recebida fica a até0,01ano de arredondar dias/352;11.120coincidem exatamente. Isso é evidência aritmética da inadequação da coluna para representar idade cronológica; não revela a fórmula original da planilha.6722casos superestimam mais de0,1ano e601mais de0,5ano frente à referência relativa do diagnóstico. A revisão usa datas candidatas compatíveis com o recorte0–19anos completos, mantendo intervalo e hipótese, sem fixar século absoluto. Casos sem identificação suficiente não recebem uma data inventada. Valores negativos originais continuam na auditoria.','',
    '## Julgamento variável por variável','']
    registered=pd.read_csv(r/'decisoes_21_variaveis.csv').set_index('variavel')
    for c in ORIGINAL:
        typ,action,trans,alt,lim=DECISIONS[c];row=p.loc[c];trans=registered.loc[c,'transformacao']
        lines += [f'### {c}',f'**Tipo:** {typ}.',f'**Limpeza:** {action}',f'**Transformação:** {trans}',f'**Alternativas e julgamento:** {alt}',f'**Limite:** {lim}',(f'**Evidência desta versão:** {int(row.n_valid)} datas absolutas reconhecidas; {int(row["missing"])} sem data absoluta fixada, incluindo séculos ambíguos. Isso não significa campo vazio: há {int(row.n_raw_empty_literal)} vazios literais na origem. Datas/candidatos brutos permanecem na proveniência.' if c in ['Atendimento','DN'] else f'**Evidência desta versão:** {int(row.n_valid)} disponíveis antes de imputar; {int(row["missing"])} ausentes/invalidado/mascarados ({row.missing_pct:.2f}%); {int(row.n_unique)} valores distintos.'),'']
    lines += ['## Por que as representações são separadas','',
    'A base semântica preserva unidades, faltantes e suspeitas. As matrizes numéricas são representações aplicadas: unidades originais, Z-score e uma alternativa log1p somente em Peso antes do Z-score. Indicadores e one-hot permanecem0/1. Z-score não torna a distribuição normal e não é robusto a outliers. Log não é imposto a todas as medidas. Não existe uma transformação universalmente ótima antes de definir a finalidade do modelo.','',
    'A política principal revisa os alertas: não elimina peso alto só por ultrapassar 150 kg, preserva baixa estatura potencial de lactente e não apaga FC 300 ou PAD positiva por serem extremas. AHA contempla taquiarritmias infantis com FC ≥220. Suspeitas fortes, como registros de FC >500 na amostra, seguem mascaradas por uma regra operacional explícita, sem declarar um limite físico. A política histórica e a alternativa preservada ficam disponíveis; não há prova clínica de erro individual. A alternativa que conserva suspeitos permite inspecionar o efeito da política. Toda imputação continua marcada. PPA histórica não é reconstruída com pressão imputada. IMC não é recalculado a partir de pais imputados: nos ensaios essa estratégia foi pior que preencher o IMC diretamente.','',
    '## Consistência conjunta e as duas formas de retenção','',
    'Peso e altura individuais não bastam para validar sua combinação. A regra operacional ampla de IMC entre 5 e 100 serve para sinalizar trios que precisam de revisão; não é intervalo clínico de normalidade. Quando a combinação observada ultrapassa essa regra, peso, altura e IMC são mascarados juntos somente na matriz da política revisada, sem decidir qual campo errou nem alterar idade. A base semântica e a variante preservada mantêm tudo. Um IMC histórico sozinho não contorna a sinalização conjunta. A regra permite valores extremos como 84 quando os pais são operacionalmente utilizáveis; não prova validade clínica individual.','',
    'Separadamente, uma equivalência candidata cruzava desenvolvimento e teste: apenas o registro do desenvolvimento foi retirado do ajuste. Ele permanece na base e recebe aplicação do transformador. Não há exclusão de pessoas ou confirmação de identidade por essa operação.','',
    '## Limites das comparações','',
    'O mascaramento artificial verifica reconstrução de valores disponíveis; não demonstra o mecanismo real das ausências. As faixas de idade são operacionais, com mínimo de medidas por grupo e fallback documentado. Sexo só acrescentaria complexidade se o ganho adicional fosse consistente. Não se usam notas de modelos ou o alvo para decidir imputações.','',
    'A matriz de desenvolvimento já transformada não serve para selecionar modelos por CV interna sem reajustar o transformador em cada fold. A população já foi explorada em etapas anteriores e o teste não é inteiramente virgem de exploração. Esta revisão da A2 não recalcula os experimentos anteriores; após mudanças na idade esses resultados não descrevem automaticamente a base nova.','',
    '## Fontes e uso de IA','',
    'Tema, dicionário e descrição das avaliações do SIGAA; conceitos das aulas de dados, exploração, limpeza, transformação, criação e redução. Mediana, codificação, Z-score, log e criação de atributos são conceitos empregados. Mediana condicionada por idade é uma aplicação operacional de imputação por tendência central; não uma referência clínica. Welch e V de Cramér são complementos exploratórios, não apresentados como conteúdo necessariamente desenvolvido em aula.','',
    '[AHA: valores altos podem ser achados de taquiarritmia, não prova de erro](https://www.heart.org/-/media/CPR-Files/CPR-Guidelines-Files/2025-Algorithms/Algorithm-PALS-Tachyarrhythmia-250117.pdf). Não foi aplicada conduta ou diagnóstico; a fonte fundamenta preservar a incerteza. [Documentação oficial sobre pré-processamento](https://scikit-learn.org/stable/modules/preprocessing.html) e [prevenção de vazamento](https://scikit-learn.org/stable/common_pitfalls.html). Percentis clínicos incompletamente verificados não foram fabricados.','',
    'Codex auxiliou a investigação, implementação, comparações, verificações e redação. A leitura do grupo é necessária antes de apresentação ou entrega; testes técnicos não substituem validação clínica ou aprovação do professor.']
    detailed='\n\n'.join(lines)
    # Restore normal spacing in fixed phrases while preserving actual variable names.
    for x,y in [('dos21','dos 21'),('indicadores0/1','indicadores 0/1'),('permanecem0/1','permanecem 0/1'),('Em11.191registros','Em 11.191 registros'),('até0,01ano','até 0,01 ano'),(';11.120coincidem','; 11.120 coincidem'),('.6722casos','. 6.722 casos'),('de0,1ano','de 0,1 ano'),('e601mais','e 601 mais'),('de0,5ano','de 0,5 ano'),('recorte0–19anos','recorte 0–19 anos')]:detailed=detailed.replace(x,y)
    (docs/'Decisoes_Preprocessamento_A2.md').write_text(detailed)
    pdf(root,s,p,freq,biv,cat,comparisons,artifact_dir=a)
    return docs


def pdf(root,s,prof,freq,biv,cat,comp,artifact_dir=None):
    a=Path(artifact_dir) if artifact_dir is not None else root/'artifacts/a2_preprocessing'
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,Table,TableStyle,PageBreak,Image
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.pdfbase.pdfdoc import PDFString
    from reportlab.pdfgen.canvas import Canvas
    # Prefer installed Arial; use Matplotlib's bundled DejaVu Sans elsewhere.
    fonts=Path('/System/Library/Fonts/Supplemental')
    if (fonts/'Arial.ttf').is_file() and (fonts/'Arial Bold.ttf').is_file():
        regular,bold=fonts/'Arial.ttf',fonts/'Arial Bold.ttf'
    else:
        import matplotlib
        fonts=Path(matplotlib.get_data_path())/'fonts/ttf'
        regular,bold=fonts/'DejaVuSans.ttf',fonts/'DejaVuSans-Bold.ttf'
    for name,file in [('A2Sans',regular),('A2Bold',bold)]:
        pdfmetrics.registerFont(TTFont(name,str(file)))
    pdfmetrics.registerFontFamily('A2Sans',normal='A2Sans',bold='A2Bold',italic='A2Sans',boldItalic='A2Bold')
    class C(Canvas):
        def __init__(self,*a,**kw):super().__init__(*a,**kw);self._doc.Catalog.Lang=PDFString('pt-BR')
    W,H=A4;width=W-72;story=[]
    body=ParagraphStyle('body',fontName='A2Sans',fontSize=10,leading=12,spaceAfter=5,textColor=colors.HexColor('#18323d'))
    head=ParagraphStyle('head',parent=body,fontName='A2Bold',fontSize=11,leading=13,spaceBefore=6,spaceAfter=5)
    cell=ParagraphStyle('cell',parent=body,leading=11.2,spaceAfter=0)
    def P(t,h=False):story.append(Paragraph(t,head if h else body))
    def table(headers,rows,widths):
        t=Table([[Paragraph('<b>'+escape(str(x))+'</b>',cell) for x in headers]]+[[Paragraph(escape(str(x)),cell) for x in row] for row in rows],colWidths=widths,repeatRows=1)
        t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#e6eff2')),('VALIGN',(0,0),(-1,-1),'TOP'),('LINEBELOW',(0,0),(-1,-1),.25,colors.HexColor('#c6d8de')),('LEFTPADDING',(0,0),(-1,-1),4),('RIGHTPADDING',(0,0),(-1,-1),4),('TOPPADDING',(0,0),(-1,-1),3),('BOTTOMPADDING',(0,0),(-1,-1),3)]));story.append(t);story.append(Spacer(1,6))
    def f(x,d=1):return '-' if pd.isna(x) else f'{float(x):,.{d}f}'.replace(',','X').replace('.',',').replace('X','.')
    def n(x):return f'{int(x):,}'.replace(',','.')
    lab={'PA SISTOLICA':'PAS','PA DIASTOLICA':'PAD','IDADE':'Idade'}
    P('A2 - Revisão do pré-processamento',True)
    P('Mineração de Dados - UFG | Pedro Matos, João Vitor Fernandes, Mateus Nery e Antônio Henrique | 04/11/2026')
    P('<b>Escopo:</b> dados e representações aplicadas antes da modelagem. Revisão integrante da A2; a A1 já entregue permanece como registro da avaliação. Os experimentos anteriores ainda não foram recalculados.')
    P('1. População e decisões de base',True)
    P(f'A entrada contém <b>{n(s["n_source"])} registros e 21 variáveis</b>. Todas as linhas e IDs são preservados. Há <b>{n(s["n_known_target"])} alvos conhecidos</b>; desconhecidos não são imputados. Igualdade de atributos não prova duplicação de paciente. ID, datas e convênio ficam fora da matriz principal.')
    P('2. Univariada numérica antes de imputar',True)
    P('População completa; política de mascaramento declarada. Ausência inclui valores invalidados ou mascarados. Quartis, média e dispersão usam somente medidas disponíveis; estimativas da matriz não entram nesta descrição.')
    rows=[]
    for c in NUMERIC:
        r=prof.loc[c];rows.append([lab.get(c,c),n(r.n_valid),f(r.missing_pct)+'%',f(r['mean']),f(r['median']),f(r.sd),f(r.q1)+' a '+f(r.q3),f(r.minimum)+' a '+f(r.maximum)])
    table(['Campo','n','Aus.','Média','Med.','DP','Q1 a Q3','Mín. a máx.'],rows,[58,43,43,43,43,38,74,width-442])
    P('Idade: uma correção fundamentada',True)
    P('Em 11.191 casos comparáveis, a idade recebida acompanha dias/352 a até 0,01 ano; 11.120 coincidem exatamente após arredondamento. Isso não estabelece a fórmula da planilha, mas impede tratar a coluna recebida como cronologicamente correta. Recalculamos idade relativa quando os pares de datas são compatíveis e suficientemente precisos.')
    P('Não fixamos século absoluto por conveniência. O intervalo de idade e a hipótese do recorte 0-19 anos completos ficam registrados. O aniversário de 20 anos não pertence ao recorte. Idade original e valores negativos continuam na auditoria; fallback é identificado como menos confiável.')
    P('ID e datas são descritos por cobertura, formatos, candidatos e estados, não por média numérica de códigos. Datas inexistentes ou com texto residual não são reconstruídas por palpite.')
    story.append(PageBreak())
    P('2. Univariada categórica (continuação)',True)
    P(f'Denominador: {n(s["n_source"])} registros. São exibidas até duas categorias frequentes; o complemento mantém todas as categorias, contagens e faltantes. Ausente em SOPRO é achado observado, não falta de registro.')
    rows=[]
    for c in [x for x in ORIGINAL if x not in NUMERIC+['ID','Atendimento','DN']]:
        q=freq[(freq.variable==c)&(freq.value!='__AUSENTE__')].head(2)
        desc='; '.join(str(r.value)[:48]+': '+n(r.n)+' ('+f(r.pct_all)+'%)' for _,r in q.iterrows())
        rows.append([c,int(prof.loc[c].n_unique),f(prof.loc[c].missing_pct)+'%',desc])
    table(['Campo','Cat.','Aus.','Categorias frequentes'],rows,[87,34,43,width-164])
    P('Retenção e redução',True)
    P('PULSOS, B2 e SOPRO conservam categorias raras. HDA2 continua disponível na representação completa; uma alternativa reduzida permite retirá-la junto ao IMC. A regra de 50% de vazios ou de valores repetidos é uma heurística, não uma remoção clínica automática.')
    P('Convênio permanece na base semântica e na análise, mas não na matriz principal: alta cardinalidade administrativa e finalidade distinta. Prefixos numéricos de MOTIVO2 não identificam categorias únicas; preserva-se a descrição completa.')
    P('Os contextos e achados não são declarados seguros para triagem antes do diagnóstico. Esta preparação conserva e transforma a informação; a escolha da disponibilidade em cada cenário deverá ser reavaliada antes da modelagem.')
    story.append(PageBreak())
    P('3. Limpeza: decisão, motivo e alternativa',True)
    groups=[
    ('ID / repetições','Preservar rastreio e sinalizar equivalências.','Não provar identidade nem excluir coincidências por vacuidade.'),
    ('Peso / Altura','Zero-sentinela vira ausente; formato inválido é rejeitado; extremos são flags.','Não apagar idade porque o corpo destoa; separar suspeita de erro.'),
    ('IMC','Recalcular só com pais observados utilizáveis; guardar histórico/origem.','Não produzir uma medição clínica com pais imputados.'),
    ('Atendimento / DN','Parser completo, candidatos de século e estado de cada data.','Não escolher data absoluta para forçar idade pediátrica.'),
    ('IDADE','Idade relativa com intervalo e regra do recorte; original bruto preservado.','Não confiar na coluna compatível com dias/352; não imputar idade pelo corpo circularmente.'),
    ('PAS / PAD','Flag relacional PAS≤PAD; nessa variante mascarar ambas, preservando originais.','Não decidir qual componente errou; não converter imputação em HAS.'),
    ('PPA / alvo','Sentinelas de PPA viram ausência; alvo só por rótulos documentados.','PPA é histórica; alvo não é imputado e Normais continua em revisão.'),
    ('PULSOS / B2 / SOPRO','Grafias equivalentes normalizadas; raros mantidos.','Não usar moda Normal/Ausente como exame inventado.'),
    ('FC','Faixa válida vira ponto médio com flag; invertida é invalidada.','Aproximação não é leitura exata nem diagnóstico.'),
    ('SEXO','Grafias M/F documentadas; desconhecido explícito.','Não inferir sexo pelo corpo, alvo ou moda.'),
    ('HDA1 / HDA2 / MOTIVOS','Categorias completas e falta explícita; sem copiar entre campos.','Não declarar vazio como ausência de sintomas ou de outro motivo.'),
    ('Convênio','Normalizar sem adivinhar operadora; retirar da matriz principal.','Não selecionar pelo alvo nem confundir rotina institucional com sinal clínico.'),
    ]
    table(['Campos','O que foi decidido','Por que / cuidado'],groups,[91,218,width-309])
    P('Os envelopes antigos são alertas, não prova de erro. A revisão preserva extremos potencialmente reais. A verificação conjunta sinaliza IMC fora do intervalo operacional amplo 5-100: mascara o trio na matriz, preservando original e idade, sem decidir o culpado. Isso não é faixa clínica de normalidade nem prova de erro individual.')
    story.append(PageBreak())
    P('4. Transformações realmente aplicadas',True)
    P('Ajuste somente no desenvolvimento da partição congelada; aplicação sem reajuste ao teste, às demais linhas e aos não rotulados. Não houve treinamento de classificador nesta rodada. ID e y são separados de X.')
    P('<b>Conceitos usados:</b> tipos/escalas, ausência, tendência central, codificação categórica, criação de atributos, redução, transformação logarítmica e padronização.')
    P('Imputação julgada por reconstrução no desenvolvimento',True)
    if len(comp):
        pivot=comp.pivot(index='column',columns='method',values='MAE');rows=[]
        for c in ['Peso','Altura','FC','IMC','PA SISTOLICA','PA DIASTOLICA']:
            if c in pivot.index:rows.append([lab.get(c,c),f(pivot.loc[c].get('global',np.nan),2),f(pivot.loc[c].get('age',np.nan),2),f(pivot.loc[c].get('age_sex',np.nan),2)])
        table(['Campo','Global: MAE','Por idade','Idade + sexo'],rows,[118,120,120,width-358])
    P('Cinco repetições: 20% de valores disponíveis ocultados; medianas ajustadas sem essas células. Faixas fixas exigem 30 observados, com fallback. A mediana por idade é uma aplicação da imputação por tendência central; o diagnóstico não prova o mecanismo real das ausências e não usa o alvo.')
    final_summary=json.loads((a/'summary.json').read_text())
    age_fields=[lab.get(c,c) for c,d in final_summary['imputation_choices'].items() if d['method']=='age_band']
    global_fields=[lab.get(c,c) for c,d in final_summary['imputation_choices'].items() if d['method']=='global']
    P('<b>Escolha aplicada:</b> por faixa etária em '+', '.join(age_fields)+'; global em '+', '.join(global_fields)+'. Sexo não acrescentou ganho suficiente para fragmentar os grupos. A escolha do IMC é limítrofe no mascaramento; a variante global também está disponível.')
    table(['Representação','Transformações aplicadas'],[
    ('Unidades originais','Imputação escolhida por coluna; one-hot dos nominais; indicadores de estimativa/falta/inédito.'),
    ('Z-score','Somente medidas contínuas são centradas e reescaladas; categorias e indicadores ficam 0/1.'),
    ('Log-Peso + Z-score','Alternativa: log1p somente em Peso e depois escala contínua; não se aplica log aos indicadores.'),
    ],[118,width-118])
    P('A idade usada para escolher o grupo é a disponível antes de imputar; não se cria grupo com idade estimada. IMC não é recalculado depois de preencher os pais. Categorias inéditas têm tratamento explícito, sem ampliar o vocabulário pelo teste. Não há garantia de transformação universalmente ótima antes de definir algoritmo/finalidade.')
    core=json.loads((a/'summary.json').read_text());shape=core['matrices']['units'];P(f"Matriz completa: <b>{n(shape['n_rows'])} × {n(shape['n_columns'])}</b>, finita, com ID/y separados. Parâmetros ajustados em <b>{n(core['n_fit'])}</b> registros; teste {n(core['n_test'])}. A quarentena retira do ajuste o candidato que cruza a partição, sem excluir a linha da base. CV futura exige novo ajuste em cada fold.")
    story.append(PageBreak())
    P('5. Comparação pareada e relação com o alvo',True)
    pairs=pd.read_csv(a/'report/altura_idade_mesmos_ids.csv')
    P(f'Altura × idade: mesmos {n(pairs.n.iloc[0])} IDs, disponíveis nas duas versões. Pearson {f(pairs.pearson.iloc[0],3)} → {f(pairs.pearson.iloc[1],3)}; Spearman {f(pairs.spearman.iloc[0],3)} → {f(pairs.spearman.iloc[1],3)}. A relação descreve associação; não valida a limpeza por si.')
    story.append(Image(str(a/'report/altura_idade_pareada.png'),width=width,height=151))
    P('Bivariadas numéricas: somente rótulos conhecidos',True)
    rows=[]
    for _,q in biv.iterrows():rows.append([lab.get(q.variable,q.variable),n(q.n_normal)+'/'+n(q.n_anormal),f(q.median_normal)+'/'+f(q.median_anormal),f(q.mean_difference,2),f(q.ci_low,2)+' a '+f(q.ci_high,2)])
    table(['Campo','n N/A','Med. N/A','Δ média A-N','IC95% Δ'],rows,[60,93,94,88,width-335])
    P('O intervalo de Welch compara médias, não medianas, e é complemento exploratório. A análise categórica completa publica contingências, V de Cramér e esperadas; p assintótico é omitido quando as esperadas não sustentam o teste. Associação não prova causa; falta de significância não prova equivalência.')
    cv=cat.set_index('variable')
    P('SOPRO apresenta associação descritiva forte (V de Cramér '+f(cv.loc['SOPRO','cramer_v'],3)+'); MOTIVO2 '+f(cv.loc['MOTIVO2','cramer_v'],3)+' e B2 '+f(cv.loc['B2','cramer_v'],3)+'. Esses achados podem participar do processo de rotulagem. Não se conclui causalidade ou capacidade de triagem anterior ao exame; categorias raras exigem atenção às esperadas.')
    P('Fontes e limites',True)
    P('Tema, dicionário e descrição das avaliações do SIGAA; conceitos das aulas de dados, limpeza, transformação e avaliação. Documentação oficial scikit-learn: pré-processamento e prevenção de vazamento. Percentis clínicos não verificados não foram inventados. O significado do alvo e a unidade paciente/consulta ainda precisam de esclarecimento.')
    P('IA: Codex auxiliou auditoria, código, comparações, testes e redação. Os materiais exigem leitura dos integrantes antes de entrega. As verificações técnicas não representam validação clínica. Complementos completos: decisões das 21 variáveis, tabelas, parâmetros e testes no repositório Data-Mining.')
    def footer(c,doc):
        c.setFont('A2Sans',9);c.setFillColor(colors.HexColor('#536d79'));c.drawString(36,24,'A2 - Revisão do pré-processamento - 04/11/2026');c.drawRightString(W-36,24,f'{doc.page}')
    path=root/'docs/a2/Relatorio_Preprocessamento_A2.pdf'
    SimpleDocTemplate(str(path),pagesize=A4,rightMargin=36,leftMargin=36,topMargin=32,bottomMargin=38,title='A2 - Revisao do pre-processamento',author='Grupo de Mineracao de Dados - UFG').build(story,onFirstPage=footer,onLaterPages=footer,canvasmaker=C)
    from pypdf import PdfReader
    doc=PdfReader(path)
    if len(doc.pages)!=5:raise RuntimeError(f'PDF A2 precisa de ajuste visual: {len(doc.pages)} páginas, esperadas5.')
    return path

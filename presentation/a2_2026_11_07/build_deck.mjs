import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {Presentation, PresentationFile} from '@oai/artifact-tool';

const DIR=path.dirname(fileURLToPath(import.meta.url));
const BUILD=path.join(DIR,'.build');
const SKILL=process.env.CODEX_PRESENTATIONS_SKILL;
if (!SKILL) throw new Error('Set CODEX_PRESENTATIONS_SKILL to the installed presentations skill directory.');
const {resolvePresentationFont,applyPresentationChartFont,finalizePresentation} =
  await import(path.join(SKILL,'container_tools/artifact_tool_utils.mjs'));
const PY=process.env.CODEX_PRESENTATIONS_PYTHON || 'python3';
const D=JSON.parse(await fs.readFile(path.join(BUILD,'content.json'),'utf8'));
const FINAL=process.argv.includes('--final');
const revision=process.env.UCMF_DECK_REVISION??'v1';
const OUT=path.join(DIR,'output'), QA=path.join(DIR,'qa');
await fs.mkdir(OUT,{recursive:true}); await fs.mkdir(QA,{recursive:true});
const FONT=resolvePresentationFont();
const C={ink:'#122C43',teal:'#007F82',orange:'#A54C20',muted:'#4D6172',grid:'#D7E1E7',white:'#FFFFFF',wash:'#F2F7F8',gray:'#778A9A'};
const p=Presentation.create({slideSize:{width:1280,height:720}});
const tableOwners=[],chartOwners=[],allNotes=[];
const fmt=(x,d=1)=>Number(x).toFixed(d).replace('.',',');
const pct=(x,d=1)=>fmt(100*x,d)+'%';
const int=x=>Math.round(x).toLocaleString('pt-BR');
const fam=D.families;
const row=(pool,family)=>D.metrics.find(x=>x.pool===pool&&x.family===family);
const primary=D.primary;
function txt(s,text,x,y,w,h,size=28,color=C.ink,bold=false,align='left',name=''){
 const sh=s.shapes.add({geometry:'textbox',name:name||`text-${s.shapes.items.length+1}`,position:{left:x,top:y,width:w,height:h},fill:'none',line:{fill:'none',width:0}});
 sh.text=text;sh.text.style={typeface:FONT,fontSize:size,color,bold,alignment:align,verticalAlignment:'top',autoFit:'none',wrap:'square',insets:0};return sh;
}
function box(s,text,x,y,w,h,fill=C.wash,color=C.ink,size=26){
 const sh=s.shapes.add({geometry:'rect',name:`diagram-${s.shapes.items.length+1}`,position:{left:x,top:y,width:w,height:h},fill,line:{fill:C.grid,width:1}});
 sh.text=text;sh.text.style={typeface:FONT,fontSize:size,color,bold:true,alignment:'center',verticalAlignment:'middle',autoFit:'none',insets:12};return sh;
}
function connect(s,a,b,from='right',to='left',kind='straight'){
 return s.shapes.connect(a,b,{kind,fromSide:from,toSide:to,line:{fill:C.teal,width:2},tail:{type:'arrow',width:'med',length:'med'}});
}
function slide(title,n,opts={}){
 const s=p.slides.add();s.background.fill=opts.dark?C.ink:C.white;
 if(opts.hidden)s.hidden=true;
 const color=opts.dark?C.white:C.ink;
 if(title)txt(s,title,64,48,1152,90,44,color,true,'left','slide-title');
 txt(s,opts.hidden?`Apoio ${n-14}`:`${String(n).padStart(2,'0')} / 14`,1090,676,125,24,18,opts.dark?'#BCD1DC':C.muted,false,'right','slide-number');
 return s;
}
function notes(s,n,extra=''){
 const d=D.notes[n-1];const text=`Responsável sugerido: ${d.author}\nTempo: ${Math.floor(d.seconds/60)}:${String(d.seconds%60).padStart(2,'0')}\n\n${d.text}\n\nPergunta possível: ${d.question}\nResposta: ${d.answer}\n\nFontes locais: ${d.sources.join('\n')}\n${extra}`;
 s.speakerNotes.text=text;allNotes.push({...d,notes:text});
}
function backupNotes(s,n,title,text,sources=[]){const x={number:n,title,seconds:0,author:'Todos os quatro integrantes',text,question:'',answer:'',sources,hidden:true};s.speakerNotes.text=`Slide de apoio, fora do roteiro de 15 minutos.\n\n${text}\n\nFontes locais: ${sources.join('\n')}`;allNotes.push(x);}
function table(s,values,x,y,w,h,widths,opts={}){
 const t=s.tables.add({rows:values.length,columns:values[0].length,left:x,top:y,width:w,height:h,columnWidths:widths,values});
 t.borders.assign({fill:C.grid,width:1,style:'solid'});
 for(let r=0;r<values.length;r++){
  t.rows[r].height=h/values.length;
  for(let c=0;c<values[0].length;c++){
   const cell=t.getCell(r,c);cell.fill=r===0?C.ink:(opts.highlight===r?'#E4F2F1':C.white);
   cell.text.style={typeface:FONT,fontSize:opts.size??25,color:r===0?C.white:C.ink,bold:r===0||c===0,alignment:c===0?'left':'center',verticalAlignment:'middle',autoFit:'none',insets:{left:12,right:12,top:8,bottom:8}};
  }
 }
 tableOwners.push(p.slides.items.length);return t;
}
function chart(s,categories,series,rect,opts={}){
 const ch=s.charts.add('bar',{
  position:{left:rect[0],top:rect[1],width:rect[2],height:rect[3]},categories,series,
  barOptions:{direction:opts.horizontal?'bar':'column',grouping:'clustered',gapWidth:opts.gap??60},
  hasLegend:series.length>1,legend:{position:'bottom',overlay:false,textStyle:{fontSize:22,fill:C.ink}},
  xAxis:{textStyle:{fontSize:22,fill:C.ink},line:{fill:C.grid,width:1},numberFormatCode:opts.horizontal?opts.format:undefined,min:opts.horizontal?opts.min:undefined,max:opts.horizontal?opts.max:undefined},
  yAxis:{textStyle:{fontSize:22,fill:C.ink},numberFormatCode:opts.horizontal?undefined:opts.format,min:opts.horizontal?undefined:opts.min,max:opts.horizontal?undefined:opts.max,majorGridlines:{fill:C.grid,width:1}},
  dataLabels:{showValue:true,position:'outEnd',numberFormatCode:opts.format??'0.0',textStyle:{fontSize:21,bold:true,fill:C.ink}},chartFill:C.white,plotAreaFill:C.white,chartLine:{fill:'none',width:0},plotAreaLine:{fill:'none',width:0}
 });applyPresentationChartFont(ch,{fontFamily:FONT});chartOwners.push(p.slides.items.length);return ch;
}

// 1. Cover
{
 const s=slide('',1,{dark:true});
 txt(s,'Classificação de registros\ncardíacos pediátricos',64,85,1130,160,60,C.white,true);
 txt(s,'Auditoria de atributos e avaliação comparável',64,290,1130,58,34,'#BAE3E1');
 txt(s,'Mineração de Dados\nUFG, Grupo 3, 2026/2',64,390,460,80,26,'#C7D7E0');
 txt(s,D.authors.join('\n'),585,397,630,185,25,C.white);
 notes(s,1);
}
// 2. Task
{
 const s=slide('Tarefa e significado do alvo',2);
 txt(s,'Normal ou Anormal',64,160,1100,70,50,C.teal,true);
 txt(s,'Classificação supervisionada do rótulo registrado',64,254,1120,54,32,C.ink,true);
 txt(s,'O dicionário define presença ou ausência de patologia cardíaca.',64,345,1110,80,30);
 txt(s,'Referência clínica, examinador e ordem de coleta desconhecidos.',64,457,1110,85,30);
 txt(s,'A conclusão depende da disponibilidade das entradas antes do uso.',64,581,1110,60,25,C.orange,true);
 notes(s,2);
}
// 3. Cohort, native editable flow
{
 const s=slide('Coorte e partições',3);
 const raw=box(s,'12.873 registros e 21 variáveis',64,148,1152,66);
 const known=box(s,'11.704 com rótulo',64,260,720,72);
 const unknown=box(s,'1.169 sem rótulo',860,260,356,72,C.white,C.muted,25);
 connect(s,raw,known,'bottom','top','elbow');connect(s,raw,unknown,'bottom','top','elbow');
 const dev=box(s,'9.361 desenvolvimento\n9.279 grupos candidatos',64,390,430,105,'#E4F2F1');
 const hist=box(s,'2.342 teste histórico\nsem nova avaliação',552,390,363,105,C.white,C.muted,25);
 const q=box(s,'1 em\nquarentena',973,390,243,105,C.white,C.muted,25);
 connect(s,known,dev,'bottom','top','elbow');connect(s,known,hist,'bottom','top','elbow');connect(s,known,q,'bottom','top','elbow');
 txt(s,'5.394 Normal e 3.967 Anormal no desenvolvimento (42,4% Anormal)',64,538,1152,52,28);
 txt(s,'Grupos candidatos não confirmam identidade. A linha em quarentena permanece na fonte.',64,608,1130,52,23,C.muted);
 notes(s,3);
}
//4. Semantic evidence
{
 const s=slide('Campos com risco de vazamento',4);
 table(s,[['Informação','Evidência disponível','Decisão principal'],['MOTIVO1 e MOTIVO2','Conteúdo diagnóstico explícito','Excluir'],['SOPRO, B2 e PULSOS','Possível incorporação ao rótulo','Excluir'],['PPA','Classificação de hipertensão','Excluir'],['HDA 1 e HDA2','Sintomas, proveniência temporal incerta','Excluir']],64,162,1152,350,[300,600,252],{size:25});
 txt(s,'SOPRO isolado: 91,05% de BA. B2 isolado: 55,32%.',64,550,1120,44,30,C.orange,true);
 txt(s,'A exclusão também considera o papel de cada campo na investigação diagnóstica.',64,607,1120,45,25,C.muted);
 notes(s,4);
}
//5. Feature sets
{
 const s=slide('Conjuntos de atributos',5);
 txt(s,'FISIO8',64,165,480,55,42,C.teal,true);
 txt(s,'Peso, Altura, IMC e IDADE\nPAS, PAD e FC\nSEXO',64,250,580,220,34);
 txt(s,'STRICT4',730,165,486,55,42,C.ink,true);
 txt(s,'Peso e Altura\nIDADE e SEXO',730,250,486,160,34);
 txt(s,'Cenário fisiológico',64,514,620,48,28,C.teal,true);
 txt(s,'Sensibilidade mais restrita',730,514,486,48,28,C.ink,true);
 txt(s,'Os dois cenários pressupõem disponibilidade das medidas antes do uso.',64,601,1152,62,25,C.orange);
 notes(s,5);
}
//6. Preprocessing
{
 const s=slide('Pré-processamento no treino',6);
 const a=box(s,'Limpeza e\nderivações',64,185,315,100);
 const b=box(s,'Imputação e escala\najustadas no treino',483,185,315,100);
 const c=box(s,'Aplicação ao\nfold de avaliação',901,185,315,100);
 connect(s,a,b);connect(s,b,c);
 txt(s,'Padronização de unidades e marcação de valores suspeitos.',64,370,1152,65,29);
 txt(s,'Mediana global ou por idade, codificação one-hot e escala.',64,455,1152,65,29);
 txt(s,'Padrões de ausência podem representar o processo de coleta.',64,556,1152,70,29,C.orange,true);
 notes(s,6);
}
//7. Nested CV
{
 const s=slide('Validação aninhada',7);
 const folds=[];for(let i=0;i<5;i++)folds.push(box(s,`Fold ${i+1}`,64+i*230,156,208,65,i===4?C.ink:'#E4F2F1',i===4?C.white:C.ink,26));
 txt(s,'4 folds no treino externo',64,242,790,44,28,C.teal,true);
 txt(s,'1 fold para avaliar',984,242,232,60,25,C.ink,true,'center');
 const train=box(s,'Busca interna\n3 folds por família',64,335,330,110);
 const chosen=box(s,'Escolha e ajuste\nno treino externo',454,335,350,110);
 const pred=box(s,'Previsão no\nfold externo',884,335,332,110,C.ink,C.white);
 connect(s,train,chosen);connect(s,chosen,pred);
 txt(s,'5 repetições externas, uma previsão por registro',64,512,1152,50,34,C.teal,true);
 txt(s,'Mesmos folds para todas as famílias e os dois conjuntos. Grupos candidatos permanecem juntos.',64,597,1152,65,25,C.muted);
 notes(s,7);
}
//8. Models and metrics
{
 const s=slide('Algoritmos e métricas',8);
 table(s,[['Família','Papel','Configurações'],['Referência','Classe mais frequente','1'],['Regressão logística','Baseline linear regularizado','32'],['Árvore','Regras não lineares','48'],['Floresta','Agregação de árvores','24']],64,162,1152,330,[370,552,230],{size:26});
 txt(s,'Seleção: acurácia balanceada. Limiar fixo: 0,5.',64,533,1152,48,30,C.teal,true);
 txt(s,'BA = média entre sensibilidade e especificidade. AUC complementa o limiar fixo.',64,600,1152,62,25,C.muted);
 notes(s,8);
}
//9. Main results
{
 const s=slide('Comparação principal em FISIO8',9);
 const values=[['Modelo','BA','ROC-AUC','Sensibilidade','Especificidade']];
 for(const family of ['dummy','tree','logistic','forest']){const r=row('FISIO8',family);values.push([fam[family],pct(r.balanced_accuracy),fmt(r.roc_auc,3),pct(r.recall),pct(r.specificity)]);}
 table(s,values,64,168,1152,305,[260,190,210,245,247],{size:27,highlight:4});
 txt(s,'Maior BA observada: '+pct(primary.balanced_accuracy),64,513,1152,55,36,C.teal,true);
 txt(s,'9.361 previsões externas. Comparação interna à mesma coorte, sem validação clínica independente.',64,591,1152,65,25,C.muted);
 notes(s,9);
}
//10. Confusion matrix
{
 const s=slide('Erros da floresta em FISIO8',10);
 const r=primary;
 table(s,[['Registro / previsão','Normal','Anormal','Total'],['Normal',int(r.tn),int(r.fp),int(r.tn+r.fp)],['Anormal',int(r.fn),int(r.tp),int(r.fn+r.tp)],['Total',int(r.tn+r.fn),int(r.fp+r.tp),int(r.n)]],64,180,780,335,[270,170,170,170],{size:28});
 txt(s,pct(1-r.recall),915,205,300,85,64,C.orange,true);
 txt(s,'dos Anormal\nrecebem previsão Normal',915,305,300,150,29);
 txt(s,'Limiar 0,5. Cada erro é definido contra o rótulo registrado.',64,559,1152,62,27,C.muted);
 notes(s,10);
}
//11. Permutation importance native chart
{
 const s=slide('Dependência dos atributos',11);
 const labels=D.importance.map(x=>x.variable==='PA SISTOLICA'?'PAS':x.variable==='PA DIASTOLICA'?'PAD':x.variable);
 chart(s,labels,[{name:'Queda média de BA',values:D.importance.map(x=>Number((100*x.mean).toFixed(4))),fill:C.teal}],[64,150,1152,405],{horizontal:true,min:0,max:6,format:'0.0" pp"',gap:55});
 txt(s,'Permutação no fold externo, 5 folds e 3 repetições por variável.',64,576,1152,44,25,C.muted);
 txt(s,'Importância mede dependência do modelo e não demonstra causalidade ou proveniência.',64,622,1152,46,24,C.orange);
 notes(s,11);
}
//12. Sensitivity, native chart
{
 const s=slide('Sensibilidades e processo de coleta',12);
 const cats=['Árvore','Logística','Floresta'];
 chart(s,cats,[{name:'FISIO8',values:['tree','logistic','forest'].map(f=>Number(row('FISIO8',f).balanced_accuracy.toFixed(6))),fill:C.teal},{name:'STRICT4',values:['tree','logistic','forest'].map(f=>Number(row('STRICT4',f).balanced_accuracy.toFixed(6))),fill:C.gray}],[64,145,820,415],{min:.5,max:.7,format:'0.0%',gap:75});
 txt(s,'Somente máscaras\nde disponibilidade',930,195,285,95,28,C.ink,true);
 txt(s,'BA '+pct(D.controls.find(x=>x.pool==='FISIO8').balanced_accuracy),930,328,285,65,40,C.orange,true);
 txt(s,'FISIO8, árvore fixa\ncontrole exploratório',930,415,285,90,25,C.muted);
 txt(s,'A diferença entre os conjuntos não identifica isoladamente o efeito de cada medida.',64,605,1152,62,25,C.muted);
 notes(s,12);
}
//13. Limitations
{
 const s=slide('Limites da evidência',13);
 const lines=['Referência do alvo e ordem de coleta desconhecidas','Grupos candidatos sem identidade de paciente confirmada','Serviço de cardiologia e seleção de registros com rótulo','Exploração histórica da coorte permanece relevante'];
 lines.forEach((x,i)=>txt(s,x,64,166+i*100,1152,74,32,i===0?C.orange:C.ink,i===0));
 txt(s,'A validação aninhada controla a busca desta execução. Ela não apaga decisões anteriores.',64,602,1152,60,25,C.muted);
 notes(s,13);
}
//14. Conclusion
{
 const s=slide('Conclusão',14,{dark:true});
 txt(s,pct(primary.balanced_accuracy),64,168,520,95,76,'#BAE3E1',true);
 txt(s,'maior BA observada\nna floresta FISIO8',64,283,580,110,34,C.white);
 txt(s,'Discriminação limitada\ndo rótulo registrado',730,184,486,145,38,C.white,true);
 txt(s,'Próximo avanço: esclarecer a formação do alvo e a ordem de coleta, seguido de avaliação confirmatória separada.',64,466,1152,130,32,C.white);
 notes(s,14);
}
//15-17. Complete matrix of 21 fields, native editable tables.
const short={
 'ID':'Identificador declarado do paciente', 'Peso':'Medida corporal, condição temporal', 'Altura':'Medida corporal, condição temporal', 'IMC':'Derivado histórico, redundância', 'Atendimento':'Metadado temporal, gera idade', 'DN':'Quase identificador, gera idade','IDADE':'Idade na visita, condição temporal',
 'Convenio':'Proxy administrativo e de seleção','PULSOS':'Possível incorporação no rótulo','PA SISTOLICA':'Medida, possível critério de HAS','PA DIASTOLICA':'Medida, possível critério de HAS','PPA':'Classificação de HAS derivada','NORMAL X ANORMAL':'Alvo registrado, somente y','B2':'Possível incorporação, ausculta',
 'SOPRO':'Possível incorporação, ausculta','FC':'Medida, possível uso na decisão','HDA 1':'Sintomas, proveniência incerta','HDA2':'Sintomas e preenchimento esparso','SEXO':'Cadastro básico, condição temporal','MOTIVO1':'Diagnóstico prévio explícito','MOTIVO2':'Diagnóstico prévio explícito'};
for(let group=0;group<3;group++){
 const n=15+group;const s=slide(`Matriz das 21 variáveis, parte ${group+1}`,n,{hidden:true});
 const vars=D.policy.variables.slice(group*7,group*7+7);
 const vals=[['Atributo','FISIO8','STRICT4','Fundamento']];
 vars.forEach(v=>vals.push([v.variavel,v.decisao.FISIO==='incluir'?'Inclui':v.decisao.FISIO==='somente_y'?'Somente y':'Exclui',v.decisao.STRICT==='incluir'?'Inclui':v.decisao.STRICT==='somente_y'?'Somente y':'Exclui',short[v.variavel]]));
 table(s,vals,64,154,1152,464,[300,170,170,512],{size:23});
 txt(s,'Decisões conservadoras. A tabela não declara vazamento comprovado em todas as exclusões.',64,633,1152,35,22,C.muted);
 backupNotes(s,n,`Matriz das 21 variáveis, parte ${group+1}`,vars.map(v=>`${v.variavel}: ${v.decisao.motivo} Evidência: ${v.decisao.evidencia} Alternativa: ${v.decisao.alternativa} Limite: ${v.decisao.limite}`).join('\n\n'),['Politica_Atributos.json','Parecer_Semantico_e_Decisoes.md']);
}
//18. Definitions
{
 const s=slide('Métricas e classe positiva',18,{hidden:true});
 txt(s,'Positiva: Anormal. Limiar fixo: 0,5.',64,160,1152,55,34,C.teal,true);
 const defs=['Sensibilidade = TP / (TP + FN)','Especificidade = TN / (TN + FP)','BA = (sensibilidade + especificidade) / 2','ROC-AUC resume a ordenação dos escores'];
 defs.forEach((t,i)=>txt(s,t,64,265+i*83,1152,65,31));
 backupNotes(s,18,'Métricas e classe positiva','TP e TN representam concordância com os rótulos registrados. FP e FN representam divergência. A referência que prevê Normal para todos tem sensibilidade zero e especificidade um, portanto BA de 0,5. AUC usa os escores ao longo de limiares e não prova calibração. A definição da classe positiva e o limiar permanecem fixos para as comparações.',['family_nested_metrics.csv','protocol_before_results.json']);
}
//19. Search
{
 const s=slide('Espaço de busca por família',19,{hidden:true});
 table(s,[['Família','Configurações','Variações previstas'],['Referência','1','Classe mais frequente'],['Árvore','48','Profundidade, folha, critério, pesos e imputação'],['Logística','32','Regularização, pesos, imputação e representação'],['Floresta','24','Profundidade, folha, pesos e imputação'],['Total','105','Mesma busca por cenário']],64,155,1152,390,[260,230,662],{size:24});
 txt(s,'Busca interna por família em cada fold externo. Seleção final em todo o desenvolvimento é um ajuste separado.',64,589,1152,73,25,C.muted);
 backupNotes(s,19,'Espaço de busca por família','Árvore: profundidades 2, 4 e 6, folhas mínimas 20 ou 50, critérios gini/entropy, peso padrão ou balanceado e imputação global ou por idade. Logística: C em 0,01, 0,1, 1 e 10, pesos, duas imputações e representações padronizada ou log/padronizada. Floresta: 150 árvores, profundidade 4, 8 ou ilimitada, folhas 10 ou 30, pesos e imputação. A contagem total de 105 representa o produto das opções em cada família. O número de candidatos não implica o mesmo custo computacional. O protocolo congela a ordem para desempates.',['protocol_before_results.json']);
}
//20. Exploratory probes
{
 const s=slide('Ensaios com variável única',20,{hidden:true});
 const selected=['SOPRO','B2','PULSOS','PPA','MOTIVO1','MOTIVO2','HDA 1','HDA2'];
 const values=[['Variável','BA do ensaio','Papel na revisão']];
 selected.forEach(name=>{const r=D.probes.find(x=>x.variable===name);values.push([name,pct(r.cv_balanced_accuracy),'Auditoria no desenvolvimento']);});
 table(s,values,64,148,1152,450,[340,280,532],{size:23});
 txt(s,'Sinal preditivo não demonstra ordem temporal nem geração de y. Campos excluídos não competem pelo modelo principal.',64,621,1152,48,23,C.orange);
 backupNotes(s,20,'Ensaios com variável única','Os ensaios usam uma variável por vez para investigar associação preditiva no desenvolvimento e não para selecionar campos admissíveis. Sua configuração e interpretação são distintas da validação aninhada das famílias. Variáveis preparadas podem manter informação de seus pais determinísticos. Mesmo um escore muito alto não prova incorporação nem retrospectividade, e um baixo não absolve diagnóstico prévio. Os ensaios não participam da escolha do modelo principal.',['variable_probes.csv','protocol_before_results.json']);
}
//21. Sources and disclosure
{
 const s=slide('Fontes e reprodução',21,{hidden:true});
 txt(s,'Fontes locais',64,160,1152,45,34,C.teal,true);
 txt(s,'Dicionário e tema do estudo UCMF\nMaterial complementar de PPA e investigação diagnóstica\nRubrica A2, protocolo congelado e manifestos de execução',64,230,1152,177,29);
 txt(s,'github.com/pedroafm06/Data-Mining-A2',64,442,1152,72,29);
 txt(s,'Uso de IA: Codex/OpenAI no código, nas análises e na redação. Conferência por fontes locais e saídas reproduzíveis.',64,552,1152,104,27,C.muted);
 backupNotes(s,21,'Fontes e reprodução','Fontes primárias: Tema do estudo de caso.pdf, Variáveis do conjunto de dados (SIGAA 03-11-2026).pdf, complementos Guideline for diagnostic.pdf e Explanation about the PPA variable.pdf. A1 é fonte secundária preservada. A rubrica recebida em 07/11/2026 exige artigo IEEE curto e exclusão de campos com leakage. Código e execução: src/kdd_revision/rubric_audit.py, artifacts/a2_rubric_audit/protocol_before_results.json, verification.json e manifest.json. A origem bruta permanece local e não está embutida no deck. IA generativa: Codex/OpenAI apoiou scripts, auditoria, organização metodológica e redação. O grupo deve compreender e conferir todos os resultados e responder pela entrega. Nenhuma alegação de revisão humana posterior é pressuposta.',['Politica_Atributos.json','manifest.json','verification.json']);
}

if(p.slides.items.length!==21)throw new Error('Expected 21 slides: 14 main and 7 hidden backup');
const proto=p.toProto();await fs.writeFile(path.join(BUILD,'deck.proto.json'),JSON.stringify(proto));
const candidate=path.join(BUILD,`candidate-${revision}.pptx`);
await (await PresentationFile.exportPptx(p)).save(candidate);
for(const [index,s] of p.slides.items.entries()){
 const file=path.join(QA,`slide-${String(index+1).padStart(2,'0')}.png`);
 const img=await p.export({slide:s,format:'png',scale:1});await fs.writeFile(file,new Uint8Array(await img.arrayBuffer()));
 const layout=await s.export({format:'layout'});await fs.writeFile(path.join(QA,`slide-${String(index+1).padStart(2,'0')}.layout.json`),await layout.text());
}
let script='# Roteiro e preparação para arguição\n\n14 slides principais, 14 min 30 s. Os sete slides de apoio ficam ocultos na apresentação. Qualquer integrante deve compreender todo o roteiro.\n\n';
for(const a of D.authors){const sec=D.notes.filter(n=>n.author===a).reduce((x,n)=>x+n.seconds,0);script+=`- ${a}: ${Math.floor(sec/60)} min ${sec%60} s.\n`;}
for(const n of allNotes){script+=`\n## ${n.number}. ${n.title}${n.hidden?' (apoio)':''}\n\n`;if(!n.hidden)script+=`Responsável sugerido: ${n.author}. Tempo: ${Math.floor(n.seconds/60)}:${String(n.seconds%60).padStart(2,'0')}.\n\n`;script+=n.text+'\n\n';if(n.question)script+=`**Pergunta possível:** ${n.question}\n\n**Resposta:** ${n.answer}\n\n`;script+='**Fontes locais:** '+n.sources.join(', ')+'.\n';}
script+='\n## Preparação conjunta\n\nCada integrante deve conseguir explicar a classe positiva, a diferença entre treino interno e avaliação externa, o motivo das exclusões, a interpretação da matriz e os limites da referência do alvo. Ensaiar a transição entre autores. O tempo indicado é uma meta de ensaio, não uma medição de apresentação real. Os slides de apoio não entram nos 14 min 30 s.\n';
await fs.writeFile(path.join(FINAL?OUT:BUILD,'Roteiro_e_Arguicao.md'),script);
await fs.writeFile(path.join(QA,'authoring_summary.json'),JSON.stringify({font:FONT,slides:21,main:14,hidden:7,seconds:870,tableOwners,chartOwners,source_complete:D.verification.complete,historical_test_used:D.verification.historical_test_rows_used},null,2));
if(FINAL){
 const finalPath=path.join(OUT,`Apresentacao_A2_UCMF${revision==='v1'?'':'-'+revision}.pptx`);
 const result=await finalizePresentation({workspaceDir:DIR,candidatePath:candidate,finalPath,pythonExecutable:PY,integrityValidatorPath:path.join(SKILL,'container_tools/inspect_presentation_package_integrity.py'),layoutValidatorPath:path.join(SKILL,'container_tools/inspect_presentation_layout_geometry.py'),layoutArgs:['--expected-slide-size-emu','12192000,6858000','--validate-bullet-geometry','--validate-heading-fit',...tableOwners.flatMap(n=>['--require-native-table-slide',String(n)])],explicitTotalSlideCount:21,requiredNativeTableOwnerSlides:tableOwners,requiredNativeChartOwnerSlides:chartOwners,materializeLiteralChartWorkbooks:true,fontPolicy:{basis:'design',families:[FONT]},verifyArtifactToolImport:true,receiptPath:path.join(QA,`final-${revision}.validation.json`)});
 console.log(JSON.stringify({finalPath,result},null,2));
}else console.log(JSON.stringify({draft:candidate,slides:p.slides.items.length,font:FONT}));

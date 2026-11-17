import fs from 'node:fs/promises';
import path from 'node:path';
import {createRequire} from 'node:module';
import {fileURLToPath, pathToFileURL} from 'node:url';

const dir = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(dir, '../..');
const runtime = process.env.RUNTIME_NODE_MODULES;
const skill = process.env.CODEX_PRESENTATIONS_SKILL;
const work = path.join(root, 'work/a2_apresentacao_inf');
const require = createRequire(path.join(runtime, 'presentation-runtime.cjs'));
const {Presentation, PresentationFile} = await import(pathToFileURL(require.resolve('@oai/artifact-tool')));
const {finalizePresentation} =
  await import(path.join(skill, 'container_tools/artifact_tool_utils.mjs'));

const results = JSON.parse(await fs.readFile(path.join(root, 'resultados/a2/revisao_final_2026_11_16/reviewed_results.json'), 'utf8'));
const script = JSON.parse(await fs.readFile(path.join(dir, 'roteiro.json'), 'utf8'));
const background = new Uint8Array(await fs.readFile(path.join(work, 'template-000.jpg')));
const presentation = Presentation.create({slideSize:{width:1280,height:720}});
const palette = {blue:'#005C9C', ink:'#142632', muted:'#415766', light:'#E9F3FA', faint:'#F4F7F9',
  line:'#D5E3EC', white:'#FFFFFF', red:'#99362C', warm:'#FBEEEB'};
const headFont = 'Caladea';
const bodyFont = 'Open Sans';
const tableOwners = [];
const slideCount = script.slides.length;
const allNotes = script.slides;
const totalSlideCount = slideCount;
const metric = (pool, family) => results.metrics.find(m => m.pool === pool && m.family === family);
const percent = (x, decimals=2) => (100*x).toFixed(decimals).replace('.',',')+'%';
const number = n => n.toLocaleString('pt-BR');
const points = (x, decimals=2) => (100*x).toFixed(decimals).replace('.',',');
const importance = (pool, family, key) => results.importance.find(x => x.pool === pool && x.family === family && x.variable === key).mean;
const fisio = metric('FISIO8','forest');
const strict = metric('STRICT4','tree');
const clin = metric('CLINICO','tree');
const famDiff = results.bootstrap.differences.find(x => x.a === 'FISIO8/forest' && x.b === 'FISIO8/logistic');
const treePaths = results.tree_rules_development.FISIO8.map(leaf => leaf.conditions.slice(0,2));
const weightLimit = Number(treePaths[0][0].split(' ').at(-1));
const ageLimit = Number(treePaths.find(([branch]) => branch.includes('≤'))[1].split(' ').at(-1));
const pulseLimit = Number(treePaths.find(([branch]) => branch.includes('>'))[1].split(' ').at(-1));
const decimal = (x, decimals=2) => x.toFixed(decimals).replace('.',',');

function text(s, value, x, y, w, h, opt={}) {
  const box = s.shapes.add({geometry:'textbox', name:opt.name||'texto',
    position:{left:x,top:y,width:w,height:h},fill:'none',line:{fill:'none',width:0}});
  box.text = value;
  box.text.style = {typeface:opt.font||bodyFont,fontSize:opt.size||29,color:opt.color||palette.ink,
    bold:!!opt.bold,italic:!!opt.italic,alignment:opt.align||'left',verticalAlignment:opt.valign||'middle',
    autoFit:'none',wrap:'square',insets:0};
  return box;
}
function rect(s, x, y, w, h, fill, name='destaque') {
  return s.shapes.add({geometry:'rect',name,position:{left:x,top:y,width:w,height:h},fill,line:{fill:'none',width:0}});
}
function slide(n, title) {
  const s = presentation.slides.add();
  s.background.fill = palette.white;
  s.images.add({blob:background,contentType:'image/jpeg',alt:'Fundo institucional da UFG usado no Canva da A1',
    fit:'contain',position:{left:0,top:0,width:1280,height:720}});
  if (title) text(s,title,51,59,1178,73,{font:headFont,size:49,bold:true,color:palette.blue,align:'center',name:'slide-title'});
  text(s,n<=slideCount?String(n).padStart(2,'0')+' / '+slideCount:'Apoio '+(n-slideCount),42,659,190,36,{size:21,color:palette.white,italic:true,name:'número do slide'});
  const note = allNotes[n-1];
  if (note.number !== n || (title && note.title !== title)) throw new Error('Nomes dos slides e roteiro divergem no slide '+n);
  s.speakerNotes.text = (note.author||'Consulta durante a arguição')+(note.seconds?'  ·  '+clock(note.seconds):'')+'\n\n'+note.text+'\n\nNotas de apoio\n'+(note.technical_notes||[]).join('\n')+'\n\nFontes\n'+note.sources.join('\n');
  return s;
}
function clock(seconds) {
  return Math.floor(seconds / 60)+':'+String(seconds % 60).padStart(2,'0');
}
const H = {size:32,bold:true,color:palette.blue};
const m = {size:27,color:palette.muted};
const center = {align:'center'};
function table(s, values, x, y, widths, heights, {emphasis, errorCell=false, bodySize=29, labelSize=27, headerSize=26}={}) {
  const t = s.tables.add({rows:values.length,columns:values[0].length,left:x,top:y,
    width:widths.reduce((a,b)=>a+b,0),height:heights.reduce((a,b)=>a+b,0),columnWidths:widths,values});
  t.borders.assign({fill:palette.line,width:1,style:'solid'});
  for (let row=0;row<values.length;row++) {
    t.rows[row].height=heights[row];
    for (let col=0;col<values[row].length;col++) {
      const cell=t.getCell(row,col);
      const isError=errorCell && row===2 && col===1;
      cell.fill=row===0?palette.blue:isError?palette.warm:row===emphasis?palette.light:col===0?palette.faint:palette.white;
      cell.text.style={typeface:bodyFont,fontSize:row===0?headerSize:col===0?labelSize:errorCell?38:bodySize,color:row===0?palette.white:isError?palette.red:palette.ink,
        bold:true,alignment:col===0?'left':'center',verticalAlignment:'middle',autoFit:'none',insets:{left:15,right:12,top:6,bottom:6}};
    }
  }
  tableOwners.push(presentation.slides.items.length);
}

{
  const s=slide(1,'');
  text(s,'Classificação de registros\ncardíacos pediátricos',120,111,1040,164,
    {size:58,bold:true,align:'center',name:'título de capa'});
  text(s,'Mineração de Dados · Avaliação 2',140,274,1000,54,{...H,...center});
  text(s,'Antônio Henrique · João Vitor · Mateus Nery · Pedro Matos',105,347,1070,47,{size:27,...center});
  text(s,'Grupo 3 · INF/UFG · Prof. Rogério Lopes Salvini · 2026/2',125,408,1030,42,{...m,...center});
}
{
  const s=slide(2,'A base e o objetivo');
  text(s,'As medidas ajudam a prever o rótulo Normal ou Anormal?',90,146,1100,68,{size:32,bold:true,...center});
  text(s,number(results.n_original),100,227,490,84,{size:69,bold:true,color:palette.blue,...center});
  text(s,'fichas na base original',100,310,490,48,{size:30,...center});
  text(s,number(results.n_labelled)+' com rótulo',100,363,490,47,{...m,...center});
  text(s,number(results.n_development),671,227,510,84,{size:69,bold:true,color:palette.blue,...center});
  text(s,'fichas na avaliação final',671,310,510,48,{size:30,...center});
  text(s,number(results.class_counts.Normal)+' Normal e '+number(results.class_counts.Anormal)+' Anormal',649,363,552,47,{...m,...center});
  text(s,'Atendimentos de cardiologia pediátrica no Real Hospital Português, Recife',83,443,1114,47,{size:26,color:palette.muted,...center});
}
{
  const s=slide(3,'Seleção das entradas');
  text(s,'8 entradas principais',96,160,560,51,H);
  text(s,'Idade e sexo\nPeso, altura e IMC\nPressão sistólica e diastólica\nFrequência cardíaca',96,225,585,221,{size:31});
  text(s,'Campos excluídos',745,160,450,51,H);
  text(s,'Motivo do encaminhamento\npode antecipar o rótulo.',745,229,450,104,{size:29});
  text(s,'ID e convênio não medem\no estado do paciente.',745,358,450,95,{size:29});
}
{
  const s=slide(4,'Limpeza dos dados');
  text(s,'Exemplo real de frequência cardíaca',96,148,1088,49,{...H,size:31});
  table(s,[['Campo','Registro original','Após a limpeza'],['Batimentos por minuto','1.120','Ausente']],
    96,216,[420,335,335],[51,72],{bodySize:37,labelSize:28});
  text(s,'O valor supera a regra de suspeita de 500 batimentos/min.',96,354,1092,49,{size:29});
  text(s,'Também padronizamos números, conferimos datas e marcamos inconsistências.',96,419,1092,75,{size:29});
}
{
  const s=slide(5,'Preenchimento e atributos derivados');
  text(s,'Preenchimento da frequência cardíaca',96,151,1088,46,{...H,size:31});
  table(s,[['Após a limpeza','Mediana do treino*','Indicador de preenchimento'],['Ausente','92 batimentos/min','1']],
    96,211,[310,370,410],[52,66],{bodySize:34});
  text(s,'*92 é a mediana no ajuste final da floresta.',96,335,1088,46,{...m});
  text(s,'IMC de outra ficha real',96,398,415,65,{size:29,bold:true,color:palette.blue});
  text(s,'5 kg ÷ (0,51 m)² = 19,22 kg/m²',510,396,680,68,{size:35,bold:true});
}
{
  const s=slide(6,'Representação para os modelos');
  text(s,'Categorias em colunas de 0 ou 1',96,149,1088,50,H);
  table(s,[['Sexo registrado','Coluna F','Coluna M'],['F','1','0'],['M','0','1']],
    96,210,[410,340,340],[45,48,48],{bodySize:33});
  text(s,'Logística',96,374,265,47,{size:30,bold:true,color:palette.blue});
  text(s,'Testamos padronização e logaritmo do peso.',367,374,825,47,{size:29});
  text(s,'Floresta final',96,437,265,47,{size:30,bold:true,color:palette.blue});
  text(s,'Manteve as medidas nas unidades originais.',367,437,825,47,{size:29});
}
{
  const s=slide(7,'Três maneiras de classificar');
  table(s,[['Modelo','Como faz a previsão','Por que comparar'],
    ['Árvore de decisão','Perguntas em sequência\nEx.: peso até 8,85 kg?','Permite acompanhar\nas decisões.'],
    ['Regressão logística','Combina contribuições\npara estimar uma chance.','Testa uma relação\nmais simples.'],
    ['Floresta aleatória','Faz a média das chances\nde 150 árvores.','Capta relações\nmais variadas.']],
    80,163,[320,430,370],[49,83,83,83],{bodySize:27,labelSize:28});
}
{
  const s=slide(8,'Escolha dos ajustes e avaliação');
  text(s,'Cinco partes, com as mesmas divisões para todos os modelos',96,147,1090,53,{size:30,bold:true});
  for(let i=0;i<5;i++){
    rect(s,98+i*220,222,204,61,i===4?palette.blue:palette.light,'parte da validação '+(i+1));
    text(s,String(i+1),98+i*220,223,204,58,{size:31,bold:true,color:i===4?palette.white:palette.blue,...center});
  }
  text(s,'Treino e escolha dos ajustes',98,293,870,47,{size:29,bold:true});
  text(s,'Avaliação',978,293,204,47,{size:28,bold:true,color:palette.blue,...center});
  text(s,'Dentro do treino, 3 divisões comparam 105 configurações por cenário.',98,354,1084,65,{size:28});
  text(s,'Calculamos o preenchimento só no treino. Fichas idênticas ficam juntas.',98,430,1084,65,{size:28});
}
{
  const s=slide(9,'Acurácia balanceada');
  text(s,'Referência simples que prevê Normal para todas as fichas',96,147,1088,60,{size:30,...center});
  text(s,'100%',118,222,472,93,{size:73,bold:true,color:palette.blue,...center});
  text(s,'Especificidade\nNormais reconhecidos',100,311,508,76,{size:28,...center});
  text(s,'0%',690,222,472,93,{size:73,bold:true,color:palette.red,...center});
  text(s,'Sensibilidade\nAnormais reconhecidos',666,311,520,76,{size:28,...center});
  text(s,'Média dos acertos de cada classe = 50%',104,396,1072,67,{size:38,bold:true,...center});
}
{
  const s=slide(10,'Comparação dos modelos');
  text(s,'Acurácia balanceada nas oito entradas principais',96,146,1088,52,{...m,...center,size:29});
  const scores=['dummy','tree','logistic','forest'].map((fam,i)=>[
    ['Sempre Normal','Árvore de decisão','Regressão logística','Floresta aleatória'][i],percent(metric('FISIO8',fam).balanced_accuracy)]);
  table(s,[['Modelo','Pontuação'],...scores],112,215,[574,482],[48,46,46,46,46],{emphasis:4,bodySize:33,labelSize:29,headerSize:28});
  text(s,'Ajuste final da floresta com pelo menos 30 fichas por folha.',112,459,1056,51,{size:27,color:palette.muted});
}
{
  const s=slide(11,'Acertos e erros da floresta');
  table(s,[['Rótulo registrado','Previu Normal','Previu Anormal'],['Normal',number(fisio.tn),number(fisio.fp)],
    ['Anormal',number(fisio.fn),number(fisio.tp)]],87,169,[308,231,231],[58,77,77],{errorCell:true,headerSize:26,labelSize:29});
  text(s,'42 em 100',891,186,312,79,{size:51,bold:true,color:palette.red,...center});
  text(s,'registros Anormal\npassaram como Normal',873,270,334,96,{size:28,...center});
  text(s,'Reconheceu 58% dos Anormais e 68% dos Normais.',96,422,1088,63,{size:31,bold:true,...center});
}
{
  const s=slide(12,'Métricas que complementam a comparação');
  table(s,[['Métrica','Floresta','O que acrescenta'],
    ['Precisão',percent(fisio.precision),'Acertos entre previsões Anormal'],
    ['F1',percent(fisio.f1),'Combina precisão e sensibilidade'],
    ['Precisão média (AP)',percent(fisio.average_precision),'Precisão ao recuperar mais Anormais']],
    78,178,[326,250,550],[53,77,77,77],{bodySize:28,labelSize:29,headerSize:26});
}
{
  const s=slide(13,'Quais medidas a floresta mais usou');
  text(s,'Embaralhamos uma medida entre as fichas e medimos a queda.',96,147,1088,73,{size:29,...center});
  const features=[['Frequência cardíaca','FC'],['Peso','Peso'],['Idade','IDADE']];
  features.forEach(([label,key],i)=>{
    const x=82+i*376;
    text(s,points(importance('FISIO8','forest',key))+' p.p.',x,242,364,96,{size:61,bold:true,color:palette.blue,...center});
    text(s,label,x,342,364,65,{size:29,bold:true,...center});
  });
  text(s,'Uma queda maior indica maior dependência daquela medida.',96,433,1088,55,{...m,...center});
}
{
  const s=slide(14,'O resultado muda com as entradas');
  table(s,[['Cenário','Informações disponíveis','Melhor pontuação'],
    ['4 entradas','Idade, sexo, peso e altura',percent(strict.balanced_accuracy)],
    ['8 entradas\nPrincipal','As 4 básicas, IMC, duas\npressões e frequência cardíaca',percent(fisio.balanced_accuracy)],
    ['13 entradas\nExploratório','As 8 principais, sopro, B2, pulsos,\npressão classificada e sintomas',percent(clin.balanced_accuracy)]],
    64,166,[249,632,271],[51,65,86,86],{emphasis:2,bodySize:27,labelSize:27,headerSize:26});
  text(s,'Achados do exame podem ter participado da definição do rótulo.',80,451,1120,52,{size:28,bold:true,...center});
}
{
  const s=slide(15,'O papel do sopro');
  text(s,'Fichas com rótulo Anormal em cada grupo',96,146,1088,53,{size:31,...center});
  const groups=results.eda.sopro_by_status;
  for(const [i,key] of ['Ausência registrada','Presença registrada'].entries()){
    const row=groups[key], x=105+i*565;
    text(s,percent(row.n_anormal/row.n,1),x,214,500,89,{size:73,bold:true,color:palette.blue,...center});
    text(s,i===0?'Sopro registrado como ausente':'Com sopro registrado',x,309,500,62,{size:28,bold:true,...center});
  }
  text(s,'Ainda falta confirmar quando o achado e o rótulo foram registrados.',88,448,1104,54,{size:28,bold:true,...center});
}
{
  const s=slide(16,'Conclusões do trabalho');
  text(s,percent(fisio.balanced_accuracy),100,161,418,106,{size:83,bold:true,color:palette.blue,...center});
  text(s,'acurácia balanceada\ncom 8 entradas',98,278,422,102,{size:30,...center});
  text(s,'A floresta superou a referência,\ncom muitos Anormais ainda perdidos.',606,162,587,112,{size:31,bold:true});
  text(s,'Próximo passo',606,303,587,49,{...H,size:30});
  text(s,'Confirmar a origem do rótulo\ne avaliar em novas fichas.',606,357,587,100,{size:30});
}


const seconds=script.slides.reduce((sum,item)=>sum+item.seconds,0);
if(presentation.slides.items.length!==totalSlideCount||slideCount!==16||seconds!==835) throw new Error('Temporização e número de slides divergentes');
const candidate=path.join(work,'candidate.pptx');
await (await PresentationFile.exportPptx(presentation)).save(candidate);

const out=path.join(dir,'output');
await fs.mkdir(out,{recursive:true});
const name=process.env.UCMF_DECK_NAME||'Apresentacao_A2_INF';
const validated=await fs.mkdtemp(path.join(work,'validacao-'));
const finalPath=path.join(validated,name+'.pptx');
await finalizePresentation({workspaceDir:work,candidatePath:candidate,finalPath,
  pythonExecutable:process.env.CODEX_PRESENTATIONS_PYTHON||'python3',
  integrityValidatorPath:path.join(skill,'container_tools/inspect_presentation_package_integrity.py'),
  layoutValidatorPath:path.join(skill,'container_tools/inspect_presentation_layout_geometry.py'),
  layoutArgs:['--expected-slide-size-emu','12192000,6858000','--validate-heading-fit',...tableOwners.flatMap(n=>['--require-native-table-slide',String(n)])],
  explicitTotalSlideCount:totalSlideCount,requiredNativeTableOwnerSlides:tableOwners,
  fontPolicy:{basis:'design',families:[headFont,bodyFont]},
  verifyArtifactToolImport:true,receiptPath:path.join(work,name+'.'+path.basename(validated)+'.validation.json')});

await fs.copyFile(finalPath,path.join(out,name+'.pptx'));

const totals = new Map();
let elapsed = 0;
let talk = '# Roteiro da apresentação da A2\n\nTempo de fala previsto de 13 min 55 s, mais 35 s para pausas e transições. Total planejado de 14 min 30 s, com 30 s de margem até o limite de 15 minutos. Confirmar em ensaio.\n\n';
for(const n of script.slides) totals.set(n.author,(totals.get(n.author)||0)+n.seconds);
for(const [author, duration] of totals) talk += '- '+author+' · '+clock(duration)+'\n';
for(const n of script.slides){
  talk+='\n## '+n.number+'. '+n.title+'\n\n'+n.author+' · '+clock(elapsed)+' a '+clock(elapsed+n.seconds)+'\n\n'+n.text+'\n';
  if(n.technical_notes?.length) talk+='\nNotas de apoio, para consulta e arguição\n\n'+n.technical_notes.map(x=>'- '+x).join('\n')+'\n';
  elapsed+=n.seconds;
}
talk+='\n## Arguição\n';
for(const item of script.qa) talk+='\n**'+item.question+'**\n\n'+item.answer+'\n';
await fs.writeFile(path.join(out,'Roteiro_A2_INF.md'),talk,'utf8');
console.log(finalPath);

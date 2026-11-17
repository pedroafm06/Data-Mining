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
const metric = (pool, family) => results.metrics.find(m => m.pool === pool && m.family === family);
const percent = (x, decimals=2) => (100*x).toFixed(decimals).replace('.',',')+'%';
const number = n => n.toLocaleString('pt-BR');
const points = (x, decimals=2) => (100*x).toFixed(decimals).replace('.',',');
const importance = (pool, family, key) => results.importance.find(x => x.pool === pool && x.family === family && x.variable === key).mean;
const fisio = metric('FISIO8','forest');
const strict = metric('STRICT4','tree');
const clin = metric('CLINICO','tree');
const famDiff = results.bootstrap.differences.find(x => x.a === 'FISIO8/forest' && x.b === 'FISIO8/logistic');

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
  text(s,String(n).padStart(2,'0')+' / 14',42,659,190,36,{size:21,color:palette.white,italic:true,name:'número do slide'});
  const note = script.slides[n-1];
  if (note.number !== n || (title && note.title !== title)) throw new Error('Nomes dos slides e roteiro divergem no slide '+n);
  s.speakerNotes.text = note.author+'  ·  '+clock(note.seconds)+'\n\n'+note.text+'\n\nFontes\n'+note.sources.join('\n');
  return s;
}
function clock(seconds) {
  return Math.floor(seconds / 60)+':'+String(seconds % 60).padStart(2,'0');
}
const H = {size:32,bold:true,color:palette.blue};
const m = {size:24,color:palette.muted};
const center = {align:'center'};
function table(s, values, x, y, widths, heights, {emphasis, errorCell=false}={}) {
  const t = s.tables.add({rows:values.length,columns:values[0].length,left:x,top:y,
    width:widths.reduce((a,b)=>a+b,0),height:heights.reduce((a,b)=>a+b,0),columnWidths:widths,values});
  t.borders.assign({fill:palette.line,width:1,style:'solid'});
  for (let row=0;row<values.length;row++) {
    t.rows[row].height=heights[row];
    for (let col=0;col<values[row].length;col++) {
      const cell=t.getCell(row,col);
      const isError=errorCell && row===2 && col===1;
      cell.fill=row===0?palette.blue:isError?palette.warm:row===emphasis?palette.light:col===0?palette.faint:palette.white;
      cell.text.style={typeface:bodyFont,fontSize:row===0||col===0?23:errorCell?38:30,color:row===0?palette.white:isError?palette.red:palette.ink,
        bold:true,alignment:col===0?'left':'center',verticalAlignment:'middle',autoFit:'none',insets:{left:15,right:12,top:6,bottom:6}};
    }
  }
  tableOwners.push(presentation.slides.items.length);
}

{
  const s=slide(1,'');
  text(s,'Classificação de registros\ncardíacos pediátricos',135,115,1010,158,
    {size:58,bold:true,align:'center',name:'título de capa'});
  text(s,'Mineração de Dados · Avaliação 2',140,275,1000,54,{...H,...center});
  text(s,'Grupo 3 · Antônio Henrique · João Vitor · Mateus Nery · Pedro Matos',125,341,1030,48,{size:25,...center});
  text(s,'INF0414 · Prof. Rogério Lopes Salvini · UFG · 2026/2',155,394,970,42,{...m,...center});
}
{
  const s=slide(2,'O que o modelo tenta prever');
  text(s,'Uma ficha fictícia',118,156,550,53,H);
  rect(s,118,219,514,184,palette.light,'campos da ficha fictícia');
  text(s,'Idade  6 anos\nPeso  20 kg\nFrequência cardíaca  90 bpm',147,235,455,149,{size:29});
  text(s,'Medidas usadas como entrada',118,411,514,48,m);
  text(s,'Rótulo registrado',747,180,430,55,H);
  text(s,'Normal ou Anormal',747,249,445,70,{size:44,bold:true,color:palette.ink});
  text(s,'O modelo aprende com fichas\nem que o rótulo já é conhecido',747,328,443,86,{size:25,color:palette.muted});
}
{
  const s=slide(3,'De onde vêm os dados');
  text(s,'Real Hospital Português · Recife',120,148,1040,54,{...m,...center,size:28});
  text(s,number(results.n_original),124,214,452,90,{size:70,bold:true,color:palette.blue,...center});
  text(s,'fichas na base original',124,299,452,52,{size:30,...center});
  text(s,number(results.n_development),675,214,480,90,{size:70,bold:true,color:palette.blue,...center});
  text(s,'fichas na avaliação final',675,299,480,52,{size:30,...center});
  text(s,number(results.class_counts.Normal)+' Normal     ·     '+number(results.class_counts.Anormal)+' Anormal',
    182,380,916,53,{size:29,color:palette.muted,...center});
}
{
  const s=slide(4,'Limpeza e transformação');
  text(s,'Limpeza',116,163,470,62,H);
  text(s,'Unificamos unidades e marcamos\nvalores suspeitos como ausentes.',116,226,500,98,{size:28});
  text(s,'Exemplo fictício · altura de 0 cm',116,342,490,46,{...m,size:23});
  text(s,'Transformação',686,163,487,62,H);
  text(s,'Preenchemos ausências com\nvalores aprendidos no treino.',686,226,487,98,{size:28});
  text(s,'A logística usa medidas em escala comum.',686,342,488,59,{...m,size:23});
}
{
  const s=slide(5,'Quando uma entrada já traz a resposta');
  text(s,'Motivo do encaminhamento',132,165,1016,51,{...H,...center});
  rect(s,170,225,940,86,palette.light,'exemplo de encaminhamento');
  text(s,'“Cardiopatia já estabelecida”',182,232,916,68,{size:41,bold:true,...center});
  text(s,'Um campo assim pode antecipar o rótulo.',128,326,1024,57,{size:31,...center});
  text(s,'Excluímos os motivos de encaminhamento dos três cenários.',130,403,1020,52,{...m,...center});
}
{
  const s=slide(6,'Três maneiras de classificar');
  const blocks=[
    ['Árvore de decisão','Faz perguntas em sequência.','A frequência cardíaca ultrapassa um limite?'],
    ['Regressão logística','Combina as medidas em uma estimativa.','Cada medida contribui para a chance de Anormal.'],
    ['Floresta aleatória','Reúne as previsões de muitas árvores.','Cada árvore contribui para a decisão final.'],
  ];
  blocks.forEach(([name,detail,example],i)=>{
    const y=153+i*102;
    text(s,name,106,y,381,45,{...H,size:29});
    text(s,detail,494,y,674,43,{size:27,bold:true});
    text(s,example,494,y+37,674,40,m);
    if(i<2)rect(s,109,y+87,1060,1,palette.line,'linha de leitura');
  });
}
{
  const s=slide(7,'Como avaliamos os modelos');
  text(s,'Dividimos as fichas em cinco partes.',117,151,1035,46,{size:29});
  for(let i=0;i<5;i++){
    rect(s,119+i*211,225,193,63,i===4?palette.blue:palette.light,'parte '+(i+1));
    text(s,String(i+1),119+i*211,226,193,59,{size:28,bold:true,color:i===4?palette.white:palette.blue,...center});
  }
  text(s,'Quatro partes para escolher ajustes e treinar',119,303,819,49,{size:27,bold:true});
  text(s,'Uma para avaliar',957,303,218,52,{size:23,bold:true,color:palette.blue,...center});
  text(s,'Cada parte é usada uma vez na avaliação.',119,365,1036,49,m);
  text(s,'Fichas com entradas idênticas ficam juntas.',119,420,1036,48,{...m,bold:true});
}
{
  const s=slide(8,'Acurácia balanceada');
  text(s,'Se o modelo previsse sempre Normal',135,150,1010,55,{size:31,...center});
  text(s,'100% dos Normais',111,228,500,73,{size:43,color:palette.blue,bold:true,...center});
  text(s,'reconhecidos',111,300,500,44,{...m,...center});
  text(s,'0% dos Anormais',669,228,500,73,{size:43,color:palette.red,bold:true,...center});
  text(s,'reconhecidos',669,300,500,44,{...m,...center});
  text(s,'Média dos dois acertos = 50%',129,378,1022,71,{size:41,bold:true,...center});
}
{
  const s=slide(9,'A floresta teve o melhor resultado');
  text(s,'Cenário principal com oito entradas por ficha',115,134,1050,42,{...m,...center});
  const scores = ['dummy','tree','logistic','forest'].map((fam,i) => [
    ['Sempre Normal','Árvore de decisão','Regressão logística','Floresta aleatória'][i], percent(metric('FISIO8',fam).balanced_accuracy)
  ]);
  table(s,[['Modelo','Acurácia balanceada'],...scores],139,191,[411,293],[52,47,47,47,47],{emphasis:4});
  text(s,'+'+points(famDiff.diff)+' p.p.',948,215,257,73,{size:48,bold:true,color:palette.blue});
  text(s,'da floresta sobre\na logística',948,293,252,90,{size:27,color:palette.muted});
}
{
  const s=slide(10,'Os erros da floresta');
  table(s,[['Rótulo registrado','Previu Normal','Previu Anormal'],['Normal',number(fisio.tn),number(fisio.fp)],
    ['Anormal',number(fisio.fn),number(fisio.tp)]],95,192,[276,208,217],[54,72,72],{errorCell:true});
  text(s,'42 de cada 100',835,201,367,70,{size:46,bold:true,color:palette.red});
  text(s,'registros Anormal receberam\nprevisão Normal.',835,278,375,95,{size:27,color:palette.ink});
  text(s,'Floresta no cenário principal, nas 9.361 fichas avaliadas.',98,412,1080,50,m);
}
{
  const s=slide(11,'Quais medidas a floresta mais usou');
  text(s,'Embaralhamos uma medida entre as fichas e medimos a queda.',99,148,1082,58,{size:27,...center});
  const feature=[['Frequência cardíaca','FC'],['Peso','Peso'],['Idade','IDADE']];
  feature.forEach(([label,key],i)=>{
    const x=91+i*373;
    text(s,points(importance('FISIO8','forest',key))+' p.p.',x,235,352,88,{size:56,bold:true,color:palette.blue,...center});
    text(s,label,x,324,352,58,{size:28,bold:true,...center});
  });
  text(s,'Queda na acurácia balanceada da floresta',110,415,1060,44,{...m,...center});
}
{
  const s=slide(12,'O resultado muda com as entradas');
  text(s,'Melhor resultado em cada conjunto de informações',113,136,1054,42,{...m,...center});
  const scenarios=[['4 entradas básicas',strict,'Árvore'],['8 entradas principais',fisio,'Floresta'],['13 entradas com achados',clin,'Árvore · exploratório']];
  scenarios.forEach(([label,result,model],i)=>{
    const x=73+i*378, emphasized=i===1;
    text(s,label,x,216,378,48,{...center,size:25,bold:true});
    text(s,percent(result.balanced_accuracy),x,268,378,90,{...center,size:66,bold:true,color:emphasized?palette.blue:palette.muted});
    text(s,model,x,355,378,42,{...m,...center});
  });
  text(s,'Os 13 dados incluem achados do exame, como sopro.',117,434,1046,43,{...m,...center});

}
{
  const s=slide(13,'O papel do sopro');
  text(s,'Proporção de fichas com rótulo Anormal',105,147,1070,53,{size:29,...center});
  const groups=results.eda.sopro_by_status;
  for(const [i,key] of ['Ausência registrada','Presença registrada'].entries()){
    const row=groups[key], x=146+i*543;
    text(s,percent(row.n_anormal/row.n,1),x,212,440,90,{size:74,bold:true,color:palette.blue,...center});
    text(s,i===0?'Sopro marcado como ausente':'Com sopro registrado',x,304,440,65,{size:25,...center});
  }
  text(s,'O sopro pode ter participado da definição do próprio rótulo.',104,401,1072,64,{size:28,bold:true,...center});
}
{
  const s=slide(14,'O que os resultados permitem concluir');
  text(s,percent(fisio.balanced_accuracy),112,150,376,125,{size:83,bold:true,color:palette.blue});
  text(s,'acurácia balanceada\ncom as oito entradas principais',116,282,426,88,{size:29});
  text(s,'As medidas trazem informação\nsobre o rótulo registrado.',602,157,577,94,{size:32,bold:true});
  text(s,'Confirmar como o rótulo foi criado\ne avaliar em novas fichas.',602,277,577,94,{size:28,color:palette.muted});
  text(s,'github.com/pedroafm06/Data-Mining',121,419,1047,43,{size:23,color:palette.blue,...center});
}

const seconds=script.slides.reduce((sum,item)=>sum+item.seconds,0);
if(presentation.slides.items.length!==14||seconds!==850) throw new Error('Temporização e número de slides divergentes');
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
  explicitTotalSlideCount:14,requiredNativeTableOwnerSlides:tableOwners,
  fontPolicy:{basis:'design',families:[headFont,bodyFont]},
  verifyArtifactToolImport:true,receiptPath:path.join(work,name+'.validation.json')});

await fs.copyFile(finalPath,path.join(out,name+'.pptx'));

const totals = new Map();
let elapsed = 0;
let talk = '# Roteiro da apresentação da A2\n\nTempo planejado de 14 min 10 s, com 50 s de margem até o limite de 15 minutos.\n\n';
for(const n of script.slides) totals.set(n.author,(totals.get(n.author)||0)+n.seconds);
for(const [author, duration] of totals) talk += '- '+author+' · '+clock(duration)+'\n';
for(const n of script.slides){
  talk+='\n## '+n.number+'. '+n.title+'\n\n'+n.author+' · '+clock(elapsed)+' a '+clock(elapsed+n.seconds)+'\n\n'+n.text+'\n';
  elapsed+=n.seconds;
}
talk+='\n## Arguição\n';
for(const item of script.qa) talk+='\n**'+item.question+'**\n\n'+item.answer+'\n';
await fs.writeFile(path.join(out,'Roteiro_A2_INF.md'),talk,'utf8');
console.log(finalPath);

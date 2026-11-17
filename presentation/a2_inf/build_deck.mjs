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
const visibleSlides = [];
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
  visibleSlides.at(-1)?.content.push(value);
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
  visibleSlides.push({number:n,title,content:[]});
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
  visibleSlides.at(-1)?.content.push(...values.map(row=>row.join(' | ')));
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
  text(s,'Classificação de registros\ncardíacos pediátricos',120,111,1040,164,{size:58,bold:true,align:'center',name:'título de capa'});
  text(s,'Mineração de Dados · Avaliação 2',140,274,1000,54,{...H,...center});
  text(s,'Antônio Henrique · João Vitor · Mateus Nery · Pedro Matos',105,347,1070,47,{size:27,...center});
  text(s,'Grupo 3 · INF/UFG · Prof. Rogério Lopes Salvini · 2026/2',125,408,1030,42,{...m,...center});
}
{
  const s=slide(2,'Problema e dados');
  text(s,'As medidas ajudam a prever o rótulo Normal ou Anormal?',85,146,1110,58,{size:32,bold:true,...center});
  text(s,number(results.n_original)+' fichas',90,220,525,70,{size:53,bold:true,color:palette.blue});
  text(s,'21 campos por registro\nCardiologia pediátrica\nReal Hospital Português · Recife',90,303,560,150,{size:28});
  text(s,'Classificação supervisionada',704,222,490,51,{size:30,bold:true,color:palette.blue});
  text(s,'Entradas: medidas da ficha\nResposta: rótulo já registrado\nAnormal é a classe positiva',704,287,495,153,{size:28});
  text(s,'Prever a classificação da ficha não equivale a confirmar um diagnóstico.',90,454,1100,51,{size:27,bold:true});
}
{
  const s=slide(3,'Quais fichas entraram na avaliação');
  table(s,[['Etapa de seleção','Registros','Decisão'],
    ['Base original',number(results.n_original),'Conservar a fonte original'],
    ['Com rótulo',number(results.n_labelled),'1.169 sem rótulo ficam fora do treino'],
    ['Separação histórica','2.342 + 1','Teste já examinado + 1 ficha em quarentena'],
    ['Desenvolvimento',number(results.n_development),'5.394 Normal e 3.967 Anormal']],
    80,154,[365,220,535],[48,58,58,58,58],{emphasis:4,bodySize:26,labelSize:27,headerSize:26});
  text(s,'Fichas equivalentes ficam juntas: 9.166 grupos para a validação.',88,459,1104,52,{size:28,bold:true});
}
{
  const s=slide(4,'Seleção das variáveis');
  table(s,[['Decisão','Variáveis','Justificativa'],
    ['8 principais','Idade, sexo, peso, altura, IMC,\npressões e frequência cardíaca','Disponibilidade das medidas\na confirmar para uso futuro'],
    ['Excluir','MOTIVO1/2 e HDA2','Indícios diagnósticos ou\nbaixa cobertura e incerteza'],
    ['Excluir','ID, convênio e datas brutas','Identificação e cadastro;\ndatas entram só na idade'],
    ['Explorar à parte','Sopro, B2, pulsos, pressão\nclassificada e sintomas','Possível participação\nna definição do rótulo']],
    68,155,[238,490,416],[48,75,75,75,75],{emphasis:1,bodySize:25,labelSize:27,headerSize:26});
}
{
  const s=slide(5,'Limpeza: regras e exemplos');
  table(s,[['O que verificamos','Tratamento','Por quê'],
    ['Grafias e números','Uniformizar categorias e decimais','Evitar valores iguais com formas distintas'],
    ['Datas e idade','Conferir formato, século e coerência','Evitar uma idade derivada contraditória'],
    ['Pressões incoerentes','Mascarar o par se sistólica ≤ diastólica','Não escolher arbitrariamente qual está certa'],
    ['Frequência cardíaca: 1.120','Ausente se > 500 batimentos/min','Não supor que o valor correto era 112']],
    65,159,[322,410,418],[49,61,61,61,61],{emphasis:4,bodySize:24,labelSize:26,headerSize:26});
  text(s,'Preservamos a ficha e registramos a regra; os limites são hipóteses de curadoria.',78,476,1126,51,{size:25,bold:true});
}
{
  const s=slide(6,'Dados ausentes e preenchimento');
  text(s,'Após a limpeza: pressões ≈ 56% ausentes; IMC 34,6%.',85,149,1110,53,{size:30,bold:true,...center});
  table(s,[['Alternativa testada','Como funciona','Motivo'],
    ['Mediana global','Valor central aprendido no treino','Menor influência de extremos'],
    ['Mediana por idade','Faixa com pelo menos 30 observações;\nsenão, usar a global','Considerar diferenças do crescimento']],
    82,221,[282,494,340],[46,63,76],{bodySize:25,labelSize:27});
  text(s,'Exemplo: FC ausente → 92 batimentos/min + indicador de preenchimento = 1',85,415,1110,60,{size:28,bold:true});
  text(s,'92 vem do ajuste final da floresta; cada treino da validação aprende sua mediana.',85,472,1110,37,{size:24,color:palette.muted});
}
{
  const s=slide(7,'Idade e IMC: atributos derivados');
  text(s,'Idade contínua',89,156,500,49,H);
  text(s,'Nascimento → atendimento\nDiferença entre datas coerentes\nInformação original ajuda na ambiguidade',89,224,527,164,{size:27});
  text(s,'Preserva diferenças dentro\ndo primeiro ano de vida.',89,403,527,80,{size:28,bold:true});
  text(s,'IMC de uma ficha real',696,156,500,49,H);
  text(s,'5 kg e 51 cm observados\n51 cm = 0,51 m',696,225,500,96,{size:30});
  text(s,'5 ÷ (0,51)² = 19,22 kg/m²',670,326,535,74,{size:34,bold:true,color:palette.blue});
  text(s,'Reconstruir com medidas utilizáveis;\nnão com peso e altura preenchidos.',670,417,535,84,{size:27});
}
{
  const s=slide(8,'Representação para os modelos');
  table(s,[['Sexo nominal','Coluna F','Coluna M'],['F','1','0'],['M','0','1']],
    84,159,[280,142,142],[46,53,53],{bodySize:32,labelSize:28});
  text(s,'One-hot: colunas 0/1,\nsem impor uma ordem às categorias.',84,337,555,97,{size:28,bold:true});
  text(s,'Regressão logística',705,157,490,52,H);
  text(s,'Padronizar = subtrair a média\ne dividir pelo desvio do treino.\nComparamos com log(1 + Peso)\nantes da padronização.',705,216,490,181,{size:27});
  text(s,'Árvores e floresta',705,404,490,45,{size:29,bold:true,color:palette.blue});
  text(s,'Unidades originais: cortes usam\na ordenação dos valores.',705,455,490,72,{size:27});
}
{
  const s=slide(9,'Por que comparar três modelos');
  table(s,[['Modelo','Como aprende','O que queríamos comparar'],
    ['Árvore de decisão','Faz perguntas em sequência\ne separa grupos de fichas','Regras fáceis de acompanhar'],
    ['Regressão logística','Combina as medidas em um escore\ne o transforma em chance','Uma relação mais simples\ncom controle de complexidade'],
    ['Floresta aleatória','Combina muitas árvores diferentes','Relações não lineares\ne interações entre medidas']],
    75,165,[298,420,412],[48,79,89,79],{bodySize:26,labelSize:27});
  text(s,'Referência mínima: sempre prever a classe mais frequente, Normal.',87,475,1106,49,{size:28,bold:true});
}
{
  const s=slide(10,'Como a árvore decide');
  text(s,'Critério Gini: buscar divisões com classes menos misturadas.',89,146,1100,48,{size:29,...center});
  rect(s,346,216,588,61,palette.light,'pergunta raiz da árvore');
  text(s,'Peso até '+decimal(weightLimit)+' kg?',346,217,588,59,{size:35,bold:true,color:palette.blue,...center});
  text(s,'SIM → examina a idade',93,315,505,54,{size:30,bold:true,...center});
  text(s,'Corte de aproximadamente '+Math.round(ageLimit*365)+' dias',93,379,505,47,{size:28,...center});
  text(s,'NÃO → examina a frequência',673,315,520,54,{size:30,bold:true,...center});
  text(s,'Corte de '+decimal(pulseLimit,1)+' batimentos/min',673,379,520,47,{size:28,...center});
  text(s,'Primeiras perguntas da árvore final. Há outros cortes até a previsão.',89,448,1100,49,{size:28,bold:true,...center});
  text(s,'Os limites foram aprendidos nesta base; não são regras clínicas.',89,495,1100,36,{size:25,color:palette.muted,...center});
}
{
  const s=slide(11,'Como a logística e a floresta preveem');
  text(s,'Regressão logística',87,157,520,51,H);
  text(s,'Medidas × pesos aprendidos\n→ soma das contribuições\n→ chance entre 0 e 1',87,224,525,150,{size:31});
  text(s,'Regularização limita pesos extremos\ne reduz ajustes excessivos ao treino.',87,398,530,98,{size:27});
  text(s,'Floresta aleatória',709,157,495,51,H);
  text(s,'150 árvores com amostras\ne escolhas de atributos diferentes\n→ média das chances',709,224,495,150,{size:30});
  text(s,'Combinar árvores reduz a dependência\nde uma única sequência de cortes.',709,398,495,98,{size:27});
  text(s,'Corte fixo: chance ≥ 0,5 recebe previsão Anormal.',87,490,1116,43,{size:29,bold:true,...center});
}
{
  const s=slide(12,'Validação sem misturar treino e avaliação');
  text(s,'5 partes externas: cada ficha é avaliada uma vez fora do seu treino.',87,146,1106,51,{size:28,bold:true});
  for(let i=0;i<5;i++){
    rect(s,89+i*222,215,204,57,i===4?palette.blue:palette.light,'parte externa '+(i+1));
    text(s,String(i+1),89+i*222,215,204,57,{size:30,bold:true,color:i===4?palette.white:palette.blue,...center});
  }
  text(s,'4 partes: treino + escolha dos ajustes',89,286,860,46,{size:29,bold:true});
  text(s,'1: avaliação',977,286,204,46,{size:27,bold:true,color:palette.blue,...center});
  text(s,'Dentro do treino: 3 divisões internas escolhem a configuração.',89,348,1104,47,{size:28});
  text(s,'Medianas, categorias e escalas são aprendidas somente no treino.',89,410,1104,47,{size:28});
  text(s,'Fichas equivalentes no mesmo grupo; mesmos cortes para comparar modelos.',89,472,1104,51,{size:26,bold:true});
}
{
  const s=slide(13,'Quais alternativas foram comparadas');
  table(s,[['Família','Configurações','O que variou'],
    ['Árvore','48','Critério, profundidade, folha, pesos e preenchimento'],
    ['Logística','32','Regularização, escala/log, pesos e preenchimento'],
    ['Floresta','24','Profundidade, folha, pesos e preenchimento'],
    ['Sempre Normal','1','Referência sem ajuste de hiperparâmetros']],
    76,153,[268,231,629],[48,51,51,51,51],{bodySize:24,labelSize:27,headerSize:26});
  text(s,'105 por cenário. Ajustes escolhidos pela acurácia balanceada interna.',84,424,1110,46,{size:27,bold:true});
  text(s,'Floresta final: 150 árvores, folha mínima 30, pesos balanceados, mediana global.',84,474,1110,53,{size:26});
}
{
  const s=slide(14,'Por que usar acurácia balanceada');
  text(s,'Sempre prever Normal acerta 57,62% das fichas, mas perde todos os Anormal.',83,147,1114,67,{size:28,bold:true,...center});
  text(s,'100%',104,234,510,83,{size:65,bold:true,color:palette.blue,...center});
  text(s,'Especificidade\nNormais reconhecidos',104,320,510,83,{size:28,...center});
  text(s,'0%',674,234,510,83,{size:65,bold:true,color:palette.red,...center});
  text(s,'Sensibilidade\nAnormais reconhecidos',674,320,510,83,{size:28,...center});
  text(s,'BA = (sensibilidade + especificidade) ÷ 2 = 50%',89,430,1100,65,{size:34,bold:true,...center});
  text(s,'Cada classe recebe o mesmo peso; também olhamos os erros separadamente.',89,497,1100,39,{size:25,...center});
}
{
  const s=slide(15,'Comparação dos modelos');
  const scores=['dummy','tree','logistic','forest'].map((fam,i)=>[
    ['Sempre Normal','Árvore de decisão','Regressão logística','Floresta aleatória'][i],percent(metric('FISIO8',fam).balanced_accuracy)]);
  table(s,[['8 entradas principais','Acurácia balanceada'],...scores],92,158,[618,478],[49,49,49,49,49],{emphasis:4,bodySize:32,labelSize:29,headerSize:27});
  text(s,'Floresta − logística: +'+points(famDiff.diff)+' pontos percentuais.',92,421,1096,48,{size:29,bold:true});
  text(s,'Intervalo de 95%: +0,43 a +2,01 p.p. · Ganho pequeno nesta avaliação.',92,474,1096,52,{size:26});
}
{
  const s=slide(16,'Acertos e erros da floresta');
  table(s,[['Rótulo registrado','Previu Normal','Previu Anormal'],['Normal',number(fisio.tn),number(fisio.fp)],['Anormal',number(fisio.fn),number(fisio.tp)]],
    80,171,[316,239,239],[57,80,80],{errorCell:true,headerSize:25,labelSize:28});
  text(s,'42 em 100',906,194,290,73,{size:49,bold:true,color:palette.red,...center});
  text(s,'registros Anormal\npassaram como Normal',889,283,308,100,{size:27,...center});
  text(s,'Sensibilidade: '+percent(fisio.recall)+'     Especificidade: '+percent(fisio.specificity),89,430,1100,51,{size:30,bold:true,...center});
  text(s,'São previsões externas da validação; não são acertos no próprio treino.',89,490,1100,38,{size:25,...center});
}
{
  const s=slide(17,'O que as outras métricas acrescentam');
  table(s,[['Métrica','Floresta','Interpretação'],
    ['Precisão',percent(fisio.precision),'Entre as previsões Anormal,\nquantas tinham esse rótulo?'],
    ['F1',percent(fisio.f1),'Combina precisão e sensibilidade;\npenaliza desequilíbrio entre elas.'],
    ['Precisão média (AP)',percent(fisio.average_precision),'Resume a precisão ao variar o corte\ne recuperar mais Anormais.']],
    76,157,[330,210,588],[50,85,85,85],{bodySize:27,labelSize:28,headerSize:27});
  text(s,'Precisão: previsões Anormal. Sensibilidade: todos os registros com rótulo Anormal.',83,475,1114,46,{size:25,bold:true});
}
{
  const s=slide(18,'O que aprendemos com os erros');
  text(s,'Entre os registros Anormal com idade conhecida',89,151,1100,49,{size:30,...center});
  table(s,[['Resultado da floresta','Idade mediana'],['Previu Normal: falsos negativos',decimal(results.errors.FISIO8.median_age_fn)+' anos'],['Reconheceu Anormal: verdadeiros positivos',decimal(results.errors.FISIO8.median_age_tp)+' anos']],
    91,220,[773,325],[49,67,67],{bodySize:34,labelSize:28});
  text(s,'Os grupos têm perfis diferentes. Isso não mede a taxa de erro em cada idade.',91,412,1098,63,{size:28,bold:true});
  text(s,'Para investigar: comparar acertos e totais por faixa, ausências e incerteza.',91,477,1098,42,{size:26});
}
{
  const s=slide(19,'Quais medidas a floresta mais usou');
  text(s,'Permutação: embaralhar uma medida entre fichas e medir a queda da BA.',89,148,1100,68,{size:28,bold:true,...center});
  const features=[['Frequência cardíaca','FC'],['Peso','Peso'],['Idade','IDADE']];
  features.forEach(([label,key],i)=>{
    const x=82+i*376;
    text(s,points(importance('FISIO8','forest',key))+' p.p.',x,248,364,82,{size:57,bold:true,color:palette.blue,...center});
    text(s,label,x,345,364,61,{size:29,bold:true,...center});
  });
  text(s,'Queda maior → maior dependência do modelo nesse teste.',89,426,1100,49,{size:29,bold:true,...center});
  text(s,'Não é efeito causal; medidas relacionadas podem compensar umas às outras.',89,477,1100,40,{size:25,...center});
}
{
  const s=slide(20,'O resultado muda com as entradas');
  table(s,[['Cenário','Entradas','Melhor BA observada'],
    ['4 · restrito','Peso, altura, idade e sexo',percent(strict.balanced_accuracy)+' · árvore'],
    ['8 · principal','As 4 + IMC, duas pressões\ne frequência cardíaca',percent(fisio.balanced_accuracy)+' · floresta'],
    ['13 · exploratório','As 8 + sopro, B2, pulsos,\npressão classificada e sintomas',percent(clin.balanced_accuracy)+' · árvore']],
    68,149,[270,535,339],[48,65,80,87],{emphasis:2,bodySize:26,labelSize:27,headerSize:26});
  text(s,'Mesmas fichas e cortes. Cada número usa a melhor família daquele cenário.',80,446,1120,44,{size:25,bold:true});
  text(s,'Os cinco campos adicionais podem participar da definição do próprio rótulo.',80,484,1120,37,{size:25});
}
{
  const s=slide(21,'O papel do sopro');
  text(s,'Sopro é um som ouvido no exame. Proporção com rótulo Anormal:',89,147,1100,53,{size:29,...center});
  const groups=results.eda.sopro_by_status;
  for(const [i,key] of ['Ausência registrada','Presença registrada'].entries()){
    const row=groups[key], x=94+i*568;
    text(s,percent(row.n_anormal/row.n,1),x,221,523,86,{size:67,bold:true,color:palette.blue,...center});
    text(s,i===0?'Sopro explicitamente ausente':'Sopro presente',x,317,523,57,{size:29,bold:true,...center});
  }
  text(s,'Campo não preenchido é diferente de ausência de sopro.',89,399,1100,47,{size:28,bold:true,...center});
  text(s,'Associação forte não prova vazamento. Falta conhecer a ordem da coleta\ne se o achado ajudou a definir a classe: 91,92% permanece exploratório.',89,456,1100,81,{size:27,...center});
}
{
  const s=slide(22,'Conclusões e próximos passos');
  text(s,percent(fisio.balanced_accuracy),87,161,421,93,{size:72,bold:true,color:palette.blue,...center});
  text(s,'BA com 8 entradas\n58% dos Anormal reconhecidos',87,270,421,101,{size:29,bold:true,...center});
  text(s,'Ganho sobre a referência,\ncom muitos erros restantes.',87,403,421,92,{size:29,...center});
  text(s,'O KDD completo',659,158,540,51,H);
  text(s,'Selecionar → limpar → transformar\n→ modelar → avaliar e interpretar',659,225,540,98,{size:29});
  text(s,'Para avançar',659,352,540,48,H);
  text(s,'Confirmar como o rótulo foi definido\ne avaliar em nova amostra independente.',659,417,540,93,{size:28});
}


const seconds=script.slides.reduce((sum,item)=>sum+item.seconds,0);
if(presentation.slides.items.length!==totalSlideCount||slideCount!==22||seconds!==script.timing.speech_seconds) throw new Error('Temporização e número de slides divergentes');
await fs.writeFile(path.join(work,'revisao_22','conteudo_visivel.json'),JSON.stringify(visibleSlides,null,2));
const candidate=path.join(work,'revisao_22','candidate.pptx');
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
const wordCount=script.slides.reduce((sum,item)=>sum+item.text.trim().split(/\s+/u).length,0);
let talk = '# Roteiro da apresentação da A2\n\n22 slides, todos apresentados. Fala com '+wordCount+' palavras. A estimativa adota '+script.timing.assumed_words_per_minute+' palavras/min, com '+script.timing.pauses_and_transitions_seconds+' s de pausas e transições. Duração calculada: '+clock(script.timing.planned_total_seconds)+'. O tempo real depende de ensaio. As notas técnicas e a arguição são material de estudo, fora da fala planejada.\n\n';
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

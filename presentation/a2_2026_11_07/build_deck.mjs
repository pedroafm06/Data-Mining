// Gera output/Apresentacao_A2_UCMF.pptx a partir de .build/content.json (python build_data.py).
// Todos os números vêm de content.json; este arquivo só posiciona texto, tabelas e gráficos nativos.
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import pptxgen from 'pptxgenjs';

const DIR = path.dirname(fileURLToPath(import.meta.url));
const D = JSON.parse(fs.readFileSync(path.join(DIR, '.build/content.json'), 'utf8'));
const V = D.V;
const OUT = path.join(DIR, 'output');
fs.mkdirSync(OUT, {recursive: true});

const C = {ink: '122C43', teal: '007F82', orange: 'A54C20', muted: '4D6172', grid: 'D7E1E7', white: 'FFFFFF', wash: 'F2F7F8', gray: '9AA7B1', pale: 'BAE3E1'};
const FONT = 'Calibri';
const MAIN = 15;
const px = v => v / 96; // layout pensado em 1280 x 720 px

const pres = new pptxgen();
pres.layout = 'LAYOUT_WIDE';
pres.author = D.authors.join(', ');
pres.title = 'Classificação de registros de cardiologia pediátrica';

function slide(title, n, opts = {}) {
  const s = pres.addSlide();
  s.background = {color: opts.dark ? C.ink : C.white};
  if (opts.hidden) s.hidden = true;
  if (title) s.addText(title, {x: px(64), y: px(40), w: px(1152), h: px(80), fontFace: FONT, fontSize: 34, bold: true, color: opts.dark ? C.white : C.ink, margin: 0});
  const label = opts.hidden ? `Apoio ${n - MAIN}` : `${String(n).padStart(2, '0')} / ${MAIN}`;
  s.addText(label, {x: px(1060), y: px(670), w: px(160), h: px(30), fontFace: FONT, fontSize: 12, color: opts.dark ? 'BCD1DC' : C.muted, align: 'right', margin: 0});
  return s;
}
function txt(s, text, x, y, w, h, size = 22, color = C.ink, bold = false, align = 'left') {
  s.addText(text, {x: px(x), y: px(y), w: px(w), h: px(h), fontFace: FONT, fontSize: size, color, bold, align, valign: 'top', margin: 0, paraSpaceAfter: 4});
}
function box(s, text, x, y, w, h, fill = C.wash, color = C.ink, size = 20) {
  s.addText(text, {x: px(x), y: px(y), w: px(w), h: px(h), fontFace: FONT, fontSize: size, color, bold: true, align: 'center', valign: 'middle',
    fill: {color: fill}, line: {color: C.grid, width: 1}, margin: 6});
}
function arrow(s, x1, y1, x2, y2) {
  s.addShape(pres.shapes.LINE, {x: px(x1), y: px(y1), w: px(Math.max(x2 - x1, 0.01)), h: px(Math.max(y2 - y1, 0.01)), line: {color: C.teal, width: 2, endArrowType: 'triangle'}});
}
function table(s, rows, x, y, w, colW, opts = {}) {
  const size = opts.size ?? 18;
  const data = rows.map((r, i) => r.map((cell, j) => ({
    text: String(cell),
    options: {bold: i === 0 || j === 0, color: i === 0 ? C.white : C.ink, fill: {color: i === 0 ? C.ink : (opts.highlight === i ? 'E4F2F1' : C.white)},
      align: j === 0 ? 'left' : 'center', valign: 'middle', fontFace: FONT, fontSize: size}
  })));
  s.addTable(data, {x: px(x), y: px(y), w: px(w), colW: colW.map(px), border: {type: 'solid', color: C.grid, pt: 1}, rowH: px(opts.rowH ?? 46), margin: 4});
}
function notes(s, n) {
  const d = D.notes[n - 1];
  const qa = d.qa.map(([q, a]) => `Pergunta provável: ${q}\nResposta: ${a}`).join('\n\n');
  s.addNotes(`Responsável: ${d.author}\nTempo: ${Math.floor(d.seconds / 60)}:${String(d.seconds % 60).padStart(2, '0')}\n\n${d.text}\n\n${qa}`);
}

// 1. Capa
{
  const s = slide('', 1, {dark: true});
  txt(s, 'Classificação de registros\nde cardiologia pediátrica', 64, 110, 1150, 170, 46, C.white, true);
  txt(s, 'O peso do exame físico frente às medidas', 64, 300, 1150, 50, 26, C.pale);
  txt(s, 'Mineração de Dados\nUFG, Grupo 3, 2026/2', 64, 420, 460, 80, 20, 'C7D7E0');
  txt(s, D.authors.join('\n'), 585, 420, 630, 170, 20, C.white);
  notes(s, 1);
}
// 2. Tarefa
{
  const s = slide('Tarefa', 2);
  txt(s, 'Normal ou Anormal?', 64, 170, 1100, 70, 44, C.teal, true);
  txt(s, 'Classe positiva: Anormal', 64, 270, 1100, 50, 28, C.ink, true);
  txt(s, 'Entrada: o que se coleta no atendimento, antes do laudo', 64, 350, 1150, 50, 26);
  txt(s, 'Uso pensado: apoio à triagem', 64, 430, 1150, 50, 26, C.orange, true);
  notes(s, 2);
}
// 3. Dados e partições
{
  const s = slide('Dados e partições', 3);
  box(s, `${V.n_source} registros · 21 atributos`, 64, 140, 1152, 64, C.wash, C.ink, 22);
  box(s, `${V.n_labelled} com rótulo`, 64, 260, 760, 64, C.wash, C.ink, 22);
  box(s, `${V.n_unlabelled} sem rótulo`, 880, 260, 336, 64, C.white, C.muted, 20);
  arrow(s, 444, 204, 444, 260); arrow(s, 1048, 204, 1048, 260);
  box(s, `${V.n_dev} desenvolvimento\nescolha e avaliação dos modelos`, 64, 380, 470, 100, 'E4F2F1', C.ink, 20);
  box(s, `${V.n_test} teste histórico\navaliação secundária`, 584, 380, 350, 100, C.white, C.muted, 20);
  arrow(s, 299, 324, 299, 380); arrow(s, 759, 324, 759, 380);
  txt(s, `${V.n_normal} Normal · ${V.n_anormal} Anormal (${V.pct_anormal})`, 64, 530, 1152, 50, 28, C.teal, true);
  notes(s, 3);
}
// 4. Achados do exame
{
  const s = slide('O exame físico separa as classes', 4);
  s.addChart(pres.charts.BAR, [{name: '% de anormais', labels: D.finding_chart.categories, values: D.finding_chart.values}], {
    x: px(64), y: px(130), w: px(800), h: px(520), barDir: 'bar', chartColors: [C.orange], catAxisLabelFontSize: 16, valAxisLabelFontSize: 14,
    valAxisMaxVal: 100, valAxisMinVal: 0, showValue: true, dataLabelFontSize: 14, dataLabelFormatCode: '0"%"', catAxisOrientation: 'maxMin',
    valGridLine: {color: C.grid, size: 1}, showLegend: false, catAxisLabelFontFace: FONT});
  txt(s, `${V.sop_sis}`, 900, 200, 320, 70, 48, C.orange, true);
  txt(s, 'anormais com\nsopro sistólico', 900, 275, 320, 80, 22);
  txt(s, `${V.sop_aus}`, 900, 400, 320, 70, 48, C.gray, true);
  txt(s, 'anormais\nsem sopro', 900, 475, 320, 80, 22);
  notes(s, 4);
}
// 5. Idade e FC
{
  const s = slide('Idade e frequência cardíaca', 5);
  txt(s, 'Idade mediana', 64, 160, 540, 40, 24, C.muted, true);
  txt(s, `${V.age_med_a} anos`, 64, 210, 540, 70, 48, C.orange, true); txt(s, 'Anormal', 64, 285, 540, 36, 20);
  txt(s, `${V.age_med_n} anos`, 330, 210, 300, 70, 48, C.gray, true); txt(s, 'Normal', 330, 285, 300, 36, 20);
  txt(s, `Menos de 1 ano: ${V.under1_a} dos anormais e ${V.under1_n} dos normais`, 64, 345, 560, 70, 20);
  txt(s, 'FC mediana', 680, 160, 540, 40, 24, C.muted, true);
  txt(s, `${V.fc_med_a} bpm`, 680, 210, 300, 70, 48, C.orange, true); txt(s, 'Anormal', 680, 285, 300, 36, 20);
  txt(s, `${V.fc_med_n} bpm`, 960, 210, 260, 70, 48, C.gray, true); txt(s, 'Normal', 960, 285, 260, 36, 20);
  txt(s, 'A FC cai com a idade: parte da diferença é idade', 680, 345, 540, 70, 20);
  txt(s, 'Compatível com cardiopatia congênita percebida cedo', 64, 520, 1152, 50, 26, C.teal, true);
  notes(s, 5);
}
// 6. Critério de vazamento
{
  const s = slide('Critério de vazamento: disponível antes do laudo?', 6);
  txt(s, 'Sai', 64, 140, 560, 44, 28, C.orange, true);
  table(s, [['Atributo', 'Motivo'], ['ID, datas brutas', 'Identificação'], ['Convênio', `Origem do paciente (SUS: ${V.sus_pct} anormais)`], ['MOTIVO1 e 2', 'Diagnóstico escrito'], ['HDA2', `${V.hda2_miss} ausentes`]],
    64, 195, 600, [190, 410], {size: 16, rowH: 52});
  txt(s, 'Fica', 720, 140, 500, 44, 28, C.teal, true);
  txt(s, 'Peso, Altura, IMC, Idade, Sexo\nPAS, PAD, FC e PPA\nSOPRO, B2 e PULSOS\nHDA1 (sintomas)', 720, 200, 500, 220, 22);
  txt(s, `SOPRO sozinho: BA de ${V.probe_sopro}\npoder preditivo, não vazamento`, 720, 450, 500, 90, 22, C.teal, true);
  notes(s, 6);
}
// 7. Três cenários
{
  const s = slide('Três cenários, mesmo protocolo', 7);
  const cols = [['CLINICO', 'principal', 'Medidas, idade, sexo\nSinais vitais e PPA\nSOPRO, B2, PULSOS\nHDA1', C.teal], ['FISIO8', 'sensibilidade', 'Medidas, idade, sexo\nSinais vitais', C.ink], ['STRICT4', 'sensibilidade', 'Peso, Altura\nIdade, Sexo', C.muted]];
  cols.forEach(([name, role, attrs, color], i) => {
    const x = 64 + i * 392;
    txt(s, name, x, 160, 360, 50, 34, color, true);
    txt(s, `${D.pools[name].length} atributos · ${role}`, x, 215, 360, 36, 18, C.muted);
    txt(s, attrs, x, 270, 360, 200, 22);
  });
  txt(s, 'Mesmos registros, mesmos folds, mesmas sementes', 64, 540, 1152, 50, 24, C.orange, true);
  notes(s, 7);
}
// 8. Da A1 para a A2
{
  const s = slide('Da A1 para a A2', 8);
  txt(s, `${V.a1_dup} duplicados na A1 = ${V.a1_dup_unl} sem rótulo + ${V.a1_dup_lab} rotulados`, 64, 150, 1152, 50, 26, C.ink, true);
  txt(s, `A2: ${V.a1_final} + ${V.a1_dup_lab} = ${V.n_labelled} rotulados; registros iguais ficam no mesmo grupo`, 64, 215, 1152, 50, 22);
  table(s, [['Plano da A1', 'Na A2', 'Por quê'], ['Idade em 4 faixas', 'Idade contínua', 'Árvores escolhem os cortes'], ['Sexo em Binary Encoding', 'One-hot', 'Uma coluna por categoria'], ['Imputação por faixa etária', 'Opção testada', 'Escolhida na validação interna']],
    64, 310, 1152, [380, 300, 472], {size: 18, rowH: 56});
  notes(s, 8);
}
// 9. Pré-processamento e validação aninhada
{
  const s = slide('Pré-processamento e validação aninhada', 9);
  for (let i = 0; i < 5; i++) box(s, `Fold ${i + 1}`, 64 + i * 230, 150, 208, 60, i === 4 ? C.ink : 'E4F2F1', i === 4 ? C.white : C.ink, 20);
  txt(s, '4 folds: treino externo', 64, 222, 900, 36, 20, C.teal, true);
  txt(s, '1 fold: avaliação', 984, 222, 232, 36, 20, C.ink, true, 'center');
  box(s, '3 folds internos\nescolhem hiperparâmetros', 64, 300, 340, 100);
  box(s, 'Ajuste no treino\nexterno', 470, 300, 330, 100);
  box(s, 'Previsão no\nfold externo', 870, 300, 346, 100, C.ink, C.white);
  arrow(s, 404, 350, 470, 350); arrow(s, 800, 350, 870, 350);
  txt(s, 'Medianas, escalas e categorias ajustadas só no treino', 64, 450, 1152, 40, 22);
  txt(s, 'Estratificada e agrupada · sementes 42, 743 e 811+k', 64, 500, 1152, 40, 22, C.orange, true);
  notes(s, 9);
}
// 10. Modelos e métricas
{
  const s = slide('Modelos e métricas', 10);
  table(s, [['Modelo', 'Papel'], ['Classe majoritária', 'Baseline simples'], ['Árvore de decisão', 'Modelo comparado, interpretável'], ['Regressão logística', 'Modelo comparado, linear'], ['Floresta aleatória', 'Modelo comparado, conjunto de árvores']],
    64, 150, 1152, [420, 732], {size: 20, rowH: 54});
  txt(s, `${V.n_configs} configurações por cenário · limiar 0,5`, 64, 470, 1152, 40, 22);
  txt(s, 'BA = (sensibilidade + especificidade) / 2', 64, 530, 1152, 40, 24, C.teal, true);
  notes(s, 10);
}
// 11. Resultado principal
{
  const s = slide('CLINICO: três modelos empatados', 11);
  table(s, D.results_main, 64, 150, 1152, [380, 193, 193, 193, 193], {size: 20, rowH: 56, highlight: 2});
  txt(s, `Diferença entre os três: ${V.spread_clin} ponto de BA`, 64, 470, 1152, 40, 24, C.teal, true);
  txt(s, 'Previsões externas da validação aninhada', 64, 530, 1152, 40, 20, C.muted);
  notes(s, 11);
}
// 12. De onde vem a informação
{
  const s = slide('De onde vem a informação', 12);
  const colors = {STRICT4: C.gray, FISIO8: C.ink, CLINICO: C.teal};
  s.addChart(pres.charts.BAR, D.scenario_chart.series.map(x => ({name: x.name, labels: D.scenario_chart.categories, values: x.values})), {
    x: px(64), y: px(130), w: px(800), h: px(500), barDir: 'col', barGrouping: 'clustered', chartColors: D.scenario_chart.series.map(x => colors[x.name]),
    valAxisMinVal: 50, valAxisMaxVal: 100, showValue: true, dataLabelFontSize: 12, dataLabelFormatCode: '0.0', showLegend: true, legendPos: 'b', legendFontSize: 14,
    catAxisLabelFontSize: 16, valAxisLabelFontSize: 14, valAxisTitle: 'BA (%)', showValAxisTitle: true, valGridLine: {color: C.grid, size: 1}});
  txt(s, `−${V.gain_cf} p.p.`, 900, 180, 320, 60, 40, C.orange, true); txt(s, 'sem o exame físico', 900, 245, 320, 36, 20);
  txt(s, `−${V.gain_fs} p.p.`, 900, 320, 320, 60, 40, C.gray, true); txt(s, 'sem os sinais vitais', 900, 385, 320, 36, 20);
  txt(s, `Teste histórico: ${V.t_clin} · ${V.t_fisio} · ${V.t_strict}`, 900, 470, 320, 100, 18, C.muted);
  notes(s, 12);
}
// 13. Importância
{
  const s = slide('Importância por permutação', 13);
  D.importance_chart.forEach((c, i) => {
    const x = 64 + i * 590;
    txt(s, c.title, x, 135, 560, 36, 22, i === 0 ? C.teal : C.ink, true);
    s.addChart(pres.charts.BAR, [{name: 'Queda de BA (p.p.)', labels: c.categories, values: c.values}], {
      x: px(x), y: px(180), w: px(560), h: px(400), barDir: 'bar', catAxisOrientation: 'maxMin', chartColors: [i === 0 ? C.teal : C.ink],
      showValue: true, dataLabelFontSize: 14, dataLabelFormatCode: '0.0', valAxisMinVal: 0, catAxisLabelFontSize: 16, valAxisLabelFontSize: 12, showLegend: false, valGridLine: {color: C.grid, size: 1}});
  });
  txt(s, 'Queda de BA ao embaralhar o atributo no fold externo', 64, 600, 1152, 36, 18, C.muted);
  notes(s, 13);
}
// 14. Análise de erros
{
  const s = slide('Análise de erros (CLINICO, árvore)', 14);
  table(s, D.confusion, 64, 160, 620, [260, 180, 180], {size: 22, rowH: 70});
  txt(s, V.fn_sem_sopro, 760, 150, 460, 80, 60, C.orange, true);
  txt(s, `dos ${V.fn} falsos negativos\nnão têm sopro`, 760, 240, 460, 80, 22);
  txt(s, V.fp_com_sopro, 760, 350, 460, 70, 44, C.gray, true);
  txt(s, `dos ${V.fp} falsos positivos têm sopro`, 760, 425, 460, 40, 20);
  txt(s, 'Na triagem, o falso negativo é o erro caro', 64, 540, 1152, 44, 26, C.teal, true);
  notes(s, 14);
}
// 15. Conclusão
{
  const s = slide('Conclusão e limitações', 15, {dark: true});
  txt(s, V.ba_clin, 64, 140, 400, 80, 60, C.pale, true);
  txt(s, 'BA no CLINICO\na informação está na ausculta', 64, 230, 520, 80, 22, C.white);
  txt(s, 'Limitações', 640, 140, 580, 44, 26, C.pale, true);
  txt(s, '• Rótulo sem padrão de referência\n• Ordem de registro suposta, sem horários\n• Avaliação interna a uma coorte\n• Grupos não identificam pacientes', 640, 195, 580, 220, 20, C.white);
  txt(s, 'Próximo passo: ajustar o limiar para a sensibilidade e estudar as crianças sem sopro', 64, 480, 1152, 80, 24, C.white, true);
  notes(s, 15);
}
// Apoio (ocultos)
{
  const s = slide('Todas as métricas (%)', 16, {hidden: true});
  table(s, D.results_all, 40, 120, 1200, [140, 210, 120, 120, 120, 120, 120, 120, 130], {size: 12, rowH: 38});
  s.addNotes('Slide de apoio. Previsões externas da validação aninhada nos três cenários.');
}
{
  const s = slide('Teste histórico (BA, %)', 17, {hidden: true});
  table(s, D.test_table, 64, 160, 900, [300, 200, 200, 200], {size: 20, rowH: 60});
  txt(s, `${V.n_test} registros; já examinados em fases anteriores. Avaliação secundária, aplicada uma vez.`, 64, 460, 1152, 60, 20, C.muted);
  s.addNotes('Slide de apoio. Modelos finais aplicados uma única vez ao teste histórico.');
}
{
  const s = slide('Reprodução e uso de IA', 18, {hidden: true});
  txt(s, 'github.com/pedroafm06/Data-Mining', 64, 150, 1152, 44, 26, C.teal, true);
  txt(s, `Números: ${D.source}`, 64, 215, 1152, 40, 18, C.muted);
  txt(s, 'IA generativa: Claude (Anthropic) na A1; Codex (OpenAI) no desenvolvimento da A2; Claude Code nesta revisão (cenário CLINICO, geradores, artigo, slides e README). Decisões do grupo; números conferidos nas saídas do código.', 64, 290, 1152, 160, 20);
  s.addNotes('Slide de apoio. Declaração de uso de IA e onde reproduzir.');
}

const file = path.join(OUT, 'Apresentacao_A2_UCMF.pptx');
await pres.writeFile({fileName: file});
console.log(JSON.stringify({pptx: file, slides: pres.slides.length, main: MAIN, seconds: D.total_seconds}));

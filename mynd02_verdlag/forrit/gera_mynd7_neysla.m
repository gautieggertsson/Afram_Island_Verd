%% gera_mynd7_neysla.m
% Neyslumynd verðlagsgreinarinnar (mynd 7): einstaklingsbundin neysla á
% mann 2024 (AIC, magnvísitala, ESB = 100) fyrir ESB-ríkin 27 og Ísland,
% raðað lækkandi.
%
% Ísland í dag er dregið fram með rauðri súlu: 116, fjórða sæti. Þar að
% auki er sýnd ljósrauð súla þar sem Ísland lenti héldust neysluútgjöld
% heimila í evrum óbreytt en verðlag körfunnar sjálfrar (A01, 172,7)
% félli að spágildi aðhvarfs á launakostnað: magnvísitalan hækkar þá um
% 25,7 til 34,2%, úr 116 í 145,9 til 155,6, og Ísland fer í efsta sæti,
% upp fyrir Lúxemborg. Súlan sýnir neðri mörkin, 145,9, og grönn lárétt
% lína bilið upp í efri mörkin, 155,6. Þetta er reikningur á kaupmætti
% óbreyttra útgjalda, ekki spá.
%
% Les eingöngu nidurstodur/neysla_mynd.csv, sem forritið
% neysla_naemniprof.py skrifar úr frystum gögnum.
%
% Keyrsla frá rót verkefnisins:
%   matlab -batch "run('mynd02_verdlag/forrit/gera_mynd7_neysla.m')"
%
% MATLAB: R2024b.

clear; close all;

SCRIPT_DIR = fileparts(mfilename('fullpath'));
ROOT = fileparts(SCRIPT_DIR);
DATA = fullfile(ROOT, 'nidurstodur', 'neysla_mynd.csv');
OUT = fullfile(ROOT, 'mynd');
assert(isfile(DATA), 'Gagnaskráin fannst ekki: %s', DATA);

T = readtable(DATA, 'Delimiter', ';', 'VariableNamingRule', 'preserve');
assert(height(T) == 30, 'Vænt 28 ríki auk neðri og efri marka.');
assert(T.a01(strcmp(T.geo, 'IS')) == 116, 'IS-gildið stenst ekki viðmiðun.');
volLag = T.a01(strcmp(T.geo, 'IS_leidrett_lag'));
volHa = T.a01(strcmp(T.geo, 'IS_leidrett_ha'));
assert(abs(volLag - 145.9) < 0.05, 'Neðri mörkin standast ekki viðmiðun.');
assert(abs(volHa - 155.6) < 0.05, 'Efri mörkin standast ekki viðmiðun.');

% Súlan sýnir neðri mörkin; efri mörkin verða lárétt bil-lína. Efri
% röðin er felld úr töflunni fyrir röðun.
T = T(~strcmp(T.geo, 'IS_leidrett_ha'), :);

% Raðað lækkandi; leiðrétta gildið, 145,9, fer þá efst, upp fyrir
% Lúxemborg. Stöðug röðun heldur jafnstæðum ríkjum í sömu innbyrðis röð.
[~, ix] = sort(T.a01, 'descend');
T = T(ix, :);
n = height(T);
iIS = find(strcmp(T.geo, 'IS'));
iSPAD = find(strcmp(T.geo, 'IS_leidrett_lag'));
assert(iSPAD == 1, 'Leiðrétta gildið á að lenda efst.');
assert(iIS == 4 + 1, 'Ísland í dag á að vera í fjórða sæti ríkjanna.');

GREY = [0.75 0.75 0.75]; RED = [192 57 43]/255;
INK = [26 26 26]/255; MUT = [107 107 107]/255;
set(groot, 'DefaultAxesFontName', 'Helvetica', ...
    'DefaultTextFontName', 'Helvetica');

fig = figure('Visible','off', 'Units','inches', ...
    'Position',[1 1 7.6 5.6], 'Color','w');
ax = axes(fig); hold(ax, 'on');

y = 1:n;                                   % röð 1 efst (YDir reverse)
onnur = setdiff(1:n, [iIS iSPAD]);
barh(ax, y(onnur), T.a01(onnur), 0.72, ...
    'FaceColor', GREY, 'EdgeColor', 'none');
barh(ax, y(iIS), T.a01(iIS), 0.72, ...
    'FaceColor', RED, 'EdgeColor', 'none');
barh(ax, y(iSPAD), T.a01(iSPAD), 0.72, ...
    'FaceColor', RED, 'FaceAlpha', 0.35, ...
    'EdgeColor', RED, 'LineWidth', 1.0, 'LineStyle', '-');

% Viðmiðunarlína: meðaltal ESB = 100.
plot(ax, [100 100], [0.35 n + 0.65], '-', ...
    'Color', 0.55*INK + 0.45*[1 1 1], 'LineWidth', 0.9);
text(ax, 101.5, n + 0.25, 'meðaltal ESB = 100', 'FontSize', 7.5, ...
    'FontAngle', 'italic', 'Color', MUT);

% Grönn lárétt bil-lína frá neðri mörkum upp í efri mörkin, með
% lóðréttum endahökum.
plot(ax, [volLag volHa], [y(iSPAD) y(iSPAD)], '-', 'Color', RED, ...
    'LineWidth', 0.9);
plot(ax, [volHa volHa], y(iSPAD) + [-0.16 0.16], '-', 'Color', RED, ...
    'LineWidth', 0.9);

text(ax, T.a01(iIS) + 2.5, y(iIS), ...
    'Ísland í dag: 116 (4. sæti)', 'Color', RED, ...
    'FontWeight', 'bold', 'FontSize', 8.5, 'VerticalAlignment', 'middle');
text(ax, volHa + 2.5, y(iSPAD), ...
    'Ísland við spágildi: 146 til 156 (1. sæti)', 'Color', RED, ...
    'FontWeight', 'bold', 'FontSize', 8.5, 'VerticalAlignment', 'middle');

% Stytt heiti á ásnum: mörkin eru sýnd á súlunni sjálfri.
T.land{iSPAD} = 'Ísland við spágildi';

xlim(ax, [0 220]); ylim(ax, [0.25 n + 0.75]);
ax.YDir = 'reverse';
ax.YTick = y; ax.YTickLabel = T.land;
ax.XTick = 0:25:200;
ax.FontSize = 7; ax.XColor = MUT; ax.YColor = MUT;
ax.TickDir = 'out'; ax.Box = 'off';
ax.TickLabelInterpreter = 'none';
xlabel(ax, 'Einstaklingsbundin neysla á mann 2024, magnvísitala (ESB = 100)', ...
    'FontSize', 8.5, 'Color', INK);

pdfPath = fullfile(OUT, 'm7_neysla.pdf');
pngPath = fullfile(OUT, 'm7_neysla.png');
exportgraphics(fig, pdfPath, 'ContentType', 'vector');
exportgraphics(fig, pngPath, 'Resolution', 240);
close(fig);
fprintf('Skrifað:\n  %s\n  %s\n', pdfPath, pngPath);

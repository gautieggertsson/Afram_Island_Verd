%% gera_mynd5_innganga.m
% Inngöngumynd verðlagsgreinarinnar (mynd 5): frávik Finnlands, Svíþjóðar
% og Austurríkis frá metna sambandi verðlags og launa, 1995--2024, ásamt
% stöðu Íslands 2024 sem bili.
%
% Þykkar línur: fimm ára miðjusett meðaltal (leitni); daufar línur:
% árleg gildi. Ísland 2024 er sýnt sem lóðrétt bil, 24 til 31 prósent,
% með kúlum á báðum endum.
%
% Les eingöngu nidurstodur/innganga_fravik.csv, sem forritið
% innganga_naemniprof.py skrifar úr frystum gögnum.
%
% Keyrsla frá rót verkefnisins:
%   matlab -batch "run('mynd02_verdlag/forrit/gera_mynd5_innganga.m')"
%
% MATLAB: R2024b.

clear; close all;

SCRIPT_DIR = fileparts(mfilename('fullpath'));
ROOT = fileparts(SCRIPT_DIR);
DATA = fullfile(ROOT, 'nidurstodur', 'innganga_fravik.csv');
OUT = fullfile(ROOT, 'mynd');
assert(isfile(DATA), 'Gagnaskráin fannst ekki: %s', DATA);

T = readtable(DATA, 'Delimiter', ';', 'VariableNamingRule', 'preserve');
assert(height(T) == 30, 'Vænt 30 ára, 1995--2024.');
assert(abs(100*T.FI(1) - 18.8) < 0.2, 'FI 1995 stenst ekki viðmiðun.');
assert(abs(100*T.SE_leitni(end) - 4.4) < 0.2, 'SE-leitni 2024 stenst ekki.');

BLUE = [42 120 214]/255; ORANGE = [222 110 44]/255;
GREEN = [24 145 95]/255; RED = [192 57 43]/255;
INK = [26 26 26]/255; MUT = [107 107 107]/255;
set(groot, 'DefaultAxesFontName', 'Helvetica', ...
    'DefaultTextFontName', 'Helvetica');

fig = figure('Visible','off', 'Units','inches', ...
    'Position',[1 1 7.6 4.8], 'Color','w');
ax = axes(fig); hold(ax, 'on');

ar = T.ar;
plot(ax, ar, 100*T.FI, '-', 'Color', [BLUE 0.25], 'LineWidth', 0.8);
plot(ax, ar, 100*T.SE, '-', 'Color', [ORANGE 0.25], 'LineWidth', 0.8);
plot(ax, ar, 100*T.AT, '-', 'Color', [GREEN 0.25], 'LineWidth', 0.8);
plot(ax, ar, 100*T.FI_leitni, '-', 'Color', BLUE, 'LineWidth', 2.2);
plot(ax, ar, 100*T.SE_leitni, '-', 'Color', ORANGE, 'LineWidth', 2.2);
plot(ax, ar, 100*T.AT_leitni, '-', 'Color', GREEN, 'LineWidth', 2.2);

yline(ax, 0, '-', 'Color', 0.55*INK + 0.45*[1 1 1], 'LineWidth', 0.9);
text(ax, 1995.3, 1.3, 'metna sambandið', 'FontSize', 8, ...
    'FontAngle', 'italic', 'Color', MUT);

% Ísland 2024: bil 24 til 31 prósent með kúlum á báðum endum.
xIS = 2026.4;
plot(ax, [xIS xIS], [23.8 30.5], '-', 'Color', RED, 'LineWidth', 2.0);
scatter(ax, [xIS xIS], [23.8 30.5], 46, 'o', ...
    'MarkerFaceColor', RED, 'MarkerEdgeColor', 'none');
text(ax, xIS - 0.7, 27.2, sprintf('Ísland 2024\n24 til 31%%'), ...
    'Color', RED, 'FontWeight', 'bold', 'FontSize', 9, ...
    'HorizontalAlignment', 'right');

text(ax, 2024.6, 100*T.FI_leitni(end), 'Finnland', 'Color', BLUE, ...
    'FontWeight', 'bold', 'FontSize', 9.5);
text(ax, 2024.6, 100*T.SE_leitni(end), 'Svíþjóð', 'Color', ORANGE, ...
    'FontWeight', 'bold', 'FontSize', 9.5);
text(ax, 2024.6, 100*T.AT_leitni(end), 'Austurríki', 'Color', GREEN, ...
    'FontWeight', 'bold', 'FontSize', 9.5);

xlim(ax, [1994.5 2029]); ylim(ax, [-11 33]);
ax.XTick = 1995:5:2024; ax.YTick = -10:10:30;
ax.YTickLabel = ["-10%" "0" "+10%" "+20%" "+30%"];
ax.FontSize = 8; ax.XColor = MUT; ax.YColor = MUT;
ax.TickDir = 'out'; ax.Box = 'off';

pdfPath = fullfile(OUT, 'm5_innganga.pdf');
pngPath = fullfile(OUT, 'm5_innganga.png');
exportgraphics(fig, pdfPath, 'ContentType', 'vector');
exportgraphics(fig, pngPath, 'Resolution', 240);
close(fig);
fprintf('Skrifað:\n  %s\n  %s\n', pdfPath, pngPath);

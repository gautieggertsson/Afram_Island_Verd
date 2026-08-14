%% gera_mynd4_matvara.m
% Verðlag matvöru á Íslandi 2024 eftir vöruflokkum (mynd 4 í greininni).
%
% Lárétt súlurit: verðlagsvísitölur fimm matvöruflokka á Íslandi árið
% 2024, meðaltal ESB = 100. Tollvörðu flokkarnir, kjöt og mjólkurvörur og
% egg, eru rauðir; fiskur, sem ber enga innflutningstolla, er blár.
%
% Les eingöngu nidurstodur/matvara_undirflokkar.csv, sem forritið
% matvara_undirflokkar.py skrifar úr frystum Eurostat-gögnum.
%
% Keyrsla frá rót verkefnisins:
%   matlab -batch "run('mynd02_verdlag/forrit/gera_mynd4_matvara.m')"
%
% MATLAB: R2024b.

clear; close all;

SCRIPT_DIR = fileparts(mfilename('fullpath'));
ROOT = fileparts(SCRIPT_DIR);
DATA = fullfile(ROOT, 'nidurstodur', 'matvara_undirflokkar.csv');
OUT = fullfile(ROOT, 'mynd');
assert(isfile(DATA), 'Gagnaskráin fannst ekki: %s', DATA);

T = readtable(DATA, 'Delimiter', ';', 'VariableNamingRule', 'preserve', ...
    'TextType', 'string');

% Flokkarnir fimm sem myndin sýnir, neðst upp í efst.
KODAR = ["A01010103"; "A01010105"; "A0101"; "A01010104"; "A01010102"];
VIDMID = [110.1; 122.4; 143.9; 171.7; 172.5];
TOLLVARDIR = [false; false; false; true; true];
FISKUR = [true; false; false; false; false];

n = numel(KODAR);
gildi = zeros(n, 1);
heiti = strings(n, 1);
for i = 1:n
    r = T(T.flokkur == KODAR(i), :);
    assert(height(r) == 1, 'Flokkur fannst ekki: %s', KODAR(i));
    gildi(i) = r.pli_2024;
    heiti(i) = r.heiti;
end
assert(all(abs(gildi - VIDMID) < 1e-9), 'Gildin standast ekki viðmiðun.');

GRAY = [168 166 158]/255; BLUE = [42 120 214]/255;
RED = [192 57 43]/255; INK = [26 26 26]/255; MUT = [107 107 107]/255;
set(groot, 'DefaultAxesFontName', 'Helvetica', ...
    'DefaultTextFontName', 'Helvetica');

fig = figure('Visible','off', 'Units','inches', ...
    'Position',[1 1 7.4 4.2], 'Color','w');
ax = axes(fig, 'Position', [0.27 0.12 0.69 0.80]); hold(ax, 'on');

for i = 1:n
    c = GRAY;
    if TOLLVARDIR(i); c = RED; end
    if FISKUR(i); c = BLUE; end
    barh(ax, i, gildi(i), 0.62, 'FaceColor', c, 'EdgeColor', 'none');
    text(ax, -4, i, heiti(i), 'HorizontalAlignment', 'right', ...
        'FontSize', 9, 'Color', INK, 'Clipping', 'off');
    text(ax, gildi(i) + 3, i, ...
        ['+' strrep(sprintf('%.1f', gildi(i) - 100), '.', ',') '%'], ...
        'FontSize', 9, 'FontWeight', 'bold', 'Color', c, 'Clipping', 'off');
end

plot(ax, [100 100], [0.35 n + 0.95], '--', ...
    'Color', 0.6*INK + 0.4*[1 1 1], 'LineWidth', 0.9);
text(ax, 100, n + 1.05, 'Meðaltal ESB = 100', 'FontSize', 7.5, ...
    'Color', MUT, 'HorizontalAlignment', 'center', 'Clipping', 'off');

text(ax, 8, n + 0.44, 'Tollvörðu flokkarnir', 'FontSize', 8, ...
    'Color', RED, 'FontWeight', 'bold');
text(ax, 8, 1 + 0.44, 'Engir innflutningstollar', 'FontSize', 8, ...
    'Color', BLUE, 'FontWeight', 'bold');

xlim(ax, [0 200]); ylim(ax, [0.35 n + 1.3]);
ax.YTick = []; ax.YAxis.Visible = 'off'; ax.Box = 'off';
ax.XTick = 0:50:200;
ax.FontSize = 8; ax.XColor = MUT; ax.TickDir = 'out';
xlabel(ax, 'Verðlagsvísitala 2024, meðaltal ESB = 100', ...
    'FontSize', 9, 'Color', INK);

pdfPath = fullfile(OUT, 'm4_matvara.pdf');
pngPath = fullfile(OUT, 'm4_matvara.png');
exportgraphics(fig, pdfPath, 'ContentType', 'vector');
exportgraphics(fig, pngPath, 'Resolution', 240);
close(fig);
fprintf('Skrifað:\n  %s\n  %s\n', pdfPath, pngPath);

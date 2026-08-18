%% gera_mynd3_adhvarf.m
% Aðhvarfsmynd verðlagsgreinarinnar (mynd 3).
%
% Punktarit: launakostnaður á vinnustund 2024 á lárétta ásnum (log-kvarði)
% og E011-verðlagsvísitala á þeim lóðrétta (log-kvarði). Aðhvarfslínan er
% metin á ESB-ríkjunum 27; Ísland er utan mats og sýnt sérstaklega.
% Skyggða beltið er fast: metið log-verðlag ±2 staðalvillur leifa.
% Samanburður við Noreg og Sviss er ekki á myndinni; hann er rakinn í
% utanesb_naemniprof.py og í kafla 4.1 í greininni.
%
% Les eingöngu nidurstodur/adhvarf_utanesb.csv, sem forritið
% utanesb_naemniprof.py skrifar úr frystum gögnum.
%
% Keyrsla frá rót verkefnisins:
%   matlab -batch "run('mynd02_verdlag/forrit/gera_mynd3_adhvarf.m')"
%
% MATLAB: R2024b.

clear; close all;

SCRIPT_DIR = fileparts(mfilename('fullpath'));
ROOT = fileparts(SCRIPT_DIR);
DATA = fullfile(ROOT, 'nidurstodur', 'adhvarf_utanesb.csv');
OUT = fullfile(ROOT, 'mynd');
assert(isfile(DATA), 'Gagnaskráin fannst ekki: %s', DATA);

T = readtable(DATA, 'Delimiter', ';', 'VariableNamingRule', 'preserve', ...
    'TextType', 'string');
E = T(T.hlutverk == "mat", :);
assert(height(E) == 27, 'Vænt 27 ESB-ríkja í mati.');

x = log(E.launakostnadur_eur);
y = log(E.pli_E011);
n = numel(x);
mx = mean(x); my = mean(y);
b = sum((x - mx) .* (y - my)) / sum((x - mx).^2);
a = my - b * mx;
res = y - (a + b * x);
s = sqrt(sum(res.^2) / (n - 2));
assert(abs(b - 0.4238) < 5e-4, 'Teygnin stenst ekki viðmiðun.');

wIS = T.launakostnadur_eur(T.geo == "IS");
pIS = T.pli_E011(T.geo == "IS");
predIS = exp(a + b * log(wIS));
assert(abs(predIS - 130.64) < 0.05, 'Spáin fyrir Ísland stenst ekki viðmiðun.');

% Bein mæling vinnustunda (vinnumarkaðsrannsóknin) og bil matsins,
% lesið úr sömu frystu niðurstöðuskrá og kafli 4.1 styðst við.
V = readtable(fullfile(ROOT, 'nidurstodur', 'vinnustundir_naemniprof.csv'), ...
    'Delimiter', ';', 'VariableNamingRule', 'preserve', 'TextType', 'string');
wDirect = V.timakaup_eur(startsWith(V.adferd, "Vinnumarkaðsrannsókn"));
predDirect = exp(a + b * log(wDirect));
assert(abs(predDirect - 124.1) < 0.05, 'Spágildi beinu mælingarinnar stenst ekki viðmiðun.');
fravikMax = max(V.fravik);
assert(abs(fravikMax - 0.3075) < 5e-4, 'Efri mörk fráviksbilsins standast ekki viðmiðun.');

GRAY = [140 138 132]/255; BLUE = [42 120 214]/255;
RED = [192 57 43]/255; INK = [26 26 26]/255; MUT = [107 107 107]/255;
set(groot, 'DefaultAxesFontName', 'Helvetica', ...
    'DefaultTextFontName', 'Helvetica');

fig = figure('Visible','off', 'Units','inches', ...
    'Position',[1 1 7.6 5.4], 'Color','w');
ax = axes(fig); hold(ax, 'on');

gx = linspace(log(9), log(60), 200);
gl = a + b * gx;
fill(ax, exp([gx fliplr(gx)]), exp([gl - 2*s, fliplr(gl + 2*s)]), ...
    BLUE, 'FaceAlpha', 0.10, 'EdgeColor', 'none');
plot(ax, exp(gx), exp(gl), '-', 'Color', BLUE, 'LineWidth', 1.6);

scatter(ax, E.launakostnadur_eur, E.pli_E011, 30, ...
    'MarkerFaceColor', GRAY, 'MarkerEdgeColor', 'none');
for i = 1:height(E)
    text(ax, E.launakostnadur_eur(i)*1.025, E.pli_E011(i), E.geo(i), ...
        'FontSize', 6, 'Color', MUT);
end

LRED = RED + (1 - RED) * 0.62;
plot(ax, [wDirect wIS], [pIS pIS], '-', 'Color', LRED, 'LineWidth', 2.6);
scatter(ax, wIS, pIS, 80, 'o', ...
    'MarkerFaceColor', RED, 'MarkerEdgeColor', 'none');
scatter(ax, wDirect, pIS, 80, 'o', ...
    'MarkerFaceColor', 'none', 'MarkerEdgeColor', RED, 'LineWidth', 1.3);

plot(ax, [wIS wIS], [predIS pIS], ':', 'Color', RED, 'LineWidth', 1.1);
plot(ax, [wDirect wDirect], [predDirect pIS], ':', 'Color', LRED, 'LineWidth', 1.1);
text(ax, wDirect*0.96, pIS*1.005, ...
    sprintf('Ísland: 161,7\nspáð miðað við laun: 124–131\nfrávik: +24 til +31%%'), ...
    'Color', RED, 'FontWeight', 'bold', 'FontSize', 9, ...
    'HorizontalAlignment', 'right');
text(ax, 9.6, 176, ...
    sprintf('ESB-ríkin 27 mynda regluna:\nhærri laun, hærra verðlag,\num 0,4%% á móti hverju 1%%'), ...
    'Color', MUT, 'FontSize', 8, 'VerticalAlignment', 'top');

set(ax, 'XScale', 'log', 'YScale', 'log');
ax.XTick = [10 15 20 30 40 55];
ax.YTick = [60 80 100 120 140 160 180];
ax.XTickLabel = string(ax.XTick);
ax.YTickLabel = string(ax.YTick);
ax.XMinorTick = 'off'; ax.YMinorTick = 'off';
ax.XAxis.MinorTickValues = []; ax.YAxis.MinorTickValues = [];
ax.FontSize = 8; ax.XColor = MUT; ax.YColor = MUT;
ax.TickDir = 'out'; ax.Box = 'off';
xlabel(ax, 'Laun á klukkustund 2024, evrur (log-kvarði)', ...
    'FontSize', 9, 'Color', INK);
ylabel(ax, 'Verðlagsvísitala E011, ESB = 100 (log-kvarði)', ...
    'FontSize', 9, 'Color', INK);
xlim(ax, [9 60]); ylim(ax, [52 180]);

pdfPath = fullfile(OUT, 'm3_adhvarf.pdf');
pngPath = fullfile(OUT, 'm3_adhvarf.png');
exportgraphics(fig, pdfPath, 'ContentType', 'vector');
exportgraphics(fig, pngPath, 'Resolution', 240);
close(fig);
fprintf('Skrifað:\n  %s\n  %s\n', pdfPath, pngPath);

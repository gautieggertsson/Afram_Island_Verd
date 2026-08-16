%% gera_mynd6_spa.m
% Framreikningsmynd verðlagsgreinarinnar (mynd 4 í greininni):
% verðlag á Íslandi eftir inngöngu í ESB, heimfært af hjöðnunarferlum
% Finnlands og Svíþjóðar 1995--2024. Dekkra bandið sýnir sameiginlega
% ferlið (helmingunartími 7,6 ár) heimfært á báða enda íslensku
% upphafsstöðunnar; ljósara bandið bætir við óvissu um hraðann,
% helmingunartíma 6 til 14 ár úr frávikasafni viðauka C. Grái borðinn
% sýnir verðlagið sem launin skýra, 124 til 131. Lóðrétti ásinn byrjar
% í 120.
%
% Les eingöngu nidurstodur/framreikningur_island.csv, sem forritið
% framreikningur_naemniprof.py skrifar úr frystum gögnum.
%
% Keyrsla frá rót verkefnisins:
%   matlab -batch "run('mynd02_verdlag/forrit/gera_mynd6_spa.m')"
%
% MATLAB: R2024b.

clear; close all;

SCRIPT_DIR = fileparts(mfilename('fullpath'));
ROOT = fileparts(SCRIPT_DIR);
DATA = fullfile(ROOT, 'nidurstodur', 'framreikningur_island.csv');
OUT = fullfile(ROOT, 'mynd');
assert(isfile(DATA), 'Gagnaskráin fannst ekki: %s', DATA);

T = readtable(DATA, 'Delimiter', ';', 'VariableNamingRule', 'preserve');
assert(height(T) == 31, 'Vænt 31 árs, 0--30.');
P_IS = 161.7;
assert(abs(T.mid(1) - P_IS) < 0.05, 'Upphafsgildið stenst ekki.');
assert(abs(T.ytra_lag(11) - 141) < 1 && abs(T.ytra_ha(11) - 153) < 1, ...
    '10 ára bilið stenst ekki viðmiðun.');

RED = [192 57 43]/255; INK = [26 26 26]/255; MUT = [107 107 107]/255;
GREY = [102 102 102]/255;
set(groot, 'DefaultAxesFontName', 'Helvetica', ...
    'DefaultTextFontName', 'Helvetica');

fig = figure('Visible','off', 'Units','inches', ...
    'Position',[1 1 7.6 4.8], 'Color','w');
ax = axes(fig); hold(ax, 'on');

t = T.t;

% Ljósara bandið: hraðaóvissa panelsins (helmingunartími 6 til 14 ár).
fill(ax, [t; flipud(t)], [T.ytra_lag; flipud(T.ytra_ha)], RED, ...
    'FaceAlpha', 0.10, 'EdgeColor', 'none');
% Dekkra bandið: ferli Finnlands og Svíþjóðar.
fill(ax, [t; flipud(t)], [T.innra_lag; flipud(T.innra_ha)], RED, ...
    'FaceAlpha', 0.22, 'EdgeColor', 'none');
plot(ax, t, T.mid, '--', 'Color', RED, 'LineWidth', 2.2);
scatter(ax, 0, P_IS, 46, 'o', 'MarkerFaceColor', RED, ...
    'MarkerEdgeColor', 'none');
text(ax, 0.5, P_IS, 'Ísland 2024: 161,7', 'Color', RED, ...
    'FontWeight', 'bold', 'FontSize', 9.5);

% Grái borðinn: verðlagið sem launin skýra.
fill(ax, [t; flipud(t)], ...
    [ones(size(t))*123.9; ones(size(t))*130.6], GREY, ...
    'FaceAlpha', 0.10, 'EdgeColor', 'none');
text(ax, 29.7, 127.3, 'verðlag sem launin skýra: 124 til 131', ...
    'FontSize', 8, 'FontAngle', 'italic', 'Color', GREY, ...
    'HorizontalAlignment', 'right');

% Merkingar á fimm ára fresti: verðlagsbil yfir bandinu og
% lækkunarprósentur undir því.
for h = [5 10 15 20 25]
    i = h + 1;
    lo = T.ytra_lag(i); hi = T.ytra_ha(i);
    fall_lag = 100*(1 - hi/P_IS); fall_ha = 100*(1 - lo/P_IS);
    plot(ax, [h h], [lo hi], '-', 'Color', [RED 0.6], 'LineWidth', 0.9);
    text(ax, h, hi + 0.8, sprintf('%.0f-%.0f', lo, hi), 'Color', RED, ...
        'FontSize', 8, 'HorizontalAlignment', 'center');
    % ASCII-texti (bandstrik, ekki U+2212, sem PDF-leturgerðin
    % skilar sem '#'); orðið 'lækkun' aðeins við fyrsta merkið.
    if h == 5
        fallmerki = sprintf('lækkun %.0f-%.0f%%', fall_lag, fall_ha);
    else
        fallmerki = sprintf('%.0f-%.0f%%', fall_lag, fall_ha);
    end
    text(ax, h, lo - 1.0, fallmerki, 'Color', RED, ...
        'FontSize', 8, 'FontAngle', 'italic', ...
        'HorizontalAlignment', 'center', 'VerticalAlignment', 'top');
end

xlabel(ax, 'Ár frá inngöngu', 'FontSize', 9, 'Color', INK);
ylabel(ax, 'Verðlag einkaneyslu, meðaltal ESB = 100', 'FontSize', 9, ...
    'Color', INK);
xlim(ax, [-0.5 30]); ylim(ax, [120 166]);
ax.XTick = 0:5:30; ax.YTick = 120:10:160;
ax.FontSize = 8; ax.XColor = MUT; ax.YColor = MUT;
ax.TickDir = 'out'; ax.Box = 'off';

pdfPath = fullfile(OUT, 'm6_spa.pdf');
pngPath = fullfile(OUT, 'm6_spa.png');
exportgraphics(fig, pdfPath, 'ContentType', 'vector');
exportgraphics(fig, pngPath, 'Resolution', 240);
close(fig);
fprintf('Skrifað:\n  %s\n  %s\n', pdfPath, pngPath);

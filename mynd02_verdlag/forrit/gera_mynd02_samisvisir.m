%% gera_mynd02_samisvisir.m
% Samanburðarmynd verðlagsgreinarinnar: sami verðlagsvísir báðum megin.
% A01-útgáfan er mynd 1 í greininni; E011-útgáfan er varðveitt hér í
% pakkanum og niðurstaðan er hin sama (67 í stað 72, sömu sæti):
%
%   m2_verdlag_E011: einkaneysluútgjöld heimila (E011) báðum megin.
%   m2_verdlag_A01:  einstaklingsbundin neysla (A01) báðum megin.
%
% Vinstri hlið deilir vísinum með hlutfallslegu miðgildi jafngildra
% ráðstöfunartekna (aðferð Áfram Íslands); hægri hlið sýnir vísinn
% ódeildan. Kóðinn les eingöngu frosna gagnavinnubók.
%
% Keyrsla frá rót verkefnisins:
%   matlab -batch "run('mynd02_verdlag/forrit/gera_mynd02_samisvisir.m')"
%
% MATLAB: R2024b.

clear; close all;

SCRIPT_DIR = fileparts(mfilename('fullpath'));
ROOT = fileparts(SCRIPT_DIR);
DATA = fullfile(ROOT, 'gogn', 'mynd02_verdlag_frosin.xlsx');
OUT = fullfile(ROOT, 'mynd');
RESULTS = fullfile(ROOT, 'nidurstodur');
if ~exist(OUT, 'dir'); mkdir(OUT); end
if ~exist(RESULTS, 'dir'); mkdir(RESULTS); end
assert(isfile(DATA), 'Frosna gagnavinnubókin fannst ekki: %s', DATA);

raw = readtable(DATA, 'Sheet', 'Inntak_myndar', ...
    'Range', 'A4:H33', ...
    'VariableNamingRule', 'preserve', 'TextType', 'string');

required = ["geo","land","hlutverk","midgildi_tekna_replik_eur", ...
    "midgildi_tekna_nuverandi_eur","tekjuheimild_replik","pli_A01","pli_E011"];
assert(all(ismember(required, string(raw.Properties.VariableNames))), ...
    'Vinnubókin hefur ekki vænta dálka.');
assert(numel(unique(raw.geo)) == height(raw), ...
    'Hvert svæðisauðkenni á aðeins að koma einu sinni fyrir.');

countryMask = raw.hlutverk == "land";
euMask = raw.geo == "EU27_2020" & raw.hlutverk == "vidmid";
assert(sum(countryMask) == 28, 'Vænt 27 ESB-ríkja og Íslands.');
assert(sum(euMask) == 1, 'Vænt nákvæmlega einnar ESB-27 viðmiðunar.');

euIncome = raw.midgildi_tekna_replik_eur(euMask);
assert(abs(euIncome - 21582) < 1e-8, 'Miðgildi ESB-27 stenst ekki viðmiðun.');
C = raw(countryMask,:);
C.tekjuhlutfall = C.midgildi_tekna_replik_eur ./ euIncome;

inputIs = find(C.geo == "IS");
assert(numel(inputIs) == 1, 'Ísland fannst ekki nákvæmlega einu sinni.');
assert(abs(C.midgildi_tekna_replik_eur(inputIs) - 51875.0453887822) < 1e-6, ...
    'Framreiknaðar tekjur Íslands standast ekki viðmiðun.');
assert(abs(C.pli_A01(inputIs) - 172.7) < 1e-10, ...
    'A01-verðlagsvísir Íslands stenst ekki viðmiðun.');
assert(abs(C.pli_E011(inputIs) - 161.7) < 1e-10, ...
    'E011-verðlagsvísir Íslands stenst ekki viðmiðun.');

variants = struct( ...
    'pli',    {"pli_E011", "pli_A01"}, ...
    'tag',    {"E011", "A01"}, ...
    'heiti',  {"Einkaneysla heimila (E011)", ...
               "Einstaklingsbundin neysla (A01)"}, ...
    'maxv',   {190, 195});

GRAY = [168 166 158]/255; BLUE = [42 120 214]/255;
RED = [192 57 43]/255; INK = [26 26 26]/255; MUT = [107 107 107]/255;
set(groot, 'DefaultAxesFontName', 'Helvetica', ...
    'DefaultTextFontName', 'Helvetica');

for k = 1:numel(variants)
    v = variants(k);
    C.pli = C.(v.pli);
    C.tekjuleidrett = C.pli ./ C.tekjuhlutfall;

    left = sortrows(C, {'tekjuleidrett','geo'}, {'descend','ascend'});
    right = sortrows(C, {'pli','geo'}, {'descend','ascend'});
    left.saeti = (1:height(left))';
    right.saeti = (1:height(right))';

    leftIs = find(left.geo == "IS");
    rightIs = find(right.geo == "IS");
    assert(rightIs == 1, ...
        'Ísland á að vera efst á ódeilda verðlagskvarðanum (%s).', v.tag);

    leftOut = left(:, {'saeti','geo','land','midgildi_tekna_replik_eur', ...
        'tekjuhlutfall','pli','tekjuleidrett'});
    rightOut = right(:, {'saeti','geo','land','pli'});
    writetable(leftOut, fullfile(RESULTS, ...
        sprintf('mynd02_vinstri_%s.csv', v.tag)), 'Delimiter', ';');
    writetable(rightOut, fullfile(RESULTS, ...
        sprintf('mynd02_haegri_%s.csv', v.tag)), 'Delimiter', ';');

    % Verkefnisregla: besta staðan (lægsta verðlagsgildið) er efsta súlan.
    L = [cellstr(flipud(left.land)), num2cell(flipud(left.tekjuleidrett))];
    R = [cellstr(flipud(right.land)), num2cell(flipud(right.pli))];

    fig = nyfig(8.6, 7.6);
    axL = axes(fig, 'Position', [0.135 0.05 0.30 0.875]);
    yL = spjald(axL, L, GRAY, ...
        sprintf('Aðferð Áfram Íslands:\nVerðlagi deilt með tekjum'), ...
        sprintf('%s, útreikningur 2024', v.heiti), ...
        v.maxv, 100, 'ESB-27 = 100', 0, RED, INK, MUT);

    axR = axes(fig, 'Position', [0.665 0.05 0.30 0.875]);
    yR = spjald(axR, R, BLUE, ...
        sprintf('Sami verðlagsvísir\nán tekjudeilingar'), ...
        sprintf('%s, verðlag 2024', v.heiti), ...
        v.maxv, 100, 'ESB-27 = 100', 1, RED, INK, MUT);

    xisl = left.tekjuleidrett(leftIs) + v.maxv*0.055;
    % Birt sæti fylgja snúnu röðinni (1 = lægsta gildið efst).
    pila(fig, axL, axR, yL, yR, ...
        sprintf('%d. sæti þegar deilt er með tekjum\n%d. sæti á verðlagskvarðanum', ...
        height(left) + 1 - leftIs, height(right) + 1 - rightIs), ...
        RED, xisl, -1);

    pdfPath = fullfile(OUT, sprintf('m2_verdlag_%s.pdf', v.tag));
    pngPath = fullfile(OUT, sprintf('m2_verdlag_%s.png', v.tag));
    exportgraphics(fig, pdfPath, 'ContentType','vector');
    exportgraphics(fig, pngPath, 'Resolution',240);
    close(fig);

    fprintf('%s: Ísland vísir %.1f; deilt %.6f; sæti %d -> %d.\n', ...
        v.tag, C.pli(inputIs), C.tekjuleidrett(inputIs), leftIs, rightIs);
    fprintf('Skrifað:\n  %s\n  %s\n', pdfPath, pngPath);
end

%% Hjálparföll

function fig = nyfig(w, h)
    fig = figure('Visible','off', 'Units','inches', ...
        'Position',[1 1 w h], 'Color','w');
end

function s = isl(v, d)
    s = strrep(sprintf(['%.' num2str(d) 'f'], v), '.', ',');
end

function out = tern(cond, a, b)
    if cond; out = a; else; out = b; end
end

function snyrta(ax, titl, sub, INK, MUT)
    if contains(titl, newline)
        pos = ax.Position;
        pos(4) = pos(4) - 0.055;
        ax.Position = pos;
    end
    ax.YTick = []; ax.Box = 'off'; ax.YAxis.Visible = 'off';
    ax.XAxis.FontSize = 7; ax.XAxis.Color = MUT; ax.TickDir = 'out';
    title(ax, titl, 'FontSize',9.5, 'FontWeight','bold', 'Color',INK, ...
        'Units','normalized', 'Position',[0 1.055 0], ...
        'HorizontalAlignment','left');
    text(ax, 0, 1.018, sub, 'Units','normalized', ...
        'FontSize',7.4, 'Color',MUT);
end

function icey = spjald(ax, data, color, titl, sub, maxv, eu, eulab, d, RED, INK, MUT)
    hold(ax, 'on');
    n = size(data, 1); icey = [];
    % Fyrst eru súlur og landaheiti teiknuð, síðan viðmiðunarlínan og loks
    % tölumerkin. Þannig sker ESB-línan aldrei tölurnar við súluendana.
    for i = 1:n
        y = n - i + 1;
        nm = data{i,1}; v = data{i,2};
        ice = strncmp(nm, 'Ísland', 6);
        c = color; if ice; c = RED; end
        barh(ax, y, max(v,0), 0.62, 'FaceColor',c, 'EdgeColor','none');
        text(ax, -maxv*0.015, y, sprintf('%d. %s', i, nm), ...
            'HorizontalAlignment','right', ...
            'FontSize',tern(ice,7.6,7.0), ...
            'Color',tern(ice,RED,INK), ...
            'FontWeight',tern(ice,'bold','normal'), 'Clipping','off');
        if ice; icey = y; end
    end
    plot(ax, [eu eu], [0.3 n+1.6], '--', ...
        'Color',0.6*INK + 0.4*[1 1 1], 'LineWidth',0.9);
    for i = 1:n
        y = n - i + 1;
        nm = data{i,1}; v = data{i,2};
        ice = strncmp(nm, 'Ísland', 6);
        text(ax, max(v,0)+maxv*0.012, y, isl(v,d), ...
            'FontSize',tern(ice,7.2,6.4), ...
            'Color',tern(ice,RED,MUT), ...
            'FontWeight',tern(ice,'bold','normal'), ...
            'BackgroundColor','w', 'Margin',0.4, 'Clipping','off');
    end
    text(ax, eu, n+0.9, eulab, 'FontSize',6.6, ...
        'Color',MUT, 'Clipping','off');
    xlim(ax, [0 maxv]); ylim(ax, [0.3 n+1.6]);
    snyrta(ax, titl, sub, INK, MUT);
end

function pila(fig, axL, axR, yL, yR, txt, RED, xstart, hlid)
    p1 = gagn2fig(axL, min(xstart, axL.XLim(2)), yL);
    p2 = gagn2fig(axR, axR.XLim(1), yR);
    p2(1) = p2(1) - 0.072;
    annotation(fig, 'arrow', [p1(1) p2(1)], [p1(2) p2(2)], ...
        'Color',RED, 'LineWidth',1.6, 'HeadWidth',8, 'HeadLength',8);
    ov = axes(fig, 'Position',[0 0 1 1], 'Visible','off', 'HitTest','off');
    xlim(ov,[0 1]); ylim(ov,[0 1]);
    dv = (p2-p1)/max(norm(p2-p1),eps);
    nh = [-dv(2) dv(1)]; if nh(2) < 0; nh = -nh; end
    pos = (p1+p2)/2 + hlid*nh*0.055;
    text(ov, pos(1), pos(2), txt, 'Color',RED, 'FontSize',9.2, ...
        'FontWeight','bold', 'HorizontalAlignment','center', ...
        'BackgroundColor','w', 'Margin',2);
end

function p = gagn2fig(ax, x, y)
    pos = ax.Position; xl = ax.XLim; yl = ax.YLim;
    p = [pos(1)+pos(3)*(x-xl(1))/(xl(2)-xl(1)), ...
         pos(2)+pos(4)*(y-yl(1))/(yl(2)-yl(1))];
end

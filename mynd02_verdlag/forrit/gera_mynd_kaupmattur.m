%% gera_mynd_kaupmattur.m
% Kaupmáttarmynd verðlagsgreinarinnar (mynd 2): kaupmáttur vinnustundar.
%
% Vinstri hlið: launakostnaður á vinnustund í evrum (Eurostat,
% lc_lci_lev, 2024); Ísland í 2. sæti. Hægri hlið: sami launakostnaður
% deildur með verðlagsvísitölu einkaneysluútgjalda heimila (E011);
% Ísland í 9. sæti. Viðmiðunarlínurnar eru tvær á hvorri hlið:
% meðaltal ESB-27 (33,5 evrur, strikalína; hið sama á báðum hliðum því
% verðlagsvísitala ESB er 100) og óvegið meðaltal ríkjanna 27 (punktalína).
%
% Les aðeins frosnar niðurstöður: nidurstodur/kaupmattur_vinnustundar.csv.
%
% Keyrsla frá rót verkefnisins:
%   matlab -batch "run('mynd02_verdlag/forrit/gera_mynd_kaupmattur.m')"

clear; close all;

SCRIPT_DIR = fileparts(mfilename('fullpath'));
ROOT = fileparts(SCRIPT_DIR);
DATA = fullfile(ROOT, 'nidurstodur', 'kaupmattur_vinnustundar.csv');
OUT = fullfile(ROOT, 'mynd');
assert(isfile(DATA), 'Gagnaskráin fannst ekki: %s', DATA);

T = readtable(DATA, 'Delimiter', ';', 'VariableNamingRule', 'preserve', ...
    'TextType', 'string');
assert(height(T) == 28, 'Vænt 28 landa.');

EU = 33.5;
euUnwL = mean(T.launakostnadur_eur(T.geo ~= "IS"));
euUnwR = mean(T.verdleidrett(T.geo ~= "IS"));
assert(abs(euUnwL - 28.4) < 0.1 && abs(euUnwR - 27.7) < 0.1, ...
    'Óvegin meðaltöl standast ekki viðmiðun.');
left = sortrows(T, {'launakostnadur_eur','geo'}, {'descend','ascend'});
right = sortrows(T, {'verdleidrett','geo'}, {'descend','ascend'});
leftIs = find(left.geo == "IS");
rightIs = find(right.geo == "IS");
assert(leftIs == 2 && rightIs == 9, ...
    'Vænt sæti 2 og 9; fékk %d og %d.', leftIs, rightIs);

L = [cellstr(left.land), num2cell(left.launakostnadur_eur)];
R = [cellstr(right.land), num2cell(right.verdleidrett)];

GRAY = [168 166 158]/255; BLUE = [42 120 214]/255;
RED = [192 57 43]/255; INK = [26 26 26]/255; MUT = [107 107 107]/255;
set(groot, 'DefaultAxesFontName', 'Helvetica', ...
    'DefaultTextFontName', 'Helvetica');

fig = nyfig(8.6, 7.6);
axL = axes(fig, 'Position', [0.135 0.05 0.30 0.875]);
yL = spjald(axL, L, GRAY, ...
    sprintf('Launakostnaður á vinnustund\ní evrum á markaðsgengi'), ...
    'Ísland næsthæst í Evrópu', ...
    62, EU, 'Meðallaunakostnaður íbúa í ESB = 33,5', euUnwL, ...
    sprintf('Meðallaunakostnaður 27 ESB-ríkja (óvegið) = %s', ...
    isl(euUnwL,1)), 1, RED, INK, MUT);

axR = axes(fig, 'Position', [0.665 0.05 0.30 0.875]);
yR = spjald(axR, R, BLUE, ...
    sprintf('Sami launakostnaður,\nleiðréttur fyrir verðlagi'), ...
    'Kaupmáttur vinnustundar: um miðjan hóp', ...
    62, EU, 'Meðalkaupmáttur íbúa í ESB = 33,5', euUnwR, ...
    sprintf('Meðalkaupmáttur 27 ESB-ríkja (óvegið) = %s', ...
    isl(euUnwR,1)), 1, RED, INK, MUT);

xisl = left.launakostnadur_eur(leftIs) + 62*0.055;
pila(fig, axL, axR, yL, yR, ...
    sprintf('2. sæti í evrum\n9. sæti þegar verðlag\ner tekið til greina'), ...
    RED, xisl, -1);

pdfPath = fullfile(OUT, 'm_kaupmattur_vinnustundar.pdf');
pngPath = fullfile(OUT, 'm_kaupmattur_vinnustundar.png');
exportgraphics(fig, pdfPath, 'ContentType','vector');
exportgraphics(fig, pngPath, 'Resolution',240);
close(fig);
fprintf('Skrifað:\n  %s\n  %s\n', pdfPath, pngPath);

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

function icey = spjald(ax, data, color, titl, sub, maxv, eu, eulab, eu2, eulab2, d, RED, INK, MUT)
    hold(ax, 'on');
    n = size(data, 1); icey = [];
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
    plot(ax, [eu eu], [0.3 n+0.55], '--', ...
        'Color',0.55*INK + 0.45*[1 1 1], 'LineWidth',1.0);
    plot(ax, [eu2 eu2], [0.3 n+0.55], ':', ...
        'Color',0.45*INK + 0.55*[1 1 1], 'LineWidth',1.5);
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
    text(ax, maxv - 4.4, n+1.3, eulab, 'FontSize',6.6, ...
        'Color',MUT, 'HorizontalAlignment','right', 'Clipping','off');
    plot(ax, [maxv-3.9 maxv-0.2], [n+1.3 n+1.3], '--', ...
        'Color',0.55*INK + 0.45*[1 1 1], 'LineWidth',1.0);
    text(ax, maxv - 4.4, n+0.78, eulab2, 'FontSize',6.6, ...
        'Color',MUT, 'HorizontalAlignment','right', 'Clipping','off');
    plot(ax, [maxv-3.9 maxv-0.2], [n+0.78 n+0.78], ':', ...
        'Color',0.45*INK + 0.55*[1 1 1], 'LineWidth',1.5);
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

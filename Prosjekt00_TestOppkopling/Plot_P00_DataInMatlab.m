
%% Matlabfil for å plotting av data fra Pythonprosjekt
%
% Dersom du ønsker å bruke Matlab sin funksjonalitet til plotting av
% data fra Python, så må du først gjennomføre prosjektet i Python
% og deretter endre koden i denne filen slik at den stemmer overens
% med headeren i målefilen og/eller beregningsfilen(e).
%
% Funksjonen readtable fjerner automatisk headeren i .txt-filen, og kaller
% kolonnene med data for Var1, Var2, Var3,...
%
% Tips: Ved å kopierer inn hver header 2 ganger,
% så kan bruke siste kopi til å navngi vektorene i Matlab.

clear all
close all

Meas = readtable('Meas_P00_TestOppkopling_1.txt');
% ******** Kopier inn header fra .txt-fil to ganger ***********

% 0=Tid, 1=Lys, 2=VinkelPosMotorA,
% 3=HastighetMotorA, 4=joyForward,
% 5=joySide, 6=joy2
Tid             = Meas.Var1;
Lys             = Meas.Var2;
VinkelPosMotorA = Meas.Var3;
HastighetMotorA = Meas.Var4;
joyForward      = Meas.Var5;
joySide         = Meas.Var6;
joy2            = Meas.Var7;


CalcOnline = readtable('CalcOnline_P00_TestOppkopling_1.txt');
% ******** Kopier inn header fra .txt-fil to ganger ***********

% 0=Pos_vs_Hastighet, 1=Forward_vs_Side,
% 2=summeringAvPowerA, 3=powerA, 4=mellomRegninger
Pos_vs_Hastighet_online  = CalcOnline.Var1;
Forward_vs_Side_online   = CalcOnline.Var2;
summeringAvPowerA_online = CalcOnline.Var3;
powerA_online            = CalcOnline.Var4;
mellomRegninger_online   = CalcOnline.Var5;


CalcOffline = readtable('CalcOffline_P00_TestOppkopling_1.txt');
% ******** Kopier inn header fra .txt-fil to ganger ***********

% 0=Pos_vs_Hastighet, 1=Forward_vs_Side,
% 2=summeringAvPowerA, 3=powerA, 4=mellomRegninger
Pos_vs_Hastighet_offline  = CalcOffline.Var1;
Forward_vs_Side_offline   = CalcOffline.Var2;
summeringAvPowerA_offline = CalcOffline.Var3;
powerA_offline            = CalcOffline.Var4;
mellomRegninger_offline   = CalcOffline.Var5;


figure(1)
set(0,'defaultTextInterpreter','latex');
set(0,'defaultAxesFontSize',14)
set(gcf,'Position',[100 200 800 700])
blue_line = 2;
red_line = 1;

subplot(3,2,1)
plot(Tid,HastighetMotorA,'b-','LineWidth',blue_line)
grid on
title('Hastighet motor A')
axis tight

subplot(3,2,2)
plot(Tid,powerA_online ,'b-','LineWidth',blue_line)
hold on
plot(Tid,powerA_offline ,'r','LineWidth',red_line)
grid on
legend('online','offline','Location','best')
title('Power A')
axis tight

subplot(3,2,3)
plot(Tid,summeringAvPowerA_online,'b','LineWidth',blue_line)
hold on
plot(Tid,summeringAvPowerA_offline,'r','LineWidth',red_line)
grid on
legend('online','offline','Location','best')
title('Summering av Power A')
axis tight

subplot(3,2,4)
plot(Tid,Forward_vs_Side_online,'b','LineWidth',blue_line)
hold on
plot(Tid,Forward_vs_Side_offline,'r','LineWidth',red_line)
grid on
legend('online','offline')
title('Forward vs side joystick')
axis tight

subplot(3,2,5)
plot(Tid,Pos_vs_Hastighet_online,'b','LineWidth',blue_line)
hold on
plot(Tid,Pos_vs_Hastighet_offline,'r','LineWidth',red_line)
grid on
title('Posisjon vs hastihet motor A')
legend('online','offline','Location','northwest')
axis tight

tidspunkt = find(Tid>5.2);
text(Tid(tidspunkt(1)), Pos_vs_Hastighet_online(tidspunkt(1)),...
    {'$ \leftarrow$ Beregninger med',' mellomregning = $a+b$'},...
    'FontSize',14)

tidspunkt = find(Tid>5.4);
text(Tid(tidspunkt(1)), Pos_vs_Hastighet_offline(tidspunkt(1)),...
    {'$ \leftarrow$ Beregninger med',' mellomregning = $a-b$'},...
    'Interpreter','latex',...
    'FontSize',14)


subplot(3,2,6)
plot3(Pos_vs_Hastighet_offline,...
    summeringAvPowerA_offline,...
    Forward_vs_Side_offline)
xlabel('x-akse')
ylabel('y-akse')
zlabel('z-akse')
grid on
title({'T{\o}ysefigur for {\aa} vise hvordan {\ae}, {\o} og {\aa}'},...
    {'m{\aa} skrives med bruk av  \LaTeX-interpreter'})
axis tight

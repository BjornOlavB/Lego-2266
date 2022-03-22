#!/usr/bin/env pybricks-micropython
# coding=utf-8

# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# P0X_BeskrivendeTekst
#
# Hensikten med programmet er å ................
#
# Følgende sensorer brukes:
# - Lyssensor
# - ...
# - ...
#
# Følgende motorer brukes:
# - motor A
# - ...
#
# ---------------------------------------------------------------------

try:
    from pybricks.hubs import EV3Brick
    from pybricks.parameters import Port
    from pybricks.ev3devices import *
    from styrestikke.EV3AndJoystick import *
    from time import perf_counter, sleep
    import styrestikke.config
except Exception as e:
    pass  # for å kunne eksportere funksjoner
import statistics
import struct
import socket
import json
import _thread
import sys
import math
import random

# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#            1) EXPERIMENT SETUP AND FILENAME
#
# Skal prosjektet gjennomføres med eller uten USB-ledning?
wired = True

# --> Filnavn for lagring av MÅLINGER som gjøres online
filenameMeas = "Meas_P07_VacuRobot.txt"

# --> Filnavn for lagring av BEREGNEDE VARIABLE som gjøres online
#     Typisk navn:  "CalcOnline_P0X_BeskrivendeTekst_Y.txt"
#     Dersom du ikke vil lagre BEREGNEDE VARIABLE, la det stå
#     filenameCalcOnline = ".txt"
filenameCalcOnline = "CalcOnline_P07_VacuRobot.txt"
# --------------------------------------------------------------------


def main():
    try:
        # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        #     2) EQUIPMENT. INITIALIZE MOTORS AND SENSORS
        #
        # Initialiser robot, sensorer, motorer og styrestikke.
        #
        # Spesifiser hvilke sensorer og motorer som brukes.
        # Du må også spesifisere hvilken port de er tilkoplet.
        #
        # For ryddig og oversiktlig kode er det lurt å slette
        # koden for de sensorene og motorene som ikke brukes.

        robot = Initialize(wired, filenameMeas, filenameCalcOnline)

        # oppdater portnummer
        myColorSensor = ColorSensor(Port.S3)
        myUltrasonicSensor = UltrasonicSensor(Port.S2)
        myGyroSensor = GyroSensor(Port.S4)

        motorB = Motor(Port.B)
        motorB.reset_angle(0)
        motorC = Motor(Port.C)
        motorC.reset_angle(0)

        # Sjekker at joystick er tilkoplet EV3
        if robot["joystick"]["in_file"] is not None:
            _thread.start_new_thread(getJoystickValues, [robot])
        else:
            print(" --> Joystick er ikke koplet til")
        sleep(0)

        print("2) EQUIPMENT. INITIALIZE MOTORS AND SENSORS.")
        # ------------------------------------------------------------

        # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        #               3) MEASUREMENTS. INITIALIZE LISTS
        #
        # Denne seksjonen inneholder alle tilgjengelige målinger
        # fra EV3 og styrestikke, i tillegg til tid. Du skal velge
        # ut hvilke målinger du vil benytte i prosjektet ved å slette
        # koden til de målingene du ikke skal bruke. Legg merke til
        # at listene i utgangspunktet er tomme.
        #
        # Listene med målinger fylles opp i seksjon
        #  --> 5) GET TIME AND MEASUREMENT
        # og lagres til .txt-filen i seksjon
        #  --> 6) STORE MEASUREMENTS TO FILE

        Tid = []                # registring av tidspunkt for målinger
        Lys = []                # måling av reflektert lys fra ColorSensor

        joyForward = []         # måling av foroverbevegelse styrestikke
        joySide = []            # måling av sidebevegelse styrestikke
        Avstand = []        # målinger av lydsensor

        print("3) MEASUREMENTS. LISTS INITIALIZED.")
        # ------------------------------------------------------------

        # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        #         4) optional: OWN VARIABLES. INITIALIZE LISTS
        #
        # Denne seksjonen definerer lister med EGNE VARIABLE som
        # skal beregnes. Tenk nøye gjennom hvilke lister som skal
        # ha en initialverdi.
        #
        # Bruken av denne seksjonen avhenger av hvordan prosjektet
        # gjennomføres. Dersom det er et såkalt "online"-prosjekt
        # som ikke kan gjennomføre offline, så MÅ denne seksjonen
        # i hovedfilen benyttes. Dette fordi du er nødt til å
        # beregne bl.a. motorpådraget (som er en EGEN VARIABEL).
        #
        # Dersom prosjektet er et "offline"-prosjekt hvor du kun
        # ønsker å lagre målinger, så trenger du ikke bruke denne
        # seksjonen. Dette fordi du alternativt kan spesifisere
        # EGEN VARIABLE offline i seksjonen
        #  --> C) offline: OWN VARIABLES. INITIALIZE LISTS
        # i plottefilen.

        Ts = []             # tidsskritt
        PowerB = []         # berenging av motorpådrag B
        PowerC = []         # berenging av motorpådrag C
        IAE = []            # int av abs. error
        MAE = []            # min abs. error
        TV_B = []           # total variation motor B
        TV_C = []           # total variation motor C
        Avvik = []
        AvvikFilter = []
        I = []
        reverse = []
        PosX = []
        PosY = []
        GyroAngle = []          # måling av gyrovinkel fra GyroSensor

        medianLys = []
        STD_Lys = []

        print("4) OWN VARIABLES. LISTS INITIALIZED.")
        # ------------------------------------------------------------

        # indeks som øker for hver runde
        k = 0

        # Går inn i løkke
        while True:

            # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++
            #                  5) GET TIME AND MEASUREMENT
            #
            # I denne seksjonen registres måletidspunkt og målinger
            # fra sensorer, motorer og styrestikke, og disse legges
            # inn i listene definert i seksjon
            #  -->  3) MEASUREMENTS. INITIALIZE LISTS

            if k == 0:
                # Definer starttidspunkt for eksperimentet
                starttidspunkt = perf_counter()
                Tid.append(0)
            else:
                # For hver ny runde i while-løkka, registrerer
                # måletidspunkt
                Tid.append(perf_counter() - starttidspunkt)

            Lys.append(myColorSensor.reflection())
            Avstand.append(myUltrasonicSensor.distance())
            GyroAngle.append(myGyroSensor.angle())

            joyForward.append(config.joyForwardInstance)
            joySide.append(config.joySideInstance)

            # --------------------------------------------------------

            # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++
            #            6) STORE MEASUREMENTS TO FILE
            #
            # I denne seksjonen lagres MÅLINGENE til .txt-filen.
            #
            # For å holde orden i koden bør du benytte samme
            # struktur/rekkefølge i seksjonen
            #   --> 3) MEASUREMENTS. INITIALIZE LISTS
            #   --> 5) GET TIME AND MEASUREMENT
            #   --> 6) STORE MEASUREMENTS TO FILE
            #
            # I plottefilen må du passe på at seksjonene
            #  --> B) offline: MEASUREMENTS. INTITALIZE LISTS ACCORDING to 6)
            #  --> E) offline: UNPACK MEASUREMENTS FROM FILE ACCORDING TO 6)
            # har lik struktur som her i seksjon 6)

            # Legger først inn 4 linjer som header i filen med målinger.
            # Husk at siste element i strengen må være '\n'
            if k == 0:
                MeasurementToFileHeader = "Tall viser til kolonnenummer:\n"
                MeasurementToFileHeader += "0=Tid, 1=Lys, 2=Avstand, 3=Vinkel \n"
                MeasurementToFileHeader += "4=, 5=, 6=, 7= \n"
                MeasurementToFileHeader += "8=, 9= \n"
                robot["measurements"].write(MeasurementToFileHeader)

            MeasurementToFile = ""
            MeasurementToFile += str(Tid[-1]) + ","
            MeasurementToFile += str(Lys[-1]) + ","
            MeasurementToFile += str(GyroAngle[-1]) + ","
            MeasurementToFile += str(Avstand[-1]) + "\n"

            # Skriv MeasurementToFile til .txt-filen navngitt øverst
            robot["measurements"].write(MeasurementToFile)
            # --------------------------------------------------------

            # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++
            #    7) optional: PERFORM CALCULATIONS AND SET MOTOR POWER
            #
            # På samme måte som i seksjon
            #  -->  4) optional: OWN VARIABLES. INITIALIZE LISTS
            # så er bruken av seksjon 7) avhengig av hvordan
            # prosjektet gjennomføres. Dersom seksjon 4) ikke benyttes
            # så kan heller ikke seksjon 7) benyttes. Du må i så
            # fall kommentere bort kallet til MathCalculations()
            # nedenfor. Du må også kommentere bort motorpådragene.

            MathCalculations(Tid, Lys, Ts, Avvik, AvvikFilter, IAE, MAE, TV_B, TV_C, I,
                             PowerB, PowerC, medianLys, STD_Lys, Avstand, reverse, GyroAngle, PosX, PosY)

            # Hvis motor(er) brukes i prosjektet så sendes til slutt
            # beregnet pådrag til motor(ene).
            motorB.dc(PowerB[-1])
            motorC.dc(PowerC[-1])

            # --------------------------------------------------------

            # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++
            #        8) optional: STORE CALCULATIONS FROM 6) TO FILE
            #
            # På samme måte som i seksjonene
            #  --> 4) optional: OWN VARIABLES. INITIALIZE LISTS
            #  --> 7) optional: PERFORM CALCULATIONS AND SET MOTOR POWER
            # så er bruken av seksjon 8) avhengig av hvordan prosjektet
            # gjennomføres. Dersom seksjonene 4) og 7) ikke benyttes
            # så kan heller ikke seksjon 8) benyttes. La i så fall
            # filnavnet for lagring av beregnede variable være tomt.
            #
            # Hvis du velger å bruke seksjonene 4), 7) og 8),
            # så må du ikke nødvendigvis lagre ALLE egne variable.

            # Vi legger først inn 3 linjer som header i filen med beregnede
            # variable. Du kan legge inn flere linjer om du vil.
            if len(filenameCalcOnline) > 4:
                if k == 0:
                    CalculationsToFileHeader = "Tallformatet viser til kolonnenummer:\n"
                    CalculationsToFileHeader += "0=Ts, 1=PowerB, 2=PowerC, \n"
                    CalculationsToFileHeader += "3=IAE, 4=MAE \n"
                    CalculationsToFileHeader += "5=TV_B, 6=TV_C \n"
                    CalculationsToFileHeader += "7=Avvik, 8=MedianLys, 9=STD_Lys \n"
                    CalculationsToFileHeader += "10=GyroAngle, 11=PosX, 12=PosY \n"
                    robot["calculations"].write(CalculationsToFileHeader)
                CalculationsToFile = ""
                CalculationsToFile += str(Ts[-1]) + ","
                CalculationsToFile += str(PowerB[-1]) + ","
                CalculationsToFile += str(PowerC[-1]) + ","
                CalculationsToFile += str(IAE[-1]) + ","
                CalculationsToFile += str(MAE[-1]) + ","
                CalculationsToFile += str(TV_B[-1]) + ","
                CalculationsToFile += str(TV_C[-1]) + ","
                CalculationsToFile += str(Avvik[-1]) + ","
                CalculationsToFile += str(medianLys[-1]) + ","
                CalculationsToFile += str(STD_Lys[-1]) + ","
                CalculationsToFile += str(GyroAngle[-1]) + ","
                CalculationsToFile += str(PosX[-1]) + ","
                CalculationsToFile += str(PosY[-1]) + "\n"

                # Skriv CalcultedToFile til .txt-filen navngitt i seksjon 1)
                robot["calculations"].write(CalculationsToFile)
            # --------------------------------------------------------

            # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++
            #     9) wired only: SEND DATA TO F) FOR PLOTTING
            #
            # Denne seksjonen kjører kun når det er ledning mellom
            # EV3 og datamaskin ("wired"). Seksjonen sender over til
            # plottefile utvalgte DATA bestående av både:
            #   - MÅLINGER spesifisert i seksjon 3) og
            #   - EGNE VARIABLE spesifisert i seksjon 4).
            #
            # For å holde orden i koden bør du beholde rekkefølgen
            # på de utvalgte listene med MÅLINGER og EGEN VARIABLE
            # slik de er definert i seksjonene 3) og 4).
            #
            # I plottefilen må du passe på at seksjonene
            #  --> D) online: DATA TO PLOT. INITIALIZE LISTS ACCORDING TO 9)
            #  --> F) online: RECEIVE DATA TO PLOT ACCORDING TO 9)
            # har lik struktur som her i seksjon 9)

            if wired:
                DataToOnlinePlot = {}

                # målinger
                DataToOnlinePlot["Tid"] = (Tid[-1])
                DataToOnlinePlot["Lys"] = (Lys[-1])
                DataToOnlinePlot["Avstand"] = (Avstand[-1])
                DataToOnlinePlot["joyForward"] = (joyForward[-1])
                DataToOnlinePlot["joySide"] = (joySide[-1])
                DataToOnlinePlot["GyroAngle"] = (GyroAngle[-1])

                # egne variable
                DataToOnlinePlot["Ts"] = (Ts[-1])
                DataToOnlinePlot["PowerB"] = (PowerB[-1])
                DataToOnlinePlot["PowerC"] = (PowerC[-1])
                DataToOnlinePlot["IAE"] = (IAE[-1])
                DataToOnlinePlot["MAE"] = (MAE[-1])
                DataToOnlinePlot["TV_B"] = (TV_B[-1])
                DataToOnlinePlot["TV_C"] = (TV_C[-1])
                DataToOnlinePlot["Avvik"] = (Avvik[-1])
                DataToOnlinePlot["MedianLys"] = (medianLys[-1])
                DataToOnlinePlot["STD_Lys"] = (STD_Lys[-1])
                DataToOnlinePlot["PosX"] = (PosX[-1])
                DataToOnlinePlot["PosY"] = (PosY[-1])

                # sender over data
                msg = json.dumps(DataToOnlinePlot)
                robot["connection"].send(bytes(msg, "utf-b") + b"?")
            # --------------------------------------------------------

            # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++
            #            10) STOP EXPERIMENT AND INCREASE k
            #
            # Hvis du får socket timeouts, fjern kommentar foran sleep(1)
            # sleep(1)

            # Hvis skyteknappen trykkes inn så skal programmet avsluttes
            if config.joyMainSwitch:
                print("joyMainSwitch er satt til 1")
                break

            # Teller opp k
            k += 1
            # --------------------------------------------------------

    except Exception as e:
        sys.print_exception(e)
    finally:
        # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        #                  11) CLOSE JOYSTICK AND EV3
        #
        # Spesifiser hvordan du vil at motoren(e) skal stoppe.
        # Det er 3 forskjellige måter å stoppe motorene på:
        # - stop() ruller videre og bremser ikke.
        # - brake() ruller videre, men bruker strømmen generert
        #   av rotasjonen til å bremse.
        # - hold() bråstopper umiddelbart og holder posisjonen
        motorB.brake()
        motorC.brake()

        # Lukker forbindelsen til både styrestikke og EV3.
        CloseJoystickAndEV3(robot, wired)
        # --------------------------------------------------------


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#               12) MATH CALCULATIONS
# Her gjøres alle beregninger basert på målinger og egendefinerte
# lister med variable.
#
# Denne funksjonen kalles enten fra seksjonen
#  --> 7) optional: PERFORM CALCULATIONS AND SET MOTOR POWER
# ovenfor i online, eller fra
#  --> H) offline: PERFORM CALCULATIONS
# i offline fra plottefilen.
#
# Pass på at funksjonsbeskrivelsen og kallet til
# funksjonen er identiske i
#   - seksjonene 7) og 12) for online bruk,
# eller i seksjonene
#   - seksjonene H) og 12) for offline bruk

def MathCalculations(Tid, Lys, Ts, Avvik, AvvikFilter, IAE, MAE, TV_B, TV_C, I, PowerB, PowerC, middleLys, STD_Lys, Avstand, reverse, GyroAngle, PosX, PosY):

    # Parametre
    u_0 = 15
    a = 0.3  # 'Gir' for bil
    b = 0.6
    Kp = 3.5
    Ki = 1.4
    Kd = 0.3
    m = 15
    alpha = 0.3
    # Avvik beregning
    referanse = Lys[0]

    # Initialverdibereging

    if len(Tid) == 1:
        reverse.append(False)
        Ts.append(0)  # Tidsskritt
        IAE.append(0)  # Integral of Absolute Error
        MAE.append(0)  # Mean Absoute Error
        TV_B.append(0)  # Total Variaton motorB
        TV_C.append(0)
        Avvik.append(0)  # Total Variaton motorC
        AvvikFilter.append(0)  # Total Variaton motorC
        middleLys.append(0)
        STD_Lys.append(0)
        I.append(0)
        PowerB.append(0)
        PowerC.append(0)
        PosX.append(0)
        PosY.append(0)

    else:
        Ts.append(Tid[-1]-Tid[-2])

        Avvik.append(Lys[-1] - referanse)
        AvvikFilter.append(IIR_filter(Avvik, AvvikFilter, alpha))

        I.append(EulerForward(Ki*Avvik[-1], Ts[-1], I[-1]))

        # Pådragsberegning
        # Checks distance to wall
        if Avstand[-1] <= 90:
            reverse.append(True)
        if reverse[-1]:
            if Avstand[-1] <= 200:

                if Avstand[-1] <= 150:
                    PowerB.append(-u_0)
                    PowerC.append(-u_0)
                    avgSpeed = (PowerB[-1]+PowerC[-1])/2
                    PosX.append(EulerForward(
                        avgSpeed, Ts[-1], PosX[-1])*math.cos(GyroAngle[-1]))
                    PosY.append(EulerForward(
                        avgSpeed, Ts[-1], PosY[-1])*math.sin(GyroAngle[-1]))
                else:
                    a = random.randrange(15, 30)
                    PowerB.append(a)
                    PowerC.append(-a)

            else:
                reverse.append(False)
        else:
            PowerB.append(u_0)
            PowerC.append(u_0)

        # Postion Calulation
            avgSpeed = (PowerB[-1]+PowerC[-1])/2
            PosX.append(EulerForward(
                avgSpeed, Ts[-1], PosX[-1])*math.cos(GyroAngle[-1]))
            PosY.append(EulerForward(
                avgSpeed, Ts[-1], PosY[-1])*math.sin(GyroAngle[-1]))

        # Numerisk integrasjon av Lys - referanse
        IAE.append(EulerForward(Avvik[-1], Ts[-1], IAE[-1]))
        MAE.append(mean_abs_error(Avvik, m))

        TV_B.append(TV(PowerB[-1], PowerB[-2], TV_B))
        TV_C.append(TV(PowerC[-1], PowerC[-2], TV_C))

        middleLys.append(middleValue(Lys))

        STD_Lys.append(STD(Lys[-1], referanse, STD_Lys))

    # Matematiske beregninger


# ---------------------------------------------------------------------

def PID(u_0, Kp, Kd, e_t, ef_t, I, ts):
    # u_0        -->    Base pull
    # Kp, Ki, Kd -->    Constants
    # e_t        -->    Deviation form refernece
    # ef_t       -->    Filterd Deviation form refernece
    # I          -->    Integrated I part
    return Kp*e_t[-1] + I[-1] + Kd*Derivasjon(ef_t, ts)


def IIR_filter(list, IIR_prev, alpha):

    IIR_Value = alpha*list[-1]+(1-alpha)*IIR_prev[-1]
    return IIR_Value


def EulerForward(functionValue, Ts, intValueOld):
    intValueNew = intValueOld + Ts*functionValue
    return abs(intValueNew)


def Derivasjon(functionValue, dt):

    derivative = (functionValue[-1] - functionValue[-2]) / (dt[-1])
    return derivative


def TV(functionValue, functionValueOld, TV):
    return TV[-1] + abs(functionValue-functionValueOld)


def mean_abs_error(list, m):

    if len(list) < m:
        # sjekker at m ikke er større en k
        m = len(list)

    # Glatting av målinger i FIR filter
    intValueNew = (1/m)*(sum(list[-m:]))
    # Retunering av utregnet verdi FIR VALUE
    return abs(intValueNew)


def middleValue(list):
    return (sum(list))/len(list)


def STD(list, medianList, std):
    return math.sqrt((std[-1]+(list-medianList)**2)/(len(std)))


if __name__ == '__main__':
    main()

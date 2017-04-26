import numpy as np
import pandas as pd
import math
from SDToolbox import *
from matplotlib.legend_handler import HandlerLine2D
from zndMZ_reactionLength import *
import matplotlib.pyplot as plt
import cantera as ct
import csv



P1 = 101325
combVolume = 0.02
T0 = [293,393,493, 2000]
mech = ['h2air_highT.cti','gri30_highT.cti','h2-n2o_highT.cti','Wang_highT.cti','Konnov.cti', 'gri30.cti']
mech_name = ['h2air_highT','gri30_highT','h2-n2o_highT','Wang_highT','Konnov', 'gri30']

nH20 = 0
nH2 = 0.29
nO2 = (1-(nH2+nH20))*0.21
nN2 = (1-(nH2+nH20))*0.79
q = 'H2:'+str(nH2)+' O2:'+str(nO2)+' N2:'+str(nN2)+' H2O:'+str(nH20)+''
print q

for l in range(0,len(mech)):

    with open('Constant_Volume_Excel_H2_%s.csv'% mech_name[l],'w') as fname:
        a = csv.writer(fname, delimiter=';', lineterminator='\n')
        data = [['Czas [s*1.0e-4]',' T [K]', 'P [Pa]', 'T_grad [K]']]
        a.writerows(data)

    for j in range(0, len(T0)):
        gas1 = ct.Solution(mech[l])
        gas1.TPX = T0[j], P1, q #'H2:2.0 O2:1.0 N2:3.76'
        igniter = Reservoir(gas1)

        dose=5e-04
        dt = 0.0015
        igniter_mdot = dose/dt # 0,3333 - najlepszy

        # Define reactor
        gas1.TPX = T0[j], P1, q

        r1 = Reactor(gas1)
        r1.volume = combVolume
        m3 = MassFlowController(igniter, r1, mdot=igniter_mdot)
        sim = ReactorNet([r1])

        time = 0.0
        dt = 1.0e-2
        P = []
        T = []
        T_grad = []
        tt = []
        n =[]

        while (time < 1):                # tu przyjuje warunek czasowy
            time += dt
            sim.advance(time)
            tt.append(time)
            P.append(r1.thermo.P)
            T.append(r1.thermo.T)
        for n in range(0, len(T)-1):
            T_grad.append(T[n+1] - T[n])
            if T_grad[n] < 0.1:        # tu przyjuje warunek zmiany temperatury
               break


        del tt[-(len(tt)-len(T_grad)):]
        del P[-(len(P) - len(T_grad)):] # wyrownuje rozmiar tablic
        del T[-(len(T) - len(T_grad)):]


        with open('Constant_Volume_Excel_H2_%s.csv'% mech_name[l], 'a') as fname:
            a = csv.writer(fname, delimiter=';', lineterminator='\n')
            data = zip(tt,T,P,T_grad)
            a.writerows(data)


        #plt.suptitle('%s' % mech[l], fontsize=14)
        plt.subplot(2, 2, 1)
        #print max(P)
        line1, = plt.plot(tt,P, label='T0 = %d K'%(T0[j]))
        plt.legend(handler_map={line1: HandlerLine2D(numpoints=4)},bbox_to_anchor=(1.05, 1), loc=0, borderaxespad=0.,prop={'size':8})
        plt.title("Pressure(t)",fontsize = 14)
        plt.ylabel("Prseeure [Pa]")
        plt.xlabel("t [s]")

        plt.subplot(2, 2, 3)
        #print max(T)
        line1, = plt.plot(tt, T, label='T0 = %d K' % (T0[j]))
        plt.legend(handler_map={line1: HandlerLine2D(numpoints=4)},bbox_to_anchor=(1.05, 1), loc=0, borderaxespad=0.,prop={'size':8})
        plt.title("Temperature(t)",fontsize = 14)
        plt.ylabel("T [K]")
        plt.xlabel("t [s]")

        #plt.subplot(2, 2, 3)
        #print max(T_grad)
        #line1, = plt.plot(tt, T_grad, label='T0 = %d K' % (T0[j]))
        #plt.legend(handler_map={line1: HandlerLine2D(numpoints=4)}, bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
        #plt.title("Temperature gradient (t)",fontsize = 14)
        #plt.ylabel("T_grad [K]")
        #plt.xlabel("t [s]")

    plt.tight_layout()
    plt.savefig("Figure %s"% mech_name[l],bbox_inches='tight')
    plt.show()
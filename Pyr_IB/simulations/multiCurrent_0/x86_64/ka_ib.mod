COMMENT

   **************************************************
   File generated by: neuroConstruct v1.6.0 
   **************************************************


ENDCOMMENT


?  This is a NEURON mod file generated from a ChannelML file

?  Unit system of original ChannelML file: Physiological Units

COMMENT
    ChannelML file based on Traub et al. 2003
ENDCOMMENT

TITLE Channel: ka_ib

COMMENT
    Potasium A-type conductance (transient, inactivating). Channel used in Traub et al 2005, slight modification of ka
ENDCOMMENT


UNITS {
    (mA) = (milliamp)
    (mV) = (millivolt)
    (S) = (siemens)
    (um) = (micrometer)
    (molar) = (1/liter)
    (mM) = (millimolar)
    (l) = (liter)
}


    
NEURON {
      

    SUFFIX ka_ib
    USEION k READ ek WRITE ik VALENCE 1  ? reversal potential of ion is read, outgoing current is written
           
        
    RANGE gmax, gion
    
    RANGE minf, mtau
    
    RANGE hinf, htau
    
}

PARAMETER { 
      

    gmax = 0.03 (S/cm2)  ? default value, should be overwritten when conductance placed on cell
    
}



ASSIGNED {
      

    v (mV)
    
    celsius (degC)
          

    ? Reversal potential of k
    ek (mV)
    ? The outward flow of ion: k calculated by rate equations...
    ik (mA/cm2)
    
    
    gion (S/cm2)
    minf
    mtau (ms)
    hinf
    htau (ms)
    
}

BREAKPOINT { 
                        
    SOLVE states METHOD cnexp
         

    gion = gmax*((m)^4)*((1*h)^1)      

    ik = gion*(v - ek)
            

}



INITIAL {
    
    ek = -95
        
    rates(v)
    m = minf
        h = hinf
        
    
}
    
STATE {
    m
    h
    
}

DERIVATIVE states {
    rates(v)
    m' = (minf - m)/mtau
    h' = (hinf - h)/htau
    
}

PROCEDURE rates(v(mV)) {  
    
    ? Note: not all of these may be used, depending on the form of rate equations
    LOCAL  alpha, beta, tau, inf, gamma, zeta, temp_adj_m, A_tau_m, B_tau_m, Vhalf_tau_m, A_inf_m, B_inf_m, Vhalf_inf_m, temp_adj_h, A_tau_h, B_tau_h, Vhalf_tau_h, A_inf_h, B_inf_h, Vhalf_inf_h
        
    TABLE minf, mtau,hinf, htau
 DEPEND celsius
 FROM -120 TO 60 WITH 741
    
    
    UNITSOFF
    temp_adj_m = 1
    temp_adj_h = 1
    
            
                
           

        
    ?      ***  Adding rate equations for gate: m  ***
         
    ? Found a generic form of the rate equation for tau, using expression: 0.185 + 0.5 / ((exp (( v + 35.8 )/19.7)) + (exp ((-v - 79.7)/12.7)))
    tau = 0.185 + 0.5 / ((exp (( v + 35.8 )/19.7)) + (exp ((-v - 79.7)/12.7)))
        
    mtau = tau/temp_adj_m
    
    ? Found a parameterised form of rate equation for inf, using expression: A / (1 + exp((v-Vhalf)/B))
    A_inf_m = 1
    B_inf_m = -8.5
    Vhalf_inf_m = -60 
    inf = A_inf_m / (exp((v - Vhalf_inf_m) / B_inf_m) + 1)
    
    minf = inf
          
       
    
    ?     *** Finished rate equations for gate: m ***
    

    
            
                
           

        
    ?      ***  Adding rate equations for gate: h  ***
         
    ? Found a generic form of the rate equation for tau, using expression: v < -63.0 ? 2.6 * 0.5 / ((exp (( v + 46 )/5)) + (exp (( -v - 238 )/37.5))) : 2.6 * 9.5
    
    
    if (v < -63.0 ) {
        tau =  2.6 * 0.5 / ((exp (( v + 46 )/5)) + (exp (( -v - 238 )/37.5))) 
    } else {
        tau =  2.6 * 9.5
    }
    htau = tau/temp_adj_h
    
    ? Found a parameterised form of rate equation for inf, using expression: A / (1 + exp((v-Vhalf)/B))
    A_inf_h = 1
    B_inf_h = 6
    Vhalf_inf_h = -78 
    inf = A_inf_h / (exp((v - Vhalf_inf_h) / B_inf_h) + 1)
    
    hinf = inf
          
       
    
    ?     *** Finished rate equations for gate: h ***
    

         

}


UNITSON



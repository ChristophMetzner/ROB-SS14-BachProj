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

TITLE Channel: kahp_deeppyr

COMMENT
    Slow [Ca2+] dependent K AHP (afterhyperpolarization) conductance. Based on kahp from Traub et al 2003
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
      

    SUFFIX kahp_deeppyr
    USEION k READ ek WRITE ik VALENCE 1  ? reversal potential of ion is read, outgoing current is written
           
        
    USEION ca READ cai VALENCE 2 ? internal concentration of ion is read

    
    RANGE gmax, gion
    
    RANGE minf, mtau
    
}

PARAMETER { 
      

    gmax = 0.0001 (S/cm2)  ? default value, should be overwritten when conductance placed on cell
    
}



ASSIGNED {
      

    v (mV)
    
    celsius (degC)
          

    ? Reversal potential of k
    ek (mV)
    ? The outward flow of ion: k calculated by rate equations...
    ik (mA/cm2)
          

    ? The internal concentration of ion: ca is used in the rate equations...
    cai (mM)   
    
    
    gion (S/cm2)
    minf
    mtau (ms)
    
}

BREAKPOINT { SOLVE states METHOD derivimplicit     

    gion = gmax*((m)^1)      

    ik = gion*(v - ek)
            

}



INITIAL {
    
    ek = -95
        
    settables(v,cai)
    m = minf
        
    
}
    
STATE {
    m
    
}

DERIVATIVE states {
    settables(v,cai)
    m' = (minf - m)/mtau
    
}

PROCEDURE settables(v(mV), cai(mM)) {  
    
    ? Note: not all of these may be used, depending on the form of rate equations
    LOCAL  alpha, beta, tau, inf, gamma, zeta, ca_conc, temp_adj_m, A_alpha_m, B_alpha_m, Vhalf_alpha_m, A_beta_m, B_beta_m, Vhalf_beta_m
    
    
    UNITSOFF
    temp_adj_m = 1
    
    ? Gate depends on the concentration of ca
    ca_conc = cai ? In NEURON, the variable for the concentration  of ca is cai
    
            
                
           

        
    ?      ***  Adding rate equations for gate: m  ***
         
    ? Found a generic form of the rate equation for alpha, using expression: ca_conc < 0.0001 ? ca_conc/0.01 : 0.01
    
    ? Equations can depend on concentration. NEURON uses 'SI Units' internally for concentration, 
    ? but the ChannelML file is in Physiological Units...
    ca_conc = ca_conc / 1000000
    
    
    if (ca_conc < 0.0001 ) {
        alpha =  ca_conc/0.01 
    } else {
        alpha =  0.01
    }
    ? Resetting concentration...
    ca_conc = ca_conc * 1000000
    
     
    ? Found a generic form of the rate equation for beta, using expression: 0.001
    
    ? Equations can depend on concentration. NEURON uses 'SI Units' internally for concentration, 
    ? but the ChannelML file is in Physiological Units...
    ca_conc = ca_conc / 1000000
    beta = 0.001
        
    ? Resetting concentration...
    ca_conc = ca_conc * 1000000
    
    mtau = 1/(temp_adj_m*(alpha + beta))
    minf = alpha/(alpha + beta)
          
       
    
    ?     *** Finished rate equations for gate: m ***
    

         

}


UNITSON



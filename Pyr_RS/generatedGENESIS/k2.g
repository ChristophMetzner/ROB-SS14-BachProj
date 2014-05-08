

// **************************************************
// File generated by: neuroConstruct v1.5.2 
// **************************************************




// This is a GENESIS script file generated from a ChannelML v1.8.1 file
// The ChannelML file is mapped onto a tabchannel object


// Units of ChannelML file: Physiological Units, units of GENESIS file generated: SI Units

/*
    ChannelML file based on Traub et al. 2003
*/

function make_k2

        /*
            Potasium K2-type current (slowly activating and inactivating). Based on NEURON port of FRB L2/3 model from Traub et al 2003. Same channel used in Traub et al 2005

            
Reference: Roger D. Traub, Eberhard H. Buhl, Tengis Gloveli, and Miles A. Whittington                
Fast Rhythmic Bursting Can Be Induced in Layer 2/3 Cortical Neurons by Enhancing Persistent Na+ Conductance or by Blocking BK Channels
J Neurophysiol 89: 909-921, 2003
            Pubmed: http://www.ncbi.nlm.nih.gov/entrez/query.fcgi?cmd=Retrieve&db=pubmed&dopt=Abstract&list_uids=12574468

            
Reference: Roger D. Traub, Diego Contreras, Mark O. Cunningham, Hilary Murray, Fiona E. N. LeBeau, Anita Roopun, Andrea Bibbig, W. Bryan Wilent, Michael J. Higley, and Miles A. Whittington
Single-column thalamocortical network model exhibiting gamma oscillations, sleep spindles, and epileptogenic bursts.
J. Neurophysiol. 93, 2194-2232, 2005
            Pubmed: http://www.ncbi.nlm.nih.gov/pubmed/15525801?dopt=Abstract

        */
        

        str chanpath = "/library/k2"

        if ({exists {chanpath}})
            return
        end
        
        create tabchannel {chanpath}
            

        setfield {chanpath} \ 
            Ek              -0.095 \
            Ik              0  \
            Xpower          1 \
            Ypower          1
        
        setfield {chanpath} \
            Gbar 1 \
            Gk              0 

        
        // No Q10 temperature adjustment found
        float temp_adj_m = 1
        float temp_adj_h = 1
    

        float tab_divs = 741
        float v_min = -0.12

        float v_max = 0.06

        float v, dv, i
            
        // Creating table for gate m, using name X for it here

        float dv = ({v_max} - {v_min})/{tab_divs}
            
        call {chanpath} TABCREATE X {tab_divs} {v_min} {v_max}
                
        v = {v_min}

            

        for (i = 0; i <= ({tab_divs}); i = i + 1)
            
            // Looking at rate: tau
                

            float tau
                
                        
            // Found a generic form of rate equation for tau, using expression: 4.95 + 0.5 / ( (exp ( (v - 81) / 25.6)) + (exp ( (- v - 132) / 18 )))
            // Will translate this for GENESIS compatibility...
                    
            // Equation (and all ChannelML file values) in Physiological Units but this script in SI Units
            

            v = v * 1000 // temporarily set v to units of equation...
            tau = 4.95 + 0.5 / { {exp { {v - 81} / 25.6}} + {exp { {- v - 132} / 18 }}}
            
            v = v * 0.001 // reset v
            
            // Set correct units of tau
            tau = tau * 0.001
            // Looking at rate: inf
                

            float inf
                
            float A, B, Vhalf
                             

            // ChannelML form of equation: inf which is of form sigmoid, with params:
            // A = 1, B = -17, Vhalf = -10, in units: Physiological Units
            A = 1
            B = -0.017
            Vhalf = -0.01
            inf = A / ( {exp {(v - Vhalf) / B}} + 1)
        

            // Evaluating the tau and inf expressions

                    
            tau = tau/temp_adj_m
    

            
            // Working out the "real" alpha and beta expressions from the tau and inf
            
            float alpha
            float beta
            alpha = inf / tau   
            beta = (1- inf)/tau
            
            
            setfield {chanpath} X_A->table[{i}] {alpha}
            setfield {chanpath} X_B->table[{i}] {alpha + beta}

                
            v = v + dv

        end // end of for (i = 0; i <= ({tab_divs}); i = i + 1)
            
        setfield {chanpath} X_A->calc_mode 1 X_B->calc_mode 1
                    
        // Creating table for gate h, using name Y for it here

        float dv = ({v_max} - {v_min})/{tab_divs}
            
        call {chanpath} TABCREATE Y {tab_divs} {v_min} {v_max}
                
        v = {v_min}

            

        for (i = 0; i <= ({tab_divs}); i = i + 1)
            
            // Looking at rate: tau
                

            float tau
                
                        
            // Found a generic form of rate equation for tau, using expression: 60 + 0.5 / ((exp (( v - 1.33 )/200)) + (exp ((- v - 130)/ 7.1)))
            // Will translate this for GENESIS compatibility...
                    
            // Equation (and all ChannelML file values) in Physiological Units but this script in SI Units
            

            v = v * 1000 // temporarily set v to units of equation...
            tau = 60 + 0.5 / {{exp {{ v - 1.33 }/200}} + {exp {{- v - 130}/ 7.1}}}
            
            v = v * 0.001 // reset v
            
            // Set correct units of tau
            tau = tau * 0.001
            // Looking at rate: inf
                

            float inf
                
            float A, B, Vhalf
                             

            // ChannelML form of equation: inf which is of form sigmoid, with params:
            // A = 1, B = 10.6, Vhalf = -58, in units: Physiological Units
            A = 1
            B = 0.0106
            Vhalf = -0.058
            inf = A / ( {exp {(v - Vhalf) / B}} + 1)
        

            // Evaluating the tau and inf expressions

                    
            tau = tau/temp_adj_h
    

            
            // Working out the "real" alpha and beta expressions from the tau and inf
            
            float alpha
            float beta
            alpha = inf / tau   
            beta = (1- inf)/tau
            
            
            setfield {chanpath} Y_A->table[{i}] {alpha}
            setfield {chanpath} Y_B->table[{i}] {alpha + beta}

                
            v = v + dv

        end // end of for (i = 0; i <= ({tab_divs}); i = i + 1)
            
        setfield {chanpath} Y_A->calc_mode 1 Y_B->calc_mode 1
                    


end


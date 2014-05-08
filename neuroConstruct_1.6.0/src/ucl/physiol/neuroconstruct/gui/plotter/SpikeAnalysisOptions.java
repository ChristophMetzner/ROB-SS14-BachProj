/**
 *  neuroConstruct
 *  Software for developing large scale 3D networks of biologically realistic neurons
 * 
 *  Copyright (c) 2009 Padraig Gleeson
 *  UCL Department of Neuroscience, Physiology and Pharmacology
 *
 *  Development of this software was made possible with funding from the
 *  Medical Research Council and the Wellcome Trust
 *  
 *  This program is free software; you can redistribute it and/or modify
 *  it under the terms of the GNU General Public License as published by
 *  the Free Software Foundation; either version 2 of the License, or
 *  (at your option) any later version.
 *  
 *  This program is distributed in the hope that it will be useful,
 *  but WITHOUT ANY WARRANTY; without even the implied warranty of
 *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 *  GNU General Public License for more details.

 *  You should have received a copy of the GNU General Public License
 *  along with this program; if not, write to the Free Software
 *  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
 *
 */

package ucl.physiol.neuroconstruct.gui.plotter;

/**
 * Class to store info on options for analysing the spiking patterns of plots
 *
 * @author Padraig Gleeson
 *  
 */

public class SpikeAnalysisOptions
{
    float threshold = -20;

    float startTime = 0;
    float stopTime = 100;


    public SpikeAnalysisOptions()
    {
    }

    public float getThreshold()
    {
        return threshold;
    }
    public void setThreshold(float threshold)
    {
        this.threshold = threshold;
    }
    public float getStopTime()
    {
        return stopTime;
    }
    public float getStartTime()
    {
        return startTime;
    }
    public void setStartTime(float startTime)
    {
        this.startTime = startTime;
    }
    public void setStopTime(float stopTime)
    {
        this.stopTime = stopTime;
    }
}

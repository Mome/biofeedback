/*
*         
*
*
*
*
*
*
*
*  Copyright (C) 2012 Libelium Comunicaciones Distribuidas S.L.
*  http://www.libelium.com
*
*  This program is free software: you can redistribute it and/or modify
*  it under the terms of the GNU General Public License as published by
*  the Free Software Foundation, either version 3 of the License, or
*  (at your option) any later version.
*
*  This program is distributed in the hope that it will be useful,
*  but WITHOUT ANY WARRANTY; without even the implied warranty of
*  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
*  GNU General Public License for more details.
*
*  You should have received a copy of the GNU General Public License
*  along with this program.  If not, see .
*
*  Version 0.1
*  Author: Luis Martín & Ahmad Saad
*/


// ensure this library description is only included once
#ifndef airFlowClass_h
#define airFlowClass_h

#include "Arduino.h"


// library interface description
class airFlowClass {
		
	public:   
	
		airFlowClass(void);	
  		
  		int airFlowValue(void);
				  
	private:	

}; 

extern airFlowClass airFlower;

#endif


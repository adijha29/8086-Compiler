import streamlit as st
import pandas as pd
import numpy as np
import base64
import re

st.set_page_config(layout="wide")

st.markdown("<h1 style='text-align: center; color: white;'>8086 Compiler</h1>", unsafe_allow_html=True)
c1,c2=st.columns((2,1))

REGISTERS_INFO={"AH":"00","AL":"00","BH":"00","BL":"00","CH":"00","CL":"00","DH":"00","DL":"00"}
Registers16=("AX","BX","CX","DX")
Registers8=("AL","BL","CL","DL","AH","BH","CH","DH")
FLAG_INFO={'OF':'0','DF':'0','IF':'0','TF':'0','SF':'0','ZF':'0','AC':'0','PF':'0','CF':'0'}
LABEL = {}
OPCODE = {
'MOV':'00000','INC':'00001','DEC':'00010','ADD':'00011','SUB':'00100','ADC':'00101','SBB':'00110','MUL':'00111','DIV':'01000','CMP':'01001','CBW':'01010','CWD':'01011','NEG':'01100','AND':'01101','OR':'01110','NOT':'01111','XOR':'10000','XCHG':'10001','PUSHF':'10010',
'POPF':'10011'}
prevCarry = '-1'
#-------------------------------------------------------------------------------------------------------------------


#---------------------------------------------------Conversion-------------------------------------------
def hexToBinary(val,size):
    output = "{0:04b}".format(int(val,base=16))
    while len(output)<size :
        output = '0' + output
    return output

def binaryToHex(val,size):
    n = int(val,base=2)
    hexn = str(hex(n))
    hexn=hexn.upper()
    hexn = hexn[2:]
    while len(hexn)<size :
        hexn = '0' + hexn
    return hexn
#-------------------------------------------------------------------------------------------------------


#--------------------------------------------Getting 8 and 16 bit values--------------------------------
def getValueOf8(x):
    if x=='AL':
        return REGISTERS_INFO['AL']
    elif x=='AH':
        return REGISTERS_INFO['AH']
    elif x=='BL':
        return REGISTERS_INFO['BL']
    elif x=='BH':
        return REGISTERS_INFO['BH']
    elif x=='CL':
        return REGISTERS_INFO['CL']
    elif x=='CH':
        return REGISTERS_INFO['CH']
    elif x=='DL':
        return REGISTERS_INFO['DL']
    elif x=='DH':
        return REGISTERS_INFO['DH']

def getValueOf16(x):
    if x=='AX':
        return REGISTERS_INFO['AH']+REGISTERS_INFO['AL']
    elif x=='BX':
        return REGISTERS_INFO['BH']+REGISTERS_INFO['BL']
    elif x=='CX':
        return REGISTERS_INFO['CH']+REGISTERS_INFO['CL']
    elif x=='DX':
        return REGISTERS_INFO['DH']+REGISTERS_INFO['DL']
#------------------------------------------------------------------------------------------------------------------


#------------------------------------------------UPDATE-----------------------------------------------------------
def update_16(reg,val):
    upper=val[:2]
    lower=val[2:]
    if reg=="AX":
        REGISTERS_INFO['AL'] = lower
        REGISTERS_INFO['AH'] = upper
    elif reg=="BX":
        REGISTERS_INFO['BL'] = lower
        REGISTERS_INFO['BH'] = upper
    elif reg=="CX":
        REGISTERS_INFO['CL'] = lower
        REGISTERS_INFO['CH'] = upper
    elif reg=="DX":
        REGISTERS_INFO['DL'] = lower
        REGISTERS_INFO['DH'] = upper
        
def update_8(reg,val):
    if reg=='AL':
        REGISTERS_INFO['AL'] = val
    elif reg=='BL':
        REGISTERS_INFO['BL'] = val
    elif reg=='CL':
        REGISTERS_INFO['CL'] = val
    elif reg=='DL':
        REGISTERS_INFO['DL'] = val
    elif reg=='AH':
        REGISTERS_INFO['AH'] = val
    elif reg=='BH':
        REGISTERS_INFO['BH'] = val
    elif reg=='CH':
        REGISTERS_INFO['CH'] = val
    elif reg=='DH':
        REGISTERS_INFO['DH'] = val
#------------------------------------------------------------------------------------------------------------------


#----------------------------------------------------MOV-----------------------------------------------------------
def mov8RR(a,b):
    b = getValueOf8(b)
    b=b[:-1]
    update_8(a,b)

def mov8RV(a,b):
    b=b[:-1]
    update_8(a,b)

def mov16RV(a,b):
    b=b[:-1]
    update_16(a,b)

def mov16RR(a,b):
    b=b[:-1]
    b = getValueOf16(b)
    update_16(a,b)
#------------------------------------------------------------------------------------------------------------------


#----------------------------------------------------ADDITION---------------------------------------------
def addBit(a,b,c):
    if a=="1" and b=="1" and c=="1":
        return 1,1
    elif (a=="1" and b=="1") or (a=="1" and c=="1") or (b=="1" and c=="1"):
        return 0,1
    elif a=="1" or b=="1" or c=="1":
        return 1,0
    else:
        return 0,0

def add4VV(x,y,carry):
    global prevCarry
    x = x[:-1]
    y = y[:-1]
    
    binx = hexToBinary(x,4)
    biny = hexToBinary(y,4)
    
    ans = [0,0,0,0]
    for i in range(3,-1,-1):
        ans[i],tcarry = addBit(binx[i],biny[i],carry)
        carry = str(tcarry)
        if i==1:
            prevCarry = carry
    
    ansStr = ''.join([str(elem) for elem in ans])
    return ansStr,carry

def add8VV(a,b,carry):
    # Trim the value to lower Nibbe and Higher Nibble
    bit11 = a[3:4]+'H'
    bit12 = a[2:3]+'H'

    bit21 = b[3:4]+'H'
    bit22 = b[2:3]+'H'
    
    auxiCarry = 0
    
    # Performing 4 bit addition 4 times
    sum1,carry1 = add4VV(bit11,bit21,carry)
    sum2,carry2 = add4VV(bit12,bit22,str(carry1))

    auxiCarry = carry1
    carry = carry2
    sumV = sum2+sum1
    
    sumV = binaryToHex(sumV,2)
    
    return carry,auxiCarry,sumV

def add8RV(x,y,carry):
    # Getting Register Values
    xVal = getValueOf8(x)
    
    lowerNib1 = xVal[1:]+'H'
    lowerNib2 = y[1:2]+'H'
    higherNib1 = xVal[:1]+'H'
    higherNib2 = y[:1]+'H'
    
    sum1,carry = add4VV(lowerNib1,lowerNib2,carry)
    auxiCarry = carry
    sum2,carry = add4VV(higherNib1,higherNib2,carry)
    
    finSum = binaryToHex(sum2+sum1,2)
    if len(finSum)==1:
        finSum = '0' + finSum
   
    return carry,auxiCarry,finSum

def add8RR(x,y,carry):
    # Getting Register Values
    xVal = getValueOf8(x)
    yVal = getValueOf8(y)
    
    lowerNib1 = xVal[1:]+'H'
    lowerNib2 = yVal[1:]+'H'
    higherNib1 = xVal[:1]+'H'
    higherNib2 = yVal[:1]+'H'
    
    sum1,carry = add4VV(lowerNib1,lowerNib2,carry)
    auxiCarry = carry
    sum2,carry = add4VV(higherNib1,higherNib2,carry)
    
    finSum = binaryToHex(sum2+sum1,2)
    if len(finSum)==1:
        finSum = '0' + finSum

    return carry,auxiCarry,finSum

def add16VV(a,b,carry):
    # Trim the value to lower Nibbe and Higher Nibble
    bit11 = a[3:4]+'H'
    bit12 = a[2:3]+'H'
    bit13 = a[1:2]+'H'
    bit14 = a[:1]+'H'

    bit21 = b[3:4]+'H'
    bit22 = b[2:3]+'H'
    bit23 = b[1:2]+'H'
    bit24 = b[:1]+'H'
    
    auxiCarry = 0
    
    # Performing 4 bit addition 4 times
    sum1,carry1 = add4VV(bit11,bit21,carry)
    sum2,carry2 = add4VV(bit12,bit22,str(carry1))
    sum3,carry3 = add4VV(bit13,bit23,str(carry2))
    sum4,carry4 = add4VV(bit14,bit24,str(carry3))

    auxiCarry = carry2
    carry = carry4
    sumV = sum4+sum3+sum2+sum1
    
    sumV = binaryToHex(sumV,4)
    
    return carry,auxiCarry,sumV

def add16RV(a,b,carry):
    # Getting Register Values
    a = getValueOf16(a)
    
    # Trim the value to lower Nibbe and Higher Nibble
    bit11 = a[3:4]+'H'
    bit12 = a[2:3]+'H'
    bit13 = a[1:2]+'H'
    bit14 = a[:1]+'H'

    bit21 = b[3:4]+'H'
    bit22 = b[2:3]+'H'
    bit23 = b[1:2]+'H'
    bit24 = b[:1]+'H'
    
    auxiCarry = 0
    
    # Performing 4 bit addition 4 times
    sum1,carry1 = add4VV(bit11,bit21,carry)
    sum2,carry2 = add4VV(bit12,bit22,str(carry1))
    sum3,carry3 = add4VV(bit13,bit23,str(carry2))
    sum4,carry4 = add4VV(bit14,bit24,str(carry3))

    auxiCarry = carry2
    carry = carry4
    sumV = sum4+sum3+sum2+sum1
    
    sumV = binaryToHex(sumV,4)
    
    return carry,auxiCarry,sumV

def add16RR(a,b,carry):
    # Getting Register Values
    a = getValueOf16(a)
    b = getValueOf16(b)
    
    # Trim the value to lower Nibbe and Higher Nibble
    bit11 = a[3:4]+'H'
    bit12 = a[2:3]+'H'
    bit13 = a[1:2]+'H'
    bit14 = a[:1]+'H'

    bit21 = b[3:4]+'H'
    bit22 = b[2:3]+'H'
    bit23 = b[1:2]+'H'
    bit24 = b[:1]+'H'
    
    auxiCarry = 0

    # Performing 4 bit addition 4 times
    sum1,carry1 = add4VV(bit11,bit21,carry)
    sum2,carry2 = add4VV(bit12,bit22,str(carry1))
    sum3,carry3 = add4VV(bit13,bit23,str(carry2))
    sum4,carry4 = add4VV(bit14,bit24,str(carry3))

    auxiCarry = carry2
    carry = carry4
    sumV = sum4+sum3+sum2+sum1
    
    sumV = binaryToHex(sumV,4)

    return auxiCarry,carry,sumV
#-----------------------------------------------------------------------------------------------------------------


#----------------------------------------------------SUBTRACTION----------------------------------------------
def subBit(a,b,c):
    if a=="0" and b=="1" and c=="1":
        return 0,1
    elif a=="1" and b=="0" and c=="0":
        return 1,0
    elif (a=="0" and b=="0" and c=="0") or (a=="1" and b=="0" and c=="1") or (a=="1" and b=="1" and c=="0"):
        return 0,0
    else:
        return 1,1

def sub4VV(x,y,carry):
    global prevCarry
    x = x[:-1]
    y = y[:-1]

    binx = hexToBinary(x,4)
    biny = hexToBinary(y,4)
    
    ans = [0,0,0,0]
    for i in range(3,-1,-1):
        ans[i],tcarry = subBit(binx[i],biny[i],carry)
        carry = str(tcarry)
        if i==1:
            prevCarry = carry
    
    ansStr = ''.join([str(elem) for elem in ans])
    return ansStr,carry

def sub8RV(x,y,carry):
    xVal = getValueOf8(x)
    lowerNib1 = xVal[1:]+'H'
    lowerNib2 = y[1:2]+'H'
    higherNib1 = xVal[:1]+'H'
    higherNib2 = y[:1]+'H'
    
    sum1,carry = sub4VV(lowerNib1,lowerNib2,carry)
    auxiCarry = carry
    sum2,carry = sub4VV(higherNib1,higherNib2,carry)
    
    finSum = binaryToHex(sum2+sum1,2)
    if len(finSum)==1:
        finSum = '0' + finSum

    return carry,auxiCarry,finSum

def sub8RR(x,y,carry):
    xVal = getValueOf8(x)
    yVal = getValueOf8(y)
    
    lowerNib1 = xVal[1:]+'H'
    lowerNib2 = yVal[1:]+'H'
    higherNib1 = xVal[:1]+'H'
    higherNib2 = yVal[:1]+'H'
    
    sum1,carry = sub4VV(lowerNib1,lowerNib2,carry)
    auxiCarry = carry
    sum2,carry = sub4VV(higherNib1,higherNib2,carry)
    
    finSum = binaryToHex(sum2+sum1,2)
    if len(finSum)==1:
        finSum = '0' + finSum

    return carry,auxiCarry,finSum

def sub16RV(a,b,carry):
    a = getValueOf16(a)
    # Trim the value to lower Nibbe and Higher Nibble
    bit11 = a[3:4]+'H'
    bit12 = a[2:3]+'H'
    bit13 = a[1:2]+'H'
    bit14 = a[:1]+'H'

    bit21 = b[3:4]+'H'
    bit22 = b[2:3]+'H'
    bit23 = b[1:2]+'H'
    bit24 = b[:1]+'H'
    
    auxiCarry = 0
    
    # Performing 4 bit addition 4 times
    sum1,carry1 = sub4VV(bit11,bit21,carry)
    sum2,carry2 = sub4VV(bit12,bit22,str(carry1))
    sum3,carry3 = sub4VV(bit13,bit23,str(carry2))
    sum4,carry4 = sub4VV(bit14,bit24,str(carry3))

    auxiCarry = carry2
    carry = carry4
    sumV = sum4+sum3+sum2+sum1
    
    sumV = binaryToHex(sumV,4)

    return carry,auxiCarry,sumV

def sub16RR(a,b,carry):
    a = getValueOf16(a)
    b = getValueOf16(b)

    # Trim the value to lower Nibbe and Higher Nibble
    bit11 = a[3:4]+'H'
    bit12 = a[2:3]+'H'
    bit13 = a[1:2]+'H'
    bit14 = a[:1]+'H'

    bit21 = b[3:4]+'H'
    bit22 = b[2:3]+'H'
    bit23 = b[1:2]+'H'
    bit24 = b[:1]+'H'
    
    auxiCarry = 0

    # Performing 4 bit addition 4 times
    sum1,carry1 = sub4VV(bit11,bit21,carry)
    sum2,carry2 = sub4VV(bit12,bit22,str(carry1))
    sum3,carry3 = sub4VV(bit13,bit23,str(carry2))
    sum4,carry4 = sub4VV(bit14,bit24,str(carry3))

    auxiCarry = carry2
    carry = carry4
    sumV = sum4+sum3+sum2+sum1
    
    sumV = binaryToHex(sumV,4)

    return carry,auxiCarry,sumV
#------------------------------------------------------------------------------------------------------------------


#--------------------------------------------------LOGICAL OPERATIONS (1-bit)--------------------------------------
def AND_OP(a,b):
    if a=='1' and b=="1":
        return "1"
    else:
        return "0"

def OR_OP(a,b):
    if a=='0' and b=='0':
        return "0"
    else:
        return "1"

def XOR_OP(a,b):
    if a==b:
        return '0'
    else:
        return '1'
    
def NOT_OP(a):
    if a=='1':
        return '0'
    else:
        return '1'

#---------------------------------------------------------------------------------------------------------------


#---------------------------------------------------AND---------------------------------------------------------
def AND_8RR(a,b):
    a = getValueOf8(a)
    b = getValueOf8(b)
    
    bina = hexToBinary(a,8)
    binb = hexToBinary(b,8)
    
    result = ""
    
    for i in range(8):
        result = result + AND_OP(bina[i],binb[i])
        
    result = binaryToHex(result,2)
    
    return result

def AND_16RR(a,b):
    a = getValueOf16(a)
    b = getValueOf16(b)

    bina = hexToBinary(a,16)
    binb = hexToBinary(b,16)
    
    result = ""
    
    for i in range(16):
        result = result + AND_OP(bina[i],binb[i])
        
    result = binaryToHex(result,4)
     
    return result

def AND_8RV(a,b):
    a = getValueOf8(a)
    b=b[:-1]
    
    bina = hexToBinary(a,8)
    binb = hexToBinary(b,8)
    
    result = ""
    
    for i in range(8):
        result = result + AND_OP(bina[i],binb[i])
        
    result = binaryToHex(result,2)
    
    return result

def AND_16RV(a,b):
    a = getValueOf16(a)
    b=b[:-1]

    bina = hexToBinary(a,16)
    binb = hexToBinary(b,16)
    
    result = ""
    
    for i in range(16):
        result = result + AND_OP(bina[i],binb[i])
        
    result = binaryToHex(result,4)
     
    return result    
#------------------------------------------------------------------------------------------------------------------


#---------------------------------------------------OR---------------------------------------------------------
def OR_8RR(a,b):
    a = getValueOf8(a)
    b = getValueOf8(b)
    
    bina = hexToBinary(a,8)
    binb = hexToBinary(b,8)
    
    result = ""
    
    for i in range(8):
        result = result + OR_OP(bina[i],binb[i])
        
    result = binaryToHex(result,2)
    
    return result

def OR_16RR(a,b):
    a = getValueOf16(a)
    b = getValueOf16(b)

    bina = hexToBinary(a,16)
    binb = hexToBinary(b,16)
    
    result = ""
    
    for i in range(16):
        result = result + OR_OP(bina[i],binb[i])
        
    result = binaryToHex(result,4)
     
    return result

def OR_8RV(a,b):
    a = getValueOf8(a)
    b=b[:-1]
    
    bina = hexToBinary(a,8)
    binb = hexToBinary(b,8)
    
    result = ""
    
    for i in range(8):
        result = result + OR_OP(bina[i],binb[i])
        
    result = binaryToHex(result,2)
    
    return result

def OR_16RV(a,b):
    a = getValueOf16(a)
    b=b[:-1]

    bina = hexToBinary(a,16)
    binb = hexToBinary(b,16)
    
    result = ""
    
    for i in range(16):
        result = result + OR_OP(bina[i],binb[i])
        
    result = binaryToHex(result,4)
     
    return result   
#------------------------------------------------------------------------------------------------------------------


#-----------------------------------------------NOT operation------------------------------------------------------
def NOT_8R(a):
    a=getValueOf8(a)
    
    bina=hexToBinary(a,8)
    
    result=""
    
    for i in range(8):
        result=result+NOT_OP(bina[i])
        
    result=binaryToHex(result,2)
    
    return result

def NOT_16R(a):
    a=getValueOf16(a)
    
    bina=hexToBinary(a,16)
    
    result=""
    
    for i in range(16):
        result=result+NOT_OP(bina[i])
        
    result=binaryToHex(result,4)
    
    return result
#------------------------------------------------------------------------------------------------------------------


#-----------------------------------------------NEG operation------------------------------------------------------
def NEG_8R(a):
    result=NOT_8R(a)
    temp='01'
    
    a,b,result=add8VV(temp,result,'0')
    
    return result
    
def NEG_16R(a):
    result=NOT_16R(a)
    temp='0001'
    
    a,b,result=add16VV(temp,result,'0')
    
    return result 
#------------------------------------------------------------------------------------------------------------------


#----------------------------------------------------XOR operation--------------------------------------------------
def XOR_8RR(a,b):
    a = getValueOf8(a)
    b = getValueOf8(b)
    
    bina = hexToBinary(a,8)
    binb = hexToBinary(b,8)
    
    result = ""
    
    for i in range(8):
        result = result + XOR_OP(bina[i],binb[i])
        
    result = binaryToHex(result,2)
    
    return result

def XOR_16RR(a,b):
    a = getValueOf16(a)
    b = getValueOf16(b)

    bina = hexToBinary(a,16)
    binb = hexToBinary(b,16)
    
    result = ""
    
    for i in range(16):
        result = result + XOR_OP(bina[i],binb[i])
        
    result = binaryToHex(result,4)
     
    return result

def XOR_8RV(a,b):
    a = getValueOf8(a)
    b=b[:-1]
    
    bina = hexToBinary(a,8)
    binb = hexToBinary(b,8)
    
    result = ""
    
    for i in range(8):
        result = result + XOR_OP(bina[i],binb[i])
        
    result = binaryToHex(result,2)
    
    return result

def XOR_16RV(a,b):
    a = getValueOf16(a)
    b=b[:-1]

    bina = hexToBinary(a,16)
    binb = hexToBinary(b,16)
    
    result = ""
    
    for i in range(16):
        result = result + XOR_OP(bina[i],binb[i])
        
    result = binaryToHex(result,4)
     
    return result
#-------------------------------------------------------------------------------------------------------------------

#----------------------------------------------------Left Shift operation--------------------------------------------------
def SHL_8RR(a,b):
    first = getValueOf8(a)             # Getting value of Register
    second = getValueOf8(b)            

    first = hexToBinary(first,8)          # Converting HEX to Binary
    second = hexToBinary(second,8)

    temp = first
    
    first = int(first,base=2)              # Converting Binary to Decimal
    second = int(second,base=2)
    
    carry = temp[min(second-1,len(temp)-1)]
    
    if second > len(temp):
        carry = 0
    
    first = first << second               # Shifting value

    first = bin(first)[-8:]              # Converting Decimal to Binary

    first = binaryToHex(first,2)         # Converting Binary to HEX
    
    return carry,first

def SHL_16RR(a,b):
    first = getValueOf16(a)             # Getting value of Register
    second = getValueOf16(b)            

    first = hexToBinary(first,16)          # Converting HEX to Binary
    second = hexToBinary(second,16)
    
    temp = first
    
    first = int(first,base=2)              # Converting Binary to Decimal
    second = int(second,base=2)
    
    carry = temp[min(second-1,len(temp)-1)]
    
    if second > len(temp):
        carry = 0
    
    first = first << second               # Shifting value

    first = bin(first)[-16:]              # Converting Decimal to Binary

    first = binaryToHex(first,4)         # Converting Binary to HEX
    
    return carry,first

def SHL_8RV(a,b):
    first = getValueOf8(a)             # Getting value of Register 
    b=b[:-1]
 
    first = hexToBinary(first,8)          # Converting HEX to Binary
    second = hexToBinary(b,8)

    temp = first
    
    first = int(first,base=2)              # Converting Binary to Decimal
    second = int(second,base=2)
    
    carry = temp[min(second-1,len(temp)-1)]
    
    if second > len(temp):
        carry = 0
    
    first = first << second               # Shifting value

    first = bin(first)[-8:]              # Converting Decimal to Binary

    first = binaryToHex(first,2)         # Converting Binary to HEX
    
    return carry,first

def SHL_16RV(a,b):
    first = getValueOf16(a)             # Getting value of Register 
    b=b[:-1]
 
    first = hexToBinary(first,16)          # Converting HEX to Binary
    second = hexToBinary(b,16)

    temp = first
    
    first = int(first,base=2)              # Converting Binary to Decimal
    second = int(second,base=2)
    
    carry = temp[min(second-1,len(temp)-1)]
    
    if second > len(temp):
        carry = 0

    first = first << second               # Shifting value

    first = bin(first)[-16:]              # Converting Decimal to Binary

    first = binaryToHex(first,4)         # Converting Binary to HEX
    
    return carry,first
#-------------------------------------------------------------------------------------------------------------------

#----------------------------------------------------Right Shift operation--------------------------------------------------
def SHR(a,b,n):
    first = hexToBinary(a,n)
    second = hexToBinary(b,n)
    
    second = int(second,base=2)
    
    shift_str=''
    for i in range(second):
        shift_str += '0'
    
    first = shift_str + first
    finalVal = first[:n]
    carry=first[n]
    
    finalVal = binaryToHex(finalVal,n/4)
    return carry,finalVal

def SHR_8RR(a,b):
    a = getValueOf8(a)
    b = getValueOf8(b)
    carry,finVal = SHR(a,b,8)
    return carry,finVal

def SHR_8RV(a,b):
    a = getValueOf8(a)
    b = b[:-1]
    carry,finVal = SHR(a,b,8)
    return carry,finVal

def SHR_16RR(a,b):
    a = getValueOf16(a)
    b = getValueOf16(b)
    carry,finVal = SHR(a,b,16)
    return carry,finVal

def SHR_16RV(a,b):
    a = getValueOf16(a)
    b = b[:-1]
    carry,finVal = SHR(a,b,16)
    return carry,finVal
#-------------------------------------------------------------------------------------------------------------------

#----------------------------------------------------Right Shift Arithmetic Operation--------------------------------------------------
def SAR(a,b,n):
    first = hexToBinary(a,n)
    second = hexToBinary(b,n)
    
    second = int(second,base=2)
    temp = first[0]
    shift_str=''
    for i in range(second):
        shift_str += temp
    
    first = shift_str + first
    finalVal = first[:n]
    carry=first[n]
    
    finalVal = binaryToHex(finalVal,n/4)
    return carry,finalVal

def SAR_8RR(a,b):
    a = getValueOf8(a)
    b = getValueOf8(b)
    carry,finVal = SAR(a,b,8)
    return carry,finVal

def SAR_8RV(a,b):
    a = getValueOf8(a)
    b = b[:-1]
    carry,finVal = SAR(a,b,8)
    return carry,finVal

def SAR_16RR(a,b):
    a = getValueOf16(a)
    b = getValueOf16(b)
    carry,finVal = SAR(a,b,16)
    return carry,finVal

def SAR_16RV(a,b):
    a = getValueOf16(a)
    b = b[:-1]
    carry,finVal = SAR(a,b,16)
    return carry,finVal
#-------------------------------------------------------------------------------------------------------------------

#----------------------------------------------------Rotate Left Operation-------------------------------
def ROL(a,b,n):
    first = hexToBinary(a,n)
    second = hexToBinary(b,n)
    
    second = int(second,base=2)
    pos = second % n
    pos = pos
    finVal = ''
    for i in range(n):
        finVal = finVal + first[pos]
        pos = pos + 1
        pos = pos % (n)
    
    carry = finVal[n-1]
    finVal = binaryToHex(finVal,n/4)
    return carry,finVal

def ROL_8RR(a,b):
    a = getValueOf8(a)
    b = getValueOf8(b)
    carry,finVal = ROL(a,b,8)
    return carry,finVal

def ROL_8RV(a,b):
    a = getValueOf8(a)
    b = b[:-1]
    carry,finVal = ROL(a,b,8)
    return carry,finVal

def ROL_16RR(a,b):
    a = getValueOf16(a)
    b = getValueOf16(b)
    carry,finVal = ROL(a,b,16)
    return carry,finVal

def ROL_16RV(a,b):
    a = getValueOf16(a)
    b = b[:-1]
    carry,finVal = ROL(a,b,16)
    return carry,finVal
#-------------------------------------------------------------------------------------------------------------------

#----------------------------------------------------Rotate Right Operation-------------------------------
def ROR(a,b,n):
    first = hexToBinary(a,n)
    second = hexToBinary(b,n)
    
    second = int(second,base=2)
    second=second%n
    
    temp_str=first[-second:]
    
    first = temp_str + first
    
    finVal=first[:n]
    carry = finVal[0]
    
    finVal = binaryToHex(finVal,n/4)
    
    return carry,finVal

def ROR_8RR(a,b):
    a = getValueOf8(a)
    b = getValueOf8(b)
    carry,finVal = ROR(a,b,8)
    return carry,finVal

def ROR_8RV(a,b):
    a = getValueOf8(a)
    b = b[:-1]
    carry,finVal = ROR(a,b,8)
    return carry,finVal

def ROR_16RR(a,b):
    a = getValueOf16(a)
    b = getValueOf16(b)
    carry,finVal = ROR(a,b,16)
    return carry,finVal

def ROR_16RV(a,b):
    a = getValueOf16(a)
    b = b[:-1]
    carry,finVal = ROR(a,b,16)
    return carry,finVal
#-------------------------------------------------------------------------------------------------------------------

#---------------------------------------Rotate Right with Carry----------------------------------------------
def RCR_8RR(a,b):
    a = getValueOf8(a)
    b = getValueOf8(b)
    a = FLAG_INFO['CF'] + a
    val = ROL(a,b,9)
    carry,finVal = val[0], val[1:]
    return carry,finVal

def RCR_8RV(a,b):
    a = getValueOf8(a)
    b = b[:-1]
    a = FLAG_INFO['CF'] + a
    val = ROL(a,b,9)
    carry,finVal = val[0], val[1:]
    return carry,finVal

def RCR_16RR(a,b):
    a = getValueOf16(a)
    b = getValueOf16(b)
    a = FLAG_INFO['CF'] + a
    val = ROL(a,b,17)
    carry,finVal = val[0], val[1:]
    return carry,finVal

def RCR_16RV(a,b):
    a = getValueOf16(a)
    b = b[:-1]
    a = FLAG_INFO['CF'] + a
    val = ROL(a,b,17)
    carry,finVal = val[0], val[1:]
    return carry,finVal
#-------------------------------------------------------------------------------------------------------------------

#---------------------------------------Rotate Left with Carry----------------------------------------------
def RCL_8RR(a,b):
    a = getValueOf8(a)
    b = getValueOf8(b)
    a = FLAG_INFO['CF'] + a
    val = ROL(a,b,9)
    carry,finVal = val[0], val[1:]
    return carry,finVal

def RCL_8RV(a,b):
    a = getValueOf8(a)
    b = b[:-1]
    a = FLAG_INFO['CF'] + a
    val = ROL(a,b,9)
    carry,finVal = val[0], val[1:]
    return carry,finVal

def RCL_16RR(a,b):
    a = getValueOf16(a)
    b = getValueOf16(b)
    a = FLAG_INFO['CF'] + a
    val = ROL(a,b,17)
    carry,finVal = val[0], val[1:]
    return carry,finVal

def RCL_16RV(a,b):
    a = getValueOf16(a)
    b = b[:-1]
    a = FLAG_INFO['CF'] + a
    val = ROL(a,b,17)
    carry,finVal = val[0], val[1:]
    return carry,finVal
#-------------------------------------------------------------------------------------------------------------------

#-------------------------------------------------------MULTIPY---------------------------------------------------
def mul(a,b,n):
    # converting it to Binary
    a = hexToBinary(a,n)
    b = hexToBinary(b,n)
    # converting value to decimal
    a = int(a,base=2)
    b = int(b,base=2)

    # Performing Multiplication Operation
    res = a*b;

    # converting decimal to binary
    res = bin(res)
    # converting binary to HEX
    res = binaryToHex(res,2*n)

    return res[0:n],res[n:]

def mul8(b):
    a = getValueOf8('AL')
    b = getValueOf8(b)
    ah,al = mul(a,b,8)
    return ah,al

def mul16(b):
    a = getValueOf16('AX')
    b = getValueOf16(b)
    dx,ax = mul(a,b,16)
    return dx,ax
#-------------------------------------------------------------------------------------------------------------------

#-------------------------------------------------------DIVISION---------------------------------------------------
def div(a,b,n):
    # converting it to Binary
    a = hexToBinary(a,2*n)
    b = hexToBinary(b,n)
    # converting value to decimal
    a = int(a,base=2)
    b = int(b,base=2)

    # Performing Multiplication Operation
    quot = a / b;
    rem = a % b

    # converting decimal to binary
    quot = bin(quot)
    rem = bin(rem)
    # converting binary to HEX
    quot = binaryToHex(quot,n)
    rem = binaryToHex(rem,n)

    return rem,quot

def div8(b):
    a = getValueOf8('AX')
    b = getValueOf8(b)
    ah,al = div(a,b,8)
    return ah,al

def div16(b):
    a = getValueOf16('DX') + getValueOf16('AX')
    b = getValueOf16(b)
    dx,ax = div(a,b,16)
    return dx,ax
#-------------------------------------------------------------------------------------------------------------------

def cbw():
    a = getValueOf8('AL')
    a = hexToBinary(a,8)
    s = ''
    for i in range(8):
        s = s + a[0]
    return s

def cwd():
    a = getValueOf16('AX')
    a = hexToBinary(a,16)
    s = ''
    for i in range(16):
        s = s + a[0]
    return s

#-------------------------------------------------------------------------------------------------------------------
def HashLabels():
    file = open('Assembly_code.txt','r')
    code = file.readlines()
    for i in range(len(code)):
        if code[i].find(':') != -1 :
            pos = code[i].find(':')
            LABEL[code[i][:pos]] = i

def Reg_update():
    global prevCarry
    c2.markdown("<h4 style='text-align: left; color: white;'>REGISTERS :</h1>", unsafe_allow_html=True)
    
    main_f=open("Assembly_code.txt",'r')
    code=main_f.readlines()
    
    for i in range(len(code)):
        a=re.split(',| ',code[i])
        a = list(filter(None, a))             # Remove null strings from list
        
        a=[x.upper() for x in a]
        
        if len(a)==3:
            a[2]=a[2].strip()                   # Length of instruction can be of 2 or 3
        else:
            a[1]=a[1].strip()

        # Instructions Implemented
        if a[0]=="ADD":
            if a[1] in Registers16 and a[2] in Registers16:
                carry,auxiCarry,sumV = add16RR(a[1],a[2],'0')
                update_16(a[1],sumV)
                FLAG_INFO['SF'] = hexToBinary(sumV,16)[15]
                FLAG_INFO['CF'] = carry
                FLAG_INFO['AC'] = auxiCarry
                FLAG_INFO['ZF'] = '1' if int(sumV,base=16)==0 else '0'
                FLAG_INFO['OF'] = XOR_OP(carry,prevCarry)
            elif a[1] in Registers16:
                carry,auxiCarry,sumV = add16RV(a[1],a[2],'0')
                update_16(a[1],sumV)
                FLAG_INFO['SF'] = hexToBinary(sumV,16)[15]
                FLAG_INFO['CF'] = carry
                FLAG_INFO['AC'] = auxiCarry
                FLAG_INFO['ZF'] = '1' if int(sumV,base=16)==0 else '0'
                FLAG_INFO['OF'] = XOR_OP(carry,prevCarry)
            elif a[1] in Registers8 and a[2] in Registers8:
                carry,auxiCarry,sumV = add8RR(a[1],a[2],'0')
                update_8(a[1],sumV)
                FLAG_INFO['SF'] = hexToBinary(sumV,8)[7]
                FLAG_INFO['CF'] = carry
                FLAG_INFO['AC'] = auxiCarry
                FLAG_INFO['ZF'] = '1' if int(sumV,base=16)==0 else '0'
                FLAG_INFO['OF'] = XOR_OP(carry,prevCarry)
            else:
                carry,auxiCarry,sumV = add8RV(a[1],a[2],'0')
                update_8(a[1],sumV)
                FLAG_INFO['SF'] = hexToBinary(sumV,8)[7]
                FLAG_INFO['CF'] = carry
                FLAG_INFO['AC'] = auxiCarry
                FLAG_INFO['ZF'] = '1' if int(sumV,base=16)==0 else '0'
                FLAG_INFO['OF'] = XOR_OP(carry,prevCarry)
             
        elif a[0]=="SUB":
            if a[1] in Registers16 and a[2] in Registers16:
                carry,auxiCarry,sumV = sub16RR(a[1],a[2],'0')
                update_16(a[1],sumV)
                FLAG_INFO['SF'] = hexToBinary(sumV,16)[15]
                FLAG_INFO['CF'] = carry
                FLAG_INFO['AC'] = auxiCarry
                FLAG_INFO['ZF'] = '1' if int(sumV,base=16)==0 else '0'
                FLAG_INFO['OF'] = XOR_OP(carry,prevCarry)
            elif a[1] in Registers16:
                carry,auxiCarry,sumV = sub16RV(a[1],a[2],'0')
                update_16(a[1],sumV)
                FLAG_INFO['SF'] = hexToBinary(sumV,16)[15]
                FLAG_INFO['CF'] = carry
                FLAG_INFO['AC'] = auxiCarry
                FLAG_INFO['ZF'] = '1' if int(sumV,base=16)==0 else '0'
                FLAG_INFO['OF'] = XOR_OP(carry,prevCarry)
            elif a[1] in Registers8 and a[2] in Registers8:
                carry,auxiCarry,sumV = sub8RR(a[1],a[2],'0')
                update_8(a[1],sumV)
                FLAG_INFO['SF'] = hexToBinary(sumV,8)[7]
                FLAG_INFO['CF'] = carry
                FLAG_INFO['AC'] = auxiCarry
                FLAG_INFO['ZF'] = '1' if int(sumV,base=16)==0 else '0'
                FLAG_INFO['OF'] = XOR_OP(carry,prevCarry)
            else:
                carry,auxiCarry,sumV = sub8RV(a[1],a[2],'0')
                update_8(a[1],sumV)
                FLAG_INFO['SF'] = hexToBinary(sumV,8)[7]
                FLAG_INFO['CF'] = carry
                FLAG_INFO['AC'] = auxiCarry
                FLAG_INFO['ZF'] = '1' if int(sumV,base=16)==0 else '0'
                FLAG_INFO['OF'] = XOR_OP(carry,prevCarry)
        
        elif a[0]=="ADC":
            if a[1] in Registers16 and a[2] in Registers16:
                carry,auxiCarry,sumV = add16RR(a[1],a[2],FLAG_INFO['CF'])
                update_16(a[1],sumV)
                FLAG_INFO['SF'] = hexToBinary(sumV,16)[15]
                FLAG_INFO['CF'] = carry
                FLAG_INFO['AC'] = auxiCarry
                FLAG_INFO['ZF'] = '1' if int(sumV,base=16)==0 else '0'
                FLAG_INFO['OF'] = XOR_OP(carry,prevCarry)
            elif a[1] in Registers16:
                carry,auxiCarry,sumV = add16RV(a[1],a[2],FLAG_INFO['CF'])
                update_16(a[1],sumV)
                FLAG_INFO['SF'] = hexToBinary(sumV,16)[15]
                FLAG_INFO['CF'] = carry
                FLAG_INFO['AC'] = auxiCarry
                FLAG_INFO['ZF'] = '1' if int(sumV,base=16)==0 else '0'
                FLAG_INFO['OF'] = XOR_OP(carry,prevCarry)
            elif a[1] in Registers8 and a[2] in Registers8:
                carry,auxiCarry,sumV = add8RR(a[1],a[2],FLAG_INFO['CF'])
                update_8(a[1],sumV)
                FLAG_INFO['SF'] = hexToBinary(sumV,8)[7]
                FLAG_INFO['CF'] = carry
                FLAG_INFO['AC'] = auxiCarry
                FLAG_INFO['ZF'] = '1' if int(sumV,base=16)==0 else '0'
                FLAG_INFO['OF'] = XOR_OP(carry,prevCarry)
            else:
                carry,auxiCarry,sumV = add8RV(a[1],a[2],FLAG_INFO['CF'])
                update_8(a[1],sumV)
                FLAG_INFO['SF'] = hexToBinary(sumV,8)[7]
                FLAG_INFO['CF'] = carry
                FLAG_INFO['AC'] = auxiCarry
                FLAG_INFO['ZF'] = '1' if int(sumV,base=16)==0 else '0'
                FLAG_INFO['OF'] = XOR_OP(carry,prevCarry)
        
        elif a[0]=="SBB":
            if a[1] in Registers16 and a[2] in Registers16:
                carry,auxiCarry,sumV = sub16RR(a[1],a[2],FLAG_INFO['CF'])
                update_16(a[1],sumV)
                FLAG_INFO['SF'] = hexToBinary(sumV,16)[15]
                FLAG_INFO['CF'] = carry
                FLAG_INFO['AC'] = auxiCarry
                FLAG_INFO['ZF'] = '1' if int(sumV,base=16)==0 else '0'
                FLAG_INFO['OF'] = XOR_OP(carry,prevCarry)
            elif a[1] in Registers16:
                carry,auxiCarry,sumV = sub16RV(a[1],a[2],FLAG_INFO['CF'])
                update_16(a[1],sumV)
                FLAG_INFO['SF'] = hexToBinary(sumV,16)[15]
                FLAG_INFO['CF'] = carry
                FLAG_INFO['AC'] = auxiCarry
                FLAG_INFO['ZF'] = '1' if int(sumV,base=16)==0 else '0'
                FLAG_INFO['OF'] = XOR_OP(carry,prevCarry)
            elif a[1] in Registers8 and a[2] in Registers8:
                carry,auxiCarry,sumV = sub8RR(a[1],a[2],FLAG_INFO['CF'])
                update_8(a[1],sumV)
                FLAG_INFO['SF'] = hexToBinary(sumV,8)[7]
                FLAG_INFO['CF'] = carry
                FLAG_INFO['AC'] = auxiCarry
                FLAG_INFO['ZF'] = '1' if int(sumV,base=16)==0 else '0'
                FLAG_INFO['OF'] = XOR_OP(carry,prevCarry)
            else:
                carry,auxiCarry,sumV = sub8RV(a[1],a[2],FLAG_INFO['CF'])
                update_8(a[1],sumV)
                FLAG_INFO['SF'] = hexToBinary(sumV,8)[7]
                FLAG_INFO['CF'] = carry
                FLAG_INFO['AC'] = auxiCarry
                FLAG_INFO['ZF'] = '1' if int(sumV,base=16)==0 else '0'
                FLAG_INFO['OF'] = XOR_OP(carry,prevCarry)
                
        elif a[0]=="INC":
            if a[1] in Registers16:
                carry,auxiCarry,sumV = add16RV(a[1],"0001H",'0')
                FLAG_INFO['SF'] = hexToBinary(sumV,16)[15]
                update_16(a[1],sumV)
                FLAG_INFO['CF'] = carry
                FLAG_INFO['AC'] = auxiCarry
                FLAG_INFO['ZF'] = '1' if int(sumV,base=16)==0 else '0'
                FLAG_INFO['OF'] = XOR_OP(carry,prevCarry)
            else:
                carry,auxiCarry,sumV = add8RV(a[1],"01H",'0')
                update_8(a[1],sumV)
                FLAG_INFO['SF'] = hexToBinary(sumV,8)[7]
                FLAG_INFO['CF'] = carry
                FLAG_INFO['AC'] = auxiCarry
                FLAG_INFO['ZF'] = '1' if int(sumV,base=16)==0 else '0'
                FLAG_INFO['OF'] = XOR_OP(carry,prevCarry)
        
        elif a[0]=="DEC":
            if a[1] in Registers16:
                carry,auxiCarry,sumV = sub16RV(a[1],"0001H",'0')
                update_16(a[1],sumV)
                FLAG_INFO['SF'] = hexToBinary(sumV,16)[15]
                FLAG_INFO['CF'] = carry
                FLAG_INFO['AC'] = auxiCarry
                FLAG_INFO['ZF'] = '1' if int(sumV,base=16)==0 else '0'
                FLAG_INFO['OF'] = XOR_OP(carry,prevCarry)
            else:
                carry,auxiCarry,sumV = sub8RV(a[1],"01H",'0')
                update_8(a[1],sumV)
                FLAG_INFO['SF'] = hexToBinary(sumV,8)[7]
                FLAG_INFO['CF'] = carry
                FLAG_INFO['AC'] = auxiCarry
                FLAG_INFO['ZF'] = '1' if int(sumV,base=16)==0 else '0'
                FLAG_INFO['OF'] = XOR_OP(carry,prevCarry)
        
        elif a[0]=="MOV":
            if a[1] in Registers16 and a[2] in Registers16:
                mov16RR(a[1],a[2])
            elif a[1] in Registers16:
                mov16RV(a[1],a[2])
            elif a[1] in Registers8 and a[2] in Registers8:
                mov8RR(a[1],a[2])
            elif a[1] in Registers8:
                mov8RV(a[1],a[2])
        
        elif a[0]=="CLC":
            FLAG_INFO['CF'] = '0'
          
        elif a[0]=="STC":
            FLAG_INFO['CF']='1'
        
        elif a[0]=="CMC":
            if FLAG_INFO['CF']=='1':
                FLAG_INFO['CF'] = '0'
            else:
                FLAG_INFO['CF'] = '1'

        elif a[0]=="STD":
            FLAG_INFO['DF'] = '1'
        
        elif a[0]=="CLD":
            FLAG_INFO['DF'] = '0'

        elif a[0]=="STI":
            FLAG_INFO['IF'] = '1'
        
        elif a[0]=='CLI':
            FLAG_INFO['IF'] = '0'
               
        elif a[0]=="AND":
            if a[1] in Registers16 and a[2] in Registers16:
                result = AND_16RR(a[1],a[2])
                update_16(a[1],result)
                FLAG_INFO['CF'] = '0'
                FLAG_INFO['OF'] = '0'
                FLAG_INFO['SF'] = hexToBinary(result,16)[15]
                FLAG_INFO['ZF'] = '1' if int(result,base=16)==0 else '0'
            elif a[1] in Registers16:
                result = AND_16RV(a[1],a[2])
                update_16(a[1],result)
                FLAG_INFO['CF'] = '0'
                FLAG_INFO['OF'] = '0'
                FLAG_INFO['SF'] = hexToBinary(result,16)[15]
                FLAG_INFO['ZF'] = '1' if int(result,base=16)==0 else '0'
            elif a[1] in Registers8 and a[2] in Registers8:
                result = AND_8RR(a[1],a[2])
                update_8(a[1],result)
                FLAG_INFO['CF'] = '0'
                FLAG_INFO['OF'] = '0'
                FLAG_INFO['SF'] = hexToBinary(result,8)[7]
                FLAG_INFO['ZF'] = '1' if int(result,base=16)==0 else '0'
            else:
                result = AND_8RV(a[1],a[2])
                update_8(a[1],result)
                FLAG_INFO['CF'] = '0'
                FLAG_INFO['OF'] = '0'
                FLAG_INFO['SF'] = hexToBinary(result,8)[7]
                FLAG_INFO['ZF'] = '1' if int(result,base=16)==0 else '0'
            
        elif a[0]=='OR':
            if a[1] in Registers16 and a[2] in Registers16:
                result = OR_16RR(a[1],a[2])
                update_16(a[1],result)
                FLAG_INFO['CF'] = '0'
                FLAG_INFO['OF'] = '0'
                FLAG_INFO['SF'] = hexToBinary(result,16)[15]
                FLAG_INFO['ZF'] = '1' if int(result,base=16)==0 else '0'
            elif a[1] in Registers16:
                result = OR_16RV(a[1],a[2])
                update_16(a[1],result)
                FLAG_INFO['CF'] = '0'
                FLAG_INFO['OF'] = '0'
                FLAG_INFO['SF'] = hexToBinary(result,16)[15]
                FLAG_INFO['ZF'] = '1' if int(result,base=16)==0 else '0'
            elif a[1] in Registers8 and a[2] in Registers8:
                result = OR_8RR(a[1],a[2])
                update_8(a[1],result)
                FLAG_INFO['CF'] = '0'
                FLAG_INFO['OF'] = '0'
                FLAG_INFO['SF'] = hexToBinary(result,8)[7]
                FLAG_INFO['ZF'] = '1' if int(result,base=16)==0 else '0'
            else:
                result = OR_8RV(a[1],a[2])
                update_8(a[1],result)
                FLAG_INFO['CF'] = '0'
                FLAG_INFO['OF'] = '0'
                FLAG_INFO['SF'] = hexToBinary(result,8)[7]
                FLAG_INFO['ZF'] = '1' if int(result,base=16)==0 else '0'
               
        elif a[0]=='NOT':
            if a[1] in Registers16:
                result=NOT_16R(a[1])
                update_16(a[1],result)
            else:
                result=NOT_8R(a[1])
                update_8(a[1],result)
                
        elif a[0]=='XOR':
            if a[1] in Registers16 and a[2] in Registers16:
                result = XOR_16RR(a[1],a[2])
                update_16(a[1],result)
                FLAG_INFO['CF'] = '0'
                FLAG_INFO['OF'] = '0'
                FLAG_INFO['SF'] = hexToBinary(result,16)[15]
                FLAG_INFO['ZF'] = '1' if int(result,base=16)==0 else '0'
            elif a[1] in Registers16:
                result = XOR_16RV(a[1],a[2])
                update_16(a[1],result)
                FLAG_INFO['CF'] = '0'
                FLAG_INFO['OF'] = '0'
                FLAG_INFO['SF'] = hexToBinary(result,16)[15]
                FLAG_INFO['ZF'] = '1' if int(result,base=16)==0 else '0'
            elif a[1] in Registers8 and a[2] in Registers8:
                result = XOR_8RR(a[1],a[2])
                update_8(a[1],result)
                FLAG_INFO['CF'] = '0'
                FLAG_INFO['OF'] = '0'
                FLAG_INFO['SF'] = hexToBinary(result,8)[7]
                FLAG_INFO['ZF'] = '1' if int(result,base=16)==0 else '0'
            else:
                result = XOR_8RV(a[1],a[2])
                update_8(a[1],result)
                FLAG_INFO['CF'] = '0'
                FLAG_INFO['OF'] = '0'
                FLAG_INFO['SF'] = hexToBinary(result,8)[7]
                FLAG_INFO['ZF'] = '1' if int(result,base=16)==0 else '0'
        
        elif a[0]=='NEG':
            if a[1] in Registers16:
                result=NEG_16R(a[1])
                update_16(a[1],result)
            else:
                result=NEG_8R(a[1])
                update_8(a[1],result)
                
        elif a[0]=="CMP":
            if a[1] in Registers16 and a[2] in Registers16:
                carry,auxiCarry,sumV = sub16RR(a[1],a[2],'0')
                FLAG_INFO['SF'] = hexToBinary(sumV,16)[15]
                FLAG_INFO['CF'] = carry
                FLAG_INFO['AC'] = auxiCarry
                FLAG_INFO['ZF'] = '1' if int(sumV,base=16)==0 else '0'
                FLAG_INFO['OF'] = XOR_OP(carry,prevCarry)
            elif a[1] in Registers16:
                carry,auxiCarry,sumV = sub16RV(a[1],a[2],'0')
                FLAG_INFO['SF'] = hexToBinary(sumV,16)[15]
                FLAG_INFO['CF'] = carry
                FLAG_INFO['AC'] = auxiCarry
                FLAG_INFO['ZF'] = '1' if int(sumV,base=16)==0 else '0'
                FLAG_INFO['OF'] = XOR_OP(carry,prevCarry)
            elif a[1] in Registers8 and a[2] in Registers8:
                carry,auxiCarry,sumV = sub8RR(a[1],a[2],'0')
                FLAG_INFO['SF'] = hexToBinary(sumV,8)[7]
                FLAG_INFO['CF'] = carry
                FLAG_INFO['AC'] = auxiCarry
                FLAG_INFO['ZF'] = '1' if int(sumV,base=16)==0 else '0'
                FLAG_INFO['OF'] = XOR_OP(carry,prevCarry)
            else:
                carry,auxiCarry,sumV = sub8RV(a[1],a[2],'0')
                FLAG_INFO['SF'] = hexToBinary(sumV,8)[7]
                FLAG_INFO['CF'] = carry
                FLAG_INFO['AC'] = auxiCarry
                FLAG_INFO['ZF'] = '1' if int(sumV,base=16)==0 else '0'
                FLAG_INFO['OF'] = XOR_OP(carry,prevCarry)
                
        elif a[0]=="XCHG":
            if a[1] in Registers16 and a[2] in Registers16:
                temp1=getValueOf16(a[1])
                temp2=getValueOf16(a[2])
                update_16(a[1],temp2)
                update_16(a[2],temp1)  
            elif a[1] in Registers8 and a[2] in Registers8:
                temp1=getValueOf8(a[1])
                temp2=getValueOf8(a[2])
                update_8(a[1],temp2)
                update_8(a[2],temp1)
                
        elif a[0]=="SHL" or a[0]=='SAL':
            if a[1] in Registers16 and a[2] in Registers16:
                carry,result=SHL_16RR(a[1],a[2])
                update_16(a[1],result)
                FLAG_INFO['CF'] = carry 
            elif a[1] in Registers16:
                carry,result=SHL_16RV(a[1],a[2])
                update_16(a[1],result)
                FLAG_INFO['CF'] = carry
            elif a[1] in Registers8 and a[2] in Registers8:
                carry,result=SHL_8RR(a[1],a[2])
                update_8(a[1],result)
                FLAG_INFO['CF'] = carry
            else:
                carry,result=SHL_8RV(a[1],a[2])
                update_8(a[1],result)
                FLAG_INFO['CF'] = carry
                
        elif a[0]=="SHR":
            if a[1] in Registers16 and a[2] in Registers16:
                carry,result=SHR_16RR(a[1],a[2])
                update_16(a[1],result)
                FLAG_INFO['CF'] = carry 
            elif a[1] in Registers16:
                carry,result=SHR_16RV(a[1],a[2])
                update_16(a[1],result)
                FLAG_INFO['CF'] = carry
            elif a[1] in Registers8 and a[2] in Registers8:
                carry,result=SHR_8RR(a[1],a[2])
                update_8(a[1],result)
                FLAG_INFO['CF'] = carry
            else:
                carry,result=SHR_8RV(a[1],a[2])
                update_8(a[1],result)
                FLAG_INFO['CF'] = carry
                
        elif a[0]=="SAR":
            if a[1] in Registers16 and a[2] in Registers16:
                carry,result=SAR_16RR(a[1],a[2])
                update_16(a[1],result)
                FLAG_INFO['CF'] = carry 
            elif a[1] in Registers16:
                carry,result=SAR_16RV(a[1],a[2])
                update_16(a[1],result)
                FLAG_INFO['CF'] = carry
            elif a[1] in Registers8 and a[2] in Registers8:
                carry,result=SAR_8RR(a[1],a[2])
                update_8(a[1],result)
                FLAG_INFO['CF'] = carry
            else:
                carry,result=SAR_8RV(a[1],a[2])
                update_8(a[1],result)
                FLAG_INFO['CF'] = carry
                
        elif a[0]=="ROL":
            if a[1] in Registers16 and a[2] in Registers16:
                carry,result=ROL_16RR(a[1],a[2])
                update_16(a[1],result)
                FLAG_INFO['CF'] = carry 
            elif a[1] in Registers16:
                carry,result=ROL_16RV(a[1],a[2])
                update_16(a[1],result)
                FLAG_INFO['CF'] = carry
            elif a[1] in Registers8 and a[2] in Registers8:
                carry,result=ROL_8RR(a[1],a[2])
                update_8(a[1],result)
                FLAG_INFO['CF'] = carry
            else:
                carry,result=ROL_8RV(a[1],a[2])
                update_8(a[1],result)
                FLAG_INFO['CF'] = carry
                
        elif a[0]=="ROR":
            if a[1] in Registers16 and a[2] in Registers16:
                carry,result=ROR_16RR(a[1],a[2])
                update_16(a[1],result)
                FLAG_INFO['CF'] = carry 
                FLAG_INFO['SF'] = result[0]
            elif a[1] in Registers16:
                carry,result=ROR_16RV(a[1],a[2])
                update_16(a[1],result)
                FLAG_INFO['SF'] = result[0]
                FLAG_INFO['CF'] = carry
            elif a[1] in Registers8 and a[2] in Registers8:
                carry,result=ROR_8RR(a[1],a[2])
                update_8(a[1],result)
                FLAG_INFO['SF'] = result[0]
                FLAG_INFO['CF'] = carry
            else:
                carry,result=ROR_8RV(a[1],a[2])
                update_8(a[1],result)
                FLAG_INFO['SF'] = result[0]
                FLAG_INFO['CF'] = carry
        
        elif a[0]=="RCR":
            if a[1] in Registers16 and a[2] in Registers16:
                carry,result=RCR_16RR(a[1],a[2])
                update_16(a[1],result)
                FLAG_INFO['CF'] = carry 
            elif a[1] in Registers16:
                carry,result=RCR_16RV(a[1],a[2])
                update_16(a[1],result)
                FLAG_INFO['CF'] = carry
            elif a[1] in Registers8 and a[2] in Registers8:
                carry,result=RCR_8RR(a[1],a[2])
                update_8(a[1],result)
                FLAG_INFO['CF'] = carry
            else:
                carry,result=RCR_8RV(a[1],a[2])
                update_8(a[1],result)
                FLAG_INFO['CF'] = carry
        
        elif a[0]=="RCL":
            if a[1] in Registers16 and a[2] in Registers16:
                carry,result=RCL_16RR(a[1],a[2])
                update_16(a[1],result)
                FLAG_INFO['CF'] = carry 
            elif a[1] in Registers16:
                carry,result=RCL_16RV(a[1],a[2])
                update_16(a[1],result)
                FLAG_INFO['CF'] = carry
            elif a[1] in Registers8 and a[2] in Registers8:
                carry,result=RCL_8RR(a[1],a[2])
                update_8(a[1],result)
                FLAG_INFO['CF'] = carry
            else:
                carry,result=RCL_8RV(a[1],a[2])
                update_8(a[1],result)
                FLAG_INFO['CF'] = carry              

        elif a[0]=='MUL':
            if a[1] in Registers16:
                dx,ax = mul16(a[1])
                update_16('DX',dx)
                update_16('AX',ax)
            elif a[1] in Registers8:
                ah,al = mul8(a[1])
                update_8('AH',ah)
                update_8('AL',al)

        elif a[0]=='DIV':
            if a[1] in Registers16:
                dx,ax = div16(a[1])
                update_16('DX',dx)
                update_16('AX',ax)
            elif a[1] in Registers8:
                ah,al = div8(a[1])
                update_8('AH',ah)
                update_8('AL',al)

        elif a[0]=='CBW':
            val = cbw()
            update_8('AH',val)
        
        elif a[0]=='CWD':
            val = cwd()
            update_16('DX',val)

    Registers = pd.DataFrame(REGISTERS_INFO,index=['|'])
    st.table(Registers)
    
    c2.markdown("<h4 style='text-align: left; color: white;'>PSW :</h1>", unsafe_allow_html=True)
    
    Flags = pd.DataFrame(FLAG_INFO,index=['|'])
    st.table(Flags)

#-------------------------------------------------------------------------------------------------------------------
with c1:
    code=st.text_area('Code :',height=500)
    Compile=st.button("Compile")
    
    if Compile:
        file=open("Assembly_code.txt","w")
        file.write(code)
        file.close()
        HashLabels()

with c2:
   
    c2.markdown("<h2 style='text-align: center; color: white;'>Overview :</h1>", unsafe_allow_html=True)
    
    Regis=c2.button('REGISTER INFO')
    
    if Regis:
        Reg_update()
    
    
st.header('Terminologies :')

display1={'OF':'Overflow Flag','DF':'Direction Flag','IF':'Interrupt Flag','TF':'Trap Flag','SF':'Sign Flag'}
display2={'ZF':'Zero Flag','AF':'Auxilary Flag','PF':'Parity Flag','CF':'Carry Flag'}
    
df1=pd.DataFrame(display1,index=['-->'])
st.table(df1)
df2=pd.DataFrame(display2,index=['-->'])
st.table(df2)
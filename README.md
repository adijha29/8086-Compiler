# 8086-Compiler

This is a graphical user interface (GUI) for the 8086 compiler. It allows users to write and compile Assembly code for the 8086 microprocessor using a user-friendly interface.

# Features
**Code Editor :** Any Code Editor can be used for seeing Code (I have used VS Code). <br/><br/>
**Instruction Implemented :** 
1. ADD, SUB, MUL, DIV (Arithmetic Instruction)
2. AND, OR, XOR, NOT, NEG (Logical Instruction)
3. MOV
4. CMC, STC, CLC, STD, CLD, etc (Flag Instruction)
5. SHL, SHR, SAR, SAL (Shift Instructions)
6. ROR, ROL, RCL, RCR (Rotate Instructions)

All the Instruction are implemented using concept of Modular Programming, also NONE of the external Libraries are used to perform operations. All the above mentioned instructions are implemented by using own functions. By using Libraries we can minimize the code size but the internal function complexity will be same, so I have implemented all the function at my own and also it has been implemented by keeping in mind the working of 8086 microprocessor Compiler Execution.

Modular Programming : If I want to implement 16-bit Addition Operation the it can be done by using the 1-bit addition function and if I want to do 8-bit addition then also it can be done by 1-bit addition function.

# Getting Started

To use the 8086 Compiler GUI, follow these steps:

1. Download the code from Github by clicking the "Download" button or by cloning the repository using Git.
2. Install python compiler (any version after 3.7)
3. Install Libraries such as streamlit, numpy, pandas, base64 and re.
3. Open the Command Prompt and move to the folder where file is located
4. Write the command **"streamlit run 8086_Compiler.py"**
5. Now type the program in Code Section (Text Editor)
6. After writing program , Click on Compile Button to compile the program
7. Now you can check Register values by clicking on the Register Button on Right Side.

# Demo
![ex1](https://user-images.githubusercontent.com/82642783/224802567-18c74d64-be38-49c6-82f1-0f1ad73da217.jpg)

![ex2](https://user-images.githubusercontent.com/82642783/224802586-5103baea-6eba-4dc1-8476-a006305766b6.jpg)


<br /> <br />
If you have some suggestions related to the code, you can contact me on <br/>
Email : adijha2905@gmail.com <br/>
LinkedIn : https://www.linkedin.com/in/aditya-jha-727029204/ <br/>

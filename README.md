# Simple Chatbot for Understanding Romanian Legislation

Project made as part of "Alexandru Ioan Cuza" University of Iași's Computational Linguistics Master's programme.

Paper can be found here: [THESIS](thesis.pdf)

## What does _legislation_ mean?

In the context of this project, base Romanian legislation is comprised of:

1. The Constitution \[[source](https://legislatie.just.ro/Public/FormaPrintabila/00000G0NF8LQJNGG75M2SUMLP2PIT6ZP)\]
2. The Civil Code \[[source](https://legislatie.just.ro/Public/FormaPrintabila/00000G1TT7EZVJJX6870CWN6ZG1TWPAC)\]
3. The Civil Procedure Code \[[source](https://legislatie.just.ro/Public/FormaPrintabila/00000G1NE6WQB9B6WYG13YGXTQETNYA8)\]
4. The Penal Code \[[source](https://legislatie.just.ro/Public/FormaPrintabila/00000G3RCJVMCPZK1D5301YV9BG07ZE3)\]
5. The Penal Procedure Code \[[source](https://legislatie.just.ro/Public/FormaPrintabila/00000G3SGIENTQKF6QX0SUWA2W5Y3ZV3)\]
6. The Fiscal Code \[[source](https://legislatie.just.ro/Public/FormaPrintabila/00000G1ZAKIDCF325CT2OM2WBUU98MOP)\]
7. The Fiscal Procedure Code \[[source](https://legislatie.just.ro/Public/FormaPrintabila/00000G1SA6VV3H1PY8920ESSHWCB3WXT)\]
8. The Labor Code \[[source](https://legislatie.just.ro/Public/FormaPrintabila/00000G3RCE89TJASJDO1SWLGVM5I6DWB)\]
9. The Administrative Code \[[source](https://legislatie.just.ro/Public/FormaPrintabila/00000G26T9IKD8IXCIZ0X39N88WZQ5GJ)\]

## System description

The UI is a single-page web application rendered as a template over a Flask API's root endpoint.

The user input query is sent over the exposed `/send` POST request and it's then handled by pattern matching using an AIML file wrapper.

The chatbot is capable of answering 4 main types of quetions:

1. What articles are of interest to me concerning X topic?
2. How many total articles are there in Code of law X?
3. What is article X of Code of law Y?
4. Define X for me

## Running the app

The flask chat app can be run like this:

```
python main.py
```

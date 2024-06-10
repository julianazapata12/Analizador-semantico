import sys
import re

currentTokenPosition = 0
currentToken = ""
vecTokenTypes = []
vecLexemes = []
numbers = set()
emails = set()
response = ""

def structMessageHtmlError(message):
    responseErrorStruct = (
        "<!DOCTYPE html>"
        "<html>"
        "<head><title>Workgroup Syntax Error</title><meta charset=\"utf-8\"/>"
        "<style>body {{ display: flex; flex-direction: column; align-items: center; }} </style></head>"
        "<body><h2>{}</h2>"
    )
    return responseErrorStruct.format(message)

def match(token):
    global currentTokenPosition
    global currentToken
    currentToken = vecTokenTypes[currentTokenPosition]
    messageErrorSemanticGeneric = f'Error sintáctico, la cadena {vecLexemes[currentTokenPosition]} de tipo {token}'
    if currentToken == token:
        currentTokenPosition += 1
    elif currentToken == "UNKNOWN":
        raise Exception(structMessageHtmlError(f'{messageErrorSemanticGeneric} desconocida esperaba un "{token}". '))
    else:
        raise Exception(structMessageHtmlError(f'{messageErrorSemanticGeneric} no corresponde al token esperado "{token}". '))

def person():
    global currentTokenPosition
    global numbers
    global emails
    global response

    number = vecLexemes[currentTokenPosition]
    if number in numbers:
        response += f"<h2>Error semántico: el número {number} ya se encuentra registrado en la organización.</h2>"
    numbers.add(number)
    match("number")
    match(";")

    name = vecLexemes[currentTokenPosition][1:-1]
    match("str")
    match(";")

    surname = vecLexemes[currentTokenPosition][1:-1]
    match("str")
    match(";")

    email = vecLexemes[currentTokenPosition]
    if email in emails:
        response += f"<h2>Error semántico: el correo {email} ya se encuentra registrado en la organización.</h2>"
    emails.add(email)
    match("email")
    match(";")

    # Add person to HTML response
    response += f"<tr><td>{number}</td><td>{name}</td><td>{surname}</td><td>{email}</td></tr>"

def persons():
    global currentTokenPosition
    global currentToken
    currentToken = vecTokenTypes[currentTokenPosition]
    if currentToken == "number":
        person()
        persons()

def workgroup():
    global response
    match("WG")
    match("(")
    response += "<table border=\"1\"><tr><th>Number</th><th>Name</th><th>Surname</th><th>Email</th></tr>"
    persons()
    match(")")
    response += "</table>"

def workgroups():
    global currentTokenPosition
    global currentToken
    currentToken = vecTokenTypes[currentTokenPosition]
    if currentToken == "WG":
        workgroup()
        workgroups()

def org():
    global response
    match("str")
    org_name = vecLexemes[currentTokenPosition - 1][1:-1]
    response = f"""<!DOCTYPE html>
    <html>
    <head>
        <title>{org_name}</title>
        <style>
            body {{
                display: flex;
                flex-direction: column;
                align-items: center;
            }}
            table {{
                margin-top: 20px;
            }}
        </style>
        <meta charset="utf-8"/>
    </head>
    <body>
        <h1>{org_name}</h1>
    """
    match("(")
    workgroups()
    match(")")
    response += "</body></html>"

def validatePositionError(inputOriginal):
    inputByLines = inputOriginal
    row = 1
    lexemeIndex = 0

    for line in inputByLines:
        positionLine = 0
        while positionLine < len(line) and lexemeIndex < len(vecLexemes):
            lexeme = vecLexemes[lexemeIndex]

            col = line.find(lexeme, positionLine)
            if col != -1:
                if lexeme == vecLexemes[currentTokenPosition]:
                    print(f'<h2>El error se produjo en la linea {row}, columna {col + 1}</h2>')
                    break
                positionLine = col + len(lexeme)
                lexemeIndex += 1
            else:
                if vecTokenTypes[currentTokenPosition] == "UNKNOWN" and positionLine > 0:
                    print(f'<h2>Error sintáctico, en la linea {row} la cadena ingresada "{vecLexemes[currentTokenPosition]}" no es válida en la posición {positionLine}.</h2>')
                if line.strip() == "":
                    print("<h2> Se alcanzó el final de línea </h2>")
                    break
                break
        row += 1

def main(filePath):
    global vecTokenTypes, vecLexemes, response

    try:
        with open(filePath, "r") as f:
            inputStr = f.read()
        inputOriginal = inputStr.splitlines()
        finalLine = len(inputOriginal)

        # Se eliminan las espacios, tabuladores y linea nueva, quedando asi
        inputStr = re.sub(r"[\n\t\s]*", "", inputStr)

        # Ahora se agregan nuevos espacios, pero exclusivamente a partir de los (, ; y ):
        inputStr = re.sub(r"\(", " ( ", inputStr)
        inputStr = re.sub(r"\)", " ) ", inputStr)
        inputStr = re.sub(r";", " ; ", inputStr)
        inputStr = re.sub(r'\s+', ' ', inputStr).strip()

        inputStr = inputStr.split(" ")

        dic_directTokens = {
            'str': 'str',
            '(': '(',
            'WG': 'WG',
            ')': ')',
            'number': 'number',
            'email': 'email',
            ';': ';',
            'UKNOWN': 'UNKNOWN'
        }
        for c in inputStr:
            r = dic_directTokens.get(c)
            if r:
                vecTokenTypes.append(r)
                vecLexemes.append(r)
            elif re.match(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", c):
                vecTokenTypes.append('email')
                vecLexemes.append(c)
            elif re.match(r'^\".*\"$', c):
                vecTokenTypes.append('str')
                vecLexemes.append(c)
            elif re.match(r"^\d+$", c):
                vecTokenTypes.append('number')
                vecLexemes.append(c)
            else:
                vecTokenTypes.append('UNKNOWN')
                vecLexemes.append(c)
        org()
        # Print the generated HTML
        print(response)

    except IndexError:
        print(structMessageHtmlError(f'Error sintáctico, en la linea {finalLine} la cadena ingresada no es válida, se esperaba un token ")" al final de la cadena.'))
        exit(0)
    except Exception as exception:
        print(exception)
        validatePositionError(inputOriginal)
        print("</body></html>")
        exit(0)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python script.py <nombre_del_archivo>")
    else:
        main(sys.argv[1])
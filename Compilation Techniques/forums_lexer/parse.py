from lexer import Error
from lexer import Lexer
import re
import string
import TClass

def check_open_close(fileName, tokens, T_OPEN, T_CLOSE, i, ignore_index):
    if tokens[i][2] == T_OPEN and i not in ignore_index:
        opentag = 1
        closetag = 0
        j = i + 1
        recent = 0
        while (j < len(tokens)):
            if tokens[j][2] == T_OPEN:
                recent = j
                ignore_index.append(j)
                opentag += 1
            if tokens[j][2] == T_CLOSE:
                closetag += 1
            j += 1
        if opentag != closetag:
            Error(fileName, tokens[recent][0], tokens[recent][1], "Invalid Syntax").printErr()
            return ignore_index, "break"
        return ignore_index, ""
    pass

def Parser(fileName):
    # valid identifier followups
    ignore_index = []
    identifier_dec = [TClass.T_BOPEN, TClass.T_EOL, TClass.T_CURLYOPEN]
    identifier_op = [TClass.T_ASSIGN, TClass.T_PLUS, TClass.T_MINUS, TClass.T_MUL, TClass.T_DIV]
    escapes = ["\\", "'", '"', "$", "n", "t", "r"]
    valid_string = frozenset(string.ascii_letters + string.digits + '"#\\-$&=' + "'")

    # file 
    with open(fileName) as file:
        data = file.read()

    tokens = Lexer(data).make_tokens()

    print("=================Lexer Result:=================\n")

    for i in range(0, len(tokens)):
        print(tokens[i])

    print("\n=================Parser Result:=================\n")

    # error checking codes starts here
    for i in range(0, len(tokens)):

        # error for invalid codes that i can think of

        # errors for syntax after identifier
        if tokens[i][2] == TClass.T_IDENTIFIER:
                # errors when identifier name starts with numbers
                if tokens[i][3][0] in "0123456789":
                    Error(fileName, tokens[i][0], tokens[i][1], "Invalid Character Error").printErr()
                    break

                # check if the syntax after identifier name is invalid
                if not ((tokens[i+1][2] in identifier_dec) or (tokens[i+1][2] in identifier_op)):
                    Error(fileName, tokens[i+1][0], tokens[i+1][1], "Invalid Syntax").printErr()
                    break


        # errors related to incomplete opening or closing statements
        result = check_open_close(fileName, tokens, TClass.T_PHPOPEN, TClass.T_PHPCLOSE, i, ignore_index)
        if result is not None:
            ignore_index = result[0]
            if result[1] != "":
                eval(result[1])

        result = check_open_close(fileName, tokens, TClass.T_CURLYOPEN, TClass.T_CURLYCLOSE, i, ignore_index)
        if result is not None:
            ignore_index = result[0]
            if result[1] != "":
                eval(result[1])

        result = check_open_close(fileName, tokens, TClass.T_BOPEN, TClass.T_BCLOSE, i, ignore_index)
        if result is not None:
            ignore_index = result[0]
            if result[1] != "":
                eval(result[1])

        # error for multi-line comment
        if tokens[i][2] == TClass.T_MULTIOPEN:
            j = i + 1
            found = False
            while (j < len(tokens) and not found):
                if tokens[j][2] == TClass.T_MULTICLOSE:
                    found = True
            if not found:
                Error(fileName, tokens[j-1][0], tokens[j-1][1], "Multi Comment Not Closed").printErr()
                break

        # error for string literal not ended with double quotes.
        if tokens[i][2] == TClass.T_LITERAL:
            identifier = tokens[i][3]
            if not (identifier.startswith('"') and identifier.endswith('"')):
                Error(fileName, tokens[i][0], tokens[i][1], "String Literal Not Closed With Duoble Quotes").printErr()
                break

        # error for invalid escape sequences
        # i have no idea lmao

        # error for invalid string characters
        if tokens[i][2] == TClass.T_LITERAL:
            identifier = set(tokens[i][3])
            # returns true if there are invalid string character inside the identifier
            valid =  not identifier <= valid_string

            if valid:
                Error(fileName, tokens[i][0], tokens[i][1], "Invalid Character(s) Inside The String").printErr()
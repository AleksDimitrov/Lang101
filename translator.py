# Authors: Ishaan Ghosh, Aleksander Dimitrov
# Description: This is Lang101, a language that is parsed into
# Python using pattern matching.

from operator import indexOf
import sys
import re
import os
import subprocess

numTabs = 0
debug = ""

# This parses the basic parts of a line,
# returning something like "int x 3".
def basicVarAssgnParse(line):  # line, body
    global debug

    parsed = re.sub("\.", "\n", line)
    parsed = re.sub("\n", " ", parsed)
    parsed = parsed.split("=")
    type_var = parsed[0].split()[0]
    name = parsed[0].split()[1]
    val = parsed[1]
    res = " ".join([type_var, name, val])
    if debug:
        print("DEBUG: ", res + "\n")
    return res

# This translates boolean var assignment (eg bool x = ~T).
def boolVarAssg(file, line):
    global debug

    clean_line = basicVarAssgnParse(line)
    line = re.search("T", clean_line)
    final = re.sub("T", " True ", clean_line)
    final = re.sub("\(T\)", "(True) ", final)
    final = re.sub("F", " False ", final)
    final = re.sub("\(F\)", "(False) ", final)
    final = re.sub("~T ", " not True ", final)
    final = re.sub("~\(", " not(", final)
    final = re.sub("~F ", " not False ", final)
    final = re.sub("~", "not ", final)
    final = re.sub("T&&", "True and ", final)
    final = re.sub("&&T", "and True ", final)
    final = re.sub("F&&", "False and ", final)
    final = re.sub("&&F", "and False ", final)
    final = re.sub("F\(", "False(", final)
    final = re.sub("\)F", ")False ", final)
    final = re.sub("T\(", "True(", final)
    final = re.sub("\)T", ")True ", final)
    final = re.sub("&&\(", "and(", final)
    final = re.sub("\)&&", ")and ", final)
    final = re.sub("\|\|\(", "or(", final)
    final = re.sub("\)\|\|", ")or ", final)
    final = re.sub("&&~", "and(", final)
    final = re.sub("~&&", ")and ", final)
    final = re.sub("\|\|\~", " or not", final)
    final = re.sub("~\|\|", " not or ", final)
    final = re.sub("T\|\|", " True or ", final)
    final = re.sub("\|\|T", " or True ", final)
    final = re.sub("F\|\|", " False or ", final)
    final = re.sub("\|\|F", " or False ", final)
    final = re.sub("&&", " and ", final)
    final = re.sub("\|\|", " or ", final)
    final = " ".join(
        final.split()[1:2] + ["="] + final.rstrip().split()[2:])

    intExprCheck = re.search(
        "(add)|(sub)|(mult)|(div)|(mod)|(gre)|(les)|(equ)", final)
    if (intExprCheck is not None):
        lineParts = final.split("=")
        if debug:
            print("DEBUG: ", lineParts[0] + "=" + intVarExpr(file, lineParts[1]) + "\n")
        return lineParts[0] + "=" + intVarExpr(file, lineParts[1])
    else:
        if debug:
            print("DEBUG: ", final + "\n")
        return final

# This translates str var literal assignment (eg str x = "test").
def strVarLiteralAssg(line):
    global debug

    final = basicVarAssgnParse(line)
    final = " ".join(
        final.split()[1:2] + ["="] + final.rstrip().split()[2:])
    if debug:
        print("DEBUG: ", final + "\n")
    return final

# This translates str var assignment (eg str x = y).
def strVarVarAssg(line):
    global debug

    final = basicVarAssgnParse(line)
    final = " ".join(
        final.split()[1:2] + ["="] + final.rstrip().split()[2:])
    if debug:
        print("DEBUG: ", strVarExpr(final) + "\n")
    return strVarExpr(final)

# This translates str var expressions (eg add("test", "1")).
def strVarExpr(line):
    global debug

    assignment = line.split("(")
    assignment[1] = re.sub(",", "+", assignment[1])
    assignment[1] = assignment[1].strip(").")
    assignment[0] = assignment[0].strip("concat")
    final = line.split("=")[0].split()[0] + "".join(assignment)
    if debug:
        print("DEBUG: ", final + "\n")
    return final

# This translates int var assignment (eg int x = 3).
def intVarAssg(file, line):
    global numTabs
    global debug

    clean_line = basicVarAssgnParse(line)
    final = " ".join(
        clean_line.split()[1:2] + ["="] + clean_line.rstrip().split()[2:])
    intExprCheck = re.search(
        "(add)|(sub)|(mult)|(div)|(mod)|(gre)|(les)|(equ)", final)
    if (intExprCheck is not None):
        lineParts = final.split("=")
        if debug:
            print("DEBUG: ", lineParts[0] + "=" + intVarExpr(file, lineParts[1]) + "\n")
        file.write(lineParts[0] + "=" + intVarExpr(file, lineParts[1])+"\n")
    else:
        if debug:
            print("DEBUG: ", final + "\n" + "\t" * numTabs + "\n")
        file.write(final + "\n" + "\t" * numTabs)

# This translates int var expressions (eg mod(4, 2)).
def intVarExpr(file, line):
    global debug

    line = line.strip()
    recurseCheck = re.search(
        "(add)|(sub)|(mult)|(div)|(mod)|(gre)|(les)|(equ)", line)
    if (recurseCheck is None):
        if (line is None):
            return "SYNERR"
        if (line == ""):
            return "SYNERR"
        else:
            return(line)

    clean = re.sub("\.", "", line)
    clean = re.sub("\n", "", clean)

    outerOp = clean[0:4]
    pythonExpr = ""

    if (outerOp == "add("):
        pythonExpr = clean[4:-1]
        commaIndex = [i.start() for i in re.finditer(",", pythonExpr)]
        odd = len(commaIndex) % 2
        index = (len(commaIndex) // 2)
        if (odd == 0):
            index -= 1

        if (len(commaIndex) > 1):
            pieces = [pythonExpr[:commaIndex[index]],
                      pythonExpr[commaIndex[index]+1:]]
            piece1 = intVarExpr(file, pieces[0])
            piece2 = intVarExpr(file, pieces[1])
            pythonExpr = piece1 + "+" + piece2
        else:
            pythonExpr = re.sub(",", "+", pythonExpr)
    elif (outerOp == "sub("):
        pythonExpr = clean[4:-1]
        commaIndex = [i.start() for i in re.finditer(",", pythonExpr)]
        odd = len(commaIndex) % 2
        index = (len(commaIndex) // 2)
        if (odd == 0):
            index -= 1

        if (len(commaIndex) > 1):
            pieces = [pythonExpr[:commaIndex[index]],
                      pythonExpr[commaIndex[index]+1:]]
            piece1 = intVarExpr(file, pieces[0])
            piece2 = intVarExpr(file, pieces[1])
            pythonExpr = piece1 + "-" + piece2
        else:
            pythonExpr = re.sub(",", "-", pythonExpr)
    elif (outerOp == "mult"):
        pythonExpr = clean[5:-1]
        commaIndex = [i.start() for i in re.finditer(",", pythonExpr)]
        odd = len(commaIndex) % 2
        index = (len(commaIndex) // 2)
        if (odd == 0):
            index -= 1

        if (len(commaIndex) > 1):
            pieces = [pythonExpr[:commaIndex[index]],
                      pythonExpr[commaIndex[index]+1:]]
            piece1 = intVarExpr(file, pieces[0])
            piece2 = intVarExpr(file, pieces[1])
            pythonExpr = piece1 + "*" + piece2
        else:
            pythonExpr = re.sub(",", "*", pythonExpr)
    elif (outerOp == "div("):
        pythonExpr = clean[4:-1]
        commaIndex = [i.start() for i in re.finditer(",", pythonExpr)]
        odd = len(commaIndex) % 2
        index = (len(commaIndex) // 2)
        if (odd == 0):
            index -= 1

        if (len(commaIndex) > 1):
            pieces = [pythonExpr[:commaIndex[index]],
                      pythonExpr[commaIndex[index]+1:]]
            piece1 = intVarExpr(file, pieces[0])
            piece2 = intVarExpr(file, pieces[1])
            pythonExpr = piece1 + "/" + piece2
        else:
            pythonExpr = re.sub(",", "/", pythonExpr)
    elif (outerOp == "mod("):
        pythonExpr = clean[4:-1]
        commaIndex = [i.start() for i in re.finditer(",", pythonExpr)]
        odd = len(commaIndex) % 2
        index = (len(commaIndex) // 2)
        if (odd == 0):
            index -= 1

        if (len(commaIndex) > 1):
            pieces = [pythonExpr[:commaIndex[index]],
                      pythonExpr[commaIndex[index]+1:]]
            piece1 = intVarExpr(file, pieces[0])
            piece2 = intVarExpr(file, pieces[1])
            pythonExpr = piece1 + "%" + piece2
        else:
            pythonExpr = re.sub(",", "%", pythonExpr)
    elif (outerOp == "gre("):
        pythonExpr = clean[4:-1]
        commaIndex = [i.start() for i in re.finditer(",", pythonExpr)]
        odd = len(commaIndex) % 2
        index = (len(commaIndex) // 2)
        if (odd == 0):
            index -= 1

        if (len(commaIndex) > 1):
            pieces = [pythonExpr[:commaIndex[index]],
                      pythonExpr[commaIndex[index]+1:]]
            piece1 = intVarExpr(file, pieces[0])
            piece2 = intVarExpr(file, pieces[1])
            pythonExpr = piece1 + ">" + piece2
        else:
            pythonExpr = re.sub(",", ">", pythonExpr)
    elif (outerOp == "les("):
        pythonExpr = clean[4:-1]
        commaIndex = [i.start() for i in re.finditer(",", pythonExpr)]
        odd = len(commaIndex) % 2
        index = (len(commaIndex) // 2)
        if (odd == 0):
            index -= 1

        if (len(commaIndex) > 1):
            pieces = [pythonExpr[:commaIndex[index]],
                      pythonExpr[commaIndex[index]+1:]]
            piece1 = intVarExpr(file, pieces[0])
            piece2 = intVarExpr(file, pieces[1])
            pythonExpr = piece1 + "<" + piece2
        else:
            pythonExpr = re.sub(",", "<", pythonExpr)
    elif (outerOp == "equ("):
        pythonExpr = clean[4:-1]
        commaIndex = [i.start() for i in re.finditer(",", pythonExpr)]
        odd = len(commaIndex) % 2
        index = (len(commaIndex) // 2)
        if (odd == 0):
            index -= 1

        if (len(commaIndex) > 1):
            pieces = [pythonExpr[:commaIndex[index]],
                      pythonExpr[commaIndex[index]+1:]]
            piece1 = intVarExpr(file, pieces[0])
            piece2 = intVarExpr(file, pieces[1])
            pythonExpr = piece1 + "==" + piece2
        else:
            pythonExpr = re.sub(",", "==", pythonExpr)
        if debug:
            print("DEBUG: ", intVarExpr(file, pythonExpr) + "\n")
    return intVarExpr(file, pythonExpr)

# This translates if statements
# (eg if[T || F] 
# {
#     if[F && T] 
#     {
#         int y = 3
#         .
#         int z = 4
#     }
# }).
def ifStmt(file, line):
    global numTabs
    global debug

    if debug:
        print("DEBUG if start line:", line)

    parsed = [char for char in line if char != " " and char != "."]
    parsed = "".join(parsed).strip("{")
    parsed = parsed.split("[")
    parsed = "".join(parsed).strip("]")

    if parsed[0] == "i":
        expr = "".join(parsed[2:])
    elif parsed[0] == "e":
        expr = "".join(parsed[4:])

    expr = expr.strip()
    ifCond = boolVarAssg(file, "bool x = " + expr)
    search_spaces = re.search("{\s+", line)
    parsed = line.strip(".")
    parsed = line.split()
    parsed2 = [char for char in line if char != " " and char != "."]
    newParsed2 = re.sub("\[\s*.*\s*\]", ifCond, line)
    newParsed2 = newParsed2.split("x =")
    newParsed2 = " ".join(newParsed2)
    newParsed = ""

    if debug:
        print("DEBUG If tabs:", numTabs)

    for i in newParsed2:
        if i == "{":
            numTabs += 1
            newParsed += ":" + "\n" + "\t" * numTabs

        elif i == "}":

            numTabs -= 1

        elif i == "[":
            newParsed += "("
        elif i == "]":
            newParsed += ")"
        else:
            newParsed += i

    if debug:
        print("DEBUG If Final: ", newParsed + "\n")

    file.write(newParsed)

# This translates while loops
# (eg while[les(1,3)] 
# {
#     while[gre(0,1)] 
#     {
#         int y = 3
#         .
#         int z = 4
#     }
# }).
def whileLoop(file, line):
    global numTabs
    global debug

    if debug:
        print("DEBUG while start line:", line)

    parsed = [char for char in line if char != " " and char != "."]
    parsed = "".join(parsed).strip("{")
    parsed = parsed.split("[")
    parsed = "".join(parsed).strip("]")
    expr = "".join(parsed[5:])
    expr = expr.strip()
    ifCond = boolVarAssg(file, "bool x = " + expr)  # x = expr
    search_spaces = re.search("{\s+", line)
    parsed = line.strip(".")
    parsed = line.split()
    parsed2 = [char for char in line if char != " " and char != "."]
    newParsed2 = re.sub("\[\s*.*\s*\]", ifCond, line)
    newParsed2 = newParsed2.split("x =")
    newParsed2 = " ".join(newParsed2)
    newParsed = ""
    for i in newParsed2:
        if i == "{":
            numTabs += 1
            newParsed += ":" + "\n" + "\t" * numTabs
        elif i == "}":
            numTabs -= 1  # 0
        elif i == "[":
            newParsed += "("
        elif i == "]":
            newParsed += ")"
        else:
            newParsed += i

    if debug:
        print("DEBUG: Final parsed from whileLoop", newParsed + "\n")

    file.write(newParsed)

# This translates comment statements (eg % This is for reference).
def comment(line):
    global debug

    parsed = re.sub("%", "#", line)
    if debug:
        print("DEBUG: Final parsed from comment", parsed + "\n")
    return parsed

# This translates print statements (eg view("print me")).
def view(file, line):
    global debug

    final = re.sub("view", "print", line)

    if final[-1] == ".":
        final = final[:-1]

    ExprCheck = re.search(
        "(add)|(sub)|(mult)|(div)|(mod)|(gre)|(les)|(equ)|T|F", line)
    if ExprCheck is not None:
        lineParts = final[:-1].split("print(")
        expr = lineParts[1]
        boolExpr = "bool x = " + expr + "."
        parsedBool = boolVarAssg(file, boolExpr)
        parsedParts = parsedBool.split("=")
        final = "print(" + parsedParts[1] + ")"
    if debug:
        print("DEBUG: Final parsed from view", final + ")\n")
    return final + "\n"

# This processes the regex to be used in the pattern matching
# for locating specific components of the syntax.
def parse(line, f2):
    global numTabs
    global debug

    line = line.strip()
    if line == "":
        if debug:
            print("DEBUG: Line is empty\n")
        return
    if line == "}" or line == "}.":
        if debug:
            print("DEBUG: Line is end of conditional or loop\n")
        numTabs -= 1
        f2.write("\n" + "\t" * numTabs)
        return
    if line == ".":
        if debug:
            print("DEBUG: Line is end of conditional or loop\n")
        f2.write("\n" + "\t" * numTabs)
        return
    if line == "{":
        if debug:
            print("DEBUG: Line is beginning of conditional or loop\n")
        numTabs += 1
        f2.write(":\n" + "\t" * numTabs)
        return
    strVarLiteralAssgSea = re.search(
        "^str\s[^0-9 .=&|]+\s=\s\"\w+\"$", line)
    if debug:
        if (strVarLiteralAssgSea is not None):
            print("DEBUG: strVarLiteralAssgSea: " + strVarLiteralAssgSea.group() + "\n")
        else:
            print("DEBUG: strVarLiteralAssgSea: None\n")
    strVarVarAssgSea = re.search("^str\s[^0-9\s.=&|]+\s=\s.+$", line)
    if debug:
        if (strVarVarAssgSea is not None):
            print("DEBUG: strVarVarAssgSea: " + strVarVarAssgSea.group() + "\n")
        else:
            print("DEBUG: strVarVarAssgSea: None\n")
    intVarAssgSea = re.search("^int\s[^0-9\s.=&|]+\s=\s.+$", line)
    if debug:
        if (intVarAssgSea is not None):
            print("DEBUG: intVarAssgSea: " + intVarAssgSea.group() + "\n")
        else:
            print("DEBUG: intVarAssgSea: None\n")
    intExprSea = re.search(
        "(add)|(sub)|(mult)|(div)|(mod)|(gre)|(les)|(equ)", line)
    if debug:
        if (intExprSea is not None):
            print("DEBUG: intExprSea: " + intExprSea.group() + "\n")
        else:
            print("DEBUG: intExprSea: None\n")
    boolVarAssgSea = re.search("^bool\s[^0-9\s.=&|]+\s=\s.+$", line)
    if debug:
        if (boolVarAssgSea is not None):
            print("DEBUG: boolVarAssgSea: " + boolVarAssgSea.group() + "\n")
        else:
            print("DEBUG: boolVarAssgSea: None\n")
    printStrSea = re.search("^view\(\".*\"\).*$", line)
    if debug:
        if (printStrSea is not None):
            print("DEBUG: printStrSea: " + printStrSea.group() + "\n")
        else:
            print("DEBUG: printStrSea: None\n")
    printValSea = re.search("^view\(.+\).*$", line)
    if debug:
        if (printValSea is not None):
            print("DEBUG: printValSea: " + printValSea.group() + "\n")
        else:
            print("DEBUG: printValSea: None\n")
    commSea = re.search("^%\s+(.*)$", line)
    if debug:
        if (commSea is not None):
            print("DEBUG: commSea: " + commSea.group() + "\n")
        else:
            print("DEBUG: commSea: None\n")
    ifWFuncSea = re.search(
        "^if\s*\[\s*.*\s*\]\s*$", line)
    if debug:
        if (ifWFuncSea is not None):
            print("DEBUG: ifWFuncSea: " + ifWFuncSea.group() + "\n")
        else:
            print("DEBUG: ifWFuncSea: None\n")
    elifWFuncSea = re.search(
        "^elif\s*\[\s*.*\s*\]\s*$", line)
    if debug:
        if (elifWFuncSea is not None):
            print("DEBUG: elifWFuncSea: " + elifWFuncSea.group() + "\n")
        else:
            print("DEBUG: elifWFuncSea: None\n")
    elseSea = re.search(
        "^else\s*$", line)
    if debug:
        if (elseSea is not None):
            print("DEBUG: elseSea: " + elseSea.group() + "\n")
        else:
            print("DEBUG: elseSea: None\n")
    whileWFuncSea = re.search(
        "^while\s*\[\s*.*\s*\]\s*$", line)
    if debug:
        if (whileWFuncSea is not None):
            print("DEBUG: whileWFuncSea: " + whileWFuncSea.group() + "\n")
        else:
            print("DEBUG: whileWFuncSea: None\n")
    if (strVarLiteralAssgSea is not None):
        strVarLiteralAssgSea = strVarLiteralAssgSea.group()
        newLine = strVarLiteralAssg(strVarLiteralAssgSea)
        f2.write(newLine + "\n")
    elif (strVarVarAssgSea is not None):
        strVarVarAssgSea = strVarVarAssgSea.group()
        newLine = strVarVarAssg(strVarVarAssgSea)
        f2.write(newLine + "\n")
    elif (intVarAssgSea is not None):
        intVarAssgSea = intVarAssgSea.group()
        newLine = intVarAssg(f2, intVarAssgSea)
    elif (boolVarAssgSea is not None):
        boolVarAssgSea = boolVarAssgSea.group()
        newLine = boolVarAssg(f2, boolVarAssgSea)
        f2.write(newLine + "\n")
    elif (printStrSea is not None):
        newLine = view(f2, printStrSea.group())
        f2.write(newLine + "\n")
    elif (printValSea is not None):
        newLine = view(f2, printValSea.group())
        f2.write(newLine + "\n")
    elif (commSea is not None):
        newLine = comment(commSea.group())
        f2.write(newLine + "\n")
    elif (whileWFuncSea is not None):
        newLine = whileLoop(f2, line)
    elif (ifWFuncSea is not None):
        newline = ifStmt(f2, line)
    elif (elifWFuncSea is not None):
        newLine = ifStmt(f2, line)
    elif (elseSea is not None):
        newLine = ifStmt(f2, line)
    elif (intExprSea is not None):
        intExprSea = intExprSea.group()
        newLine = intVarExpr(f2, intExprSea)
        if (newLine == "SYNERR"):
            f2.write("print('Syntax Error: \"" + line + "\"')\n")
        else:
            f2.write(newLine + "\n")
    else:
        f2.write("print('Syntax Error: \"" + line + "\"')\n")

# This deals with input files, additional command-line arguments
# (including an optional debug mode that explicitly highlights
# the parsing process), and simulating an interactive shell.
def main():
    global numTabs
    global debug

    fn = "shell.py"
    # x = 10
    # open("translation" + str(x) + ".py", "a")
    f3 = open(fn, "w")  # writes to input txt file

    if len(sys.argv) == 1:
        # x += 1
        print("'Welcome to your shell'\n")
        while (True):
            print(">> ", end="")
            cmd = input()
            if (cmd == "exit"):
                exit()
            printStrSea = re.search("^view\(\".*\"\)$", cmd)
            printValSea = re.search("^view\(.+\)$", cmd)
            if (printValSea is not None):
                printValSea = printValSea.group()
            if printValSea is None:
                parse(cmd, f3)
            else:
                parse(cmd, f3)
                break
    else:
        f1 = open(sys.argv[1], "r")  # reads from input .txt file
        f2 = open(sys.argv[2], "w")  # writes to output .py file

        cmdFlag = False
        argLen = len(sys.argv)
        if (argLen > 3):
            if (sys.argv[3] == "dbOn"):
                debug = True
                cmdArgsList = sys.argv[4:]
            else:
                debug = False
                cmdArgsList = sys.argv[3:]
            cmdFlag = True
            if len(cmdArgsList) == 0:
                newLine = "cmdArgs = []"
            else:
                newLine = "cmdArgs = ["
            for arg in cmdArgsList:
                strArgSea = re.search('[a-zA-Z]', arg)
                if (strArgSea is not None):
                    newLine += "\""
                    newLine += arg
                    newLine += "\","
                else:
                    newLine += arg
                    newLine += ","
            newLine = newLine[:-1]
            newLine = newLine + "]\n"
            f2.write(newLine)

        for line in f1:
            parse(line, f2)

        f3.close()
    return True

# This is what calls the main() function which starts the translator.
if __name__ == "__main__":
    main()
    fn = "shell.py"
    subprocess.run(["python3", fn], text=True)

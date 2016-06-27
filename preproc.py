#!/usr/bin/env python3
import sys
import re

defaultVars = { 
        'templater_version': 'Sprocket v0.1'
}

fileCommands = {
        "css"  : [ "/*:",   "*/"  ],
        "html" : [ "<!--:", "-->" ],
}

highlightCommands = {
        "c"    : { "keywords"  : [ "while", "if", "else", "inline", "void", "typedef",
                                   "for", "do", "int", "char", "unsigned", "enum", "return",
                                   "struct", "volatile", "switch", "case", "default" ],
                   "macros"    : [ "#define", "#include", "#ifndef", "#ifdef", "#if", "#endif" ],
                   "function"  :   "\\b[a-zA-Z_][a-zA-Z0-9_]+\\(",
                   "comments"  : ["/\\*.*?\\*/", "//.*?\n" ],
                   #"comments"  : [ "//.*?\n" ],
                   "constants" : [ "\\b[0-9]\\b", "&quot;.*?&quot;", "&lt;.*\\.h&gt;", "\\b[A-Z_][A-Z_]*\\b" ]
                 }
}

def highlightFile( inputName, output ):
    fileExt = inputName[ inputName.rindex( "." ) + 1 :]

    if fileExt in highlightCommands:
        highlight = True
        langdict = highlightCommands[fileExt]
    else:
        highlight = False

    inputFile = open( inputName, "r" );
    fbuf = inputFile.read( );

    fbuf = fbuf.replace( "&", "&amp;" )\
               .replace( "<", "&lt;" )\
               .replace( ">", "&gt;" )\
               .replace( "\"", "&quot;" )\
               .replace( "\t", "     " )

    if highlight:
        print( "have highlight file" );

        for word in langdict["comments"]:
            fbuf = re.sub( "("+word+")", "<span style='color:#b0b0b0; font-style:italic;'>\\1</span>", fbuf, 0, re.DOTALL )

        temp = re.findall( langdict["function"], fbuf )
        for thing in temp:
            foo = thing[:-1]
            fbuf = re.sub( "(\\b"+foo+"\\b)\\(", "<span style='color:#2e3a7a'>\\1</span>(", fbuf )

        for word in langdict["keywords"]:
            fbuf = re.sub( "(\\b" + word + "\\b)", "<span style='color:#3e8f3e'>\\1</span>", fbuf )

        for word in langdict["macros"]:
            fbuf = fbuf.replace( word, "<span style='color:#6f6fba'>" + word + "</span>" )

        for word in langdict["constants"]:
            fbuf = re.sub( "("+word+")", "<span style='color:#bf4444'>\\1</span>", fbuf )

        output.write( fbuf );
    else:
        output.write( fbuf );

    return

def parseFile( inputName, output, variables ):
    fileExt = inputName[ inputName.rindex( "." ) + 1 :]

    if fileExt in fileCommands:
        preprocess = True
        cmdStr = fileCommands[fileExt][0];
        cmdStrEnd = fileCommands[fileExt][1];
    else:
        preprocess = False
        #print( "    Warning: Unknown preprocessor file extension \"" + fileExt + "\" ("+ inputName + "), including raw" )
        return highlightFile( inputName, output );


    inputFile = open( inputName, "r" )

    lineNum = 1
    line = inputFile.readline( )

    while line != '':
        if preprocess and cmdStr in line and cmdStrEnd in line:
            # find the placement of preprocessor directives
            cmdStart = line.index( cmdStr ) + len( cmdStr )
            cmdEnd = line.index( cmdStrEnd )

            # Keep track of the text before and after the commands
            head = line[:cmdStart - len( cmdStr )]
            tail = line[cmdEnd + len( cmdStrEnd ):]

            # extract command
            line = line[ cmdStart : cmdEnd ]
            command = line.split( )

            output.write( head )

            # evaluate the command
            if len( command ) < 1:
                print( "    Warning: empty command tag at " + inputName + ":" + str( lineNum ))

            else:
                if   command[0] == "include" and len( command ) > 1:
                    print( "    Including " + ", ".join( command[1:] ))
                    for include in command[1:]:
                        parseFile( include, output, variables )

                elif command[0] == "variable" and len( command ) > 1:
                    for var in command[1:]:
                        if var in variables:
                            print( "    Variable " + var )
                            output.write( variables[var] )

                elif command[0] == "set" and len( command ) > 2:
                    variables.update({ command[1] : " ".join( command[2:] )})
                    print( "    Set variable " + command[1] + " to " + variables[ command[1] ] )

                else:
                    print( "    Warning: Unknown command '" + command[0] + "' at " + inputName + ":" + str( lineNum ))

                output.write( tail )
        else:
            output.write( line )


        line = inputFile.readline( )
        lineNum += 1

    return

def parseTemplate( inputName, outputName ):
    outputFile = open( outputName, "w" )

    parseFile( inputName, outputFile, defaultVars );
    return

if __name__ == "__main__":
    if len( sys.argv ) < 3:
        print( "Usage: " + sys.argv[0] + " [input template] [output file]" )

    else:
        parseTemplate( sys.argv[1], sys.argv[2] )

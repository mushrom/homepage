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

def parseFile( inputName, output, variables ):
    fileExt = inputName[ inputName.rindex( "." ) + 1 :]

    if fileExt in fileCommands:
        preprocess = True
        cmdStr = fileCommands[fileExt][0];
        cmdStrEnd = fileCommands[fileExt][1];
    else:
        preprocess = False

    inputFile = open( inputName, "r" )

    lineNum = 1
    line = inputFile.readline( )
    do_output = True;

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

            if do_output:
                output.write( head )

            # evaluate the command
            if len( command ) < 1:
                print( "    Warning: empty command tag at " + inputName + ":" + str( lineNum ))

            elif do_output:
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

                elif command[0] == "if"  and len( command ) == 2:
                    condition = ""

                    if command[1] in variables:
                        condition = variables[command[1]]
                    else:
                        condition = "false"

                    print( "    if " + command[1] + ": " + condition );
                    do_output = condition == "true";

                elif command[0] == "ifnot" and len( command ) == 2:
                    condition = ""

                    if command[1] in variables:
                        condition = variables[command[1]]
                    else:
                        condition = "false"

                    print( "    ifnot " + command[1] + ": " + condition );
                    do_output = condition != "true";

            elif command[0] == "endif":
                do_output = True;

            else:
                print( "    ignoring command '" + command[0] + "' at " + inputName + ":" + str( lineNum ))

            if do_output:
                output.write( tail )

        elif do_output:
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

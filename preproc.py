#!/usr/bin/env python3
import sys
import re

default_vars = {
        'templater_version': 'preproc thing'
}

file_commands = {
        "css"  : ("/*:",   "*/"),
        "html" : ("<!--:", "-->"),
}

command_handlers = { }

do_output = True

def preproc_command(func):
    command_handlers.update({ func.__name__[4:] : func })
    return func

@preproc_command
def pre_include( command, output, variables ):
    print( "    Including " + ", ".join( command[1:] ))
    for include in command[1:]:
        parse_file( include, output, variables )

@preproc_command
def pre_variable( command, output, variables ):
    for var in command[1:]:
        if var in variables:
            print( "    Variable " + var )
            output.write( variables[var] )

@preproc_command
def pre_set( command, output, variables ):
    variables.update({ command[1] : " ".join( command[2:] )})
    print( "    Set variable " + command[1] + " to " + variables[ command[1] ] )

@preproc_command
def pre_if( command, output, variables ):
    global do_output

    condition = variables.get(command[1]) or "false"
    do_output = condition == "true";

    print( "    if " + command[1] + ": " + condition );

@preproc_command
def pre_ifnot( command, output, variables ):
    global do_output

    condition = variables.get(command[1]) or "false"
    do_output = condition != "true";

    print( "    ifnot " + command[1] + ": " + condition );

def parse_file( input_name, output, variables ):
    global do_output

    extension = input_name[ input_name.rindex( "." ) + 1 :]
    preprocess = False

    if extension in file_commands:
        cmd_start, cmd_end = file_commands[extension]
        preprocess = True

    input_file = open( input_name, "r" )

    line_num = 1
    line = input_file.readline( )

    while line != '':
        if preprocess and cmd_start in line and cmd_end in line:
            # find the placement of preprocessor directives
            line_start = line.index(cmd_start) + len(cmd_start)
            line_end   = line.index(cmd_end)

            # Keep track of the text before and after the commands
            head = line[:line_start - len(cmd_start)]
            tail = line[line_end + len(cmd_end):]

            # extract command
            command = line[line_start : line_end].split()

            if do_output:
                output.write( head )

            # evaluate the command
            if len(command) == 0:
                print( "    Warning: empty command tag at "
                       + input_name + ":" + str( line_num ))

            elif do_output and command[0] in command_handlers:
                command_handlers[command[0]]( command, output, variables )

            elif command[0] == "endif":
                do_output = True;

            else:
                print( "    ignoring command '" + command[0] +
                       "' at " + input_name + ":" + str( line_num ))

            if do_output:
                output.write( tail )

        elif do_output:
            output.write( line )

        line = input_file.readline( )
        line_num += 1

def parse_template( input_name, output_name ):
    output_file = open( output_name, "w" )
    parse_file( input_name, output_file, default_vars );
    output_file.close()

if __name__ == "__main__":
    if len( sys.argv ) < 3:
        print( "Usage: " + sys.argv[0] + " [input template] [output file]" )

    else:
        parse_template( sys.argv[1], sys.argv[2] )

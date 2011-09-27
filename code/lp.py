
# Real-time Processor Architectures for Worst Case Execution Time Reduction
# Thesis Software Distribution.
# This code is licensed under GPL v2, and is copyright (C) Jack Whitham 2004-08.
#


import os, math, collections, sys, atexit
import extra

[ VAR_BINARY, VAR_INTEGER, VAR_MIXED, VAR_POSITIVE ] = "abcd"
GLPSOLVE_CMD_LINE = 'glpsol --math %s'

ILP_Solver = None
MODEL_FILE_NAME = None


class ILPError(Exception): 
    pass

class ILP_Solver_GLPK:
    def __init__(self):
        self.result_key = '!result: '
        self.Reset_All()

    def Reset_All(self):
        self.sect0 = []
        self.sect1 = collections.deque() # [] does not have
        self.sect2 = collections.deque() # the .clear() method
        self.sect3 = []
        self.sect4 = []
        self.all_sectors = [ [ '/* GLPK --math mode */' ],
                self.sect0, self.sect1,
                self.sect2, [ 'solve ;' ], self.sect3, 
                [ 'data ;' ], self.sect4, [ 'end ;' ] ]

    def Add_Var(self, vname, var_type):
        if ( var_type == VAR_INTEGER ):
            self.sect0.append('var %s, integer;\n' % vname)
        elif ( var_type == VAR_POSITIVE ):
            self.sect0.append('var %s, >= 0 ;\n' % vname)
        elif ( var_type == VAR_BINARY ):
            self.sect0.append('var %s, binary ;\n' % vname)
        elif ( var_type == VAR_MIXED ):
            self.sect0.append('var %s ;\n' % vname)
        else:
            assert False, "Unknown var_type %s" % var_type

        self.sect3.append(r'printf "%s%s = %%d\n", %s;' %
                    (self.result_key, vname, vname))
        self.sect3.append('\n')

    def Reset_Terms(self):
        self.sect1.clear()
        self.sect2.clear()

    def Add_Term(self, lhs, operator, rhs):
        assert not '(' in lhs
        assert not '(' in rhs
        self.sect1.append('s.t. c%05u: %s %s %s ;\n' %
                    (len(self.sect1), lhs, operator, rhs))

    def Add_Problem(self, minimise_this):
        self.sect2.append('minimize obj: %s ;\n' % minimise_this)

    def Solve(self, receive_fn):

        model_file = file(MODEL_FILE_NAME, 'wt')
        for sect in self.all_sectors:
            model_file.write(''.join(sect))
            model_file.write('\n\n')
        model_file.close()

        return self.Call_Solver(MODEL_FILE_NAME, receive_fn)

    def Call_Solver(self, model_file_name, receive_fn):


        cmdline = GLPSOLVE_CMD_LINE % model_file_name

        try:
            glpsol = os.popen(cmdline)
        except:
            raise ILPError('Could not launch ILP solver: %s' % cmdline)

        nonzero = True 
        all = []
        errors = []
        commit = []
        for line in glpsol:
            if (( line.find('PROBLEM') >= 0 )
            or ( line.find('error') >= 0 )):
                errors.append(line)

            all.append(line)

            if ( line.startswith(self.result_key) ):
                params = line[ len(self.result_key) : ]
                words = params.split('=')
                assert len(words) == 2
                key = words[ 0 ].strip()
                value = int(words[ 1 ])

                commit.append((key, value))

        glpsol.close()

        if len(errors) == 0:
            # Commit changes
            for (key, value) in commit:
                receive_fn(key, value)

        else:
            # Error 
            raise ILPError('Could not solve: %s\n%s' % (cmdline,
                '\n'.join(errors)))

        return ''.join(all)

class ILP_Solver_LPS(ILP_Solver_GLPK):
    def __init__(self):
        ILP_Solver_GLPK.__init__(self)

        import lpsolve55 

        self.lpsolve_module = lpsolve55
        self.lp_fn = self.lpsolve_module.lpsolve


    def Reset_All(self):
        # objective function
        self.sect_obj = collections.deque()
        # constraints
        self.sect_constraints = collections.deque()
        self.sect_var_constraints = []
        # variable decls
        self.sect_vars = []
        self.variables = set()

        self.all_sectors = [ ['/* lp_solve model */'],
                self.sect_obj, self.sect_constraints,
                self.sect_var_constraints,
                self.sect_vars ]


    def Add_Var(self, vname, var_type):
        if ( var_type == VAR_INTEGER ):
            self.sect_vars.append('int %s ;\n' % vname)
        elif ( var_type == VAR_POSITIVE ):
            self.sect_var_constraints.append('0 <= %s ;\n' % vname)
        elif ( var_type == VAR_BINARY ):
            self.sect_vars.append('int %s ;\n' % vname)
            self.sect_var_constraints.append('0 <= %s <= 1 ;\n' % vname)
        elif ( var_type == VAR_MIXED ):
            pass
        else:
            assert False, "Unknown var_type %s" % var_type
        self.variables.add(vname)

    def Reset_Terms(self):
        self.sect_constraints.clear()
        self.sect_obj.clear()

    def Add_Term(self, lhs, operator, rhs):
        assert not '(' in lhs
        assert not '(' in rhs


        self.sect_constraints.append('%s %s %s ;\n' % (lhs, operator, rhs))

    def Add_Problem(self, minimise_this):
        self.sect_obj.append('min: %s ;\n' % minimise_this)

    def Call_Solver(self, model_file_name, receive_fn):
        lpmod = self.lpsolve_module
        lp = self.lp_fn('read_lp', model_file_name)
        #self.lp_fn('set_verbose', lp, lpmod.NORMAL)
        self.lp_fn('set_verbose', lp, lpmod.SEVERE)
        self.lp_fn('set_presolve', lp, 
                    lpmod.PRESOLVE_ROWS | lpmod.PRESOLVE_MERGEROWS )
        self.lp_fn('solve', lp)

        # The same protocol is used in lp_report.c to retrieve results,
        # but there, precision is destroyed by printf "%12g". 
        
        orig_columns = self.lp_fn('get_Norig_columns', lp)
        orig_rows = self.lp_fn('get_Norig_rows', lp)
        assert orig_columns > 0
        assert orig_rows > 0

        MAX_EPSILON = 0.25

        for col in xrange(1, orig_columns + 1):
            vname = self.lp_fn('get_origcol_name', lp, col)
            value_f = self.lp_fn('get_var_primalresult',  lp, 
                        orig_rows + col)
            assert type(vname) == str
            assert value_f > -MAX_EPSILON, "Value is < 0: %s = %1.5f" % (
                        vname, value_f)

            value_i = math.floor(value_f + 0.5)
            epsilon = abs(value_f - value_i)
            assert epsilon < MAX_EPSILON, (
    "lp_solve did not return an integer value for variable %s: %1.5f" % (
            vname, value_f))

            value = int(value_i)

            receive_fn(vname, value)
                

        self.lp_fn('delete_lp', lp)

        return ''

def Initialise():
    global ILP_Solver

    try:
        import lpsolve55
        ILP_Solver = ILP_Solver_LPS
    except:
        ILP_Solver = ILP_Solver_GLPK

    # Find suitable MODEL_FILE_NAME
    name_stem = "20kly_model_%u.mod" % os.getpid()

    # This might work on any OS
    for var in [ "TMP", "TEMP", "TMPDIR" ]:
        value = os.getenv(var)
        if (value != None) and len(value) != 0:
            if Try_Model(os.path.join(value, name_stem)):
                return # done

    # This should work on UNIX
    if Try_Model(os.path.join("/tmp", name_stem)):
        return # done

    # This should work if there is a home directory
    if Try_Model(os.path.join(extra.Get_Home(), name_stem)):
        return # done

    # This should work if the current directory is writeable
    if Try_Model(name_stem):
        return # done

    print "No suitable place for ILP model files."
    print "Please run the program from a writeable directory."
    sys.exit(1)

def Try_Model(full_path):
    global MODEL_FILE_NAME

    MODEL_FILE_NAME = full_path
    try:
        file(MODEL_FILE_NAME, "wt").write("test")
    except:
        return False

    print 'ILP model - %s' % MODEL_FILE_NAME
    atexit.register(Remove_Model)

    # Ok, so this is a writable directory.
    # Test the ILP solver with a trivial problem.
    test = ILP_Solver()    
    test.Add_Var("x", VAR_MIXED)
    test.Add_Var("y", VAR_MIXED)
    test.Add_Term("x + y", ">=", "70")
    test.Add_Term("x", ">=", "50")
    test.Add_Term("y", ">=", "0")
    test.Add_Problem("100*x+y")

    should_be = { "x" : 50, "y" : 20 }
    failure = []

    def Receive(value, data):
        check = should_be.get(value, None)
        if check == None:
            return

        if check != data:
            failure.append("%s should be %d, is %d" % (value, check, data))

    test.Solve(Receive)
    if len(failure) != 0:
        raise ILPError("Wrong answer returned:\n%s" % ('\n'.join(failure)))

    return True

def Remove_Model():
    try:
        os.unlink(MODEL_FILE_NAME)
    except:
        pass


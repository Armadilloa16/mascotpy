##############################################################################
# author: Lyron Winderbaum (lyron.winderbaum@student.adelaide.edu.au)        #
#                                                                            #
##############################################################################
# the MASCOT-provided package msparser comes with the following disclaimer:  #
# COPYRIGHT NOTICE                                                           #
# Copyright 1998-2010 Matrix Science Limited  All Rights Reserved.           #
#                                                                            #
##############################################################################

import msparser
import os, sys, optparse

# Makes appropriate adjustments a string argument so it can be correctly
# represented in LaTeX.
def latexSafe(S):
    return S.replace("\\","\\textbackslash ")\
            .replace("_","\\_")\
            .replace(">","{\\textgreater}")\
            .replace("<","{\\textless}")\
            .replace("[","")\
            .replace("]","")


def main(argv):

    # Parse commandline options
    print
    parser = optparse.OptionParser()
    parser.add_option('-i','--inputfile',dest='i',
                      help="Filename to read mascot MS/MS search results from (.dat)")
    parser.add_option('-o','--outputfile',dest='o',
                      help="Filename to write result too (.tex)")
    parser.add_option('-n','--max-n-proteins',action="store",dest="n",
                      default=50,type="int",help="Max number of proteins to include")
    parser.add_option('-p','--min-probability',action="store",dest="p",
                      default=0.05,type="float",help="Minimum probability to include")
    parser.add_option('-s','--peptide-summary',action="store_true",dest="s",
                      default=False,help="Include peptide summary as well")
    opts, args = parser.parse_args(argv)
    # Check input file is provided extension is `.dat'
    if opts.i is None:
        parser.error('input file not given')
    ifile, fext = os.path.splitext(opts.i)
    if fext not in ('.dat',""):
        opts.i = ifile+'.dat'
        print 'warning: invalid file extension', fext
        print '         attempting to read', ifile+'.dat', 'instead.'
        print
    # If output file is not provided default to input filename
    if opts.o is None:
        opts.o = ifile+'.tex'

    # Let the user know whats up.
    print "mascotpy parameters:"
    print "--------------------"
    print "Input File:         ", opts.i
    print "Output File:        ", opts.o
    print "max # of proetins:  ", opts.n
    print "min probability:    ", opts.p
    print "includePepSummary:  ", opts.s
    print
    
    # Attempt to read inputfile and write outputfile,
    # given maxHits minProteinProb and includePepSummary.
    dat2tex(opts.i,opts.o,opts.n,opts.p,opts.s)
    
 





def dat2tex(inputfile,outputfile=None,maxHits=50,minProteinProb=0.05,includePepSummary=False):

    from django.template import Template, Context
    from django.conf import settings
    settings.configure()
    
    # Parse input parameters.
    if not __name__ == "__main__":
        inputfile, fileExtension = os.path.splitext(inputfile)
        if not fileExtension == ".dat":
            print "Invalid File extension on input file '"+fileExtension+"'"
            print "Attempting to find", inputfile+".dat instead.\n"
        # If no output file was specified use the input filename (.tex)
        if outputfile is None:
            outputfile = inputfile+".tex"
        inputfile = inputfile+".dat"
        try:
            maxHits = int(maxHits)
        except ValueError as e:
            print "Exception in parameter maxNprot:"
            print e
            return 2
        try:
            minProteinProb = float(minProteinProb)
        except ValueError as e:
            print "Exception in parameter minProb:"
            print e
            return 2
        try:
            minProteinProb = bool(includePepSummary)
        except ValueError as e:
            print "Exception in parameter includePepSummary:"
            print e
            return 2
    
    resfile = msparser.ms_mascotresfile(inputfile)
    params = resfile.params()

    if not resfile.isValid():
        print "Cannot process file '%s':" % inputfile
        print resfile.getLastErrorString()
        return 2

    if not resfile.isMSMS():
        print ".dat file '%s' is not an MS/MS search:" % inputfile
        return 2

    flags = msparser.ms_mascotresults.MSRES_GROUP_PROTEINS \
        | msparser.ms_mascotresults.MSRES_SHOW_SUBSETS \
        | msparser.ms_mascotresults.MSRES_DUPE_REMOVE_A \
        | msparser.ms_mascotresults.MSRES_DUPE_REMOVE_B \
        | msparser.ms_mascotresults.MSRES_DUPE_REMOVE_C \
        | msparser.ms_mascotresults.MSRES_DUPE_REMOVE_D \
        | msparser.ms_mascotresults.MSRES_DUPE_REMOVE_E \
        | msparser.ms_mascotresults.MSRES_DUPE_REMOVE_F

    minIonsScore = 0
    minPepLenInPepSummary = 0
    results = msparser.ms_peptidesummary(
        resfile, flags, minProteinProb, maxHits, "", minIonsScore, minPepLenInPepSummary
        )

    # Write output .tex file.
    with open(outputfile,"w") as tex:

        # Preamble
        tex.write("\\documentclass{article}\n\n\n"
                  +"\\usepackage[landscape,margin=2cm]{geometry}\n"
                  +"\\usepackage{multicol}\n"
                  +"\\usepackage{longtable}\n\n\n")
        # Document begin, title.
        tex.write("\\begin{document}\n\n"
                  +"\\begin{center}\n"
                  +"  {\\Huge "+latexSafe(params.getCOM())+"}\n"
                  +"\\end{center}\n\n")
        # MASCOT Search Parameters
        t = Template("\\vspace{2cm}\n"
                     +"\\begin{center}\n"
                     +"  {\\Large MASCOT Search Parameters}\n"
                     +"\\end{center}\n"
                     +"\\begin{center}\n"
                     +"\t\\begin{longtable}{rl}\n"
                     +2*"  " + "Database : & {{ db_name }} \\\\\n"
                     +2*"  " + "Taxonomy : & {{ taxonomy }} \\\\\n"
                     +2*"  " + "Enzyme : & {{ enzyme }} "
                     +"{% if n_cleavages == 0 %}(no missed cleavages)"
                     +"{% elif n_cleavages == 1 %}(up to one missed cleavage)"
                     +"{% else %}(up to {{ n_cleaveages }} missed cleavages)"
                     +"{% endif %} \\\\\n"
                     +2*"  " + "Fixed Modifications :\n"
                     +"{% for mod in fixed_mods %}"
                     +4*"  " + "& " + mod + " \\\\\n"
                     +"{% empty %}
                     +4*"  " + "& \\\\\n"
                     +"{% endfor %}")

        # - remove any preceeding dots '. . .' from taxonomy name
        dot_loc = params.getTAXONOMY()[::-1].find(".")
        if dot_loc != -1:
            tax_name = params.getTAXONOMY()[(len(params.getTAXONOMY())-dot_loc):]
        else:
            tax_name = params.getTAXONOMY()
        mods_fixed = params.getMODS().split(",")
        for i in range(len(mods_fixed)):
            mods_fixed[i] = latexSafe(mods_fixed[i]
            
        
        c = Context({'db_name': latexSafe(params.getDB()),
                     'taxonomy': latexSafe(tax_name),
                     'enzyme': latexSafe(params.getCLE()),
                     'n_cleavages': params.getPFA(),
                     'fixed_mods': mods_fixed})

        
        # - variable modifications
        tex.write(2*"  " + "Variable Modifications :")
        mods_variable = params.getIT_MODS().split(",")
        extra_ws = 1
        for mod in mods_variable:
            tex.write(extra_ws*" " + "& " + latexSafe(mod) + " \\\\\n")
            extra_ws = 2*2 + 25
        # - mass tolerances
        tex.write(2*"  " + "MS Mass Tolerance : & {0} {1} \\\\\n".format(params.getTOL(),params.getTOLU()) \
                  + 2*"  " + "MS/MS Mass Tolerance : & {0} {1} \\\\\n".format(params.getITOL(),params.getITOLU()) \
                  + "  " + "\\end{longtable}\n" \
                  + "\\end{center}\n\n")

        # Protein Summary
        tex.write("\\pagebreak\n"\
                  + "\\begin{center}\n" \
                  + "  " + "{\\Large \\textbf{Protein Summary}}\n"\
                  + "\\end{center}\n"\
                  + "\\begin{center}\n"\
                  + "  " + "\\begin{longtable}{llccccc}\n"\
                  + 2*"  " + "\\textbf{Accession} & \\textbf{Protein} & \\textbf{MW (kDa)} & \\textbf{IDs} & \\textbf{Score} & \\textbf{Coverage} & \\textbf{emPAI} \\\\ \\hline\n")
        prot_wrap_desc = 45
        prot_indent_desc = 5
        hit  = 1
        prot = results.getHit(hit)
        while prot:
            accession   = prot.getAccession()
            tex.write(2*"  " + latexSafe(accession) + "\n")
            # - curtail descriptions that are too long.
            description = results.getProteinDescription(accession)
            if len(description) <= prot_wrap_desc:
                tex.write(2*"  " + "& " + latexSafe(description) + "\n")
            else:
                tex.write(2*"  " + "& " + latexSafe(description[:prot_wrap_desc]) + "\n")
            tex.write(2*"  " + "& {0:.2f} %Mass\n".format(results.getProteinMass(accession)/1000)\
                      + 2*"  " + "& {0} %IDs\n".format(prot.getNumPeptides())\
                      + 2*"  " + "& {0:.2f} %Score\n".format(prot.getScore())\
                      + 2*"  " + "& {0} %Coverage\n".format(prot.getCoverage())\
                      + 2*"  " + "& {0:.2f} %emPAI\n".format(results.getProteinEmPAI(accession))\
                      + 2*"  " + "\\\\\n")
            # - include remaining description as wrapped text.
            prot_loc_desc = prot_wrap_desc
            while prot_loc_desc < len(description):
                if len(description) - prot_loc_desc < (prot_wrap_desc-prot_indent_desc):
                    tex.write(2*"  " + "&" + prot_indent_desc*" " + "\\hspace{"+str(prot_indent_desc)+"ex}" + latexSafe(description[prot_loc_desc:]) + 5*" &" + " \\\\\n")
                else:
                    tex.write(2*"  " + "&" + prot_indent_desc*" " + "\\hspace{"+str(prot_indent_desc)+"ex}" + latexSafe(description[prot_loc_desc:(prot_loc_desc+(prot_wrap_desc-prot_indent_desc))]) + 5*" &" + " \\\\\n")
                prot_loc_desc += (prot_wrap_desc-prot_indent_desc)
            hit += 1
            prot = results.getHit(hit)
        tex.write("  " + "\\end{longtable}\n"\
                  + "\\end{center}\n\n")

        # Peptide Summary
        if includePepSummary:
            tex.write("\\pagebreak\n"\
                      + "\\begin{center}\n"\
                      + "  " + "{\\Large \\textbf{Peptide Summary}}\n"\
                      + "\\end{center}\n"\
                      + "\\begin{center}\n"\
                      + "  " + "\\begin{longtable}{llcc}\n")
            pep_wrap_desc = 85
            pep_indent_desc = 15
            pep_wrap_str = 25
            pep_indent_str = 5
            hit  = 1
            prot = results.getHit(hit)
            while prot:
                accession   = prot.getAccession()
                description = results.getProteinDescription(accession)
                num_peps = prot.getNumPeptides()
                tex.write(2*"  " + "\\multicolumn{4}{c}{\\textbf{"+latexSafe(accession)+"}} \\\\\n")
                if len(description) <= pep_wrap_desc:
                    tex.write(2*"  " + "\\multicolumn{4}{c}{\\textbf{"+latexSafe(description)+"}} \\\\\n")
                else:
                    tex.write(2*"  " + "\\multicolumn{4}{c}{\\textbf{"+latexSafe(description[:85])+"}} \\\\\n")
                pep_loc_desc = pep_wrap_desc
                while pep_loc_desc < len(description):
                    if len(description) - pep_loc_desc < (pep_wrap_desc - pep_indent_desc) :
                        tex.write(2*"  " + "\\multicolumn{4}{c}{\\textbf{"+latexSafe(description[pep_loc_desc:])+"}} \\\\\n")
                    else:
                        tex.write(2*"  " + "\\multicolumn{4}{c}{\\textbf{"+latexSafe(description[pep_loc_desc:(pep_loc_desc+(pep_wrap_desc - pep_indent_desc))])+"}} \\\\\n")
                    pep_loc_desc += (pep_wrap_desc - pep_indent_desc)
                tex.write(2*"  " + "& & & \\\\\n"\
                          + 2*"  " + "& \\textbf{Variable} & &  \\textbf{(Identity/Homology)} \\\\\n"\
                          + 2*"  " + "\\textbf{Peptide} & \\textbf{Modifications} & \\textbf{Score} & \\textbf{Thresholds} \\\\ \\hline\n")
                for i in range(1, 1+num_peps):
                    q = prot.getPeptideQuery(i)
                    p = prot.getPeptideP(i)
                    if p == -1 or q == -1:
                        continue
                    pep = results.getPeptide(q, p)
                    if not pep:
                        continue
                    pep_str = pep.getPeptideStr()
                    var_mods = results.getReadableVarMods(q, pep.getRank()).split("; ")
                    if len(pep_str) <= pep_wrap_str :
                        tex.write(2*"  " + pep_str + " \n")
                    else:
                        tex.write(2*"  " + pep_str[:pep_wrap_str] + " \n")
                    tex.write(2*"  " + "& " + latexSafe(var_mods[0])\
                              + " & {0:.1f}".format(pep.getIonsScore())\
                              + " & ({0:.1f}/{1:.1f})".format(results.getPeptideThreshold(q,1/minProteinProb,1,msparser.ms_mascotresults.TT_IDENTITY),\
                              results.getPeptideThreshold(q,1/minProteinProb,1,msparser.ms_mascotresults.TT_HOMOLOGY)) + " \\\\\n")
                    pep_loc_var_mods = 1
                    pep_loc_str = pep_wrap_str
                    while (pep_loc_var_mods < len(var_mods)) or (pep_loc_str < len(pep_str)):
                        if not (pep_loc_var_mods < len(var_mods)) and (pep_loc_str < len(pep_str)):
                            if len(pep_str) - pep_loc_str < (pep_wrap_str - pep_indent_str):
                                tex.write(2*"  " + pep_indent_str*" " + pep_str[pep_loc_str:] + " & & & \\\\\n")
                            else:
                                tex.write(2*"  " + pep_indent_str*" " + \
                                          pep_str[pep_loc_str:(pep_loc_str+(pep_wrap_str - pep_indent_str))] + " & & & \\\\\n")
                        elif (pep_loc_var_mods < len(var_mods)) and  not (pep_loc_str < len(pep_str)):
                            tex.write(2*"  " + "& " + latexSafe(var_mods[pep_loc_var_mods]) + " & & \\\\\n")
                        elif (pep_loc_var_mods < len(var_mods)) and (pep_loc_str < len(pep_str)):
                            if len(pep_str) - pep_loc_str < (pep_wrap_str - pep_indent_str):
                                tex.write(2*"  " + pep_indent_str*" " + pep_str[pep_loc_str:]\
                                          + " & " + latexSafe(var_mods[pep_loc_var_mods]) + " & & \\\\\n")
                            else:
                                tex.write(2*"  " + pep_indent_str*" " + \
                                          pep_str[pep_loc_str:(pep_loc_str+(pep_wrap_str - pep_indent_str))]\
                                          + " & " + latexSafe(var_mods[pep_loc_var_mods]) + " & & \\\\\n")
                        pep_loc_str += (pep_wrap_str - pep_indent_str)
                        pep_loc_var_mods += 1
                tex.write(2*"  " + "& & & \\\\\n"\
                          + 2*"  " + "& & & \\\\\n"\
                          +2*"  " + "& & & \\\\\n")
                hit += 1
                prot = results.getHit(hit)
            tex.write("  " + "\\end{longtable}\n"\
                      + "\\end{center}\n\n")
        
        tex.write("\\end{document}")








if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))





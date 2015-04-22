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
import os, sys, getopt

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

    inputfile = ''
    outputfile = ''
    maxHits = 50
    minProteinProb = 0.05
    includePepSummary = False
    # Parse commandline options
    print
    try:
        opts, args = getopt.getopt(argv,"ho:N:P:s",["help","ofile=","maxNprot=","minProb=","summary"])
    except getopt.GetoptError as e:
        print 'Error parsing options:'
        print e.msg
        return 2
    for opt, arg in opts:
        if opt in ("-h","--help") :
            print "Help documentation"
            return 0
        elif opt in ("-o","--ofile"):
            outputfile, fileExtension = os.path.splitext(arg)
            if fileExtension not in ("",".tex") :
                print "Invalid File extension on output file ", fileExtension
                print "Writing to ", outputfile, ".tex instead."
        elif opt in ("-N","--maxNprot"):
            try:
                maxHits = int(arg)
            except ValueError as e:
                print "Error in option maxNprot:"
                print e
                return 2
        elif opt in ("-P","--minProb"):
            try:
                minProteinProb = float(arg)
            except ValueError as e:
                print "Error in option minProb:"
                print e
                return 2
        elif opt in ("-s","--summary"):
            includePepSummary = True
    # Parse inputfile
    if len(args) > 0:
        inputfile, fileExtension = os.path.splitext(args[0])
        if fileExtension not in ("",".dat"):
            print "Invalid File extension on input file '"+fileExtension+"'"
            print "Attempting to find", inputfile+".dat instead.\n"
    else :
        print "Error: No input file provided."
        return 2
    # If no outputfile provided, use the same name of the input file.
    if outputfile == '':
        outputfile = inputfile

    # Let the user know whats up.
    print "MASCOTpyLaTeX Operating Parameters:"
    print "Input File:\t\t", inputfile+".dat"
    print "Output File:\t\t", outputfile+".tex"
    print "maxNhits:\t\t", maxHits
    print "minProb:\t\t", minProteinProb
    print "includePepSummary:\t", includePepSummary
    print




    resfile = msparser.ms_mascotresfile(inputfile+".dat")
    params = resfile.params()

    if not resfile.isValid():
        print "Cannot process file '%s':" % inputfile
        print resfile.getLastErrorString()
        return 2

    if resfile.isMSMS():

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
        with open(outputfile+".tex","w") as tex:

            # Preamble
            tex.write("\\documentclass{article}\n\n\n"\
                      +"\\usepackage[landscape,margin=2cm]{geometry}\n"\
                      +"\\usepackage{multicol}\n"\
                      +"\\usepackage{longtable}\n\n\n")
            # Document begin, title.
            tex.write("\\begin{document}\n\n"\
                      +"\\begin{center}\n"\
                      +"  {\\Huge "+latexSafe(params.getCOM())+"}\n"\
                      +"\\end{center}\n\n")

            # MASCOT Search Parameters
            tex.write("\\vspace{2cm}\n"\
                      +"\\begin{center}\n"\
                      +"  {\\Large MASCOT Search Parameters}\n"\
                      +"\\end{center}\n"\
                      +"\\begin{center}\n"\
                      +"\t\\begin{longtable}{rl}\n")
            # - database
            tex.write(2*"  " + "Database : & " + latexSafe(params.getDB()) + " \\\\\n")
            # - taxonomy (remove preceeding dots '. . .')
            dot_loc = params.getTAXONOMY()[::-1].find(".")
            if dot_loc != -1:
                tax_name = params.getTAXONOMY()[(len(params.getTAXONOMY())-dot_loc):]
            else:
                tax_name = params.getTAXONOMY()
            tex.write(2*"  " + "Taxonomy : & " + latexSafe(tax_name) + " \\\\\n")
            # - enzyme (missed cleavages)
            enz_name = params.getCLE()
            n_missed_cleave = params.getPFA()
            if n_missed_cleave == 0:
                cleave_sentence = "no missed cleavages"
            elif n_missed_cleave == 1:
                cleave_sentence = "up to " + str(n_missed_cleave) + " missed cleavage"
            else:
                cleave_sentence = "up to " + str(n_missed_cleave) + " missed cleavages"
            tex.write(2*"  " + "Enzyme : & "+ latexSafe(enz_name) + " (" + cleave_sentence + ") \\\\\n")
            # - fixed modifications
            tex.write(2*"  " + "Fixed Modifications :")
            mods_fixed = params.getMODS().split(",")
            extra_ws = 1
            for mod in mods_fixed:
                tex.write(extra_ws*" " + "& " + latexSafe(mod) + " \\\\\n")
                extra_ws = 2*2 + 22
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


    else:
        print "Not an MS-MS results file - cannot show peptide summary report"


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))





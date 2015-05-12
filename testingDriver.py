

def latexSafe(S):
    return S.replace("\\","\\textbackslash ")\
            .replace("_","\\_")\
            .replace(">","{\\textgreater}")\
            .replace("<","{\\textless}")\
            .replace("[","")\
            .replace("]","")


A = "Hello\\,Goodbue[],Hmm".split(",")
print A
for i in range(len(A)):
    A[i] = latexSafe(A[i])
print A





##import mascotpy

##mascotpy.dat2tex("../mascotpy_test/F013394.dat","test.tex","Hello",includePepSummary="Hello")

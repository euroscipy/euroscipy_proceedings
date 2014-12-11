# This script allows one to recreate the figure sequence_
"""
# Download data from uniprot 

# 1. First, need to get the uniprot entries for HUMAN. This can be 
# done by going to uniprot website 
i

::

    wget ftp://ftp.ebi.ac.uk/pub/databases/uniprot/knowledgebase/uniprot_sprot.fasta.gz

then un a unix shell, type::

    gunzip uniprot_sprot.fasta.gz
    grep sp uniprot_sprot.fasta  | grep HUMAN | awk '{print substr($1, 12,  length($1))}' > entries.txt

"""

from bioservices import *
u = UniProt(verbose=True)
df = pd.read_csv(StringIO.StringIO(res.content.strip()), sep="\t")
import StringIO
entries = pd.read_csv("/home/cokelaer/entries.txt", header=None)
entries = list(entries[0].as_matrix())

# This command takes a while: about 20 minutes with a good connection.
# This will download lots of fields from uniprot for each entry.
# Later on we will play with the sequence length, which could
# have been extracted from the downloaded file but this example
# if for illustration.

# obtain a dataframe filled with all data from all entries
df = u.get_df() 

# let us build a vector made of the length of the sequence.
# we restrict ourself to 3000 nucleotides
data = df[df.Length<3000].Length


# now, we may want to figure out wha kind of distribution this sample is conng
# from. We will use the package called fitter, available on pypi with a layer
# built on top of scipy (distribution and fit)
import fitter
f = fitter.Fitter(data, bins=150)
f.distributions = ['lognorm', 'chi2', 'rayleigh', 'cauchy', 'invweibull']
f.fit()
f.summary()
f.summary(lw=3)
xlabel("Sequence length", fontsize=20)
ylabel("PDF", fontsize=20)
savefig("sequence_length_fitting.png", dpi=200)
savefig("sequence_length_fitting.eps", dpi=200)
savefig("sequence_length_fitting.svg", dpi=200)









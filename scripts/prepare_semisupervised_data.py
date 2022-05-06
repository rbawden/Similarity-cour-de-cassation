#!/usr/bin/python
import re

def prepare_data(sommaire_file, titrage_file):
    with open(sommaire_file) as sfp, open(titrage_file) as tfp:
        for matiere_sommaire, titrage in zip(sfp, tfp):
            titres = re.split(' *<t> *', titrage.strip())
            matiere, sommaire = re.split(' *<t> *', matiere_sommaire.strip())
            # one example for each level
            for t in range(len(titres)):
                if t == 0:
                    print(' <t> '.join([matiere, sommaire]) + '\t' + titres[t])
                else:
                    print(' <t> '.join([matiere,' <t> '.join(titres[:t]), sommaire]) + '\t' + titres[t])
            # end of sequence (empty)
            print(' <t> '.join([matiere,' <t> '.join(titres), sommaire]) + '\t' + '')

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('sommaire_file')
    parser.add_argument('titrage_file')
    args = parser.parse_args()
    
    prepare_data(args.sommaire_file, args.titrage_file)

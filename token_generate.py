#!/usr/bin/env python3

import argparse
from random import choice

def main(args):

    s = 'abcdefghjkmnpqrstuvwxyz23456789'
    for i in range(args.numtokens):
        token = ''
        for i in range(7):
            letter = choice(s)
            token += letter
        print(token)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Script to generate and send voting tokens')
    parser.add_argument('--numtokens', type=int, 
                        help='how many voting tokens to make', required=True)
    parser.add_argument('--mail_tokens', action='store_true', default=False)
    args = parser.parse_args()
    main(args)